---
title: Capability map and hackathon tech radar
type: synthesis
component: none
tags: [capability-map, tech-radar, selection, chapter4]
status: reviewed
sources:
  - "[[sdv-landscape-overview]]"
  - "[[chapter4-overview]] (scoring rubric: Ecosystem Integrability 27 %, bonus tech)"
last-verified: 2026-10-03
related:
  - "[[integration-matrix]]"
  - "[[gap-register]]"
  - "[[reference-architecture-doctor-whodunit]]"
  - "[[reference-architecture-hack-to-the-future]]"
  - "[[pros-cons-when-not]]"
---

# Capability map and hackathon tech radar

Two questions your team will ask in the first hour: *"which project does X?"* and *"is it safe to bet two days on it?"*.
This note answers both. Section 1 is the layer map, section 2 the radar for a 2-day hack, section 3 the fit per Chapter 4 challenge.
Everything here is condensed from the per-component overviews; follow the links for evidence.

## 1. Layer map — which project does what

| Layer | Primary choice (active, verified here) | Alternatives / adjacent | Nothing in Eclipse SDV for… |
|---|---|---|---|
| **OS / runtime image** | [[autosd-overview]] (bootc, QM partition, quadlets) | EB corbos Linux (commercial, used at HackFest), plain Ubuntu/Fedora, QNX (S-CORE targets, licence) | — |
| **Safety-oriented middleware stack** | [[s-core-overview]] v0.9 (LoLa IPC, lifecycle, persistency KVS, logging, FEO) | — | a *released* ASIL-certified stack (S-CORE 1.0 gate is Nov–Dec 2026) |
| **Embedded basic software (MCU)** | [[openbsw-overview]] (C++/Rust, CAN/UDS/DoIP, POSIX virtual ECU) | [[threadx-overview]] as RTOS underneath; Zephyr (not Eclipse) | AUTOSAR-Classic compatibility |
| **RTOS** | [[threadx-overview]] | FreeRTOS (OpenBSW default), Zephyr | — |
| **In-host IPC (zero-copy)** | [[iceoryx2-overview]] 0.10 | S-CORE LoLa (inside S-CORE only), Zenoh SHM | a 1.0 / certified release |
| **Network middleware / messaging** | [[uprotocol-overview]] over [[zenoh-overview]] | MQTT5 (uProtocol transport), SOME/IP via vsomeip (uProtocol) | SOME/IP in Rust ([[sommr-overview]] archived) |
| **Vehicle data model** | VSS 6.1 — [[vss-kuksa-overview]] | DTDL ([[chariott-overview]] Ibeji, dormant) | thermal-runaway or child-presence signals (overlay needed) |
| **Signal broker** | KUKSA Databroker 0.7.1 — [[vss-kuksa-overview]] | — | persistence/history, QoS |
| **Diagnostics** | [[opensovd-overview]] (core server + Classic Diagnostic Adapter + fault-lib/DFM) | OpenBSW UDS/DoIP server (ECU side) | in opensovd-core: `faults` (#156), `updates` (#195), SSE `cyclic-subscriptions` and `triggers`, `/docs` (#92), mDNS discovery (#31); DFM → HTTP bridge. See the coverage table in [[opensovd-reference]] |
| **In-vehicle orchestration** | [[ankaios-overview]] 1.0.4 | [[kanto-overview]] (maintenance), [[muto-overview]] (ROS 2 only), systemd/quadlets ([[autosd-overview]]) | service discovery / DNS between workloads |
| **Cloud-to-edge orchestration / OTA** | [[symphony-overview]] | Hono/Ditto via Kanto | an Ankaios provider that is documented upstream; a signed update-manifest format (nothing SUIT-like in Eclipse SDV) |
| **Test infrastructure** | [[opendut-overview]] 0.10.2 (remote L2/CAN wire to DuTs) | plain vcan + can-utils, Docker compose | fault injection / replay inside openDuT |
| **Dev tooling / prototyping** | [[autowrx-overview]] (browser, VSS-first) | [[velocitas-overview]] (maintenance, pinned to old KUKSA) | offline-capable playground |
| **Reference apps** | [[sdv-blueprints-overview]] fleet-management, service-to-signal, e2e-vehicle-signals | companion-application / software-orchestration (stale) | a blueprint that touches diagnostics, S-CORE, OpenBSW or openDuT |

## 2. Hackathon tech radar (2-day horizon)

Rings are about *risk for a team with two days*, not about project quality.
"Verified" = the quickstart ran on this machine on 2026-10-03 and the observed output is in the note.

| Ring | Project | Why it sits there | Quickstart | Verified |
|---|---|---|---|---|
| **Adopt** | KUKSA Databroker + VSS | runs in 5 min, 1 260 signals, every blueprint speaks it; biggest trap is the v1/v2 API split | Docker, no sudo | yes |
| **Adopt** | uProtocol over Zenoh (Rust) | named in both challenges; pub/sub in 15 min; pin versions and it just works | cargo, no broker | yes; uStreamer Zenoh -> MQTT5 yes ([[uprotocol-howto]]) |
| **Adopt** | iceoryx2 | 20 s build, flat ~0.3 µs latency, record/replay via `iox2`; same-host only | cargo, no Docker | yes |
| **Adopt** | OpenSOVD gateway `--mock` and CDA | Docker mock in 2 min, CDA builds in 10 min; the *only* open SOVD implementation | Docker + cargo | yes |
| **Adopt** | OpenBSW POSIX virtual ECU | builds and runs in 20 s, real UDS/DoIP; vcan needs sudo | cmake | yes (build+run) |
| **Adopt** | Blueprint fleet-management | compose up, Grafana + rFMS in 5 min; good DW scaffold | Docker | pending verifier |
| **Adopt** | Ankaios | verified rootless with user-space binaries and podman, no sudo, no systemd; manifests are 1.x syntax; restart only on exit, dependents are not restarted when a dependency dies | podman (rootless is enough) | yes (rootless) |
| **Trial** | Zenoh direct | fine when uProtocol envelope is not required; router-less; multicast scouting may fail on venue Wi-Fi (unverified; default Docker bridge passed (corrected 2026-10-03, see [[zenoh-overview]])) | pip / cargo | yes (Python) |
| **Trial** | AutoSD prebuilt QEMU/RPi4 image | bonus points; boot in <15 min from prebuilt image; *building* needs root + ~15 GB | root podman | yes, prebuilt image boot under KVM ([[autosd-quickstart]]) (corrected 2026-10-03, see [[autosd-quickstart]]) |
| **Trial** | ThreadX on AZ3166 | bonus points; two Chapter 3 winners used it; toolchain eats the first hour; needs the board | arm toolchain + board | yes, cortex_m4 library via the OpenBSW image toolchain; no board ([[threadx-overview]]) (corrected 2026-10-03, see [[threadx-overview]]) |
| **Trial** | S-CORE (Cargo path) | orchestrator + iceoryx2 example in 2 min; everything beyond that is Bazel with multi-GB toolchains | cargo (A) / Bazel (B) | partly (A) |
| **Assess** | openDuT (EDGAR only) | bonus points; use the organiser's CARL and run only EDGAR; self-hosting is ~12 containers and root | Docker + sudo | stack yes (localenv), EDGAR join no ([[opendut-quickstart]]) (corrected 2026-10-03, see [[opendut-quickstart]]) |
| **Assess** | S-CORE reference integration (Bazel) | 30+ min, Docker, toolchain downloads; HackFest branches are broken, use upstream `inc_diagnostics@gateway_cda_int` | Bazel | no |
| **Assess** | Symphony | right tool for OTA/fleet desired-state; big, K8s-flavoured; momentum unclear | Docker `maestro up` | partial, Docker API only ([[symphony-docker-no-k8s]]) (corrected 2026-10-03, see [[symphony-overview]]) |
| **Assess** | autowrx | great for the first-hour "which signals" whiteboard; depends on hosted SaaS; bundles databroker 0.4.4 | Docker | yes |
| **Hold** | Velocitas | maintenance mode, pinned to KUKSA 0.5.0, 10 GB devcontainer | devcontainer | no |
| **Hold** | Kanto, Chariott/Ibeji/Agemo/Freyja, SommR | dormant or archived; mention only as "why not" or migration ideas | — | no |
| **Hold** | Muto | ROS 2 only; use only if the team already lives in ROS 2 | ROS 2 + Docker | no |

## 3. Fit per Chapter 4 challenge

Scoring reminder from [[chapter4-overview]] and the public Evaluation Forms (https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf): HackCoaches give 80 % of the score, **Ecosystem Integrability** is the largest criterion (27 %), and openDuT, AutoSD, ThreadX and Java/Jakarta EE each add +0.10 (max +0.40).
What the rubric rewards: Integrability 4 is "Multiple projects work together in a coherent flow" and 5 adds a "Reusable PR, issue, Blueprint extension or integration"; bonus tech counts only when "meaningfully used" ([[scoring-rubric-cheatsheet]]). So: *several Eclipse projects wired through a real data path*, plus one or two cheap bonus techs.

| Project | Doctor Whodunit (fault evidence) | Hack to the Future (portable feature) | Freestyle (Track 2) | Bonus |
|---|---|---|---|---|
| KUKSA / VSS | **core** — TractionBattery.Temperature.*, DTC lists, overlay for thermal-runaway | optional — not named in this challenge; Seat.*.OccupancyStatus, derive "parked" if you bridge to it ([[reference-architecture-hack-to-the-future]] 2b) | VSS → SOVD data mapping | — |
| uProtocol / Zenoh | **core** — heartbeat / fault / mitigation topics (proposed layout in [[uprotocol-howto]]) | **core** — same app on laptop, Pi, MCU via zenoh-pico | iceoryx2 transport hardening | — |
| OpenSOVD | **core** — "diagnostic truth"; expose faults via CDA or a small core DataProvider | marginal | implement `/faults` in core (#156); DFM → SOVD bridge | — |
| OpenBSW | strong — OpenBSW-SOVD-Demo has 5 injectable DTCs + Grafana | strong — presence-sensor ECU over CAN; "Flux Capacitor" branch | upstream the DoIP ACK patch | via ThreadX |
| iceoryx2 | useful — `iox2 record/replay` as independent evidence tap | useful — in-host IPC layer that is identical on every Linux target | Zenoh key-expression gateway | — |
| Ankaios | strong — supervisor; fault injection by restart/delete; control-interface app | useful — move workloads between nodes | Ankaios ↔ AutoSD quadlet story | — |
| S-CORE | medium — safety framing, persistency for evidence; runtime link to OpenSOVD is *not* public | medium — HPC middleware target | KUKSA provider in S-CORE; LoLa ↔ uProtocol bridge | — |
| openDuT | medium — no built-in injection; EDGAR as CAN replay executor is a design, not a feature | medium — connect virtual ECU, Pi, car | fix #495 (good-first-issue) | **+0.10** |
| AutoSD | medium — Guardian in QM partition | strong — same bootc image on QEMU and RPi4 | quadlets for KUKSA/uProtocol | **+0.10** |
| ThreadX | marginal | strong — MCU leg of the feature (zenoh-pico or MQTT) | — | **+0.10** |
| Symphony | marginal | medium — describe HPC + MCU software set, OTA step | Ankaios provider | — |
| Blueprints | fleet-management as telemetry/dashboard spine; add a fault leg | service-to-signal / e2e-vehicle-signals as portability scaffold | fix #71/#72/#74 | — |

## 4. Choosing what to bet two days on

- **A spine that touches five Eclipse projects**: KUKSA (state; DW only, optional for HF) + uProtocol/Zenoh (events) + one "truth" source (OpenSOVD for DW, a second target for HF) + one orchestrator (Ankaios or quadlets) + Grafana. For HF, swap KUKSA for OpenBSW behind a CAN ↔ uProtocol adapter ([[reference-architecture-hack-to-the-future]] 2a).
- **Cheap bonus points**: AutoSD prebuilt image booted in QEMU as the runtime; openDuT EDGAR joined to the organiser's CARL; ThreadX only if a board and a toolchain are already in the room.
- **Expensive detours to avoid**: building AutoSD images, self-hosting openDuT, S-CORE Bazel builds, Velocitas devcontainers, anything in the Hold ring.
- **Where the real gaps are** (and therefore where "innovation" points are): fault paths. No blueprint, no SOVD core endpoint, no openDuT feature and no VSS branch covers faults end-to-end today. See [[gap-register]].
