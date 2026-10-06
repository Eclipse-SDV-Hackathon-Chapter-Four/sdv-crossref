---
title: Pros, cons and when not to use - SDV components
type: synthesis
component: none
tags: [pros-cons, decision]
status: reviewed
sources:
  - components/iceoryx2/iceoryx2-overview.md
  - components/zenoh/zenoh-overview.md
  - components/uprotocol/uprotocol-overview.md
  - components/ankaios/ankaios-overview.md
  - components/autosd/autosd-overview.md
  - components/kanto/kanto-overview.md
  - components/sdv-landscape/sdv-landscape-overview.md
  - components/opensovd/opensovd-overview.md
  - components/openbsw/openbsw-overview.md
  - components/threadx/threadx-overview.md
last-verified: 2026-10-03
related:
  - "[[capability-map]]"
  - "[[integration-matrix]]"
  - "[[gap-register]]"
---

# Pros, cons and when not to use

A decision view of the 19 components under `components/` for your team (the 20th folder, [[sdv-landscape-overview]], is a catalogue, not a component). Facts come from the overview notes linked in each row. Anything not stated in a note is marked **(inference)**. Versions and activity are as of 2026-10-03.

Grouping: the "core nine" ([[sdv-landscape-overview]]: S-CORE, OpenSOVD, uProtocol, Zenoh, iceoryx2, KUKSA, Ankaios, OpenBSW, ThreadX, all High activity) are split into a messaging table and a rest-of-core table. The other ten are split into orchestration/OS, tooling/test, and dormant.

## 1. Per-component trade-offs

### 1.1 Core nine: messaging (iceoryx2, Zenoh, uProtocol)

| Component | Pros | Cons | Do NOT use when | Use instead |
|---|---|---|---|---|
| iceoryx2 ([[iceoryx2-overview]]) | Zero-copy shared memory, ~0.1-0.3 us latency that stays flat with payload size (251/283 ns observed); no daemon, so no single point of failure; `iox2` CLI introspection (list, hz, record, replay); quickstart verified in under 15 min | Pre-1.0 with breaking changes every minor, and all processes need the same version; fixed-layout POD payloads only (String/Vec are UB); stale shm after crashes; `/dev/shm` sizing in containers | Data must cross machines; messages are small and rare (a socket is simpler); you need dynamic schemas/JSON or persistence; consumers run as different Unix users | [[zenoh-overview]] for network; MQTT for broker/persistence; [[uprotocol-overview]] for portable addressing |
| Zenoh ([[zenoh-overview]]) | One protocol from MCU (zenoh-pico) to cloud; query and storage built in; router-less peer mesh; Python pub/sub verified with no router, Docker or sudo | Not an automotive standard by itself; plugins must match the exact `zenohd` version; multicast scouting may be blocked on venue Wi-Fi (unverified; default Docker bridge passed it (corrected 2026-10-03, see [[zenoh-overview]])); key-expression routing takes practice to debug | Hard-real-time in-process IPC; you need a signal model | [[iceoryx2-overview]] for same-host IPC; [[vss-kuksa-overview]] for signal modelling |
| uProtocol ([[uprotocol-overview]]) | One address (UUri) and envelope (UMessage) across Zenoh/MQTT5/SOME/IP; first-class RPC with correlation; clean, mockable Rust lib; 15-min Zenoh quickstart verified | Heavy churn (0.5 -> 0.10 in a year, spec still 1.6.0-alpha.7): pin everything; SDKs uneven outside Rust; uStreamer needs static subscription JSON; no data model, no inspector/recorder | Everything is on one host and needs zero-copy; you only need signal read/write; the team knows plain Zenoh/MQTT and has no cross-transport need | [[iceoryx2-overview]]; [[vss-kuksa-overview]] gRPC; plain [[zenoh-overview]] |

### 1.2 Core nine: the rest

| Component | Pros | Cons | Do NOT use when | Use instead |
|---|---|---|---|---|
| S-CORE ([[s-core-overview]]) | Real safety-oriented middleware (ASIL-B design target); QNX, EB corbos and AutoSD images already wired; very active (v0.9.0, 29/29 repos pushed) | Bazel only, multi-GB toolchains (Path B not run); fast API churn, the Orchestrator was removed in v0.9; QNX needs a licence | You need a vehicle-signal API, cloud link or container orchestration; the team has no Bazel experience | [[vss-kuksa-overview]]; [[ankaios-overview]]; Path A Cargo route (orchestrator + iceoryx2, verified) |
| OpenSOVD ([[opensovd-overview]]) | Open implementation of a real standard (ISO 17978); CDA proven on Mercedes/BMW/Porsche cars; Docker mock in ~2 min, easy `DataProvider` extension | Core has discovery/data only, no `faults` (issue #156); CDA and core use different base paths; no CDA binary; ODX/MDD authoring barrier; spec paywalled; default security accepts any credentials | You only need signal telemetry; you need hard real-time fault reaction (SOVD is QM); you have no ODX for the ECU (CDA cannot decode) | [[vss-kuksa-overview]]; S-CORE health/lifecycle ([[s-core-overview]]) |
| VSS / KUKSA ([[vss-kuksa-overview]]) | Standard data plane in one container, ~1,260 signals; shared vocabulary; validation and JWT scopes; get/set in 5 min, verified | Three gRPC APIs over time (v1 removed in 0.7.0), CLI/SDK lag; no persistence, QoS or certification; gRPC heavy for an MCU | You need a pub/sub bus for arbitrary events, history/persistence, or a safety path | [[zenoh-overview]] or [[uprotocol-overview]] for events |
| Ankaios ([[ankaios-overview]]) | Tiny footprint (1 core/256 MB); dependency ordering; control-interface API lets a workload read/change state; simple YAML, rootless daemonless Podman | Young ecosystem; docs drift between 0.x and 1.x (Ch3 used v0.6.0); no service discovery/DNS; no rescheduling across agents; express install has no auth | You need the K8s ecosystem/Helm, autoscaling, or service discovery | k3s (per the Ankaios comparison table); [[symphony-overview]] for fleet-level desired state |
| OpenBSW ([[openbsw-overview]]) | Builds and runs on a laptop in ~15-20 s, no hardware (verified build+run); real UDS/DoCAN/DoIP stacks; Rust and ThreadX options | ETL-heavy C++, steep for 2 days; no KUKSA/Zenoh/uProtocol integration upstream; DoIP server only; vcan/TAP need sudo; sparse demo app | Pure data-plane demo; nobody writes C++; no sudo | [[vss-kuksa-overview]], [[uprotocol-overview]] or [[zenoh-overview]] with scripts |
| ThreadX ([[threadx-overview]]) | Tiny, MIT licence; certified-safety lineage; NetX Duo and vendor SDK support | C API; Rust bindings hackathon-grade; toolchain/probe/udev setup eats the first hour; quickstart not run | HPC-class Linux workloads; no board on the table (AZ3166-only Rust demo) | [[openbsw-overview]] POSIX virtual ECU; Linux on the HPC side |

### 1.3 Orchestration and OS

| Component | Pros | Cons | Do NOT use when | Use instead |
|---|---|---|---|---|
| AutoSD ([[autosd-overview]]) | Immutable atomic updates (bootc/ostree); QM partition + SELinux for mixed criticality; one aib manifest to many targets (qemu, rpi4, ebbr...) | aib/osbuild quirks, medium ease; build needs root, ~15 GB, no cross-build; few SDV RPMs; quickstart not run | You want an orchestration API; you only need to run a container fast; sample images are PoC (root/password) | [[ankaios-overview]] for an API; plain Fedora/Ubuntu for speed |
| Symphony ([[symphony-overview]]) | Fleet-level desired-state model (Target/Solution/Instance); many providers; easy to fake MQTT/HTTP targets | Big, K8s-centric; many concepts; current momentum unverified; quickstart not run | You just need to start containers on one box | [[ankaios-overview]] |
| Kanto ([[kanto-overview]]) | Small Go footprint on containerd; cloud connectivity (Hono/Ditto) and OTA built in; Yocto layer | Effectively dormant (v1.0.0, code frozen mid-2024); single node; cloud-centric defaults; no uProtocol/Zenoh path | You need multi-node orchestration, safety-oriented lifecycle, or active upstream | [[ankaios-overview]] |
| Muto ([[muto-overview]]) | Only SDV project deploying ROS 2 stacks declaratively; rollback; working ROS Racer blueprint | ROS only; small community; thin docs; version unverified (not cloned) | Workloads are not ROS | [[ankaios-overview]] (inference: the general container case) |

### 1.4 Tooling, test and reference

| Component | Pros | Cons | Do NOT use when | Use instead |
|---|---|---|---|---|
| autowrx ([[autowrx-overview]]) | Zero-install browser start; VSS-first; good for ideation and demos; `docker run` observed working | Depends on hosted SaaS; old databroker (0.4.4, v1 API) and VSS 4.0 inside; prototype-grade runtime | Real-time or safety work; uProtocol/Zenoh-native designs; offline venue without a self-hosted instance | [[vss-kuksa-overview]] current databroker |
| Velocitas ([[velocitas-overview]]) | Fastest path from a VSS idea to a container app; typed vehicle model; templates + CI | Maintenance mode, pinned to old KUKSA (0.5.0); heavy devcontainer (~10 GB, privileged); MQTT/gRPC only | Signal-only read/write; Rust-first teams; strict 2-day limit without a prebuilt image | kuksa-client ([[vss-kuksa-overview]]) |
| SDV Blueprints ([[sdv-blueprints-overview]]) | Real compose files with published images; VSS/Kuksa spine; Fleet Management repo active | Pinned old versions (Databroker 0.6.0, Zenoh mismatch); docs drift; no common integration; quickstart not run here | You need safety/security evidence, production OTA, or a maintained orchestrator demo (software-orchestration is stale) | Individual component quickstarts, e.g. [[uprotocol-overview]], [[ankaios-overview]] (inference) |
| openDuT ([[opendut-overview]]) | Transparent L2/CAN across NAT; web UI, CLI and YAML; proven with the CDA against a real car | Heavy ~12-container stack (NetBird/Keycloak/Postgres/Traefik); mandatory hostnames/OIDC/root; ~1 h setup budget; not run | You need built-in fault injection, simple local traffic, no-root laptops, or timestamp-accurate replay | Local vcan/`canplayer`/`tc netem` (inference, from the openDuT fault-injection idea) |

### 1.5 Dormant or archived

| Component | Pros | Cons | Do NOT use when | Use instead |
|---|---|---|---|---|
| Chariott family ([[chariott-overview]]) | Clean Rust, good design docs; MIT; ready gRPC/MQTT shapes | Dormant 15-27 months; nightly Rust; DTDL/Azure-centric, no VSS | Any new design | [[vss-kuksa-overview]] + [[uprotocol-overview]] or [[zenoh-overview]] |
| SommR ([[sommr-overview]]) | Concept fits the Rust-leaning ecosystem (only pro) | Archived 2025-06-12; empty repo; no maintainers | Any dependency, ever | vsomeip (not Eclipse), e.g. via the uProtocol SOME/IP transport ([[uprotocol-overview]]) |

## 2. Head-to-heads

### 2a. iceoryx2 vs Zenoh vs uProtocol vs MQTT, for a 2-day team

| Criterion | iceoryx2 ([[iceoryx2-overview]]) | Zenoh ([[zenoh-overview]]) | uProtocol ([[uprotocol-overview]]) | MQTT (per [[iceoryx2-overview]], [[uprotocol-overview]], [[threadx-overview]]) |
|---|---|---|---|---|
| Scope | One host only | Host, network, MCU, cloud | Envelope/addressing on top of a transport | Broker-based network messaging |
| Infra to run | None (no daemon) | None in peer mode; router if multicast is blocked | Needs a transport (Zenoh is best supported) | A broker (inference: e.g. Mosquitto, as in [[chariott-overview]]) |
| Time to first message | <15 min, verified | Minutes, Python verified | 15 min Rust over Zenoh, verified | Not measured in the notes |
| Payloads | Fixed-layout POD only | Any bytes | Opaque payload + protobuf attributes | Any bytes; persistence via broker |
| MCU reach | No (no_std is PoC) | zenoh-pico (Zephyr, FreeRTOS, ESP-IDF, Arduino, ThreadX) | No official embedded SDK; Ch3 hand-rolled one over MQTT | Ch3 AZ3166 board used MQTT5 |
| Main 2-day risk | Version lockstep; stale shm | Multicast on venue Wi-Fi; plugin/version coupling | Version churn across crates | Extra broker to host (inference) |

**Verdict:** start with Zenoh for anything that crosses a process boundary on the network. Add uProtocol only when the challenge asks for it or needs RPC/portable addressing (both challenges name it for events, per [[chapter4-challenge-doctor-whodunit]] and [[chapter4-challenge-hack-to-the-future]]). Use iceoryx2 only for a measured same-host latency or zero-copy need. Use MQTT when an MCU or cloud already speaks it.

### 2b. Ankaios vs systemd/quadlets (AutoSD) vs Kanto vs plain docker compose

| Criterion | Ankaios ([[ankaios-overview]]) | systemd/quadlet on AutoSD ([[autosd-overview]]) | Kanto ([[kanto-overview]]) | docker compose (inference; used by [[sdv-blueprints-overview]]) |
|---|---|---|---|---|
| Multi-node, one API | Yes (server/agent) | No (BlueChi adds multi-node systemd control, per [[sdv-landscape-overview]]) | No, single node | No |
| Dependencies / restart | State-based dependencies, `restartPolicy` | Units (general knowledge, unverified) | Not covered in the note | `depends_on`/restart (inference) |
| Runtime API for workloads | Control interface (protobuf over FIFOs, Python/Rust SDK) | D-Bus (unverified) | Cloud-driven via Hono/Ditto | None for workloads (inference) |
| Maintenance state | Active, v1.0.4 | Active (aib, eclipse-autosd) | Dormant since mid-2024 | n/a |
| Setup cost | Podman + sudo, minutes not stated | Root build, ~15 GB, prebuilt QEMU image "under 15 min" | deb + containerd + sudo | Docker only; blueprints ~5 min |
| Fit for the challenge | Doctor Whodunit names "Ankaios on AutoSD"; dynamic restart/delete = fault injection | Host OS + QM partition + root watchdog | Free-style only (Kanto -> Ankaios migration recipe) | Fast local bring-up; default Docker bridge passed Zenoh multicast on one host (corrected 2026-10-03, see [[zenoh-overview]]) |

**Verdict:** Ankaios on AutoSD is the challenge stack; use compose only to get the services talking on day 1 morning, and do not start anything new on Kanto.

### 2c. "Diagnostic truth": OpenSOVD core vs CDA vs a hand-written REST facade

| Criterion | opensovd-core ([[opensovd-overview]]) | Classic Diagnostic Adapter ([[opensovd-overview]], [[openbsw-overview]]) | Hand-written REST facade (inference) |
|---|---|---|---|
| SOVD standard resources | Discovery, `data`, `bulk-data`; no `faults` yet (#156) | `data`, `faults` (0x19/0x14), `operations`, `modes`, `locks` | Whatever you write |
| Effort | Custom `DataProvider` ~1-2 h; Docker mock ~2 min | Heavy: ODX/MDD authoring, DoIP, build from source (~2 min on 32 cores) | Lowest (inference) |
| Proof so far | Docker mock verified | Real Mercedes/BMW/Porsche cars; OpenBSW virtual ECU via DoIP ([[hackfest-openbsw-playground]]) | None |
| Meets "exposed through OpenSOVD" ([[chapter4-challenge-doctor-whodunit]]) | Yes | Yes | No (inference) |
| Upstream value | Implementing `faults` (#156) is a real contribution | DoIP ACK interop patch may not be upstreamed | None |

**Verdict:** use opensovd-core with a `DataProvider` (stretch: implement `faults`); take the CDA path only if the team starts from the OpenBSW-SOVD-Demo; a home-made REST facade misses the brief.

### 2d. Embedded leg: OpenBSW POSIX virtual ECU vs ThreadX on AZ3166 vs ESP32/Arduino

| Criterion | OpenBSW POSIX vECU ([[openbsw-overview]]) | ThreadX on AZ3166 ([[threadx-overview]]) | ESP32/Arduino (inference, except the zenoh-pico fact) |
|---|---|---|---|
| Hardware needed | None | AZ3166 board (no board = no demo) | A board (inference) |
| Time to running | ~15-20 s build+run, verified | Toolchain/probe-rs/udev eats the first hour; not run | Not covered by any note |
| SDV protocols | UDS/DoCAN/DoIP; CAN via vcan (sudo) | MQTT5 and uProtocol uMessage (Ch3 threadx-rust) | zenoh-pico supports ESP-IDF and Arduino ([[zenoh-overview]]) |
| Eclipse "bonus tech" | Indirect (ThreadX build option) | Yes (ThreadX) | No (inference) |
| Track record | HackFest OpenBSW x CDA demo | Ch3 top two teams used the AZ3166 ([[chapter3-retrospective]], [[hackathon-patterns]]) | None in the notes |
| Fit for "jump between hardware and virtual" ([[chapter4-challenge-hack-to-the-future]]) | Virtual side; same code targets S32K148/STM32 | Hardware side; Linux sim port exists, QEMU recipe unverified | Hardware side only (inference) |

**Verdict:** start on the OpenBSW POSIX virtual ECU, and move to ThreadX only if boards are on the table (Ch4 hardware is still an open question). Use ESP32/Arduino with zenoh-pico only when the team brings its own board.

## 3. Reading the trade-offs

- **Verified beats promised.** iceoryx2, Zenoh, uProtocol, KUKSA, OpenSOVD and OpenBSW quickstarts were actually run; Ankaios, AutoSD, ThreadX, openDuT, Kanto, Symphony and Velocitas were not. Budget extra time for the second list ([[capability-map]]).
- **Version pinning is the most common con.** iceoryx2 lockstep, uProtocol churn, Zenoh plugin coupling, KUKSA API changes, Ankaios 0.x vs 1.x docs. Copy one known-good version set on day 1 (inference).
- **Old tutorials lie quietly.** Ch3 material uses Ankaios v0.6.0, up-rust 0.5/0.7 and old databrokers inside autowrx/Velocitas/Blueprints. Check the version before copying an example.
- **"Do not use when" is mostly about scope, not quality.** iceoryx2 is one host, KUKSA is signals not events, SOVD is QM not safety, Ankaios is not K8s. Most wrong picks are a layer mismatch; check [[integration-matrix]] to see which layer you need.
- **Venue networking is a hidden con.** Zenoh multicast may fail on venue Wi-Fi (unverified; the default Docker bridge passed it on one host (corrected 2026-10-03, see [[zenoh-overview]])); openDuT needs hostnames, OIDC and root. Have explicit endpoints or host networking ready.
- **Dormant does not mean archived.** No WG project is marked archived and SommR is the only archived one nearby, yet Chariott is dormant and Kanto's code is frozen (only docs touched in 2026). "Last push" overstates real activity. Do not start new work on any of the three ([[sdv-landscape-overview]]).
- **The brief decides close calls.** Doctor Whodunit names OpenSOVD, Ankaios and AutoSD; picking a technically equivalent alternative costs points on ecosystem fit (inference).
- **Gaps are scoring opportunities.** SOVD `faults` (#156), the iceoryx2-to-Zenoh gateway, a Kanto-to-Ankaios recipe and AutoSD images for KUKSA/uProtocol are all small, real contributions ([[gap-register]]).
