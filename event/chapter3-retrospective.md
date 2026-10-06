---
title: Chapter 3 retrospective (30 Sep - 2 Oct 2025, Porto + Berlin)
type: event
component: none
tags: [event, retrospective, chapter3, sdv-lab, carla, ankaios, zenoh, uprotocol, ota, symphony]
status: draft
sources:
  - https://eclipsesdv.org/blogs/meet-the-2025-sdv-hackathon-finalists-and-winners-and-explore-their-code/
  - https://blogs.eclipse.org/post/christian-heissenberger/unveiling-2025-sdv-hackathon-challenges-ideas-impact-%E2%80%93-faster
  - https://blogs.eclipse.org/post/dana-vede/sdv-hackathon-chapter-three-tale-two-cities
  - https://blogs.eclipse.org/post/diana-kupfer/eclipse-sdv-hackathon-2025-%E2%80%9C-indispensable-experience-any-aspiring-software
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/sdv_lab
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/SolutionPlan_Template
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/challenge-mission-update-possible
  - https://api.github.com/orgs/Eclipse-SDV-Hackathon-Chapter-Three/repos
  - repos/sdv_lab
  - repos/hc3-ArBytesMoral
  - repos/hc3-MegaBosses
  - repos/hc3-SDVenturers
  - repos/hc3-TheBigRanch
  - repos/hc3-A-kiki
  - repos/hc3-COOTA
last-verified: 2026-10-03
related:
  - "[[chapter4-overview]]"
  - "[[hackathon-patterns]]"
  - "[[earlier-chapters]]"
  - "[[ankaios-overview]]"
  - "[[zenoh-overview]]"
  - "[[uprotocol-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[symphony-overview]]"
  - "[[muto-overview]]"
  - "[[threadx-overview]]"
---

# Chapter 3 retrospective (Porto + Berlin, 30 Sep - 2 Oct 2025)

Written for participants preparing for [[chapter4-overview]]. Companion notes: [[earlier-chapters]], [[hackathon-patterns]].
Repos were shallow-cloned on 2026-10-03 into `repos/` (commit hashes in the table at the end). Claims marked *inferred* are my reading of the repos, not stated by the organisers.

## 1. The event in numbers
- 30 Sep - 2 Oct 2025, run simultaneously at Bosch Innovation Campus (Berlin) and 42 Porto; 102 participants, 22 teams, about 30 hours of coding; 7 finalists (3 Porto, 4 Berlin). [chapter3-finalists-winners](../https://eclipsesdv.org/blogs/meet-the-2025-sdv-hackathon-finalists-and-winners-and-explore-their-code/), [chapter3-event-blog](../https://blogs.eclipse.org/post/dana-vede/sdv-hackathon-chapter-three-tale-two-cities)
- Hack MC Andre Bott (Bosch Digital), assistant Christian Heissenberger (Eclipse Foundation); coaches from ETAS, Red Hat, Elektrobit, T-Systems, Bosch. Live stream and "side challenges" connected the two sites; the organisers named two-site coach support and fair cross-site judging as their main worries. [chapter3-mc-interview](../https://blogs.eclipse.org/post/diana-kupfer/eclipse-sdv-hackathon-2025-%E2%80%9C-indispensable-experience-any-aspiring-software)
- Judging: usability, creativity, coding. Every team had to fill in a `SolutionPlan` (below) and pitch with a provided slide template (`SDV Hackathon 2025 - Pitching Slides Template.pptx` is committed in MegaBosses and TheBigRanch).

## 2. The two challenges
Official text: [chapter3-challenge-overview](../https://blogs.eclipse.org/post/christian-heissenberger/unveiling-2025-sdv-hackathon-challenges-ideas-impact-%E2%80%93-faster). Both had an accessible and an advanced path.

| Challenge | Goal | Eclipse projects named | Skills | Starter repo |
|---|---|---|---|---|
| **Virtual SDV Lab** | Build/demonstrate an ADAS or automated-driving feature in a virtual vehicle environment | Zenoh, uProtocol, Kuksa (VSS), ThreadX, Ankaios, CARLA (not Eclipse), Android Auto/AAOS | Python, C, Rust, CARLA | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/sdv_lab |
| **Mission: Update Possible** | End-to-end OTA from a cloud orchestrator to simulated vehicles/ECUs, UN R155/R156 flavour | Symphony, uProtocol, ThreadX, openBSW, Ankaios, Muto | containers/OCI, reading docs | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/challenge-mission-update-possible |

Distribution of the 7 finalists: 4 Virtual SDV Lab (SDVenturers, TheBigRanch, A-kiki, ArbytesMoral), 3 Update Possible (MegaBosses, LastOneStanding, COOTA). Both winners ranked 1st/2nd were Virtual SDV Lab, 3rd was OTA.

### 2.1 Mission: Update Possible in detail
Source: `repos/hc3-challenge-mission-update-possible/` (commit 8f3dfff, 2025-10-27), [snapshot](../https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/challenge-mission-update-possible).
- Two variants. **HPC variant**: Symphony (cloud meta-orchestrator, run locally via Docker Compose with an MQTT broker and a read-only portal) pushes over MQTT to a "Symphony Target Provider" workload that Ankaios runs in the vehicle. A web `update_trigger` workload uses the Ankaios Python SDK to start the `symphony` workload on a button press. Participants were to write a Rust provider. `repos/hc3-challenge-mission-update-possible/hpc_variant/README.md`
- **ROS variant**: Symphony + Muto (in-robot orchestrator for ROS workspaces/nodes); stretch goal: adapt the uProtocol TargetProvider so Muto uses uProtocol instead of MQTT. `repos/.../ros_variant/README.md`
- Pinned versions: Symphony 0.48-proxy.41, Ankaios v0.6.0, Podman, Docker with Compose. Ubuntu 24.04: AppArmor must be disabled for Ankaios.
- Levels: (1) OTA demo app/UX, (2) policy workflow and user containers (e.g. update only when parked), (3) real ECU firmware update (ThreadX, Raspberry Pi, flash script, privileged container with USB mount). Extra cases: multi-site rollout (Berlin/Porto), partial update and rollback, device provisioning.

## 3. The sdv_lab environment (Virtual SDV Lab)
Repo: https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/sdv_lab, shallow clone at `repos/sdv_lab`, commit `849444a8b149` (2025-10-01), Apache-style open repo with 9 stars and 24 issues at snapshot time. [README snapshot](../https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/sdv_lab)

### 3.1 Architecture
Idea: every example is **Component A** (heavy, runs on a shared GPU laptop: CARLA or an Android Automotive emulator) + **Component B** (your Rust/Python app in a container on your own laptop) + a **communication bus** (uProtocol, MQTT5 or Zenoh) between them. Everything non-GUI is a container managed by **Ankaios**. `repos/sdv_lab/README.md`, `repos/sdv_lab/assets/*.png`

```
 Shared laptop (one per team, GPU)            Team laptop(s)
 ------------------------------------         ----------------------------
 CARLA 0.9.15 server (just recipes)           Ankaios agent (podman)
 Android Studio + AAOS cluster emulator       your workloads (Rust / Python)
 Mosquitto MQTT broker  (Ankaios wkld)  <---> PID controller, ego-vehicle,
 uStreamer (uProtocol router)                  cruise-control app, ThreadX board
 Ankaios server + agent                        (Hack WiFi, IP of shared laptop
   (startup manifest shared-notebooks-         must be patched into manifests)
   manifest.yaml)
```

| Layer | What it is | Where in the repo |
|---|---|---|
| Simulator | CARLA 0.9.15 (UE4). `just` recipes: `install-server`, `server-nvidia`, `server-offscreen`, `install-client`, `run-automatic`, `run-manual`, `build-libcarla`, `make-carla`; assumes Ubuntu 22.04 (`just fix-wsl` for WSL) | `carla-setup/` |
| CARLA bridge | Rust ego-vehicle controllers translating CARLA to messages: `zenoh-control` (raw Zenoh), `uprotocol-control` (uProtocol over Zenoh), `uprotocol-sensors` (sensor streams, needs clang-12 on 24.04, script `troubleshooting/setup-ubuntu-24.04-with-clang-12.sh`), a `container/` build env | `ego-vehicle/` |
| Control example | PID cruise controller, Python+Zenoh and Rust+uProtocol versions | `pid_controller/` |
| Cluster UI | AAOS digital cluster app (Kotlin/Android Studio), emulator with `adb shell wm density 200`; variants for MQTT+Python, uProtocol+Rust, ThreadX | `aaos_digital_cluster/`, `android_python/`, `android_uprotocol/`, `android_treadx/android/` |
| Embedded | Rust ThreadX apps for the MXChip AZ3166 board with MQTT and uProtocol examples | `android_treadx/threadx/` |
| uProtocol/MQTT apps | cruise-control app (`uprotocol/cruise-control-app`), `uprotocol/mqtt`, `uprotocol/zenoh`, `uprotocol/ustreamer/config` | `uprotocol/` |
| Orchestration | Ankaios v0.6.0, server+agents via systemd (`ank-server`, `ank-agent`); manifests applied with `ank apply x.yaml`, removed with `ank apply -d`; example workloads that start other workloads via the Control Interface (Python and Rust SDK) | `ankaios/example_workloads/`, `shared-notebooks-manifest.yaml`, `shared_notebooks.md` |

Eclipse projects actually exercised: Ankaios, Zenoh, uProtocol (`up-rust` and `up-transport-zenoh`, `up-transport-mqtt5-rust`), Mosquitto, ThreadX (Rust), Kuksa (not in sdv_lab itself; teams brought it). Non-Eclipse: CARLA, Android Studio/AAOS, Podman, Cargo.

### 3.2 How teams plugged in
1. Install Podman and Ankaios v0.6.0 on your laptop (script install; on Ubuntu 24.04 disable AppArmor), `sudo systemctl start ank-server ank-agent`.
2. Connect to the Hack WiFi, find the shared laptop's IP, edit the example's manifest (`MQTT_BROKER_URI=mqtt://<ip>:1883`, Zenoh/CARLA host) and `ank apply` it.
3. Develop component B (Rust or Python) in a container; use the uProtocol/Zenoh/MQTT examples as templates; open the Android project on the shared laptop in Android Studio to see the cluster.
4. Fork the repo into your team repo (SDVenturers kept a modified `sdv_lab` fork inside theirs).

### 3.3 Known problems documented in the repo itself
- **up-rust 0.7.0 vs 0.7.1 trap**: Cargo silently upgrades `up-rust` to 0.7.1, which tightened `UUri` authority rules and broke `up-transport-zenoh`. Fix: pin `up-rust = "=0.7.0"` and `cargo update -p up-rust --precise 0.7.0`, then check with `cargo tree -p up-transport-zenoh`, commit `Cargo.lock`. This is the first block of the README (a sign it bit people). `repos/sdv_lab/README.md`
- Ubuntu 24.04 needs AppArmor disabled for Ankaios and clang-12 for `uprotocol-sensors`; 22.04 may still fail compile (see `ego-vehicle/uprotocol-sensors/README.md`).
- Ankaios: stopping server/agent does **not** stop workloads (by design); you must `ank delete workloads ...`. `shared_notebooks.md`
- CARLA: ego-vehicle controllers wait for an actor with a matching, case-sensitive `role_name` ("Waiting for the Ego Vehicle actor..."). `repos/sdv_lab/ego-vehicle/uprotocol-sensors/README.md`
- Issue tracker (24 issues, https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/sdv_lab/issues, read via WebFetch): mostly unfinished "package X as a container" prep tasks (CARLA server as Docker image, ego-vehicle, cruise control, uStreamer image, integration test CARLA<->ego<->cruise control, `ustreamer` forwarding between up to 4 components, `up-transport-mqtt5-rust` on ThreadX/Zephyr). Taken together: the lab was assembled in the weeks before the event and the integration test (#17) was still open. *inferred*

## 4. SolutionPlan_Template
Repo: https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/SolutionPlan_Template (commit `cb41719`, 2025-09-24, [snapshot](../https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/SolutionPlan_Template)). A 44-line README each team copied into its repo.
- Section 1 **Your Team at a Glance**: team name/tagline ("create a sheet of paper with your team name on the desk"), members table (name, GitHub handle, role), challenge, core idea with a sketch/mermaid chart.
- Section 2 **How Do You Work**: development process, planning and tracking, quality assurance, communication, decision making.
- It deliberately asks about *process*, not tech; the jury criteria (usability, creativity, coding) were still judged from the pitch. Real usage varied: ArBytesMoral wrote a five-phase process with spike-first risk identification and a PR template; A-kiki split into three sub-teams (chase, encirclement, infrastructure/integration) and integrated late; COOTA wrote deploy-and-rollback first, monitoring second, scale third; TheBigRanch's README still starts "# SolutionPlan_Template". How to use it: have the plan ready at hour 2 and update it before dinner on day 1 (the plan doubles as an architecture sketch).

## 5. Finalists and winners
Source: [chapter3-finalists-winners](../https://eclipsesdv.org/blogs/meet-the-2025-sdv-hackathon-finalists-and-winners-and-explore-their-code/). Rankings: 1st ArbytesMoral, 2nd SDVenturers, 3rd MegaBosses.

| Rank | Team (city) | Challenge | Repo | What they built | Components combined |
|---|---|---|---|---|---|
| 1st | ArbytesMoral (Berlin) | Virtual SDV Lab | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/ArBytesMoral | **CarMate**: voice-driven AI companion with its own mood; STT/TTS web app, a supervisor LLM agent with tools (OpenAI-style API, weather, vehicle data); vehicle data in VSS; MCU temperature in, RGB LED command out; CARLA-derived weather (wetness) into VSS; cluster display | Kuksa Databroker 0.6.0 (VSS hub), Mosquitto, Zenoh router, uProtocol over Zenoh, Ankaios (+Dashboard on :5001), CARLA, Rust ThreadX on MXChip AZ3166 over MQTT; custom workloads `mqtt-kuksa-provider`, `vehicle-data-accessor`, `carla-provider`, `car-mate-io`, `car-mate-agents` (`compute/ankaios.yaml`) |
| 2nd | SDVenturers (Berlin) | Virtual SDV Lab | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/SDVenturers | Mood detection and action: camera mood (Python `deepface`) + mocked radar heart-rate from a Rust ThreadX app on AZ3166 -> Rust ADAS drive-mode logic limits behaviour; Python and Android AAOS dashboards | MQTT (`rumqttc`) plus `up-transport-mqtt5-rust` (uProtocol over MQTT5), ThreadX, Ankaios manifest for the Rust app, AAOS cluster; forked `sdv_lab` |
| 3rd | MegaBosses (Porto) | Update Possible | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/MegaBosses | **FleetSync OTA**: policy-driven OTA: operator web app (React/TS/Vite) triggers Symphony campaigns, policy workflow (battery/state/schedule) gates, driver accept/reject HMI pop-up, instrument-cluster workload redeployed to a new version; its "rollback" was a forward redeploy by tag (`nginx` image) with no digest, trial, commit or signing ([[release-is-the-hash-of-its-parts]], [[security-version-is-not-build-order]]) | Symphony (Docker Compose, MQTT, campaigns/activations registered by script), Ankaios `state.yaml`, custom containers (`PolicyWorkflow`, `SimHeadUnit`, `InstrumentCluster_v1/v2`, `ManagementPlatform`); uProtocol and Muto appear only in docs (`Docs/ProjectSummary.md` says "uProtocol-ready"), not in code I could grep: *inferred* that the real stack was Symphony + Ankaios + MQTT |
| finalist | A-kiki (Berlin) | Virtual SDV Lab | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/A-kiki | Autonomous police lock-on and encirclement: semantic LiDAR lock-on, chase controller (pure pursuit + headway PI), A* interception, WebSocket police dashboard | CARLA 0.9.15, ROS 2 Humble (C++ camera processor, bridges), Zenoh (`ros2_camera_zenoh_bridge.py`, `kuksa_zenoh_bridge.py`), VSS schema (`vss_police_schema.json`), Ankaios for infra |
| finalist | TheBigRanch (Porto) | Virtual SDV Lab | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/TheBigRanch | Pothole map builder: IMU/pose from CARLA, detector scores vertical acceleration, SQLite tile store, web HMI heatmap and alert | CARLA bridge -> Zenoh topics (`vehicle/pose`, `vehicle/imu/raw`, `detect/pothole/event`, `map/pothole/tiles`, `hmi/alert`), Ankaios start order Bridge->Detector->Tile Store->HMI |
| finalist | LastOneStanding (Berlin) | Update Possible | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/LastManStanding | ECU OTA via self-hosted cloud data broker on Kubernetes (per organiser blog); repo contains only the pitch deck, so no code to verify | Ankaios, Symphony, uProtocol (per blog only) |
| finalist | COOTA (Porto) | Update Possible | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/COOTA | Canary orchestrator: roll out to e.g. 0.5% of devices, watch telemetry, expand or roll back automatically; backend + frontend + campaign + multi-vehicle and single-vehicle samples | Symphony, Ankaios (it kept `hpc_variant/` from the starter) |

### What the winning teams have in common
- **A story, not a component demo.** CarMate (loneliness/hands-free), mood-aware ADAS and policy-gated fleet OTA are products with a user; both Virtual-Lab finalists with pure data pipelines (potholes, police) still placed behind them. Judging weights usability and creativity. *inferred from ranking vs. criteria*
- **A hub-and-bridge architecture.** ArBytesMoral put Kuksa/VSS in the middle and wrote small providers (CARLA -> VSS, MQTT -> VSS, VSS -> uProtocol/Zenoh) rather than wiring everything point to point; A-kiki also bridged ROS 2 and Kuksa onto Zenoh. Small adapters between projects were the winning engineering pattern.
- **Hardware in the loop.** The top two both had the MXChip AZ3166 board (Rust on ThreadX) as a real sensor/actuator plus a visible LED/OLED reaction on stage; the MCU README even hard-codes WiFi `SDV_Chapter3-Team2` and a broker IP (`repos/hc3-ArBytesMoral/mcu_sw/README.md`), a reminder that network settings were compiled into firmware. `threadx-rust` was a provided repo: https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust.
- **Everything runs under Ankaios, with a dashboard** and a one-command start (`ank -k apply ankaios.yaml`, `prepareLocalWorkloads.sh`, MegaBosses `setup.sh`). The jury could see it start.
- **Demo assets in the repo** (video `SdvLab_Demo_ArBytesMoral.mp4`, `Demo.gif`, pitch PDFs).
- Outside-the-box tech was allowed: LLM, STT/TTS, deepface, ROS 2, React. The Eclipse projects were the glue, not the whole product.

## 6. Recurring problems visible in repos and READMEs
Evidence is indirect (no chat logs). Each item gives the artefact it is read from.

| Problem | Evidence |
|---|---|
| **Version drift in uProtocol crates** | sdv_lab README's opening warning; `up-rust =0.7.0` pin; `uUpdate`, `up-transport-zenoh-python` repos created in the org for gaps (https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/up-transport-zenoh-python) |
| **Environment setup eats hour 1-4** | sdv_lab README has separate paths for Ubuntu 22.04/24.04, WSL fixes, clang-12 script, AppArmor; MegaBosses ships `setup.sh`; A-kiki ships `install_dependencies.sh`; TheBigRanch copied `carla-setup` |
| **Networking: shared-laptop IPs, WiFi, brokers** | manifests must be edited with the shared laptop IP; firmware has SSID/IP baked in; A-kiki troubleshooting lists `netstat`, `ufw status`, Zenoh router restart (`repos/hc3-A-kiki/backbone/README.md`); ArBytesMoral warns the Ankaios agent name must equal `agent_compute` or the server cannot find it, and uses `ank -k` (insecure) |
| **Container images must be built locally before `ank apply`** | `prepareLocalWorkloads.sh` (ArBytesMoral), `scripts/build-pull-images.sh` (MegaBosses); images referenced as `localhost/...:latest` |
| **Podman + Docker both needed** (Ankaios needs Podman; Symphony Compose uses Docker) | challenge-mission-update-possible HPC README prerequisites |
| **Embedded toolchain pain** | ThreadX: submodules (`--recurse-submodules`), ARM GNU toolchain, OpenOCD flashing, USB mount into privileged container (starter README); see also [[threadx-overview]] |
| **Starter content incomplete at kick-off** | sdv_lab issue list (container images, integration test open); P-OTA-VEZ has 42 open issues that are a requirements checklist (static tests, atomic install, rollback, audit trail) which suggests a team that planned the whole OTA lifecycle and ran out of time (https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/P-OTA-VEZ, *inferred*) |
| **Scope: hardware needs sharing** | one shared GPU laptop per team; CARLA/AAOS only there; teams like A-kiki developed each node locally against CARLA 0.9.15 and integrated late (README "Planning & Tracking") |
| **Repo hygiene** | `~$Final Pitch.pptx` lock files and a 600 MB SDVenturers repo, big binaries committed; pitch decks were the main artefact in LastOneStanding; useful for the "commit your demo video and keep the repo cloneable" advice |
| **Time sinks** | integration between components with different transports (MQTT vs Zenoh vs uProtocol) was the common effort: ArBytesMoral needed an MQTT-Kuksa provider, a Kuksa-uProtocol accessor and a CARLA-Kuksa provider; MegaBosses needed campaigns registered by script plus three web apps |

## 7. Takeaways for Chapter 4 teams
See [[hackathon-patterns]] for the cross-edition synthesis. Specific to this retrospective:
- Pin your versions on day 0: Ankaios, `up-rust`, Symphony. Compare with the Chapter 4 challenges [[chapter4-challenge-doctor-whodunit]] and [[chapter4-challenge-hack-to-the-future]], which again put uProtocol and Ankaios at the centre, so the same traps apply.
- The reusable Chapter 3 pieces (Ankaios manifests, Zenoh/uProtocol Rust examples, ThreadX Rust board apps) are catalogued in [[earlier-chapters]].
- Components: [[ankaios-overview]], [[zenoh-overview]], [[uprotocol-overview]], [[vss-kuksa-overview]], [[symphony-overview]], [[muto-overview]], [[threadx-overview]].

## 8. Repos looked at (shallow clones, 2026-10-03)
| Path | Commit | Date |
|---|---|---|
| repos/sdv_lab | 849444a | 2025-10-01 |
| repos/hc3-SolutionPlan_Template | cb41719 | 2025-09-24 |
| repos/hc3-challenge-mission-update-possible | 8f3dfff | 2025-10-27 |
| repos/hc3-side-challenges | b658812 | 2025-09-22 (README is one line plus `backgrounds/`; contents unverified) |
| repos/hc3-ArBytesMoral | 604d390 | 2025-10-09 |
| repos/hc3-MegaBosses | c54dc8f | 2025-10-02 |
| repos/hc3-SDVenturers | 177733c | 2025-10-03 |
| repos/hc3-TheBigRanch | 42470b2 | 2025-10-02 |
| repos/hc3-A-kiki | 17608b6 | 2025-10-02 |
| repos/hc3-COOTA | 95d141d | 2025-10-02 |
| repos/hc3-LastManStanding | 2517259 | 2025-10-09 |

Unverified / gaps: exact coach list per site, final scores, the "side challenges" content, whether `uUpdate`/`Wheels-On-Fire` were notable, and any chat/Slack questions (not public). GitHub API was rate limited, so issue lists of team repos were read through WebFetch summaries.
