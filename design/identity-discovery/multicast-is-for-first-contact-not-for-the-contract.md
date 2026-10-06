---
title: Multicast is for first contact, not for the contract
type: pattern
cluster: identity-discovery
component: none
tags: [discovery, multicast, mdns, dns-sd, sovd, zenoh, scouting, udiscovery, docker, wifi]
status: draft
sources:
  - https://www.rfc-editor.org/rfc/rfc6762 (mDNS: link-local, 224.0.0.251, TTL 120 s / 75 min, goodbye TTL 0)
  - https://www.rfc-editor.org/rfc/rfc6763 (DNS-SD: <Instance>.<Service>.<Domain>, TXT key=value, txtvers)
  - https://www.w3.org/TR/wot-discovery/ (two-phase introduction / exploration; `_wot._tcp`)
  - https://github.com/ros2/rmw_zenoh/blob/rolling/docs/design.md (UDP multicast scouting disabled by default, and why)
  - repos/zenoh/DEFAULT_CONFIG.json5 (scouting.multicast 224.0.0.224:7446, ttl 1; gossip scouting)
  - repos/up-spec/up-l3/udiscovery/v3/service.adoc (uDiscovery tree, replication by a trusted OTA uEntity, ttl)
last-verified: 2026-10-03
related:
  - "[[run-a-router-only-where-multicast-cannot-reach]]"
  - "[[advertise-the-https-url-or-do-not-advertise]]"
  - "[[ros-over-zenoh-needs-a-router-and-a-contract]]"
  - "[[opensovd-reference]]"
  - "[[zenoh-overview]]"
  - "[[uprotocol-overview]]"
applies-to: [opensovd, zenoh, uprotocol, iceoryx2, ankaios]
gap-rows: [H9, B2, C1, C8]
---

# Multicast is for first contact, not for the contract

**Problem.** The demo worked on the laptop. At the venue the Wi-Fi isolates clients and filters multicast, the containers sit on separate networks or hosts (a single default Docker bridge did forward it here (corrected 2026-10-03, see [[zenoh-overview]])), and half the services never find each other. In a vehicle the opposite failure: anything that answers a multicast probe joins, including the wrong robot on the same LAN.

**Forces.**
- Zero configuration is valuable for a tester plugged into an unknown vehicle.
- Multicast is link-local by design (mDNS uses 224.0.0.251, Zenoh scouting uses IP TTL 1) and cannot cross a router or a NAT; a Linux bridge does forward it between its ports (corrected 2026-10-03, see [[zenoh-overview]]).
- A vehicle's set of services is known at install time; it is not a coffee-shop LAN.
- Discovery data is metadata that may need authentication.

**The rule.** Use multicast to **introduce** (find a candidate endpoint on the local link), never to **define** who talks to whom. The contract — which services exist, where, at what version — comes from installed knowledge (a manifest, a replicated directory) or an explicit endpoint, and the introduced endpoint is then explored over an authenticated channel. W3C WoT Discovery names this split: an open *introduction* phase (direct URL, `/.well-known/wot`, DNS-SD `_wot._tcp`) and an *exploration* phase that returns descriptions "only after suitable authentication". uProtocol uDiscovery takes the installed route: a DNS-like tree (device → vehicle domain → cloud) replicated by a trusted OTA uEntity with TTLs, no multicast at all. rmw_zenoh turned UDP multicast scouting **off** by default, "aimed at avoiding issues with misconfigured networks, operating systems, or containers" and "uncontrolled communication between robots in the same LAN".

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| mDNS + DNS-SD (RFC 6762/6763) | link-local multicast browse of `_svc._tcp`, TXT metadata, goodbye with TTL 0 | zero-config first contact on one segment |
| ISO 17978 SOVD discovery | `_sovd._tcp`, port 7690, `<id>.local`, TXT `accessurl` (https) | a tester finds the vehicle's SOVD server without config |
| W3C WoT Discovery (Rec. 2023) | introduction (open) vs exploration (authenticated, directory) | discovery split by trust level |
| uProtocol uDiscovery v3 | hierarchical directory, replicated by OTA, TTL-bounded caches | installed knowledge instead of probing |
| rmw_zenoh | router + gossip scouting; multicast disabled by default | a ROS 2 that works in containers and on shared LANs |

**On the Eclipse SDV stack.**
- OpenSOVD: implement mDNS only for the workshop tester's first contact (gap H9, issue #31), advertising the https `accessurl`; never as the way in-vehicle apps find the server ([[advertise-the-https-url-or-do-not-advertise]], [[opensovd-reference]]).
- Zenoh / uProtocol: at the venue, set `scouting.multicast.enabled=false` and `connect.endpoints` explicitly; one router per network island ([[run-a-router-only-where-multicast-cannot-reach]], [[zenoh-overview]]).
- iceoryx2 needs no network discovery: services are files under `/tmp/iceoryx2` and `/dev/shm`; in containers the "discovery" is a shared mount plus same config prefix, which belongs in the Ankaios manifest (gap C1) ([[iceoryx2-howto]]).
- Docker: the default bridge passed Zenoh scouting on one host (corrected 2026-10-03, see [[zenoh-overview]]); separate compose networks, podman and multi-host setups are untested, so explicit endpoints stay the safe default.

**The trap.** Shipping a demo whose only discovery path is multicast scouting, then debugging the venue network instead of the product.

**For a hackathon team.** Run everything with multicast disabled and explicit endpoints from one config file, and add a single mDNS responder that advertises the SOVD https URL for a phone or laptop tester. Pitch: "multicast introduces, the manifest decides".

**Evidence.** RFC 6762 §3 (".local" queries MUST go to 224.0.0.251), §10 (120 s / 75 min TTLs), §10.1 (goodbye TTL 0, delete after 1 s); RFC 6763 §4.1, §6.7 (`txtvers`). WoT Discovery W3C Recommendation 5 Dec 2023, §§ introduction/exploration. rmw_zenoh design.md "Default Configuration" (UDP Multicast: Disabled, rationale quoted). Zenoh `DEFAULT_CONFIG.json5` L139–174. uDiscovery `service.adoc` L27 (tree), L142–156 (SetServiceTopics, ttl, removal = ttl 0), L177 (trusted OTA uEntity). Venue client isolation is general experience, not measured here (unverified).
