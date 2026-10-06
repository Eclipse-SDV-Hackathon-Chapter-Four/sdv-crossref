---
title: iceoryx2 how-to recipes and pitfalls
type: howto
component: iceoryx2
tags: [iceoryx2, howto, pitfalls, containers, cleanup, permissions, cross-language]
status: draft
sources:
  - repos/iceoryx2/FAQ.md
  - repos/iceoryx2/config/README.md
  - repos/iceoryx2/iceoryx2-cxx/README.md
  - repos/iceoryx2/examples/rust/docker/README.md
  - repos/iceoryx2/examples/rust/domains/README.md
  - repos/iceoryx2/examples/cxx/cross_language_communication_basics/README.md
  - repos/iceoryx2/examples/rust/publish_subscribe_dynamic_data/publisher.rs
  - https://github.com/eclipse-iceoryx/iceoryx2/issues?q=is%3Aissue+is%3Aopen+label%3Abug
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[iceoryx2-quickstart]]"
  - "[[iceoryx2-reference]]"
  - "[[ankaios-howto]]"
---

# iceoryx2 how-to

## Use iceoryx2 in your own project
- **Rust**: in `Cargo.toml`, add `iceoryx2 = "0.10.0"` (plus `iceoryx2-bb-container = "0.10.0"` for shared-memory strings and vectors). Put **shared payload types in a separate library crate**. If each binary defines the type itself, the type names differ and you get `IncompatibleTypes`. The workaround is `#[type_name("MyType")]` (FAQ "Unable To Connect Due To IncompatibleTypes"; see repos/iceoryx2/examples/rust/_examples_common).
- **C++**: for a quick start, build the whole repo with `cmake -S . -B target/ff/cc/build`. For an out-of-tree project, install C, bb-cxx and cxx into a prefix as described in repos/iceoryx2/iceoryx2-cxx/README.md ("Build instructions for integrator"), then `find_package(iceoryx2-cxx 0.10.0 REQUIRED)` and `target_link_libraries(app iceoryx2-cxx::static-lib-cxx)` (repos/iceoryx2/examples/cxx/publish_subscribe/CMakeLists.txt).
- **Python**: `pip install iceoryx2==<same version as your Rust/C++ side>`. Payloads are `ctypes.Structure` with a `type_name()` staticmethod (repos/iceoryx2/examples/python/publish_subscribe/transmission_data.py).
- **Bazel**: supported (MODULE.bazel; repos/iceoryx2/doc/bazel, examples/bazel). S-CORE consumes it through `@score_crates//:iceoryx2`.

## Define a payload type
Rust:
```rust
#[derive(Debug, Default, ZeroCopySend)]
#[repr(C)]
#[type_name("TransmissionData")]   // only needed for cross-language / cross-crate matching
pub struct TransmissionData { pub x: i32, pub y: i32, pub funky: f64 }
```
C++: the struct must be trivially destructible and contain no pointers. For cross-language use, add `static constexpr const char* IOX2_TYPE_NAME = "TransmissionData";` (repos/iceoryx2/examples/cxx/cross_language_communication_basics/README.md). Since v0.10 there is also `IOX2_DEFINE_TYPE_NAME` for types you cannot modify. Only fixed-size ints, `f32`/`f64` and the `iceoryx2-bb-container` types are cross-language safe (example READMEs).

## Send variable-size data
Use slices: `.publish_subscribe::<[u8]>()`, set `.initial_max_slice_len(n)` and `.allocation_strategy(AllocationStrategy::PowerOfTwo)` on the publisher, then `publisher.loan_slice_uninit(len)` (repos/iceoryx2/examples/rust/publish_subscribe_dynamic_data/publisher.rs). There are two pitfalls. When the publisher reallocates and then exits, samples can be lost (FAQ "Losing Dynamic Data"). Growth can also hit `SIGBUS` under overcommit (FAQ "SIGBUS Error"). An alternative is FlatBuffers (v0.10, `examples/rust/flatbuffer_publish_subscribe`). You can also serialize to bytes yourself (protobuf/CDR) into a `[u8]` slice, but then you give up part of the zero-copy benefit.

## Wake up instead of polling
Pub/sub does not notify by itself. Pair it with an **event** service (Notifier/Listener) and wait on a `WaitSet` (examples `event_based_communication`, `event_multiplexing`). `listener.timed_wait(...)` and `blocking_wait(...)` are the primitives (repos/iceoryx2/examples/rust/event/listener.rs). Since v0.10 the Zenoh tunnel can notify an event service named after the service when it delivers remote samples (`--notify`).

## Configuration (iceoryx2.toml)
Lookup order: `$PWD/config/iceoryx2.toml`, then `$HOME/.config/iceoryx2/iceoryx2.toml`, then `/etc/iceoryx2/iceoryx2.toml`, then built-in defaults (repos/iceoryx2/config/README.md). Run `iox2 config generate local|global` to write a full file, and `iox2 config explain` to describe the keys.

Main keys: `global.root-path` (default `/tmp/iceoryx2/`; `/data/iceoryx2/` on Android; `C:\Temp\iceoryx2\` on Windows, per repos/iceoryx2/iceoryx2-pal/configuration/src/lib.rs), `global.prefix` (default `iox2_`), `global.node.cleanup-dead-nodes-on-creation|destruction`, and `defaults.publish-subscribe.*` (max-subscribers 8, max-publishers 2, max-nodes 20, publisher-history-size 0, subscriber-max-buffer-size 2, backpressure `RetryUntilDelivered`, safe-overflow true; repos/iceoryx2/iceoryx2/src/config.rs). Event defaults are 16 listeners, 16 notifiers and 36 nodes. Request-response defaults are 2 servers and 8 clients. Blackboard defaults to 8 readers. You can override any of these per service in the builder (`.max_subscribers(…)`, `.history_size(…)`, …).

A partial file works. This was used on 2026-10-03:
```toml
[global]
prefix = "hosta_"
```

## Isolate groups of processes (domains)
Give each group its own `global.prefix` (or root-path). Processes in different domains do not see each other (repos/iceoryx2/examples/rust/domains/README.md; confirmed by the control run in [[iceoryx2-quickstart]]). This is handy when several hackathon teams share one machine.

## Containers: Docker, Podman, Ankaios
- Share **both** `/dev/shm` (data) and `/tmp/iceoryx2` (service and node files) between containers and the host. `--ipc=host` is the wrong lever: the IPC namespace does not cover POSIX shared memory, and it does not share `/tmp/iceoryx2` either (repos/iceoryx2/examples/rust/docker/README.md, docker-compose.yml there; see [[share-two-directories-and-one-uid-isolate-by-prefix]]):
  `docker run -v /dev/shm:/dev/shm -v /tmp/iceoryx2:/tmp/iceoryx2 …`. Create `/tmp/iceoryx2` before you start the containers.
- Run all containers with the **same UID** as the host processes. Docker defaults to root, which forces `sudo` on the host side (docker README).
- The default container `/dev/shm` is 64 MB, and iceoryx2 preallocates for the worst case. Raise it with `--shm-size=` (FAQ "Docker - Small Shared Memory Size").
- Container `/tmp` is usually not tmpfs, so many file operations are slow. Mount tmpfs or the host `/tmp` (FAQ "Slow System").
- Ankaios (Podman runtime): put the same flags in the workload's `runtimeConfig` `commandOptions` (see [[ankaios-howto]], item 5). There is no upstream Ankaios + iceoryx2 example.
- Dead-node detection across PID namespaces has not been tested (unverified). iceoryx2 checks liveness through file locks, so the PID namespace should not matter (code-read, untested) (corrected 2026-10-03, see [[share-two-directories-and-one-uid-isolate-by-prefix]]).

## Permissions: different users
There is no access-rights management yet, so only the creating user can open the resources. For development only, build with `--features dev_permissions` (cargo) or `-DIOX2_FEATURE_DEV_PERMISSIONS=On` (CMake) to make everything world-accessible (FAQ "Accessing Services From Multiple Users"). Known issue: health checks break with dev_permissions (#1460). If `/dev/shm` has the sticky bit set, other users cannot remove the files (FAQ "Insufficient Permission To Remove Shared Memory").

## Clean up after crashes
- Normally, the next process that creates a node or opens the service cleans up dead nodes. You see `Dead node … detected` in the log (FAQ).
- In code: `Node::<ipc::Service>::list(...)`, then `NodeState::Dead(view) => view.remove_stale_resources()`. Use `service.blocking_cleanup_dead_nodes(...)` on `ExceedsMaxSupported*` errors (FAQ). Since v0.10 there is also `Node::force_remove_service` for corrupted services.
- Manual nuclear option (dev box, all iceoryx2 processes stopped): `rm -rf /dev/shm/iox2_* /tmp/iceoryx2`. The machine used on 2026-10-03 had 2858 stale `iox2_*` files.
- **Zombie processes** (children that were never reaped) keep their PID alive, so iceoryx2 does not see them as dead and you get `ExceedsMaxSupportedPublishers`. Make sure your launcher calls `wait()` (FAQ).
- **systemd**: always set `RemoveIPC=no`, or systemd deletes the shared memory and corrupts services (FAQ "Service In Corrupted State").
- `iox2 node` has only `list` and `details` on main. The cleanup subcommand that the FAQ mentions is not implemented.

## Debugging checklist
| Symptom | Cause / fix |
|---|---|
| `IncompatibleTypes` | Different type name, size or alignment. Use a shared type crate, `#[type_name]` or `IOX2_TYPE_NAME`. Reordered same-size fields pass this check silently ([[a-type-name-is-a-claim-a-layout-hash-is-a-proof]]). Observed: Rust example vs C++ example. |
| `VersionMismatch` | Processes built with different iceoryx2 versions. Observed: PyPI 0.10.0 vs main. Pin one version everywhere. |
| `ExceedsMaxSupportedPublishers/Subscribers` | Too many ports (default 2 publishers / 8 subscribers) or dead nodes not yet cleaned up. Raise the limits in the builder or config, or call `blocking_cleanup_dead_nodes`. |
| Subscriber receives nothing | The publisher exited too fast: call `update_connections()`. Different domain or prefix. Different user. |
| `SIGBUS` | `/dev/shm` full or overcommit. Check `du -sh /dev/shm` and raise `--shm-size`. |
| `HangsInCreation` / corrupted service | Something deleted files (systemd RemoveIPC, tmp cleaners), mixed versions, or a crash. Clean up stale resources. |
| Too many open files / mmaps | Raise `nofile` (benchmarks/README.md) and `vm.max_map_count` (FAQ). |
| Debug output | `export IOX2_LOG_LEVEL=Trace` (FAQ). |

## Other notable open bugs (2026-10-03)
#2035: in 0.10.0, `Publisher::loan` heap-allocates once per sample, a regression from 0.9.1 that matters for real-time use. #1880: dead-node cleanup can `fatal_panic` and kill unrelated processes during concurrent node creation. #1869: on Windows, killed processes leave stale resources that cannot be deleted. #923: pub/sub handle creation order issues. #1240: high latency on an RT kernel. QNX 8 build and fchmod issues: #1992, #1274.
