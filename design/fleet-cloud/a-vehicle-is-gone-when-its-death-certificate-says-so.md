---
title: A vehicle is gone when its death certificate says so, not when data stops
type: pattern
cluster: fleet-cloud
component: none
tags: [sparkplug, nbirth, ndeath, last-will, liveliness, zenoh, presence]
status: draft
sources:
  - https://sparkplug.eclipse.org/specification/ (sections 2.4, 5.5, 5.13; tck ids on bdSeq, Rebirth)
  - repos/zenoh/zenoh/src/api/liveliness.rs
  - repos/zenoh/DEFAULT_CONFIG.json5 (link lease 10000 ms, keep_alive 4)
last-verified: 2026-10-03
related:
  - "[[zenoh-overview]]"
  - "[[uprotocol-overview]]"
applies-to: [zenoh, uprotocol, sdv-blueprints]
gap-rows: [B1, A10]
---

# A vehicle is gone when its death certificate says so, not when data stops

**Problem.** The backend infers "offline" from silence. A parked truck, a signal that only sends on change and a tunnel all look the same as a dead one, and a reconnecting vehicle leaves stale "online" rows behind.

**Forces.**
- Cellular links drop without a goodbye; a clean shutdown is the exception.
- Silence is also normal for on-change signals and parked vehicles.
- A backend that restarts has lost the vehicle's state and must ask for it again.
- Presence must be cheap per vehicle: a million idle heartbeats cost real money.

**The rule.** Presence is a first-class message with a session identity, and the broker or session layer, not the vehicle, announces the death. Sparkplug does it with MQTT: the node registers an NDEATH as the Will in CONNECT (QoS 1, retain false) carrying a `bdSeq`; its NBIRTH carries the same `bdSeq`, the full metric set and `Node Control/Rebirth=false`. A host that sees NDEATH with a matching `bdSeq` marks the node and all its devices offline; a stale NDEATH from an older session has a different `bdSeq` and is ignored. `seq` (0-255, wrapping) on every data message exposes gaps; on a gap or a restarted host, the host publishes NCMD `Node Control/Rebirth=true` and the node answers with a fresh NBIRTH. Zenoh gives the same primitive natively: a liveliness token declared on `fleet/<vin>/alive` produces a `Put` for subscribers when it appears and a `Delete` when the session closes or its lease expires; `liveliness().get("fleet/**")` lists who is alive now, which is the "backend just restarted" answer.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Sparkplug B NBIRTH/NDEATH/DBIRTH | birth certificate first, death as MQTT Will, bdSeq pairing | ordered, correlated presence on any broker |
| Sparkplug Rebirth | `Node Control/Rebirth` command | state recovery without retained data |
| Zenoh liveliness tokens | token tied to session; put/delete events; get | presence on the data plane, router-less |
| MQTT retained Will / STATE | primary host announces ONLINE/OFFLINE | the host's own presence, so nodes know when to rebirth |
| Hono connection events | gateway/device connected notification (unverified details) | the same fact from the ingestion side |

**On the Eclipse SDV stack.**
- fleet-management has no presence at all: the consumer learns of a vehicle from the first VehicleStatus with a VIN and never learns it left; `/rfms/vehicles` is derived from distinct `vin` tags in Influx ([[sdv-blueprints-overview]]).
- uProtocol has no presence message. Define a Notification from each vehicle authority (resource `birth`, `death`) and publish a Zenoh liveliness token on the same key; this is part of gap A10 (a heartbeat/fault/event schema) and B1 (bridge).
- Across a uStreamer, a liveliness token is not forwarded (it is a Zenoh feature, not a uMessage). Test it before relying on it; unverified.
- Lease: 10 s link lease, keep_alive 4 per lease (default config), so a Zenoh death is detected in roughly 10 s, tunable per link.

**The trap.** Treating "no data for N seconds" as offline, so every quiet on-change signal flaps the vehicle.

**For a hackathon team.** Declare `fleet/<vin>/alive`, kill the vehicle container with `kill -9`, and show the dashboard tile turning grey within the lease, then recovering via `liveliness().get`. Pitch: "death is an event, not an absence".

**Evidence.** bdSeq/Rebirth/Will rules: Sparkplug 3.0 text (fetched PDF, tck-id-topics-nbirth-bdseq-*, tck-id-operational-behavior-data-commands-rebirth-*, message-flow Will QoS 1 and retain false). Liveliness API examples and semantics: repos/zenoh/zenoh/src/api/liveliness.rs. Lease: DEFAULT_CONFIG.json5. uStreamer not forwarding liveliness: unverified inference from the streamer's uMessage-only filters.
