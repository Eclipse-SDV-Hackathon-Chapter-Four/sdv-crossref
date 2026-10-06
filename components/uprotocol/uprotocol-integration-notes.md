---
title: uProtocol integration notes
type: reference
component: uprotocol
tags: [uprotocol, integration, zenoh, ankaios, kuksa, iceoryx2]
status: draft
sources:
  - repos/up-spec/up-l1/iceoryx2.adoc
  - repos/up-spec/up-l1/zenoh.adoc
  - repos/sdv_lab/pid_controller/rust-uprotocol/rust-uprotocol.yaml
  - repos/sdv_lab/uprotocol/cruise-control-app/cruise-control-app.yaml
  - repos/sdv_lab/android_treadx/threadx/threadx-app/cross/app/src/utransport.rs
  - repos/up-rust/Cargo.toml
  - https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
last-verified: 2026-10-03
related:
  - "[[uprotocol-overview]]"
  - "[[uprotocol-howto]]"
  - "[[zenoh-overview]]"
  - "[[ankaios-overview]]"
---

# uProtocol integration notes

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| Zenoh ([[zenoh-overview]]) | yes | up-transport-zenoh-rust / -cpp implement uP-L1; UMessage attributes in Zenoh attachment, key `up/<authority>/...`; Zenoh 1.x mandatory; production-grade Rust transport (v0.9.1, current), best-supported | demo | repos/up-spec/up-l1/zenoh.adoc; repos/up-transport-zenoh-rust; observed run in [[uprotocol-quickstart]] |
| MQTT 5 | yes | up-transport-mqtt5-rust (paho), bridged to Zenoh by uStreamer | demo (Chapter 3 lab: ThreadX, Android cluster, cruise control) | repos/sdv_lab/uprotocol/mqtt; repos/up-streamer-rust |
| SOME/IP (vsomeip) | yes | up-transport-vsomeip-rust; streamer `zenoh_someip` binary | prototype | repos/up-streamer-rust/example-streamer-implementations |
| Ankaios ([[ankaios-overview]]) | yes (as workload runner) | uProtocol apps shipped as containers and started with `ank apply` manifests; no Ankaios-specific uProtocol library | demo | repos/sdv_lab/pid_controller/rust-uprotocol/rust-uprotocol.yaml, repos/sdv_lab/uprotocol/cruise-control-app/cruise-control-app.yaml |
| openDuT ([[opendut-overview]]) | idea / event-claimed | Chapter 4 text: "openDuT rewires the testbench", faults "delayed or duplicated messages" can be applied at network level on Zenoh/MQTT traffic; no code found | idea | https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340 |
| OpenSOVD ([[opensovd-overview]]) | none found | Chapter 4 text says uProtocol events + OpenSOVD diagnostics; no adapter found; a uEntity could expose fault events via SOVD HTTP | idea | https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340 |
| VSS / KUKSA ([[vss-kuksa-overview]]) | none found | Web search surfaced only an old mailing-list discussion on exposing COVESA uServices from the Kuksa databroker; no code found | idea | https://www.eclipse.org/lists/sdv-wg/msg00352.html (via WebSearch, unread in full) |
| iceoryx2 ([[iceoryx2-overview]]) | partial | uP-L1 iceoryx2 mapping in spec ("MUST use" iceoryx2 0.6.1, pub/sub only, UAttributes in user header) and early up-transport-iceoryx2-rust (few commits, ~50 open issues) that pins 0.7, so spec and code disagree and neither talks to iceoryx2 0.10 (`VersionMismatch`) ([[one-type-source-generated-bindings]]) | prototype | repos/up-spec/up-l1/iceoryx2.adoc; https://github.com/orgs/eclipse-uprotocol/repositories |
| S-CORE ([[s-core-overview]]) | none found | S-CORE's production IPC is LoLa (mw::com, its own shared-memory implementation); iceoryx2 is used only by the S-CORE orchestrator (cross-process events, removed from the platform in v0.9 but repo exists) and as one FEO communication backend; no uProtocol use found | none | grep of repos/ found nothing; [[s-core-integration-notes]]; [[iceoryx2-integration-notes]] |
| AutoSD ([[autosd-overview]]) | none found as library; Chapter 4 runs Guardian on AutoSD with uProtocol events | plain containers/Rust binaries on AutoSD; no packaging found | idea | https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340 |
| OpenBSW ([[openbsw-overview]]) | none found | no uProtocol in repos/openbsw; MCU side would need a uProtocol client (see ThreadX row) | none | grep of repos/openbsw found only unrelated word list |
| ThreadX ([[threadx-overview]]) | yes (hand-rolled) | no_std send-only `UTransport` over `minimq` MQTT with hand-built prost types, publishes temperature to MQTT; streamer bridges to Zenoh | demo | repos/sdv_lab/android_treadx/threadx/threadx-app/cross/app/src/{utransport,minimqtransport,uprotocol_v1}.rs |
| Android (AAOS cluster) | yes | Kotlin app speaking uProtocol over MQTT (Paho) | demo | repos/sdv_lab/android_treadx/android/digital-cluster-app, repos/sdv_lab/aaos_digital_cluster |
| Symphony ([[symphony-overview]]) | yes | up-rust feature `symphony` exposes a uProtocol RPC server as a Symphony target | prototype | repos/up-rust/Cargo.toml, repos/up-rust/examples/symphony_target.rs |
| SDV Blueprints ([[sdv-blueprints-overview]]) | none found | not checked beyond grep of local repos | none | - |
| Velocitas ([[velocitas-overview]]) / Kanto / Muto | none found | not checked | none | - |

## Notes
- **Zenoh vs uProtocol on Zenoh**: you can still run plain Zenoh apps next to uProtocol ones, but uProtocol keys are `up/...` and attachment-encoded; a plain Zenoh app must parse the attachment to read attributes (payload itself is unaltered).
- **uProtocol on iceoryx2 vs raw iceoryx2**: gains addressing/envelope/streamer-bridging, loses zero-copy purity (serialized attributes in a ~1000 byte user header, per spec snippet) and some latency.
- **Evidence chain idea for Doctor Whodunit**: keep all heartbeat/fault/mitigation events on Zenoh, record them (tap), correlate via `traceparent`/UUID v7 timestamps, and serve them through OpenSOVD faults - none of this exists yet.
