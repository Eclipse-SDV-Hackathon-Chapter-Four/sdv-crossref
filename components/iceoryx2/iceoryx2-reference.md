---
title: iceoryx2 reference (repos, crates, versions, APIs, CLI, limits)
type: reference
component: iceoryx2
tags: [iceoryx2, reference, versions, api, cli]
status: draft
sources:
  - https://github.com/eclipse-iceoryx/iceoryx2
  - https://crates.io/crates/iceoryx2
  - https://pypi.org/project/iceoryx2/
  - repos/iceoryx2/README.md
  - repos/iceoryx2/doc/release-notes/iceoryx2-v0.10.0.md
  - repos/iceoryx2/doc/release-notes/iceoryx2-unreleased.md
  - repos/iceoryx2/iceoryx2/src/config.rs
  - https://github.com/eclipse-iceoryx/iceoryx2
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[iceoryx2-quickstart]]"
  - "[[iceoryx2-howto]]"
  - "[[iceoryx2-integration-notes]]"
---

# iceoryx2 reference

## Links
| What | Where |
|---|---|
| Main repo | https://github.com/eclipse-iceoryx/iceoryx2 (clone: repos/iceoryx2 @ `ae9be314`, 2026-10-02) |
| Website | https://iceoryx.io |
| Book (by ekxide) | https://ekxide.github.io/iceoryx2-book |
| API docs | Rust https://docs.rs/iceoryx2 · C++ https://eclipse-iceoryx.github.io/iceoryx2/cxx/latest/ · C …/c/latest/ · Python …/python/latest/ |
| FAQ | repos/iceoryx2/FAQ.md (users), FAQ_ICEORYX_DEVS.md (contributors) |
| Release notes | repos/iceoryx2/doc/release-notes/ |
| Roadmap | repos/iceoryx2/ROADMAP.md |
| Community | Discourse https://community.iceoryx.io/ , developer meetup (GitHub wiki) |
| Yocto | https://github.com/eclipse-iceoryx/meta-iceoryx2 |
| C# bindings | https://github.com/eclipse-iceoryx/iceoryx2-csharp |
| ROS 2 RMW | https://github.com/ekxide/rmw_iceoryx2 ("alpha") |
| uProtocol transport | https://github.com/eclipse-uprotocol/up-transport-iceoryx2-rust (clone: repos/up-transport-iceoryx2-rust) |
| iceoryx classic (v1/v2.x) | https://github.com/eclipse-iceoryx/iceoryx (maintenance mode) |
| Commercial support | ekxide IO GmbH, https://ekxide.io |

## Versions (crates.io API, 2026-10-03)
| Version | Date | Highlights (release notes) |
|---|---|---|
| 0.10.0 | 2026-09-18 | Tunnel allow-list, reactive tunnel, remote-host association; FlatBuffers payloads; per-subscriber history; `Node::force_remove_service`; musl; work-in-progress ROS 2 gateway; events "always deliverable" API change |
| 0.9.0–0.9.3 | 2026-05-18 … 2026-07-08 | (see release notes) |
| 0.8.0 / 0.8.1 | 2025-12-23 / 2026-01-15 | last release of the old `iceoryx2-tunnel*` crates |
| 0.7.0 | 2025-09-13 | version used by up-transport-iceoryx2-rust |
| 0.6.0 / 0.6.1 | 2025-05 | version mandated by the uProtocol iceoryx2 spec (repos/up-spec/up-l1/iceoryx2.adoc) |
| 0.5.0 | 2024-12-23 | version locked in S-CORE's `score_crates` index (MODULE.bazel.lock of s-core repos) |
| 0.1.0 | 2023-12-14 | first release |
Upcoming on main (unreleased notes): the gateway has been restructured into `iceoryx2-link` + `iceoryx2-link-gateway` + `iceoryx2-link-adapter`, and the ROS 2 adapter crates have been renamed (an API break).

## Crates and packages (selection)
`iceoryx2` (core), `iceoryx2-bb-container` (shared-memory String/Vec/FlatMap…), `iceoryx2-bb-derive-macros` (`ZeroCopySend`), `iceoryx2-cli` (`iox2`), `iceoryx2-services-discovery`, `iceoryx2-link`, `iceoryx2-link-tunnel`, `iceoryx2-link-gateway`, `iceoryx2-integrations-zenoh-link-tunnel-cli` (all 0.10.0). Python: `iceoryx2` 0.10.0 on PyPI. C/C++: built from source (CMake), no distro packages found (unverified).

## Repo layout (repos/iceoryx2)
`iceoryx2/` core · `iceoryx2-bb/` building blocks (containers, posix, lock-free) · `iceoryx2-cal/` concept abstraction layer (shm, event, zero-copy connection backends) · `iceoryx2-pal/` platform abstraction (posix, configuration) · `iceoryx2-ffi/{c,python}` · `iceoryx2-cxx/` · `iceoryx2-cli/` (iox2, iox2-service, iox2-node, iox2-config, iox2-link) · `iceoryx2-link/` (link, tunnel, carrier, gateway, adapter) · `iceoryx2-services/discovery` · `iceoryx2-userland/record-and-replay` · `integrations/{zenoh,ros2}` (separate cargo workspaces) · `benchmarks/` · `examples/{rust,cxx,c,python,bazel,nostd}` · `config/` · `doc/`.

## API skeleton (Rust; C++ and Python mirror it)
```rust
let node = NodeBuilder::new().create::<ipc::Service>()?;                    // or local::Service
let svc  = node.service_builder(&"A/B/C".try_into()?)
               .publish_subscribe::<T>()        // or ::<[u8]>() for slices
               // .request_response::<Req, Resp>() / .event() / .blackboard_creator::<K>() / .blackboard_opener::<K>()
               .max_subscribers(8).history_size(0)   // optional QoS
               .open_or_create()?;                    // or create() / open()
let publisher  = svc.publisher_builder().create()?;
let sample     = publisher.loan_uninit()?.write_payload(value); sample.send()?;
let subscriber = svc.subscriber_builder().create()?;
while let Some(s) = subscriber.receive()? { /* *s derefs to T */ }
while node.wait(Duration::from_secs(1)).is_ok() { … }   // handles SIGINT/SIGTERM
```
Request-response: `client.send_copy(req)` then `pending.receive()`, and on the server side `server.receive()` then `active_request.send_copy(resp)`, which allows streaming responses (repos/iceoryx2/doc/user-documentation/request-response.md). Event: `notifier.notify_with_custom_event_id(id)`, `listener.timed_wait|blocking_wait|try_wait`. Blackboard: writer `entry::<T>(&key).update_with_copy(v)`, reader `entry::<T>(&key).get()` (repos/iceoryx2/examples/rust/blackboard/).

## Examples (examples/rust/, mostly mirrored in cxx/c/python)
publish_subscribe, publish_subscribe_dynamic_data, publish_subscribe_with_user_header, publish_subscribe_with_backpressure, complex_data_types, cross_language_communication_{basics,complex_types,container}, request_response(_dynamic_data, _with_events), event, event_based_communication, event_multiplexing, blackboard(_event_based_communication), discovery, discovery_service, domains, service_attributes, service_types, service_variant_customization, health_monitoring, flatbuffer_publish_subscribe, flatbuffer_request_response, docker. Each has a README and an `.exp` end-to-end test. Cross-language e2e tests: examples/cross-language-end-to-end-tests/.

## CLI (`iox2`, from `iceoryx2-cli`)
`iox2 service list|details|discovery|notify|listen|publish|subscribe|record|replay|hz` · `iox2 node list|details` · `iox2 config show|generate|explain` · `iox2 link tunnel|gateway`. The subcommands are separate binaries (`iox2-service` …) found through PATH (open bugs #2050/#2045 about lookup).

## Limits and defaults
- Default per service: 2 publishers, 8 subscribers, 20 nodes, history 0, subscriber buffer 2, 2 borrowed samples, 2 loaned samples. Event: 16 listeners and 16 notifiers. Req/resp: 2 servers, 8 clients. Blackboard: 8 readers (repos/iceoryx2/iceoryx2/src/config.rs). All of these are configurable. Memory is preallocated as roughly max_subscribers × buffer × payload.
- Payload: fixed-size, self-contained, no heap or pointers, no `Drop` / trivially destructible. Slices give dynamic size with reallocation. Custom alignment via `payload_alignment()`.
- No 32-bit ↔ 64-bit interop. Same iceoryx2 version on all sides (`VersionMismatch`). Same user unless `dev_permissions`.
- No async API (#47).

## Known open bugs (28 labeled bug, 2026-10-03)
See [[iceoryx2-howto]] "Other notable open bugs" and https://github.com/eclipse-iceoryx/iceoryx2.
