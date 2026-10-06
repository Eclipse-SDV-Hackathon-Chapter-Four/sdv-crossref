---
title: uProtocol how-to recipes and hackathon ideas
type: howto
component: uprotocol
tags: [uprotocol, howto, ustreamer, pitfalls, ideas, doctor-whodunit]
status: verified
sources:
  - repos/up-streamer-rust/configurable-streamer/CONFIG.json5
  - repos/up-streamer-rust/configurable-streamer/subscription_data.json
  - repos/up-streamer-rust/configurable-streamer/README.md
  - repos/sdv_lab/uprotocol/README.md
  - repos/sdv_lab/uprotocol/ustreamer/config/CONFIG.json5
  - repos/up-rust/Cargo.toml
  - repos/up-spec/basics/uri.adoc
last-verified: 2026-10-03
related:
  - "[[uprotocol-overview]]"
  - "[[uprotocol-quickstart]]"
  - "[[uprotocol-reference]]"
  - "[[uprotocol-integration-notes]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
---

# uProtocol how-to

Nothing here except the quickstart has been executed; recipes are derived from source and marked accordingly.

## 1. Design addressing for a project (10 min)
1. One **authority** per deployment host / ECU / device (`guardian-ecu`, `cloud`, `hpc`). Lowercase `[a-z0-9-._~]`, max 128 chars. Wrong case fails URI parsing (spec: lowercase only). The sdv_lab streamer config uses mixed case (`EGOVehicle`, `AAOS`), and a VIN used as authority must be lowercased ([[authority-is-the-routing-unit]]).
2. One **ue_id** per service type (low 16 bits), instance in the high 16 bits (0 = default). e.g. `0x1001` battery-thermal-guardian, `0x1002` monitor.
3. Pick **resource ids**: 0x8000+ for topics (events), < 0x8000 for RPC methods (common convention, see spec examples `/0/3/8000`).
4. Version = ue_version_major. Subscribers use `0xFF` to match any version.
Suggested Doctor Whodunit layout (our proposal, NOT from organisers): topics `//<ecu>/1001/1/8001` heartbeat (payload: seq + monotonic ts), `/8002` fault (code, severity, injected-by), `/8003` mitigation (action, trigger fault id); RPC `//<ecu>/1001/1/0001` "get_state"; priority CS5/CS6 for fault/mitigation, CS1 for heartbeat. Use `traceparent` attribute to tie hazard -> fault -> detection -> mitigation in the evidence chain.

## 2. Publish / subscribe (L1 vs L2)
- L1 (used in quickstart): `UMessageBuilder::publish(topic).build_with_payload(..)`, `transport.send(msg)`, `transport.register_listener(&source_filter, None, listener)`.
- L2 (recommended by up-rust docs): `SimplePublisher::new(transport, uri_provider)`, `publisher.publish(resource_id, CallOptions::for_publish(..), payload)`; subscriber side `InMemorySubscriber` talks to the uSubscription service via RPC - **you must run a uSubscription service** (e.g. `up-subscription-rust`) for L2 `subscribe()`. For simple hackathon use register_listener on L1 and skip uSubscription. (repos/up-rust/Cargo.toml features `up-l2-subscriber -> usubscription`)
- Payloads: `UPayload::try_from_protobuf(msg)` -> format PROTOBUF_WRAPPED_IN_ANY; or TEXT/JSON/RAW. Define .proto types for heartbeat/fault/mitigation and share them in a crate for Rust+Python (Python SDK maturity unverified).

## 3. RPC
Server: `InMemoryRpcServer::new(transport, uri_provider)` + `register_endpoint(...)`; client: `InMemoryRpcClient::new(..)` + `invoke_method(uri, CallOptions, payload)` (see repos/up-rust/examples/simple_rpc.rs and up-transport-zenoh-rust `rpc_server`/`rpc_client`). The client waits for a response with TTL timeout. Server handlers must be idempotent (at-least-once).

## 4. Bridge two transports with the configurable uStreamer (derived, not run)
Pattern from Chapter 3 (repos/sdv_lab/uprotocol/README.md): one authority per "island", one endpoint per authority, `forwarding` lists the endpoints to forward to.
```bash
git clone --depth 1 https://github.com/eclipse-uprotocol/up-streamer-rust
cd up-streamer-rust/configurable-streamer
cargo run -- --config="CONFIG.json5"     # needs MQTT broker reachable per MQTT_CONFIG.json5
```
Or use the Chapter 3 docker-compose in `repos/sdv_lab/uprotocol/ustreamer` which pulls a prebuilt configurable streamer image from the uProtocol GHCR (image name not recorded in the repo files we grepped - unverified).
Checklist:
- Every endpoint named in `forwarding` must exist, endpoint names unique, or the streamer crashes (sdv_lab README).
- Pub/sub forwarding requires a **static subscription file** entry per publisher topic -> list of subscriber UUris (`"//authority-b/3039/1/8001": ["//authority-a/5678/1/1234"]`, repos/up-streamer-rust/configurable-streamer/subscription_data.json). Topics not listed are silently NOT forwarded. Note the key's ue_id is written as lowercase-hex-free string `3039`=0x3039.
- The `streamer_uuri` authority is the host transport authority (Zenoh side); the example MQTT broker in Chapter 3 was `test.mosquitto.org` (public, unauthenticated - do not use for anything private).
- RPC and notifications need no subscription entry; routing is by sink authority.
- SOME/IP bridging is NOT supported by the configurable streamer; use `example-streamer-implementations` bin `zenoh_someip` with vsomeip config.

## 5. Mixed-transport setup tips
- Zenoh on the vehicle side, MQTT5 to the cloud/mobile/MCU side is the pattern in both up-streamer-rust examples and the Chapter 3 lab (ThreadX board -> MQTT -> streamer -> Zenoh).
- Embedded: no official no_std crate. The Chapter 3 ThreadX app re-implements a send-only `UTransport` over `minimq` with hand-generated prost types (repos/sdv_lab/android_treadx/threadx/threadx-app/cross/app/src/utransport.rs, uprotocol_v1.rs). Good starting point for [[openbsw-overview]] / [[threadx-overview]] work.

## Pitfalls (checklist)
1. **Version matrix**: crates.io up-rust 0.9.0 pairs with up-transport-zenoh 0.9.x (zenoh ^1.9) and up-transport-mqtt5 0.4.0 (up-rust ^0.9); the streamer main uses up-rust 0.9 + zenoh transport 0.9.0. Chapter 3 lab apps use 0.5/0.6/0.7/0.8 combos - copying their Cargo.toml together with newer crates breaks the build. API differences already seen: `UPayloadFormat::UPAYLOAD_FORMAT_TEXT` vs `UPayloadFormat::Text` (git main), `UUri::try_from_parts` (not `from_parts`), typestate builder for Zenoh transport.
2. **Spec 1.5.x vs 1.6.0-alpha.x**: libraries target 1.6.0-alpha.7. UUID v7 vs v8 and different ue_id/instance semantics mean mixing old (1.5, e.g. Java/Android clients from 2023-24) with new clients is unsafe. Check which spec tag each library declares in its README.
3. **Zenoh pinning**: spec mandates Zenoh protocol major 1. up-transport-zenoh 0.9.1 needs zenoh ^1.9.0; the streamer/Chapter 3 lab used zenoh 1.2.1; up-transport-zenoh-cpp README pins zenoh-c 1.2.1. Mixed 1.x patch versions usually interoperate, but build all Rust parts from one Cargo.lock and use the same router version. (interop across patch versions: unverified)
4. **Authority names**: the key expression includes the authority; filter `//*/...` matches any. The streamer forwards by authority, so two apps with the same authority on different hosts will never be bridged (and a streamer endpoint's authority must equal what the app puts in its source UUri). Lowercase only. Local (empty) authority is rewritten by the transport.
5. **Multicast scouting** disabled in containers / many networks -> use explicit `connect`/`listen`.
6. **MQTT5** transport builds `paho-mqtt` (C) - needs cmake/openssl dev packages; Chapter 3 used a git dependency for mqtt5 at one point.
7. **Static subscriptions** in uStreamer (see above); live uSubscription mode is not implemented in what we read.
8. **crates.io staleness**: `up-subscription` on crates.io is 0.1.3 (2024); use git for current code. `up-streamer`/`up-transport-iceoryx2` are not on crates.io.
9. Success of `send()` is not a delivery receipt (up-rust docs/guide/utransport.md). For heartbeats, build your own sequence numbers and timeouts.
10. Publish has at-most-once semantics, so the heartbeat monitor must tolerate loss (N missed beats), not a single miss.

## Ideas for hackathon teams
- **Heartbeat/fault/mitigation schema crate** with .proto + Rust + Python generated types and a tiny `uguardian` helper (publish heartbeat, watchdog subscriber, emit fault, emit mitigation) usable by Doctor Whodunit teams; ties directly to the evidence chain ([[chapter4-challenge-doctor-whodunit]]).
- **Fault-injection shim**: a `UTransport` decorator (drop / delay / duplicate / corrupt by filter) wrapping the Zenoh transport - maps to openDuT campaigns "delayed or duplicated messages" ([[opendut-overview]]). Low effort, high demo value.
- **uprotocol-tap**: subscribe `//*/FFFFFFFF/FF/FFFF` (all) and dump UMessages as JSON/pcap-like log or forward to OpenSOVD/evidence store. No such tool found in org listing.
- **uProtocol <-> VSS/KUKSA provider**: map VSS paths to resource ids and publish signal updates as UMessages (no existing adapter found; see [[uprotocol-integration-notes]], [[vss-kuksa-overview]]).
- **Live uSubscription for streamer**: wire up-subscription-rust into configurable-streamer instead of static JSON (config has a reserved `live_usubscription` mode).
- **iceoryx2 transport**: spec exists (iceoryx2 0.6.1), repo has ~50 open issues - pick one, add a smoke test to the streamer's transport-smoke-suite ([[iceoryx2-overview]]).
- **Ankaios workload template** that starts a Zenoh router + uStreamer + app with the right env; Chapter 3 already has manifests for cruise-control-app ([[ankaios-overview]]).
- Documentation fixes: version-compat table across up-rust/up-transport-*/zenoh (does not exist upstream).

## Observed on 2026-10-03 (verifier): uStreamer Zenoh -> MQTT5
Setup, all from `repos/up-streamer-rust` (workspace zenoh 1.7.2, up-transport-zenoh 0.9.0, paho-mqtt 0.13.3; cmake and libssl-dev were present):
```bash
CARGO_BUILD_JOBS=8 cargo build --release -p configurable-streamer -p example-streamer-uses --features zenoh-transport,mqtt-transport --bins   # 2m59s wall, cold
printf 'listener 1883\nallow_anonymous true\n' > mosq.conf      # default mosquitto config rejects the docker-mapped connection
docker run -d --name mosq -p 1883:1883 -v $PWD/mosq.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto
cd configurable-streamer && ../target/release/configurable-streamer --config=CONFIG.json5    # unmodified CONFIG.json5, MQTT_CONFIG.json5, subscription_data.json
../target/release/mqtt_subscriber                                  # authority-a, 0x5678/1/0x1234, filter //authority-b/3039/1/8001
../target/release/zenoh_publisher --send-count 3                   # authority-b, 0x3039/1/0x8001, connects tcp/127.0.0.1:7447
```
Config used: streamer_uuri `authority-b` ue 78; static_file `subscription_data.json` (`"//authority-b/3039/1/8001": ["//authority-a/5678/1/1234"]`); zenoh endpoints authority-b and authority-c; mqtt endpoint authority-a at localhost:1883.
Result: mqtt_subscriber logged 3 `PublishReceiver: Received a message` lines (UMessage PUBLISH from `//authority-b/3039/1/8001`, protobuf Timer payload, 1 per second). Default log level hides the "Received" line unless `RUST_LOG=info`.
Notes: the streamer's `ZENOH_CONFIG.json5` makes the streamer itself a Zenoh router listening on 7447 (multicast off), so a separate `zenohd` on 7447 conflicts ("Address already in use"); publish to the streamer's 7447 instead, or move one of them. A second streamer started while one is running fails the same way. The `components/uprotocol/examples-hb` heartbeat example was not used.
