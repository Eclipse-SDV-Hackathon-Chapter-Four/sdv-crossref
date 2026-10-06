---
title: Run a router only where multicast cannot reach
type: pattern
cluster: fleet-cloud
component: none
tags: [zenoh, router, scouting, wifi, docker, cellular, topology]
status: draft
sources:
  - repos/zenoh/DEFAULT_CONFIG.json5 (scouting.multicast, gossip, mode, lease)
  - repos/fleet-management/fms-blueprint-compose-zenoh.yaml
  - repos/fleet-management/config/zenoh/config-client.json5
last-verified: 2026-10-03
related:
  - "[[zenoh-overview]]"
  - "[[authority-is-the-routing-unit]]"
applies-to: [zenoh, uprotocol, sdv-blueprints]
gap-rows: [C5]
---

# Run a router only where multicast cannot reach

**Problem.** In the vehicle, peers find each other by multicast and you need no infrastructure. On venue Wi-Fi, across separate container networks or hosts, over cellular and across vehicles, multicast does not arrive (the default Docker bridge on one host did pass it (corrected 2026-10-03, see [[zenoh-overview]])), and the demo "works on my laptop" only.

**Forces.**
- Peer mode is free and fast on one L2 segment; a router is one more process to run, secure and keep version-matched.
- Cellular and carrier NAT need an outbound connection from the vehicle to a reachable node.
- A vehicle must not depend on the cloud to talk to itself.
- Routers are the place for storages, ACL and plugins.

**The rule.** Inside a vehicle: peers (or one local router per HPC) with multicast. Vehicle to cloud: the vehicle is a client or router that dials out to a cloud router over TCP/TLS or QUIC; the cloud never dials in. Add a router exactly where multicast scouting stops: one per network island, never one per app. Set `connect.endpoints` explicitly on anything that must cross; do not rely on scouting beyond the vehicle LAN.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Zenoh router/peer/client | client connects to one router; peers mesh; `lease` 10 s with `keep_alive` 4 | liveness inside the session layer |
| Zenoh config | `scouting.multicast.enabled`, gossip, `connect.endpoints` | scouting is optional, endpoints are explicit |
| MQTT broker | star topology, clients dial out | the cellular-friendly shape |
| uStreamer | a gateway process between transports | bridging when the far side is not Zenoh |
| Hono protocol adapters | devices dial out to adapters | same outbound-only shape |

**On the Eclipse SDV stack.**
- fleet-management starts `eclipse/zenoh:1.1.0` as `fms-zenoh-router` (7447/tcp) with forwarder and consumer in client mode; scouting is not needed because the compose network names the router ([[sdv-blueprints-overview]]). Other blueprints run Zenoh 1.6.2; keep router, plugins and clients on one minor ([[zenoh-overview]]).
- Docker pitfall is real: the blueprints declare `driver: overlay` networks, which need swarm and fail on a plain Docker host (gap E15, [[known-broken-recipes]]); use `network_mode: host` or a bridge plus an explicit `tcp/<router>:7447` endpoint.
- Venue Wi-Fi often isolates clients: give every container the router address and ignore multicast.
- Missing manifest: nobody ships an Ankaios workload for router plus uStreamer (C5).

**The trap.** Relying on multicast scouting in a demo, then adding a router at the venue and finding duplicate paths because both routes stay active.

**For a hackathon team.** One `zenohd` on the shared laptop, every team app in client mode with a hard-coded endpoint, multicast disabled. Pitch: "the vehicle dials out; nothing dials in".

**Evidence.** Config options: repos/zenoh/DEFAULT_CONFIG.json5. Router compose: repos/fleet-management/fms-blueprint-compose-zenoh.yaml. Overlay bug: gap E15. Cellular behaviour (QUIC versus TCP loss recovery) not tested here (unverified).
