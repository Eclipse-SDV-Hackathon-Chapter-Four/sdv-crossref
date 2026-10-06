---
title: iceoryx2 integration notes (S-CORE, OpenSOVD, uProtocol, Zenoh, ROS 2, Ankaios, KUKSA)
type: synthesis
component: iceoryx2
tags: [iceoryx2, integration, s-core, opensovd, uprotocol, zenoh, ros2, ankaios, kuksa]
status: draft
sources:
  - repos/s-core-orchestrator/src/orchestration/src/events/iceoryx/event.rs
  - repos/s-core-orchestrator/Cargo.toml
  - repos/feo/src/feo-com/src/iox2/mod.rs
  - repos/s-core-communication/README.md
  - repos/opensovd-fault-lib/README.md
  - repos/up-spec/up-l1/iceoryx2.adoc
  - repos/up-transport-iceoryx2-rust/Cargo.toml
  - repos/iceoryx2/integrations/README.md
  - repos/iceoryx2/iceoryx2-link/README.md
  - https://github.com/ekxide/rmw_iceoryx2
  - https://github.com/eclipse-iceoryx/iceoryx2
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[s-core-overview]]"
  - "[[opensovd-overview]]"
  - "[[uprotocol-overview]]"
  - "[[zenoh-overview]]"
  - "[[ankaios-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# iceoryx2 integration notes

iceoryx2 is **not** listed as a project in either Chapter 4 challenge (see [[chapter4-overview]]). It still sits *underneath* three projects that are listed: S-CORE (orchestrator, FEO), OpenSOVD (fault-lib), and uProtocol (iceoryx2 transport spec and implementation). Knowing this helps when you run into shared-memory errors in those stacks.

## Integration matrix
| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| S-CORE orchestrator (inc_orchestrator) | yes | Rust crate `iceoryx2` (git rev pin `d3d1c9a7`, `default-features = false`). The **event** pattern (`ipc_threadsafe` Notifier/Listener, prefix `orch_node`) is used for inter-process orchestration triggers. Feature `iceoryx2-ipc` is on by default. The QNX 8 build uses `@score_crates//:iceoryx2_qnx8` (qorix-group fork). `FlatMap` from `iceoryx2-bb-container`. | prototype (in the S-CORE reference integration) | repos/s-core-orchestrator/Cargo.toml L36-48; src/orchestration/Cargo.toml; src/orchestration/src/events/iceoryx/event.rs; src/orchestration/BUILD; examples/README.md (`send_ipc_event.rs`, `inter_process_event_sender/receiver.rs`) |
| S-CORE FEO (Fixed Execution Order) | yes | `feo-com` backend `iox2` (feature `ipc_iceoryx2`/`com_iox2`) with typed **pub/sub** per topic. Demo: `bazel run //examples/rust/mini-adas:adas_primary_com_iox2_direct_unix` | prototype / demo | repos/feo/src/feo-com/src/iox2/mod.rs; repos/feo/src/feo-com/BUILD.bazel; repos/feo/examples/rust/mini-adas/README.md (commit 16c4fef, 2026-08-09) |
| S-CORE communication (`mw::com`, LoLa) | no (separate tech) | LoLa is S-CORE's own zero-copy shared-memory ara::com implementation (C++, ASIL-B targeted). iceoryx2 only appears in its MODULE.bazel.lock because of the shared `score_crates` index (iceoryx2 0.5.0 and qnx8 0.7.0 fork) | none | repos/s-core-communication/README.md; repos/s-core-communication/MODULE.bazel.lock L7382ff |
| S-CORE reference integration | indirect | Lock files pull iceoryx2 0.5.0 and the qnx8 fork through `score_crates` (for orchestrator/FEO) | prototype | repos/s-core-reference_integration/MODULE.bazel.lock L5805ff |
| OpenSOVD (fault-lib, DFM) | yes | Reporters (`fault_lib::Reporter`) publish fault records to the Diagnostic Fault Manager over iceoryx2 **pub/sub** (`dfm/event`, `dfm/enabling_condition/notification`). The query API `Iceoryx2DfmQuery` uses iceoryx2 **request_response** (`DfmQueryRequest`/`DfmQueryResponse`). iceoryx2 pinned via git rev `eba5da4b`. | prototype (runnable `dfm` + `tst_app` examples) | repos/opensovd-fault-lib/README.md L51, L60-85; src/fault_lib/src/ipc_worker.rs; src/dfm_lib/src/fault_lib_communicator.rs; src/dfm_lib/src/query_server.rs L63; docs/puml/enable_condition_ntf.puml; Cargo.toml L52 (commit 12dac50, 2026-10-01) |
| uProtocol | yes (spec + early impl) | L1 transport spec: uAttributes go into the iceoryx2 **user header**, the payload is zero-copy, PublishSubscribe only (RequestResponse "MUST NOT" be used), iceoryx2 protocol version 0.6.1. Impl: up-transport-iceoryx2-rust 0.1.0 (up-rust 0.7, iceoryx2 0.7.0, pub/sub listener/send only, two-line README, not on crates.io) | prototype | repos/up-spec/up-l1/iceoryx2.adoc; repos/up-transport-iceoryx2-rust/Cargo.toml, src/utransport_pubsub.rs (commit 1935267, 2025-10-29) |
| Zenoh | yes | `iceoryx2-link` **tunnel** with a Zenoh **carrier**: CLI `iox2-link-tunnel-zenoh` (crate `iceoryx2-integrations-zenoh-link-tunnel-cli` 0.10.0) mirrors iceoryx2 services between hosts, supports an allow-list, and supports pub/sub and event. Note this is iceoryx2↔iceoryx2 *over* Zenoh, **not** a gateway to native Zenoh key expressions | prototype ("Only recommended for experimentation"). Ran on 2026-10-03 between two local domains, see [[iceoryx2-quickstart]] | repos/iceoryx2/integrations/zenoh/; repos/iceoryx2/iceoryx2-link/README.md; release notes v0.10.0 #820 #1616 #1960 |
| ROS 2 | yes (two routes) | (a) `rmw_iceoryx2` by ekxide (alpha, rolling; pub/sub, waitset done; services, graph, QoS in progress). (b) iceoryx2 link **gateway** with a ROS 2 adapter (`integrations/ros2`, Jazzy/Humble distroboxes) | prototype | https://github.com/ekxide/rmw_iceoryx2 ; repos/iceoryx2/integrations/ros2/README.md |
| iceoryx classic | successor | No wire compatibility found. Migration means a rewrite against the new API. Classic is in maintenance mode and goes EOL after iceoryx2 1.0. Zenoh's DDS plugin still uses *classic* iceoryx for DDS shared memory (predecessor, maintenance mode; not an integration) | none | https://github.com/eclipse-iceoryx/iceoryx ; [[zenoh-overview]] |
| Ankaios | none found | Possible by giving both workloads `/dev/shm` and `/tmp/iceoryx2` mounts plus the same UID in podman `commandOptions`. No upstream example exists | idea | [[ankaios-howto]]; repos/iceoryx2/examples/rust/docker/README.md; web search 2026-10-03 |
| VSS / KUKSA | none found | No databroker ↔ iceoryx2 bridge found. Idea: a provider that maps VSS paths to iceoryx2 services | idea | web search "kuksa databroker iceoryx2" 2026-10-03 |
| openDuT | none found | — (openDuT works at network/CAN testbench level, while iceoryx2 is intra-host) | none | grep of repos/opendut* 2026-10-03 |
| AutoSD | indirect only | `eclipse-score/inc_os_autosd` builds S-CORE modules on AutoSD; its `tests/score-modules/MODULE.bazel.lock` pulls iceoryx2 0.5.0 + the qnx8 fork through `score_crates`. No AutoSD RPM or image recipe for iceoryx2 was found | prototype (transitive) | repos/inc_os_autosd/tests/score-modules/MODULE.bazel.lock L7141ff; no hits in repos/eclipse-autosd, repos/automotive-image-builder |
| OpenBSW | none found | MCU firmware with no shared memory to Linux | none | [[openbsw-integration-notes]] |
| ThreadX | none found (planned on the iceoryx2 side) | The iceoryx2 README lists ThreadX and FreeRTOS as "planned" targets | idea | repos/iceoryx2/README.md platform table |
| SDV Blueprints | none found | — | none | grep/web 2026-10-03 |

## How S-CORE uses iceoryx2, in one paragraph
S-CORE's Rust components (the orchestrator, i.e. inc_orchestrator, now `eclipse-score/orchestrator`, and FEO) use iceoryx2 directly as a Rust crate for **local IPC**. The orchestrator uses only the **event** pattern (cross-process triggers and wakeups). FEO uses typed **pub/sub** between its primary and secondary agents. Both pin iceoryx2 by git revision or through `score_crates`, not by crates.io semver, and the QNX 8 variant comes from a qorix-group fork. S-CORE's C++ `mw::com` (LoLa) is a separate shared-memory implementation. A team that wants to "talk to S-CORE" through iceoryx2 should therefore target the orchestrator or FEO topics and services, not `mw::com`. (Sources: see the matrix rows.)

## Correction for other notes
[[zenoh-overview]] / zenoh-integration-notes list an iceoryx2↔Zenoh tunnel as "the missing tunnel, if indeed missing". It exists (`iox2-link-tunnel-zenoh`, prototype, verified locally 2026-10-03). What *is* missing is a gateway between iceoryx2 services and native Zenoh key expressions, so that plain Zenoh apps could read iceoryx2 data. The zenoh-integration-notes row also says "S-CORE comms is iceoryx2-oriented". More precisely, S-CORE `mw::com` is LoLa, and only the orchestrator and FEO use iceoryx2.

## Hackathon integration ideas, ranked by effort
1. (S, half a day) **OpenSOVD fault stream tap**: run the fault-lib `dfm` + `tst_app` and attach `iox2 service list/subscribe/record` to capture fault events as independent evidence. Fits [[chapter4-challenge-doctor-whodunit]].
2. (S) **Ankaios manifest + README** for two iceoryx2 workloads with shared memory. Upstream PR candidate to Ankaios examples.
3. (M) **Upgrade up-transport-iceoryx2-rust** to iceoryx2 0.10 and the current up-rust, add a README quickstart, and run the uProtocol hello-world over shared memory. That proves "same service code, different transport" for [[chapter4-challenge-hack-to-the-future]]. Watch out: the spec pins iceoryx2 protocol 0.6.1, so a spec PR is needed too.
4. (M) **KUKSA → iceoryx2 provider**: subscribe to databroker gRPC, republish VSS signals as fixed-size iceoryx2 samples for high-rate local consumers.
5. (L) **Zenoh gateway adapter**: implement the `iceoryx2-link-adapter` trait for native Zenoh, so iceoryx2 services appear as Zenoh key expressions (the ROS 2 adapter is the template).
