---
title: iceoryx2 overview
type: overview
component: iceoryx2
tags: [iceoryx2, ipc, zero-copy, shared-memory, middleware, rust, cpp, python]
status: reviewed
sources:
  - https://github.com/eclipse-iceoryx/iceoryx2
  - repos/iceoryx2/README.md
  - repos/iceoryx2/FAQ.md
  - repos/iceoryx2/ROADMAP.md
  - repos/iceoryx2/config/README.md
  - repos/iceoryx2/internal/plots/
  - https://crates.io/crates/iceoryx2
  - https://github.com/eclipse-iceoryx/iceoryx
  - https://github.com/eclipse-iceoryx/iceoryx2
last-verified: 2026-10-03
related:
  - "[[iceoryx2-quickstart]]"
  - "[[iceoryx2-howto]]"
  - "[[iceoryx2-reference]]"
  - "[[iceoryx2-integration-notes]]"
  - "[[s-core-overview]]"
  - "[[opensovd-overview]]"
  - "[[uprotocol-overview]]"
  - "[[zenoh-overview]]"
  - "[[ankaios-overview]]"
---

# iceoryx2 overview

Repo looked at: `repos/iceoryx2`, commit `ae9be314` (2 Oct 2026), workspace version `0.10.999` (main after the v0.10.0 release).

## What it is
Eclipse iceoryx2 is a **zero-copy, lock-free inter-process communication (IPC) library with a Rust core** and C, C++ and Python bindings (repos/iceoryx2/README.md). Processes on **one machine** share data through POSIX shared memory. A publisher writes its message straight into shared memory. Subscribers get a pointer to the same memory, so the payload is never copied or serialized. Because of that, latency stays about the same whatever the payload size (see benchmarks below).

It is the successor of Eclipse iceoryx ("iceoryx classic", C++, v1/v2.x). iceoryx classic is "in maintenance mode … only security fixes" and will reach EOL "shortly after the iceoryx2 v1.0 release". The upstream recommendation is to use iceoryx2 for new projects (https://github.com/eclipse-iceoryx/iceoryx README). There is no central daemon: unlike iceoryx classic's RouDi, iceoryx2 is fully decentralized, and every process discovers services through files under `/tmp/iceoryx2` and shared memory in `/dev/shm` (repos/iceoryx2/examples/rust/docker/README.md).

## What it is NOT
- **Not a network middleware.** Shared memory stops at the machine, VM or SoC-island boundary. Host-to-host needs the **link** (a tunnel over Zenoh, or a gateway to ROS 2), which upstream calls a "prototype … Only recommended for experimentation" (repos/iceoryx2-link/README.md).
- **Not a serialization framework.** Payloads must be self-contained, fixed-layout types: no heap, no pointers, `#[repr(C)]`, trivially destructible. `String`, `Vec`, `std::string` and `std::vector` give undefined behavior. Use the shared-memory containers from `iceoryx2-bb-container`, slices, or FlatBuffers (v0.10) instead (repos/iceoryx2/examples/rust/publish_subscribe/README.md; release notes v0.10.0 #1745).
- **Not async.** There is no async API ("on our roadmap", issue #47). Use the event pattern and WaitSet for push-style wakeups (repos/iceoryx2/FAQ.md "Async API").
- **Not S-CORE's `mw::com`.** S-CORE's communication module (LoLa) has its own zero-copy shared-memory implementation of ara::com, written in C++ (repos/s-core-communication/README.md). Within S-CORE, iceoryx2 is used by the **orchestrator** and **FEO**, not by `mw::com`; see [[iceoryx2-integration-notes]].
- **Not 1.0 and not certified.** The latest release is 0.10.0 (18 Sep 2026). No safety-certified iceoryx2 release was found. Safety is a design goal (tier-1 platform = "all safety and security features are working"), but **no platform is tier 1 yet** (README platform table).

## Architecture in five nouns
| Concept | Meaning | Source |
|---|---|---|
| **Node** | A process-local entity that owns services and ports and is used for liveness and dead-node cleanup (`NodeBuilder::new().create::<ipc::Service>()`). | repos/iceoryx2/examples/rust/publish_subscribe/publisher.rs |
| **Service** | A named communication channel (`"My/Funk/ServiceName"`) with one messaging pattern and static QoS (max ports, buffer sizes, history), stored as a static config file plus dynamic shared-memory state. | repos/iceoryx2/config/README.md; `iox2 service details` output in [[iceoryx2-quickstart]] |
| **Service variant** | `ipc::Service` (shared memory between processes), `local::Service` (heap, inter-thread), plus `*_threadsafe` versions. You switch variant without changing the rest of the code. | repos/iceoryx2/FAQ.md "Inter-Thread Communication" |
| **Port** | Endpoint of a pattern: Publisher/Subscriber, Client/Server, Notifier/Listener, Writer/Reader. | repos/iceoryx2/examples/ |
| **Messaging pattern** | **publish-subscribe** (zero-copy, history, backpressure); **request-response** (streaming responses); **event** (wake-up signalling, no payload, used with WaitSet); **blackboard** (shared key-value store, one writer and many readers). Pipeline and log are planned. | README.md; ROADMAP.md "Communication" |

Key mechanics:
- **Preallocation.** Each publisher preallocates a data segment large enough for the worst case, so a sender "never runs out of memory" (repos/iceoryx2/FAQ.md "Running Out of Memory"). Memory use grows with the `max-subscribers × buffer × payload` settings.
- **No background threads.** Connections are updated when you call the API. Call `update_connections()` if a short-lived publisher sends and exits before subscribers connect (FAQ "Losing Data").
- **Typed and dynamic payloads.** Typed `publish_subscribe::<T>()` uses a fixed-size `T`. Dynamic data uses `publish_subscribe::<[u8]>()` with `initial_max_slice_len` and an `AllocationStrategy` (`PowerOfTwo` etc.), and the publisher reallocates its segment (repos/iceoryx2/examples/rust/publish_subscribe_dynamic_data/publisher.rs). Optional **user header** per sample. **FlatBuffers** payloads have been supported since v0.10.0.
- **Type safety.** Every service stores the payload type name, size and alignment. A port with a different type gets `IncompatibleTypes`. Different library versions get `VersionMismatch`. Both were observed on 2026-10-03; see [[iceoryx2-quickstart]]. The check is name, size and alignment only (alignment compared with `<=`), and the type name is user-asserted: reordered same-size fields connect silently, and a manual `IOX2_TYPE_NAME` disables the only check (corrected 2026-10-03, see [[a-type-name-is-a-claim-a-layout-hash-is-a-proof]]).
- **Domains.** Separate process groups on one host by giving each its own config `global.prefix` or root path (repos/iceoryx2/examples/rust/domains/README.md).
- **Discovery.** Services are found through the filesystem (`Node::list`, `Service::list`, `iox2 service list`). An optional discovery service publishes changes (repos/iceoryx2/iceoryx2-services/discovery).

## Maturity and versions
- Current release **v0.10.0 (crates.io 2026-09-18)**. The PyPI wheel `iceoryx2==0.10.0` is also published. Release cadence: 0.5 Dec 2024, 0.6 May 2025, 0.7 Sep 2025, 0.8 Dec 2025, 0.9 May 2026 (+3 patch releases to Jul 2026), 0.10 Sep 2026. That is roughly one minor release every 3-5 months, with patch releases in between (crates.io API, https://github.com/eclipse-iceoryx/iceoryx2). APIs still break between minors (see the "API Breaking Changes" section in repos/iceoryx2/doc/release-notes/).
- Maintained mainly by **ekxide IO GmbH**, which also offers commercial support. The roadmap is funding-driven (ROADMAP.md "Main Focus").
- About 759k crates.io downloads. Open bugs: 28 (2026-10-03, GitHub), see [[iceoryx2-reference]].

## Languages
| Language | State | Notes |
|---|---|---|
| Rust | primary, done | `cargo add iceoryx2`; MSRV 1.89 (Cargo.toml) |
| C | done | `iceoryx2-ffi/c`, built by CMake with cargo underneath |
| C++ | done | `iceoryx2-cxx`, C++17 header API over the C FFI; `find_package(iceoryx2-cxx)` |
| Python | done | `pip install iceoryx2` (ctypes structs as payloads); bug #1533: slice length is reported in bytes |
| C# | separate repo, "may not be up to date" | https://github.com/eclipse-iceoryx/iceoryx2-csharp |
| Go, Java, Kotlin, Zig, TS, … | planned | README "Language Bindings" |
Cross-language interop works only for fixed-size ints, `f32`/`f64` and the `iceoryx2-bb-container` types, and type names must match (README of each example; `cross_language_communication_*` examples).

## Platforms and safety claims
From the README support table: Linux x86_64/aarch64/32-bit, FreeBSD, macOS and Windows are **tier 2** ("restricted security and safety feature set"). **QNX 7.1/8.0 are tier 3** ("not tested in our CI"). Android, no_std bare metal and VxWorks are proof-of-concept. FreeRTOS, ThreadX and RTEMS are planned. Yocto layer: meta-iceoryx2. 32-bit and 64-bit processes cannot interoperate (FAQ). S-CORE builds a QNX 8 variant from a qorix-group fork (`iceoryx2_qnx8` in repos/s-core-orchestrator/src/orchestration/BUILD). Safety: designed for ISO 26262 contexts and ekxide sells certification support, but no certificate or ASIL claim exists for an iceoryx2 release (unverified beyond web search; see https://github.com/eclipse-iceoryx/iceoryx2).

## Performance (repo benchmarks)
- README plot data (repos/iceoryx2/internal/plots/benchmark_mechanism_comparison_i7_13700h.dat), round-trip/2 latency on an i7-13700H: **iceoryx2 ~0.09-0.10 µs, flat from 64 B to 4 MB**. iceoryx classic: 1.1 µs. Message queue: 1.1 µs at 64 B rising to 980 µs at 4 MB. Unix domain socket: 1.6 µs rising to 1100 µs. On a Raspberry Pi 4: iceoryx2 ~0.8 µs vs 2.9 µs for iceoryx classic (…_rp4.dat).
- Per-platform table (benchmark_architecture_os_comparison.dat, ns): Ryzen 9 5950X Linux 168/173, Windows 205; i7-13700H 92 (same core) / 326 (different cores); RPi 4B 774.
- **Observed 2026-10-03** (this machine, AMD Ryzen 9 5950X, `benchmark-publish-subscribe --bench-ipc`, release build): **251 ns at 8 B, 283 ns at 4 MiB** (ipc); ipc_threadsafe 339/363 ns. This confirms that latency is independent of payload size. These are busy-wait numbers. Event-based wakeups add syscall latency, and issue #1240 reports "very high latency in realtime kernel".

## Pros / cons and when not to use it
Pros: much lower and flatter latency than any socket or broker; no daemon, so there is no single point of failure; Rust core with C/C++/Python; deterministic preallocated memory; strong CLI introspection (`iox2 service list|details|subscribe|hz|record|replay`); permissive Apache-2.0/MIT license; QNX path exists and is used by S-CORE.

Cons: pre-1.0, breaking changes every minor release, and every process must use the **same iceoryx2 version**. Fixed-size, POD-like payloads require design discipline. Same-user only unless you set `dev_permissions` (no access-rights management yet). Stale shared memory after crashes. `/dev/shm` sizing in containers. The host-to-host tunnel and the ROS 2 gateway are prototypes.

Do not use it when: the data has to cross machines (use [[zenoh-overview]], SOME/IP, DDS or MQTT directly); messages are small and infrequent and a socket is simpler; you need dynamic schemas, JSON or a broker with persistence; or the consumers run as different Unix users without the dev flag.

| vs | iceoryx2 is better at | the other is better at |
|---|---|---|
| Zenoh | intra-host latency and true zero-copy for large data (Zenoh SHM still uses its own protocol and routing) | network, routing, queries and storage. They complement each other: the iceoryx2 Zenoh tunnel bridges them |
| DDS | about 10-1000× lower local latency, no serialization, no discovery traffic | interoperability standard, rich QoS, network, ROS 2 default |
| SOME/IP | local IPC | the automotive standard on Ethernet between ECUs; AUTOSAR tooling |
| MQTT | latency and determinism | broker, cloud connectivity, persistence, any language |
| uProtocol | raw speed, plain API | a transport-agnostic, portable addressing model. iceoryx2 can be one *transport* under uProtocol (up-transport-iceoryx2-rust, early) |

## Hackathon ideas (gaps and small contributions)
1. **uProtocol transport refresh**: up-transport-iceoryx2-rust pins iceoryx2 0.7 and up-rust 0.7, has a 2-line README and is pub/sub only (repos/up-transport-iceoryx2-rust/Cargo.toml). Bump it to 0.10, add an RPC (request-response is forbidden by the spec, so it would go over pub/sub), and write a quickstart. This fits the "Hack to the Future" portability story ([[chapter4-challenge-hack-to-the-future]]).
2. **OpenSOVD fault-lib on iceoryx2**: fault-lib already reports faults to the DFM over iceoryx2 (repos/opensovd-fault-lib/README.md). A Doctor Whodunit team can tap the fault stream with `iox2 service subscribe`/`record`/`replay` as an independent evidence recorder ([[chapter4-challenge-doctor-whodunit]]). `iox2 record` stamps the recorder's receive time (1 ms poll) and the header carries no publish time or sequence, so the payload must carry producer timestamps and counters; `replay --repetitions` doubles as a repetition fault injector ([[a-replay-is-evidence-only-with-the-producers-stamps]]).
3. **Ankaios manifest example** with two podman workloads sharing `/dev/shm` and `/tmp/iceoryx2` (no upstream example exists; see [[ankaios-howto]]).
4. **KUKSA/VSS bridge**: publish VSS signals from the KUKSA databroker into iceoryx2 services for local high-rate consumers. No such integration exists ([[vss-kuksa-overview]]).
5. Small PRs: fix the Python README (`pip install iceoryx2==0.10.999` is a version that does not exist, repos/iceoryx2/examples/python/README.md); give the C++ `publish_subscribe` example an `IOX2_TYPE_NAME` so it talks to the Rust example; implement the `iox2 node` cleanup subcommand that the FAQ marks as "NOT YET IMPLEMENTED" (`iox2 node` only has list/details on main).
