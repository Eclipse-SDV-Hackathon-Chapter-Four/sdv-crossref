---
title: Open on arrival, age by your own deadline — iceoryx2 discovery without a heartbeat
type: pattern
cluster: identity-discovery
component: none
tags: [iceoryx2, discovery, liveness, deadline, attributes, domains, dead-node, open-world]
status: draft
sources:
  - repos/iceoryx2/examples/rust/discovery_service/ (DiscoveryEvent::Added(StaticConfig) / Removed(ServiceHash))
  - repos/iceoryx2/iceoryx2-services/discovery/src/service_discovery/{service.rs,tracker.rs} (polling tracker, epoch)
  - repos/iceoryx2/iceoryx2-cli/iox2-service/src/cli.rs (`iox2 service discovery`, default rate 100 ms)
  - repos/iceoryx2/examples/rust/service_attributes/ (AttributeSpecifier / AttributeVerifier)
  - repos/iceoryx2/examples/rust/health_monitoring/ (event `.deadline()`, `attach_deadline`, `notifier_dead_event`, `NodeState::Dead`)
  - repos/iceoryx2/examples/rust/domains/README.md (`config.global.prefix`)
  - https://github.com/eclipse-iceoryx/iceoryx2
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[a-type-name-is-a-claim-a-layout-hash-is-a-proof]]"
  - "[[a-reboot-is-a-new-session-not-the-same-producer]]"
  - "[[a-vehicle-is-gone-when-its-death-certificate-says-so]]"
  - "[[iceoryx2-overview]]"
  - "[[iceoryx2-howto]]"
  - "[[iceoryx2-reference]]"
applies-to: [iceoryx2, s-core, opensovd, ankaios]
gap-rows: [A2, A8, B2, C1, E5]
---

# Open on arrival, age by your own deadline

**Problem.** iceoryx2 has no wildcard subscription and no broker. A consumer that opens ports only at start-up never sees the second seat module; one that keeps ports to a crashed producer shows its last value forever; and adding a heartbeat topic per producer doubles the services and still tells you nothing about *your* data.

**Forces.**
- No central daemon; every process must cope alone.
- A service outlives any single producer (it persists while any node holds it), so "service still listed" ≠ "data still fresh".
- Each consumer has its own tolerance (a 10 ms brake loop vs a 1 s dashboard).
- Teams share one machine at a hackathon.

**The rule.** Four moves, all with existing APIs.
1. **Isolate** with a domain: each system (or team) gets its own `config.global.prefix`; processes in other prefixes are invisible.
2. **Announce by creating**: the producer creates `<model>/<template>/<instance>` with `create_with_attributes` (`type.hash`, `schema.major`, `instance.id`, `producer`) and names its node (`NodeBuilder::new().name(...)`).
3. **Open on arrival**: the consumer subscribes to the discovery service (`iox2 service discovery` or the `iceoryx2-services-discovery` crate) and, on `DiscoveryEvent::Added(static_config)` whose name matches its pattern, calls `open_with_attributes(AttributeVerifier::new().require("type.hash", H))`; a refusal is logged, not ignored. `Removed` carries only the `ServiceHash`, so keep the `StaticConfig` you opened.
4. **Age by your own deadline**: attach each port's event listener to the WaitSet with `attach_deadline(listener, my_deadline)` (or the service's `.deadline()`); on `has_missed_deadline` mark that instance stale for *this* consumer and scan `Node::list` for `NodeState::Dead`, calling `try_remove_stale_resources()`. Use `notifier_dead_event` to be woken when someone else cleaned up a dead producer. No heartbeat topic exists anywhere.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| DDS DEADLINE QoS | reader declares max period; missed deadline is a status event | freshness judged by the consumer |
| DDSI-RTPS SPDP lease | participant is gone when its lease lapses | liveness without an app heartbeat |
| Zenoh liveliness tokens | token tied to a session; Delete on drop, crash or lost connectivity | death as an event, not a timeout guess |
| Sparkplug B | birth on arrival, NDEATH via MQTT Will | arrival and death as explicit messages |
| iceoryx2 health_monitoring example | per-service deadline + dead-node scan + `ProcessDied` event | the exact recipe on shared memory |

**On the Eclipse SDV stack.**
- iceoryx2 0.10: everything above is in `repos/iceoryx2/examples/rust/{discovery_service,service_attributes,health_monitoring,domains}`; the discovery service polls the filesystem (CLI default 100 ms), so arrival latency is one poll ([[iceoryx2-reference]]).
- OpenSOVD fault-lib → DFM runs over iceoryx2 (gap A2); a DFM that opens reporters on arrival and raises a fault on missed deadline is the freshness watchdog of gap A8 without a heartbeat schema ([[opensovd-overview]]).
- Ankaios / containers: the domain prefix and `/tmp/iceoryx2` + `/dev/shm` mounts belong in the manifest (gap C1).
- `iox2 node` cleanup is "NOT YET IMPLEMENTED" (gap E5); call `try_remove_stale_resources` from code.

**The trap.** Treating `DiscoveryEvent::Removed` as the producer's death; a service with a dead publisher stays listed until its last node is cleaned up, so only your deadline tells you the data stopped.

**For a hackathon team.** Run the discovery service, a consumer with a 200 ms deadline, and start two seat producers at different times; `kill -9` one and show the consumer flag it stale within one deadline and clean its node. Pitch: "we open on arrival and age by our own clock — no heartbeats".

**Evidence.** `discovery_service.rs` (Added stores `StaticConfig`, Removed has only the hash, comment says so). Tracker epoch sync: `tracker.rs`. CLI default `rate = 100`: `iox2-service/src/cli.rs` L63–70. Attributes semantics ("interpreted as requirements"): service_attributes/README.md; `IncompatibleAttributes` in `publish_subscribe.rs` L655. Deadline and dead-node code: health_monitoring/{central_daemon.rs L49–61, subscriber.rs L50–110}. `NodeState::{Alive,Dead,Inaccessible,Undefined}`: `iceoryx2/src/node/mod.rs` L382. Domains: domains/README.md, confirmed in [[iceoryx2-quickstart]].
