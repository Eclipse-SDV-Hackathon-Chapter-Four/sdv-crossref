---
title: One key scheme from MCU to cloud, fleet id as the first prefix
type: pattern
cluster: fleet-cloud
component: none
tags: [keys, zenoh, uprotocol, mqtt, sparkplug, fleet, namespace]
status: draft
sources:
  - https://github.com/eclipse-zenoh/roadmap/blob/main/rfcs/ALL/Key%20Expressions.md
  - https://sparkplug.eclipse.org/specification/ (section 4.1 topic namespace)
  - repos/up-spec/up-l1/zenoh.adoc (Zenoh Key Structure, UUri Encoding Rules)
  - repos/zenoh/DEFAULT_CONFIG.json5 (namespace, access_control)
last-verified: 2026-10-03
related:
  - "[[zenoh-overview]]"
  - "[[uprotocol-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[instance-in-the-name-type-in-the-hash]]"
applies-to: [zenoh, uprotocol, vss-kuksa, sdv-blueprints]
gap-rows: [B1, B8]
---

# One key scheme from MCU to cloud, fleet id as the first prefix

**Problem.** One key grammar on the MCU (zenoh-pico), another in the vehicle (VSS paths), a third in the broker (MQTT topics), a fourth in the cloud (Influx tags). Every seam is a hand-written mapper, and a thousand vehicles multiply the mappers.

**Forces.**
- A fleet view wants `fleet/*/speed`; a vehicle wants only its own subtree.
- Wildcards are only as good as the position of the segment they match.
- MCUs cannot afford long keys or a second encoding; the cloud wants human-readable ones.
- ACLs and downsampling rules attach to key expressions, so key shape is also policy shape.

**The rule.** Put the instance id first, the type path after it, and keep one grammar end to end. Zenoh key expressions are `/`-separated chunks where `*` matches one chunk and `**` any number; with `<fleet>/<vin>/<type path>` a fleet dashboard subscribes `fleet/*/vss/Vehicle/Speed`, one truck's debugger `fleet/<vin>/**`. Sparkplug fixes the same shape for MQTT (`spBv1.0/group_id/message_type/edge_node_id/device_id`: group = fleet, edge node = vehicle, device = ECU). uProtocol's Zenoh mapping already does it: `up/<authority>/<type>/<instance>/<version>/<resource>`, so authority is the instance slot. Vehicle-side code stays unaware of the prefix: Zenoh's session `namespace` config prefixes every outgoing key and strips it on the way in, and it may not contain wildcards.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Zenoh key expressions | chunks, `*`, `**`, `$*`; session `namespace` | one grammar MCU (zenoh-pico) to cloud, prefix without code change |
| uProtocol UUri over Zenoh | `up/authority/type/instance/version/resource`, upper-case hex ids | instance and wildcard slots defined by spec |
| MQTT Sparkplug B | `spBv1.0/group/msgtype/edge/device` | the fleet/vehicle/ECU tree on MQTT |
| COVESA VISS v2 | `*` matches one path segment | the same one-segment wildcard on a VSS tree |
| Eclipse Hono | `(tenant-id, device-id)` tuple | tenant as the fleet, device as the vehicle |

**On the Eclipse SDV stack.**
- VSS paths become keys by replacing `.` with `/`: this is gap B8 and is what [[zenoh-integration-notes]] calls "idea". The `zenoh-kuksa-provider` in service-to-signal already publishes `Vehicle/Body/Horn/IsActive` ([[sdv-blueprints-overview]]), but with no vehicle prefix.
- Choose per signal class: raw VSS keys (B8) when the envelope is not needed, UUri keys (B1) when RPC and notification matter. Do not mix both on one router without a prefix split (`vss/` versus `up/`).
- The fleet-management blueprint publishes on `up/fms-forwarder/D100/1/D100`-style keys for every truck and puts the VIN only in the protobuf payload; a router cannot filter by VIN there ([[fleet-telemetry-batched-at-the-vehicle-keyed-by-vin]]).

**The trap.** Putting the instance last (`vss/Vehicle/Speed/<vin>`): `**` then cannot be bounded and per-vehicle ACLs become impossible.

**For a hackathon team.** Two simulated vehicles publish `fleet/<vin>/vss/...` through one `zenohd`; one dashboard subscribes `fleet/*/vss/Vehicle/Speed`; the vehicle code is identical in both because the VIN comes from the session namespace. Pitch: "one key scheme from MCU to cloud".

**Evidence.** Zenoh `namespace` and ACL: repos/zenoh/DEFAULT_CONFIG.json5. UUri-to-key mapping: repos/up-spec/up-l1/zenoh.adoc. Sparkplug namespace: spec section 4.1.1 (fetched). VISS wildcard: W3C VISS v2 core (fetched summary). Chunk grammar (`*`, `**`, `$*`) from the Zenoh Key Expressions RFC, quoted from memory (unverified against the current RFC text). "Fleet-management has no VIN in the key": repos/fleet-management/components/fms-forwarder/src/main.rs.
