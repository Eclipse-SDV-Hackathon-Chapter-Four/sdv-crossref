---
title: uProtocol reference - repos, versions, APIs
type: reference
component: uprotocol
tags: [uprotocol, reference, versions, repos]
status: draft
sources:
  - repos/up-spec/up-l1/README.adoc
  - repos/up-rust/Cargo.toml
  - repos/up-rust/src/lib.rs
  - repos/up-streamer-rust/Cargo.toml
  - repos/up-transport-zenoh-rust/Cargo.toml
  - https://github.com/orgs/eclipse-uprotocol/repositories
last-verified: 2026-10-03
related:
  - "[[uprotocol-overview]]"
  - "[[uprotocol-quickstart]]"
  - "[[uprotocol-howto]]"
---

# uProtocol reference

## Repos looked at (shallow clones in repos/)
| Repo | Commit | Commit date | Notes |
|---|---|---|---|
| repos/up-spec | c89dc485abfa8ea84ea2912e644ddbf6c186ad8a | 2026-09-22 | no tags in shallow clone; libs reference v1.6.0-alpha.7 |
| repos/up-rust | 27e4ce62084459c28f9f7e3cc803c8b87725b7cc | 2026-09-30 | 0.10.0-SNAPSHOT, MSRV 1.88; `up-spec` subdir is a submodule (proto dir vendored in `proto/`; build worked on shallow clone) |
| repos/up-streamer-rust | 4e01e894513a1b7b23349de58d38ebd2faa1d83c | 2026-02-23 | workspace 0.1.0; up-rust 0.9, up-transport-zenoh 0.9.0, up-transport-mqtt5 0.4.0, vsomeip by git rev |
| repos/up-transport-zenoh-rust | 1ebc37b1fc457bdd79ec94ef65b75d901dda577a | 2026-08-13 | v0.9.1, zenoh 1.9.0, up-rust 0.9 |

## Other repos (org https://github.com/eclipse-uprotocol, not cloned)
up-cpp, up-java, up-kotlin, up-python, up-android-core, up-transport-zenoh-cpp, up-zenoh-example-cpp, up-transport-mqtt5-rust, up-transport-vsomeip-rust, up-transport-iceoryx2-rust, up-transport-socket, up-subscription-rust ("approaching beta"), up-streamer-rust, ci-cd, up-conan-recipes. up-simulator and up-client-android-java README paths returned 404 on `main` (renamed/archived? unverified).

## Crates (crates.io, 2026-10-03)
up-rust 0.9.0 (2025-11-12) | up-transport-zenoh 0.9.1 (2026-08-13) | up-transport-mqtt5 0.4.0 (2025-11-13) | up-transport-vsomeip 0.6.0 (2026-08-12) | up-subscription 0.1.3 (2024-07-30). up-rust history: 0.4.0 Jan 2025, 0.5.0 Mar, 0.6.0 Jun, 0.7.0/0.7.1 Aug-Sep, 0.8.0/0.8.1 Oct, 0.9.0 Nov 2025 - roughly a breaking release every 1-2 months.

## up-rust API map
- Types: `UUri`, `UMessage`, `UAttributes`, `UMessageBuilder` (`publish`, `notification`, `request`, `response`), `UPayloadFormat`, `UPriority`, `UCode`, `UStatus`, `UUID`.
- L1: trait `UTransport` (`send`, `receive`, `register_listener`, `unregister_listener`), trait `UListener` (`on_receive`), `LocalUriProvider` / `StaticUriProvider::new(authority, ue_id, version)`, `local_transport::LocalTransport` (in-process).
- L2 (`communication`): `Publisher`/`SimplePublisher`, `Notifier`/`SimpleNotifier`, `Subscriber`/`InMemorySubscriber`, `RpcClient`/`InMemoryRpcClient`, `RpcServer`/`InMemoryRpcServer`, `CallOptions`, `UPayload`.
- Core services clients: `core::usubscription`, `core::udiscovery`; feature `symphony` adds a Symphony target adapter (example `symphony_target`) - relevant to [[symphony-overview]].
- Features: see repos/up-rust/Cargo.toml. Examples: simple_publish, simple_notify, simple_rpc, symphony_target. Docs: `cargo doc --all-features --open`, guide in repos/up-rust/src/guide/.

## Spec map
- Basics: repos/up-spec/basics/{uri,uuid,umessage,uattributes,upriority,error_model,permissions,namespace,versioning}.adoc + Gherkin `.feature` files for UUri/UUID serialization and pattern matching.
- L1 mappings: zenoh.adoc, mqtt_5.adoc, someip.adoc, iceoryx2.adoc, cloudevents.adoc.
- L2: up-l2/api.adoc, dispatchers/README.adoc.
- L3: usubscription v3 + v4, udiscovery v3, utwin v2. Protos in up-core-api/uprotocol/core/*; service ids: uSubscription 0, uStreamer 4 (proto stub only).
- Language library requirements: languages.adoc (naming `up-<lang>`, README, CI, OFT tracing).

## Config references
- Streamer: repos/up-streamer-rust/configurable-streamer/{CONFIG.json5, ZENOH_CONFIG.json5, MQTT_CONFIG.json5, subscription_data.json}; Chapter 3 variants in repos/sdv_lab/uprotocol/ustreamer/config.
- Zenoh example config: repos/up-transport-zenoh-rust/config/.
- Deterministic smoke suite across transports: `cargo run -p transport-smoke-suite --bin transport-smoke-matrix -- --all` (repos/up-streamer-rust/README.md; 8 scenarios zenoh/mqtt/someip; not run).

## Links
- Spec: https://github.com/eclipse-uprotocol/up-spec
- Org: https://github.com/eclipse-uprotocol
- Zenoh: [[zenoh-overview]]
- Chapter 3 lab: repos/sdv_lab/uprotocol, repos/sdv_lab/pid_controller/rust-uprotocol
