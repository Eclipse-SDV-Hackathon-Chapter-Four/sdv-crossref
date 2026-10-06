---
title: A reboot is a new session, not the same producer continuing
type: pattern
cluster: identity-discovery
component: none
tags: [identity, session, reboot, someip-sd, sparkplug, dds, zenoh, iceoryx2, sequence, freshness]
status: draft
sources:
  - https://www.autosar.org/fileadmin/standards/R23-11/FO/AUTOSAR_FO_PRS_SOMEIPServiceDiscoveryProtocol.pdf (Reboot Flag + Session ID, PRS_SOMEIPSD_00254..00256, 00631; reboot detection rule)
  - https://sparkplug.eclipse.org/specification/version/3.0/documents/sparkplug-specification-3.0.0.pdf (`bdSeq` per MQTT CONNECT; `seq` restarts in NBIRTH)
  - https://www.omg.org/spec/DDSI-RTPS/2.5/PDF (participant GUID, leaseDuration, removal of a discovered participant §8.5.5.2)
  - repos/zenoh/zenoh/src/api/liveliness.rs (token tied to the session)
  - repos/iceoryx2/iceoryx2/src/node/mod.rs (NodeState, UniqueNodeId)
last-verified: 2026-10-03
related:
  - "[[claim-the-address-keep-the-name]]"
  - "[[a-vehicle-is-gone-when-its-death-certificate-says-so]]"
  - "[[the-birth-certificate-is-the-schema-data-only-refers-to-it]]"
  - "[[open-on-arrival-age-by-your-own-deadline]]"
  - "[[uprotocol-overview]]"
applies-to: [iceoryx2, zenoh, uprotocol, opensovd, vss-kuksa]
gap-rows: [A8, A10, A5]
---

# A reboot is a new session, not the same producer continuing

**Problem.** A trailer ECU reboots in two seconds. Its instance identity is unchanged, so consumers keep their state: sequence-gap detectors fire on a counter that restarted, subscriptions the provider forgot are assumed alive, and an "accumulated" value silently resets. Or the reverse: a stale message from before the reboot is taken as current.

**Forces.**
- Instance identity (which trailer) must survive reboots; archives key on it.
- Per-session state (subscriptions, counters, aliases, negotiated QoS) must not.
- Reboots can be faster than any timeout, so liveness timeouts alone miss them.
- Messages can be reordered across the reboot boundary.

**The rule.** Give every producer a **session identity** next to its instance identity, and make every stateful consumer reset on a session change. Detect the change explicitly, not by timeout. SOME/IP-SD sets a Reboot Flag in every message until the Session ID first wraps; a receiver detects a reboot if the flag goes 0→1, or stays 1 while the session id does not increase, kept per sender-receiver pair — and on detection the client must re-subscribe. Sparkplug increments `bdSeq` on every MQTT CONNECT and restarts `seq` in NBIRTH, so hosts can tell the new session from the old one's late NDEATH. RTPS gives each participant incarnation a new GUID with a lease. Zenoh liveliness tokens die with the session. Instance key in the name; session id in the header or announcement; never the other way round.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| SOME/IP-SD | Reboot Flag + Session ID per sender-receiver relation; explicit detection rule | reboots detected even when faster than TTL |
| Sparkplug B | `bdSeq` per connection, `seq` restart at birth | correlate death with the right birth; ignore stale deaths |
| DDSI-RTPS | new participant GUID per incarnation, lease-based removal | old endpoints purged, new ones rediscovered |
| Zenoh liveliness | token bound to session; Delete on drop/crash/disconnect | session end is an event |
| J1939 address claim | a rebooted ECU re-claims; consumers re-resolve NAME→address | same NAME, new lease |

**On the Eclipse SDV stack.**
- iceoryx2: each `Node` has a `UniqueNodeId`; record it with each opened port, and when a producer's node is `Dead` and a new node re-creates the service, treat it as a new session (reset gap counters and history) ([[open-on-arrival-age-by-your-own-deadline]]).
- uProtocol: UAttributes carry a UUIDv7 message id but no session id; a heartbeat/fault schema (gap A10) should add `session_id` (e.g. a UUIDv7 minted at boot) so watchdogs (gap A8) distinguish "restarted" from "frozen" ([[uprotocol-overview]]).
- Evidence recorder (gap A5): split recordings by (instance, session) so a replay never stitches two boots together.
- KUKSA: the databroker has no persistence; a broker restart is a new session for every provider, which must re-claim and republish ([[vss-kuksa-reference]]).

**The trap.** Using a monotonically increasing sequence number as both freshness check and identity, so the first message after a reboot is rejected as "old" or the gap alarm fires on every power cycle.

**For a hackathon team.** Add a boot-time UUIDv7 `session_id` to a heartbeat message; kill and restart the producer in under a second and show the watchdog log "restart (new session)" instead of "frozen" or "gap". Pitch: "same trailer, new life — and we can tell".

**Evidence.** SOME/IP-SD PRS_SOMEIPSD_00254/00255 (Reboot Flag until Session ID wraps), 00631 (per sender-receiver), detection rule text after 00256 ("if old.reboot==0 and new.reboot==1 then Reboot detected OR …"). Sparkplug `tck-id-topics-nbirth-bdseq-increment`, `tck-id-payloads-sequence-num-zero-nbirth`. RTPS 2.5 §8.5.5.2. Zenoh `LivelinessToken` doc comment. iceoryx2 `NodeState` enum. That SOME/IP clients re-subscribe on detected reboot is the commonly implemented behaviour; the exact PRS id was not located in this session (unverified).
