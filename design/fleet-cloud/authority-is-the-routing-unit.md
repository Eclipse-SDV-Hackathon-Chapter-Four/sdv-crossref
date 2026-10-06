---
title: The authority is the routing unit, so name it per vehicle and lowercase
type: pattern
cluster: fleet-cloud
component: none
tags: [uprotocol, ustreamer, authority, bridging, fleet, vin]
status: draft
sources:
  - repos/up-spec/basics/uri.adoc (Authority, lowercase-only grammar, 128 chars)
  - repos/up-spec/up-l1/zenoh.adoc
  - repos/up-streamer-rust/up-streamer/README.md
  - repos/sdv_lab/uprotocol/README.md
  - repos/fleet-management/components/fms-forwarder/src/main.rs
last-verified: 2026-10-03
related:
  - "[[uprotocol-overview]]"
  - "[[uprotocol-howto]]"
  - "[[chapter3-retrospective]]"
applies-to: [uprotocol, zenoh, sdv-blueprints]
gap-rows: [B1, B5]
---

# The authority is the routing unit, so name it per vehicle and lowercase

**Problem.** Two trucks both announce themselves as authority `fms-forwarder`. The uStreamer sees one authority and bridges nothing between them; messages for "the other one" loop back or vanish.

**Forces.**
- The spec defines authority as the deployment location, "a domain name or a VIN" (uri.adoc), so it is the natural per-vehicle key.
- The streamer holds one endpoint per authority and forwards by authority only.
- VINs are upper-case; the UUri authority grammar is `lc-unreserved` only, max 128 chars, no port, no userinfo.
- Version drift changes strictness (Chapter 3: up-rust 0.7.1 tightened authority rules and broke up-transport-zenoh).

**The rule.** One authority per host that must be addressable separately, derived from the vehicle id, lowercased. A uStreamer endpoint is `(authority, transport)`; `forwarding` lists the endpoints it feeds. The same authority on two hosts is never bridged, because the streamer cannot tell them apart. Local (empty) authority is rewritten by the transport to the host's own, so code written with an empty authority is portable but unaddressable from outside.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| uProtocol UUri | authority_name = deployment location | the per-host slot in every address |
| up-streamer-rust | endpoint per authority, static forwarding and subscription file | explicit bridge topology, no flooding |
| MQTT Sparkplug | edge_node_id unique inside group_id | same uniqueness rule, enforced by topic |
| DNS / mDNS | host name as routing label | why lowercase and no port belong in the grammar |
| Hono (tenant, device) | identity tuple, not a bare device id | tenant scopes the id |

**On the Eclipse SDV stack.**
- `streamer_uuri.authority` and each `transports.*.endpoints[].authority` in the streamer `CONFIG.json5` must equal the authority apps put in their source UUri ([[uprotocol-howto]] section on pitfalls). Pub/sub additionally needs a `subscription_data.json` entry; RPC and notifications route by sink authority.
- The sdv_lab streamer config in repos/sdv_lab uses mixed-case authorities (`EGOVehicle`, `CruiseControl`, `AAOS`) while the spec grammar is lowercase-only; it works only for the version it pinned. A VIN as authority must be lowercased (`wdd16900512...`).
- fms-forwarder and fms-consumer default to `up://fms-forwarder/...` and `up://fms-consumer/...`: every truck would share one authority ([[sdv-blueprints-overview]]). Pass `--topic up://<vin-lower>/D100/1/D100` per truck.

**The trap.** Reusing the demo's authority string on every vehicle (or upper-casing the VIN), then debugging why only one vehicle is reachable.

**For a hackathon team.** Run two forwarder containers with `--topic up://vin0001/D100/1/D100` and `vin0002`, one consumer with `up://*/D100/1/D100`, and show two series in Influx. Pitch: "authority = vehicle".

**Evidence.** Lowercase and 128-char rules: repos/up-spec/basics/uri.adoc lines 76-145. Streamer endpoint-per-authority: up-streamer README sequence diagram (`uauthority_to_uuri`). "Never bridged" is the vault's [[uprotocol-howto]] claim; code read supports it but no test was run (unverified at runtime). sdv_lab mixed case: repos/sdv_lab/uprotocol/ustreamer/config/CONFIG.json5.
