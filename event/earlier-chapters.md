---
title: Earlier hackathons - BCX 2022, Accenture 2023, Chapter 2 (2024)
type: event
component: none
tags: [event, retrospective, history, maestro, dco, hack-the-truck, ecal, velocitas, kuksa, ankaios, symphony]
status: draft
sources:
  - https://newsroom.eclipse.org/node/39793
  - https://blogs.eclipse.org/node/7908
  - https://blogs.eclipse.org/node/7997
  - https://sdv.eclipse.org/sdv-hackathon-2023/
  - https://api.github.com/orgs/Eclipse-SDV-Hackathon-Chapter-Three/repos
  - https://blogs.eclipse.org/post/diana-kupfer/eclipse-sdv-hackathon-2025-%E2%80%9C-indispensable-experience-any-aspiring-software
  - repos/acc-maestro-challenge
  - repos/acc-dco-hack-challenge
  - repos/bcx-hack-the-truck
  - repos/bcx-hackchallenge-driving-score
  - repos/bcx-hackchallenge-simulation
  - repos/bcx-hackchallenge-control-vehicle-lights
  - repos/hc2-challenge-maestro
  - repos/hc2-challenge-shift-to-sdv
  - repos/hc2-challenge-sunken-kitchen
  - repos/hc2-challenge-play-by-wire
  - repos/hc2-challenge-threadx-and-beyond
last-verified: 2026-10-03
related:
  - "[[chapter3-retrospective]]"
  - "[[hackathon-patterns]]"
  - "[[chapter4-overview]]"
  - "[[ankaios-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[symphony-overview]]"
  - "[[muto-overview]]"
  - "[[threadx-overview]]"
  - "[[sdv-blueprints-overview]]"
---

# Earlier hackathons (2022 - 2024)

Companion to [[chapter3-retrospective]]; synthesis in [[hackathon-patterns]].

## 0. Timeline and naming (read this first)
The naming is not consistent across sources, so treat the mapping as partly *inferred*.

| Edition | When / where | Org on GitHub | Notes |
|---|---|---|---|
| "Eclipse SDV Hackathon on BCX2022" | Nov 2022, Bosch Connected Experience (BCX), Berlin (*location inferred from BCX*) | https://github.com/Eclipse-SDV-Hackathon-BCX | Pre-"chapter" edition, hardware heavy |
| Accenture edition (often called Chapter One) | 28 Nov 2023, Accenture Munich, 2.5 days, 75 participants, 20+ teams of 3-5, 8 challenges, tracks "SDV Tooling" and "SDV Blueprints" (newsroom: [snapshot](../https://newsroom.eclipse.org/node/39793)) | https://github.com/Eclipse-SDV-Hackathon-Accenture | An Eclipse blog summary calls it "Chapter One" (search result, unverified); the Chapter 3 MC interview calls Karlsruhe "Chapter Two", which implies it |
| Chapter 2 | 20-22 Nov 2024, ICF Karlsruhe, hosted by Harman, 60+ participants, 13 teams, 5-6 challenges ([announcement](../https://blogs.eclipse.org/node/7908), [finalists](../https://blogs.eclipse.org/node/7997)) | https://github.com/Eclipse-SDV-Hackathon-Chapter-Two | |
| Chapter 3 | 30 Sep - 2 Oct 2025, Berlin + Porto | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three | [[chapter3-retrospective]] |

The page https://sdv.eclipse.org/sdv-hackathon-2023/ redirects to eclipsesdv.org and returned HTTP 404 on 2026-10-03 ([note](../https://sdv.eclipse.org/sdv-hackathon-2023/)); 2023 facts come from the newsroom post and the org repos. 2022 and 2023 winners: not found in sources I could fetch (a search snippet says team "Millennium" took 3rd in 2023; unverified; their repo https://github.com/Eclipse-SDV-Hackathon-Accenture/Millennium_FleetManagement exists).

## 1. BCX 2022 (Bosch Connected Experience)
Org inventory: [snapshot](../https://api.github.com/orgs/Eclipse-SDV-Hackathon-Chapter-Three/repos). Index/timetable repo: https://github.com/Eclipse-SDV-Hackathon-BCX/.github (glossary of CVI, VSS, Carla, OSM/OSRM, SOAFEE/EWAOL, JetRacer setup).

| Challenge repo | Idea | Stack | Starter value today |
|---|---|---|---|
| hackchallenge-driving-score https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-driving-score | Read speed/acceleration/braking, compute a driving score, send it on | Velocitas vehicle app (Python/Go/Rust/C++), Kuksa databroker, Chariott, Kubernetes on Leda/ARM device, optional Xen + ROS | Five-step guide (signals -> architecture -> components -> app -> build/deploy) is still a good template. `KNOWN_ISSUES.md` shows ARM device manifests that had to be hand-patched (tcp:// prefix in `DATABROKER_ADDRESS`, Muto image for arm64, quote bug in `command`) |
| hackchallenge-simulation https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-simulation | Vehicle app fed with telemetry from CARLA or AirSim | CARLA/AirSim, Kuksa, Chariott, Velocitas template; GPU VM on Azure (NVv4) with Azure Pass per team | Same "sim -> Kuksa -> app" pattern reappears in Chapter 3 |
| hackchallenge-lets-play-osm-and-carla | OpenStreetMap real-world data into CARLA | CARLA, OSM/OSRM | CARLA first-contact doc referenced by the simulation challenge |
| hackchallenge-hack-the-truck https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-hack-the-truck | Hack a real truck: camera, lightbar, steering wheel; ideas: passenger detection to LED bar, wheel as gamepad | **Eclipse eCAL** pub/sub over a plain Ethernet switch, C/C++/Python samples, example eCAL recording to replay | Hardware not reusable; eCAL monitor/recorder pattern is |
| hackchallenge-control-vehicle-lights https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-control-vehicle-lights | Control a retrofitted VW T2 light via SOME/IP | Eclipse SommR + KUKSA.val databroker | Meant to *complement* other challenges, using Kuksa as mediator |
| hackchallenge-passenger-welcome | App that welcomes a passenger approaching the car (seat/lights) | Velocitas, Kuksa, digital.auto prototyping | Prototyping tutorial reused in Chapter 2 Play by Wire |

Lesson visible here: from the start, one data hub (Kuksa/VSS) was the integration point between challenges.

## 2. Accenture 2023 (Munich)
Repo inventory (all under https://github.com/Eclipse-SDV-Hackathon-Accenture/): SeatAdjuster, maestro-challenge, muto-multi-agent-racer, fleet-management, trace-debugging-for-eclipse-ecal, closed-loop-driving-with-carla-and-ecal, hack-the-car, dco-hack-challenge, plus teams (valiants_*, FEVio_ClosedLoopDrivingChallenge, Millennium_FleetManagement, mia-fleet-management, FleetFlow, minos_hack_the_car, HackTheCar_*, IntelliSafe, wheelchair-assistant, amadeus).

### 2.1 maestro-challenge
https://github.com/Eclipse-SDV-Hackathon-Accenture/maestro-challenge (clone `repos/acc-maestro-challenge`, commit 0273a4a, 2023-11-29)
- Shape: **"we supply a stack and orchestrators, you build a scenario"**. Provided sample: Smart Trailer (trailer connects -> orchestrator starts a Digital Twin provider and a Smart Trailer app; `TrailerWeight` signal synced to a mocked cloud via Freyja). Stack: Eclipse Chariott, Ibeji, Agemo, Freyja, Mosquitto; run under **Ankaios** or **BlueChi** devcontainers; optional Azure Digital Twins and Azure Container Registry with a redeemed subscription.
- Suggested extensions: weight-aware body control, web UI for synced signals, OpenAI assistant, "intelligent orchestrator" (placement by CPU/mem/latency), workload-health dashboard.
- Dev loop recommended in the README: write workload -> build container image -> push to registry -> plug into orchestrator-specific startup config (Ankaios devcontainer uses `startupState.yaml`, scripts `run_maestro.sh`/`shutdown_maestro.sh`, REST resource-usage API, a video walk-through https://youtu.be/XQVlIctChkI).
- Staleness: Ankaios devcontainer pinned to 0.2.0-rc1 (`eclipse-ankaios/.devcontainer/Dockerfile`), docs links to Ankaios 0.2; Chariott/Ibeji/Freyja are the "Microsoft in-vehicle stack" and not part of the Chapter 3 or 4 stacks. Use as a pattern, not as a runnable kit.

### 2.2 dco-hack-challenge (Developer Console + SUMO)
https://github.com/Eclipse-SDV-Hackathon-Accenture/dco-hack-challenge (clone `repos/acc-dco-hack-challenge`, commit 284f1ff)
- Battery-simulation challenge: Eclipse SDV Developer Console (DCO) release management plus Eclipse SUMO traffic simulation; EV battery dynamics, fleet management. Java Spring Boot + Maven, NextJS React UI, Postgres, MinIO, docker-compose with scripts `10-build-script.sh`, `20-deploy-script.sh`, `30-destroy-script.sh`. Skills: Git, Maven, Spring Boot, Next.js. Coaches: Sebastian Lang, Michail Chatzipanagiotou.
- "Hack Ideas" list is very broad (OTA via release management, remote diagnostics, ML maintenance prediction, Eclipse MOSAIC). *inferred*: broad and Java-centric, so few teams used it; no finalist in later chapters used DCO.

### 2.3 Other 2023 challenges
| Repo | Shape |
|---|---|
| SeatAdjuster | Velocitas vehicle app on Leda using Kuksa/VSS; explicit "for newcomers, no prior knowledge" (creative challenge + technical challenge) https://github.com/Eclipse-SDV-Hackathon-Accenture/SeatAdjuster |
| fleet-management | Extend the SDV Blueprint (Leda, Kanto, Kuksa, Hono, InfluxDB, Grafana, Docker Compose), ideas: range prediction, campaign management https://github.com/Eclipse-SDV-Hackathon-Accenture/fleet-management; see [[sdv-blueprints-overview]] |
| muto-multi-agent-racer | F1TENTH multi-agent racing simulator; Muto, Zenoh; remote tune via mobile app https://github.com/Eclipse-SDV-Hackathon-Accenture/muto-multi-agent-racer |
| trace-debugging-for-eclipse-ecal | "Contribution challenge": add OpenTelemetry to eCAL |
| closed-loop-driving-with-carla-and-ecal | Sensor data from CARLA to control the car via eCAL |
| hack-the-car | Hack a real research vehicle (README not retrievable on `main`/`master` raw; unverified) |

## 3. Chapter 2 (Karlsruhe, Nov 2024)
Org: https://github.com/Eclipse-SDV-Hackathon-Chapter-Two. Challenge repos cloned to `repos/hc2-*`.

| Challenge | Repo | Shape | Reusable? |
|---|---|---|---|
| Play by Wire | https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challenge-play-by-wire (46a7787) | Games on HPC fed by joystick/keyboard/Forza UDP via Kuksa; digital.auto prototyping; 2 zones + HPC; bonus for CAN + Open1722; six suggested steps | Idea list and links (kuksa-val-pong, forza-udp-databroker-proxy) |
| Forget the Conventional - Shift to SDV | https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challenge-shift-to-sdv (a3a3308) | Devcontainer with Ankaios 0.5-era, Podman 4.9.3, two agents `hpc1`/`hpc2`, eCAL topics (`gps_data`, `vehicle_dynamics`, `object_detection`, `traffic_sign_detection`, radar), a web IVI, and a **Symphony Provider app** receiving an Ankaios manifest from Symphony on Azure; helper scripts `restart-shift2sdv`, `ank-logs`; ask coaches for eCAL recordings | **Direct ancestor of Chapter 3's Update Possible HPC variant**; pattern still valid, versions old |
| Sunken Kitchen | https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challenge-sunken-kitchen (0be22f6) | Open-ended: AutoSD (CentOS Stream 9) devcontainer, systemd+Podman+BlueChi, uProtocol, Kuksa Databroker, optional OpenShift; rules: at least one Eclipse project (bonus for 2+), architecture diagram, no closed source | Template for freestyle tracks, see [[chapter4-freestyle-track]] and [[autosd-overview]] |
| Maestro | https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challenge-maestro (6bf5301) | 2023 maestro updated: now **Symphony** global orchestrator (needs Kubernetes: AKS/k3s, Helm) plus in-vehicle stack (Ankaios/BlueChi); truck fleet scenario | Same caveat as 2023 |
| To ThreadX and Beyond | https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challenge-threadx-and-beyond (7c521c9, 2025-01-20) | MXChip AZ3166 starter (adapted from Microsoft getting-started, Azure IoT removed), ThreadX/NetX Duo as submodules (`--recurse-submodules`), Windows 11/WSL/Ubuntu/Mac M1 notes, flash script, then MQTT/REST + integration | **Still the basis of Chapter 3's ThreadX material** (the MissionUpdate README links its `flash.sh`); see [[threadx-overview]] |
| SDV Coding Companion | https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challenge-sdv-coding-companion (ea27491) | GenAI copilots on AWS Bedrock deployed to digital.auto playground (Autowrx); coaches issue IAM users with credits | Only if credits exist; shows LLM challenges are welcome |

Finalists and results ([snapshot](../https://blogs.eclipse.org/node/7997)): 1st FEV.io, 2nd APT, 3rd Wise Riders; Harman award Wise Riders and Caliper Kings; also ASAP, Challengers, Python Hobbits.
- **FEV.io** (Play by Wire) https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/FEVio: car game, MXChip AZ3166 as controller (OpenOCD flash, MQTT), Ankaios, Kuksa, ambient light in the winner's colour; submodules required.
- **APT** (Sunken Kitchen) https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/APT: Velocitas V2V crash and weather alerts over Mosquitto, Sumo, Kuksa.
- **Wise Riders** (ThreadX) https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/WiseRiders: uProtocol uMessage serialisation inside an RTOS; Android app in Rust sends Honk&Flash via MQTT, crash detection from accelerometer back; patched `up-transport-mqtt5`; WiFi creds hard-coded in `cloud_config.h`. Repo is about 2.4 GB, so it was not cloned; read via the web. This is the direct ancestor of the Chapter 3 `up-transport-mqtt5-rust` + ThreadX work (SDVenturers use that crate).

## 4. Which projects recurred
| Project | 2022 | 2023 | 2024 (Ch.2) | 2025 (Ch.3) | Chapter 4 |
|---|---|---|---|---|---|
| Kuksa / VSS | yes (driving score, lights) | yes (SeatAdjuster, fleet) | yes (Play by Wire, Sunken Kitchen) | yes (winner hub) | [[vss-kuksa-overview]] (Doctor Whodunit) |
| Velocitas | yes | yes | yes (APT) | named in the organiser blog only; not seen in the finalist repos I read | |
| Ankaios | - | yes (maestro) | yes (nearly all) | yes (all 7 finalists except those without code to verify) | [[ankaios-overview]] (both challenges) |
| eCAL | yes (truck) | yes (tracing, CARLA) | yes (shift-to-sdv) | no | no |
| Symphony | - | - | yes (maestro, shift) | yes (OTA) | |
| Muto | arm64 demo | racer | - | ROS variant | [[muto-overview]] |
| ThreadX | - | - | yes (challenge + 2 finalists) | yes (top 2) | |
| uProtocol / Zenoh | - | Zenoh in racer | uProtocol (Sunken Kitchen, Wise Riders) | yes (core) | [[uprotocol-overview]], [[zenoh-overview]] |
| CARLA | yes | yes | - | yes | |
| BlueChi / AutoSD | - | yes (maestro) | yes (Sunken Kitchen) | - | [[autosd-overview]] |
| Chariott/Ibeji/Freyja | yes | yes | yes (maestro) | no | dropped |
| SUMO / DCO | - | yes | APT used Sumo | - | |

## 5. Reusable assets today
Usable as patterns, with version drift noted:
- Chapter 3 `sdv_lab` (Ankaios manifests, Zenoh/uProtocol Rust and Python examples, CARLA `just` recipes, AAOS cluster app) - most current. See [[chapter3-retrospective]].
- Chapter 3 `challenge-mission-update-possible` HPC/ROS variants and Symphony docker-compose (Symphony 0.48-proxy.41, Ankaios 0.6.0).
- Chapter 2 `challenge-shift-to-sdv` devcontainer and scripts (`ank-logs`, restart script pattern), `challenge-threadx-and-beyond` for the AZ3166 toolchain, `kuksa-val-pong` / `forza-udp-databroker-proxy` for game-style demos.
- 2023 maestro Smart Trailer scenario only as a design example (old Ankaios, Microsoft in-vehicle stack).
- 2022 BCX driving-score five-step guide as a generic "how to structure a first day".
- digital.auto / Autowrx playground for rapid VSS prototyping.

## 6. Unverified or missing
2022/2023 winners; exact 2022 location; `hack-the-car` README; per-team post-mortems; issue and discussion threads for the challenge repos (the only open issues seen were on sdv_lab in Chapter 3; maestro-challenge shows 3 open, dco-hack-challenge 1 at the GitHub API listing).
