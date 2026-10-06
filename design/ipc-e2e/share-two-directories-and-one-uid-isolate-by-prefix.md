---
title: Share two directories and one UID; isolate ECUs by prefix, not by container
type: pattern
cluster: ipc-e2e
component: none
tags: [shared-memory, containers, podman, docker, ankaios, dev-shm, namespaces, uid, cleanup, domains, iceoryx2]
status: draft
sources:
  - repos/iceoryx2/examples/rust/docker/README.md
  - repos/iceoryx2/examples/rust/domains/README.md (config.global.prefix)
  - repos/iceoryx2/FAQ.md (access rights, dev_permissions, ExceedsMaxSupported, Docker shm size)
  - repos/iceoryx2/iceoryx2-bb/posix/src/process_state.rs (liveness by file lock)
  - https://man7.org/linux/man-pages/man7/ipc_namespaces.7.html (System V IPC and POSIX message queues only)
  - https://docs.docker.com/reference/cli/docker/container/run/ (--ipc modes; `none` = /dev/shm not mounted)
  - repos/s-core-communication/score/mw/com/doc/tutorial/chapter_10/README.rst (uid access control per ASIL)
last-verified: 2026-10-03
related:
  - "[[iceoryx2-howto]]"
  - "[[ankaios-howto]]"
  - "[[a-container-is-an-ecu-zenoh-is-the-only-door]]"
  - "[[freedom-from-interference-is-a-stack-of-layers]]"
applies-to: [iceoryx2, ankaios, autosd, s-core]
gap-rows: [C1, C5, E5]
---

# Share two directories and one UID; isolate ECUs by prefix, not by container

**Problem.** Two workloads in separate containers cannot see each other's iceoryx2 services, or they see each other when they were meant to be two separate "ECUs". After a crash, every restart fails with `ExceedsMaxSupportedPublishers`, and `/dev/shm` holds thousands of stale files (2858 on this vault's machine).

**Forces.**
- Containers isolate by namespace, and iceoryx2 discovers through the filesystem.
- iceoryx2 has no access-rights management yet: only the creating user can open resources.
- Rootless and rootful podman map UIDs differently.
- Preallocated worst-case memory meets a 64 MB default container `/dev/shm`.

**The rule.** An iceoryx2 domain is **(a)** a `/dev/shm` (data segments), **(b)** a `/tmp/iceoryx2` (service and node files, plus the lock files that prove a node is alive) and **(c)** one UID. Share all three between workloads that must talk. Separate workloads that must *not* talk with a distinct **`global.prefix`** (or root path) in the iceoryx2 config, not by trusting container walls. PID namespaces do not matter, because liveness is a file lock that the kernel releases on crash. The IPC namespace does not matter for POSIX shm either, because it isolates only System V IPC and POSIX message queues. What matters is which tmpfs is mounted at `/dev/shm`. Prefer explicit `-v /dev/shm:/dev/shm -v /tmp/iceoryx2:/tmp/iceoryx2` over `--ipc=host`. `--ipc=host` gives the host `/dev/shm` only by runtime convention, and it never shares `/tmp/iceoryx2`.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| iceoryx2 docker example | bind `/dev/shm` and `/tmp/iceoryx2`; create `/tmp/iceoryx2` before starting containers | the minimal working recipe |
| iceoryx2 domains example | `config.global.prefix` per group; "strictly separated" on one machine | two ECUs on one host without two kernels |
| Linux `ipc_namespaces(7)` | isolates System V IPC and POSIX message queues, not POSIX shm | why the namespace flag is the wrong lever |
| S-CORE LoLa ch. 10 | access control by `uid` lists per ASIL level, required for ASIL-B (AoU) | UID is the FFI boundary of shared memory |
| Docker/Podman `--ipc` | `none` = /dev/shm not mounted; `host` = host IPC namespace | how runtimes couple /dev/shm to IPC mode |

**On the Eclipse SDV stack.**
- Ankaios (C1): in `commandOptions`, add `-v /dev/shm:/dev/shm`, `-v /tmp/iceoryx2:/tmp/iceoryx2` and `--user <same uid>` on both workloads. Run both under the same podman mode (rootful or rootless); mixing them gives different UIDs on the files. The existing [[ankaios-howto]] recipe uses `--ipc=host` and is unverified.
- With a bind-mounted host `/dev/shm`, the host tmpfs size governs, so `--shm-size` stops being the knob (inferred from mount semantics, unverified).
- Two simulated ECUs on one laptop: give each its own prefix (`ecu_a_`, `ecu_b_`) and join them only through the Zenoh tunnel, so the only door is the one you meant ([[a-container-is-an-ecu-zenoh-is-the-only-door]]).
- Cleanup: at start-up, `Node::list` → `NodeState::Dead(v) => v.remove_stale_resources()`. On `ExceedsMaxSupported*`, call `try_cleanup_dead_nodes()` and retry. Reap children, because zombies keep PIDs alive (FAQ). `iox2 node` cleanup is not implemented (E5) ([[iceoryx2-howto]]).
- `dev_permissions` is a development flag. Shipping it removes the UID boundary that S-CORE treats as an ASIL-B assumption ([[freedom-from-interference-is-a-stack-of-layers]]).

**The trap.** Adding `--ipc=host` and expecting discovery to work, or relying on container separation to keep two "ECUs" apart while both bind the same `/dev/shm`.

**For a hackathon team.** Write one Ankaios manifest with two podman workloads sharing the two mounts and one UID, plus a third workload with prefix `ecu_b_` that provably cannot see them. Upstream it as the missing example (C1). Pitch: "a domain is two directories and one UID; an ECU boundary is a prefix plus a tunnel".

**Evidence.** The docker and domains READMEs and the FAQ were read 2026-10-03. File-lock liveness is in `process_state.rs` lines 13–15. That it holds across PID namespaces is inferred from code reading and was not tested. The `ipc_namespaces(7)` and Docker `--ipc` text were fetched 2026-10-03. The stale-file count is from [[iceoryx2-quickstart]]. The LoLa uid ACL is from tutorial chapter 10, lines 236–247.
