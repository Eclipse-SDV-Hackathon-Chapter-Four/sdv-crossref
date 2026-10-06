---
title: Hackathon patterns across editions (2022-2025) and advice for Chapter 4
type: synthesis
component: none
tags: [synthesis, retrospective, patterns, advice, first-two-hours]
status: draft
sources:
  - event/chapter3-retrospective.md
  - event/earlier-chapters.md
  - https://eclipsesdv.org/blogs/meet-the-2025-sdv-hackathon-finalists-and-winners-and-explore-their-code/
  - https://blogs.eclipse.org/node/7997
  - https://blogs.eclipse.org/post/diana-kupfer/eclipse-sdv-hackathon-2025-%E2%80%9C-indispensable-experience-any-aspiring-software
  - repos/sdv_lab
  - repos/hc3-ArBytesMoral
  - repos/hc3-A-kiki
  - repos/hc3-challenge-mission-update-possible
  - repos/hc2-challenge-shift-to-sdv
  - repos/bcx-hackchallenge-driving-score
last-verified: 2026-10-03
related:
  - "[[chapter3-retrospective]]"
  - "[[earlier-chapters]]"
  - "[[chapter4-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[ankaios-overview]]"
  - "[[uprotocol-overview]]"
  - "[[zenoh-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[opendut-overview]]"
  - "[[opensovd-overview]]"
  - "[[autosd-overview]]"
  - "[[openbsw-overview]]"
  - "[[threadx-overview]]"
  - "[[symphony-overview]]"
---

# Hackathon patterns across editions

Evidence base: [[chapter3-retrospective]] and [[earlier-chapters]] (read those for citations). Statements marked *inferred* are my synthesis, not organiser statements. There is no public Slack/chat log, so the most-asked questions are inferred from README warnings, known-issue files and issue trackers.

## 1. Challenge shapes that repeat
| Shape | Examples | What teams get | What teams must build |
|---|---|---|---|
| **A. "Here is a stack, invent a scenario"** | 2023/2024 Maestro (Smart Trailer / truck fleet), 2024 Sunken Kitchen, 2025 Virtual SDV Lab, Chapter 4 freestyle ([[chapter4-freestyle-track]]) | Devcontainer or shared hardware, sample app, a data source (simulator, board, recordings) | A feature with a story + diagram. Open-ended, so the story decides ranking |
| **B. "Fill in a missing piece of a reference pipeline"** | 2025 Update Possible (write the Rust Symphony provider), 2024 Shift to SDV connectivity path (Symphony Provider) | Working cloud+vehicle skeleton, a pinned manifest | The provider/adapter, policy logic, UI; may add rollback/canary |
| **C. "Real hardware or sim in the loop"** | 2022 Hack the Truck / lights, 2024 Play by Wire, ThreadX challenge, 2025 sdv_lab (CARLA, AZ3166) | A shared simulator or physical rig, SDK, example recordings | Anything that makes the physical/sim side react visibly |
| **D. "Portability / swap the transport"** | uProtocol over MQTT5 vs Zenoh in 2025; Chapter 4 [[chapter4-challenge-hack-to-the-future]] (same service on sim, MCU, real car) | Spec + libraries | Mapping the same service to a different transport/target |
| **E. "Prove it works" (evidence/diagnostics)** | 2023 eCAL tracing contribution; Chapter 4 [[chapter4-challenge-doctor-whodunit]] (fault injection, diagnostic truth) | Instrumented runtime | Tests, fault injection, evidence report. Newer shape; no winner yet to learn from |
| **F. "Contribute to a project"** | 2023 eCAL OpenTelemetry challenge; MC interview says one 2024 solution produced a PR to an Eclipse SDV project | Open repo | A PR; see "ideas" sections in component notes |

Every edition also had a **creative/GenAI side** (OpenAI ideas in 2023 Maestro, SDV Coding Companion 2024, CarMate 2025).

Chapter 4 recognises shapes D and E, and the hackathon continues to centre on uProtocol, Ankaios and openDuT; both challenges also name AutoSD, which first appeared as BlueChi/AutoSD in 2023-24.

## 2. Tech combos that won or reached the finals
| Edition | 1st | 2nd | 3rd | Pattern |
|---|---|---|---|---|
| 2024 | FEV.io: ThreadX board + Ankaios + Kuksa (+ game, LEDs) | APT: Velocitas + Mosquitto + Sumo + Kuksa | Wise Riders: ThreadX + uProtocol/MQTT + Android | **Microcontroller + hub + orchestrator + visible physical output** |
| 2025 | ArBytesMoral: Kuksa + Zenoh/uProtocol + Mosquitto + Ankaios + CARLA + ThreadX + LLM voice | SDVenturers: ThreadX + MQTT/uProtocol + Ankaios + AAOS + ML camera | MegaBosses: Symphony + Ankaios + MQTT + web apps (+ policy) | Same, plus an AI/UX layer; OTA team won on policy + UX rather than low-level update |

Combos that recur among finalists (all sources in the two retrospectives):
1. **Ankaios as the "how it starts" layer**, nearly universal since 2024 (manifest + Dashboard).
2. **A data hub**: Kuksa/VSS in the winning 2025 design and in 2022-2024 challenges; Zenoh topics where VSS was overkill (TheBigRanch, A-kiki).
3. **Small bridges** between worlds: MQTT-Kuksa, CARLA-Kuksa, ROS 2-Zenoh, VSS-uProtocol. Adapters were where the engineering happened; they are also good "gaps" for Chapter 4 teams (see [[vss-kuksa-overview]], [[zenoh-overview]], [[uprotocol-overview]]).
4. **An MCU running Rust or C on ThreadX** (AZ3166) as a tangible sensor/actuator (2024: two finalists; 2025: top two).
5. **A non-Eclipse "wow" layer**: LLM/STT/TTS, deepface, React dashboards, ROS 2.
6. **Orchestrators in OTA**: Symphony + Ankaios in all three 2025 OTA finalists; uProtocol appears in docs more than in code (MegaBosses).

What did *not* win: pure component integration without a user story (pothole map, police pursuit, canary rollout reached finals but not podium, *inferred*); anything needing DCO/Java stacks (no later finalist used it); Chariott/Ibeji/Freyja after 2024.

## 3. What teams typically underestimate
Derived from [[chapter3-retrospective]] section 6 and [[earlier-chapters]]:
- **Environment setup time**: distros (Ubuntu 22.04 vs 24.04), AppArmor, clang-12, WSL, Podman *and* Docker, ARM toolchains, git submodules (ThreadX `--recurse-submodules`).
- **Version pinning**: `up-rust` 0.7.0 vs 0.7.1 silently broke `up-transport-zenoh`; Ankaios devcontainers drifted from 0.2 to 0.5 to 0.6 across editions; ARM manifests needed hand patching in 2022 (`KNOWN_ISSUES.md`).
- **Networking**: shared-simulator IP must be edited into manifests, hack WiFi vs wired, compiled-in SSID/broker IP in MCU firmware, Zenoh router/scouting across subnets, `--net=host` assumptions, firewall.
- **Orchestration semantics**: Ankaios workloads survive stopping the agent; images must exist locally (`localhost/...:latest`) before `ank apply`; agent names must match.
- **Integration cost between transports** (MQTT, Zenoh, uProtocol, VSS): each bridge is a half-day.
- **Hardware sharing**: one GPU laptop per team in 2025; build and test locally against a simulator first (A-kiki did, then integrated late).
- **Scope**: OTA teams planned full lifecycle (P-OTA-VEZ's 42 issues) while the jury wanted one clean campaign-to-redeploy demo.
- **Pitch and repo**: SolutionPlan README, a demo video/GIF in the repo, pitch slides on the provided template; large binaries in repos (SDVenturers ~600 MB, WiseRiders 2.4 GB).

## 4. Questions teams asked most (inferred)
No public question log exists. Best proxies: sdv_lab README warnings, troubleshooting sections in team repos, the open issues list, the KNOWN_ISSUES of 2022, and how the repos name coaches per project (maestro README lists coaches by project and Slack handle).
1. "It does not build/start on my laptop" - OS/toolchain/Podman/Ankaios version.
2. "My workload cannot reach the broker/simulator/router" - IPs, WiFi, ports, host networking.
3. "How do I get my own container into Ankaios / why is it not running?" - manifest syntax, image availability, restart policy, `ank logs`, `ank get workloads`.
4. "Which message/topic/UUri should I use?" - uProtocol URI mapping and which transport; VSS signal paths for Kuksa.
5. "Which Eclipse project do I use for X?" - see [[capability-map]] and the component overviews.
6. "How do I flash/debug the MCU?" - OpenOCD, flash script, USB passthrough, WiFi credentials.
7. "How much do we need to demo / what does the jury want?" - SolutionPlan, pitch template, judging criteria (usability, creativity, coding).

## 5. Advice for the first two hours (cross-edition)
Hour 0-0.5, **orient**
- Read the challenge README and the *known issues / version pins* block first. Keep the exact versions (Ankaios, `up-rust`, Symphony, Podman) and OS support at hand.
- One teammate starts the environment install immediately, in parallel with ideation.
- Open the SolutionPlan template; write the one-line core idea and a sketch by minute 60.

Hour 0.5-1, **prove the starter works**
- Run the provided demo unchanged (`ank apply` + visible output) before writing a line. If it does not run by minute ~45, ask a coach; do not debug alone.
- Verify the network path first: ping, broker port, Zenoh router, simulator port, from the *team* laptop to the shared one.
- For MCU teams: flash the unmodified starter and read serial output first.

Hour 1-2, **choose and slice**
- Pick the story first (who benefits, what is shown on stage), then the minimum chain: sensor -> bridge -> service -> visible actuator/UI.
- Draw the architecture on one page, naming the transport on every arrow; this exposes which bridge to write.
- Timebox spikes (ArBytesMoral's "risk first" phase) for the one unknown technology.
- Agree integration time early (the first end-to-end skeleton by the end of day 1, even with fake data); mock inputs (`ego-vehicle-sensor-mock` existed in Chapter 3).
- Create the repo, `Cargo.lock`/requirements committed, pinned container tags, and a README with one-command start.

Self-check at minute 90: "what runs end to end today, what is mocked, what is our demo moment?".

## 6. Mapping to Chapter 4
- [[chapter4-challenge-doctor-whodunit]]: shape E. Reuse from earlier chapters: Ankaios supervision patterns and manifests from [[earlier-chapters]]/sdv_lab, uProtocol topics, Kuksa/VSS signals as the sensor interface; new components: [[opensovd-overview]], [[autosd-overview]], [[opendut-overview]]. Expect environment and image-build time to dominate the first two hours (AutoSD images, Ankaios agents), as in Chapter 3.
- [[chapter4-challenge-hack-to-the-future]]: shapes C+D. Reuse: Wise Riders / ArBytesMoral / SDVenturers ThreadX-Rust + uProtocol work, uProtocol-over-Zenoh and over-MQTT5 examples in sdv_lab; new: [[openbsw-overview]], [[opendut-overview]], AutoSD HPC image. The portability claim ("no service code change") is the Chapter 3 lesson reversed: Chapter 3 teams had to patch crates and transports per target.
- Component notes: [[ankaios-overview]], [[uprotocol-overview]], [[zenoh-overview]], [[vss-kuksa-overview]], [[threadx-overview]], [[symphony-overview]], [[muto-overview]]; event context [[chapter4-overview]], the official coach list (https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/).
