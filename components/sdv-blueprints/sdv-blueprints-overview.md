---
title: Eclipse SDV Blueprints - Overview
type: overview
component: sdv-blueprints
tags: [sdv,blueprints,fleet,kuksa,uprotocol,ankaios]
status: draft
sources:
  - https://sdv-blueprints.eclipse.dev
  - https://github.com/eclipse-sdv-blueprints
  - repos/fleet-management/README.md
  - repos/service-to-signal/README.md
  - repos/software-orchestration/README.md
  - repos/companion-application/Readme.md
  - repos/e2e-vehicle-signals/README.md
  - repos/sdv_lab/README.md
  - https://api.github.com/orgs/eclipse-sdv-blueprints/repos?per_page=100
last-verified: 2026-10-03
related:
  - "[[sdv-blueprints-overview]]"
  - "[[chapter4-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[zenoh-overview]]"
  - "[[kanto-overview]]"
  - "[[velocitas-overview]]"
  - "[[symphony-overview]]"
  - "[[chapter3-retrospective]]"
---

# Eclipse SDV Blueprints - Overview

## What a blueprint is (and is not)
A blueprint is a **reproducible, end-to-end showcase repo** that wires several Eclipse SDV projects together for one use case; "a crucial aspect of each blueprint is to ensure users can easily reproduce it" and users may use it as-is, for inspiration, or as a foundation (https://sdv-blueprints.eclipse.dev). It is NOT a product, a supported distribution or a framework: each repo is a demo with its own maturity. Docs site: **https://sdv-blueprints.eclipse.dev** (the guessed `eclipse-sdv-blueprints.github.io` returns a GitHub Pages 404, checked 2026-10-03; source: repo `blueprints-website`).

## Org inventory (GitHub API, 2026-10-03; see https://api.github.com/orgs/eclipse-sdv-blueprints/repos?per_page=100)
| repo | last push | note |
|---|---|---|
| fleet-management | 2026-09-24 | most active, 27 stars, 17 open issues, Apache-2.0 |
| e2e-vehicle-signals | 2026-09-07 | new (created 2026-04), fleet-management + HW blinker demo, has a **virtual (no-HW) setup** |
| carmate | 2026-08-28 | new (2026-07): AI companion; Kuksa+Zenoh+AutoWRX+CARLA, STT/TTS/LLM |
| commercial-sdv-stack | 2026-08-07 | OTA firmware/config of ECUs; Symphony (docker compose, Dozzle) |
| companion-application | 2026-05-26 | Leda + Velocitas + Kanto seat adjuster; docs-only repo |
| ros-racer | 2026-03-11 | ROS/F1Tenth multi-agent, Eclipse Muto ([[muto-overview]]) |
| insurance | 2026-04-02 | **ARCHIVED** (README: read-only, blueprints#20) |
| service-to-signal | 2025-12-04 | uProtocol/Zenoh horn service -> Kuksa; EPL-2.0 |
| software-orchestration | 2025-01-20 | Ankaios 0.5 / BlueChi smart trailer; stale (>20 months) |
| blueprints, blueprints-website, .github, .eclipsefdn | - | project management / site |

Cloned (shallow) to repos/: fleet-management @6bc91a2 (2026-09-24), software-orchestration @0a41785 (2025-01-20), service-to-signal @32f9ec1 (2025-12-04), companion-application @2521528 (2026-05-26), e2e-vehicle-signals @71c68cc (2026-09-07), plus repos/sdv_lab @849444a (2025-10-01, Chapter 3).

## Per-blueprint architecture

### 1. Fleet Management (rFMS) - the best scaffold
- Flow: `CSV Provider` (kuksa-csv-provider 0.4.5, replays `csv-provider/signalsFmsRecording.csv` of VSS signals) -> `Kuksa Databroker 0.6.0` (loaded with FMS VSS overlay `spec/overlay/vss.json`) -> `FMS Forwarder` (Rust uEntity, subscribes to Databroker via gRPC) -> **uProtocol Publish** (`SimplePublisher::publish`, not a Notification; corrected 2026-10-03, see [[fleet-telemetry-batched-at-the-vehicle-keyed-by-vin]]) over **Zenoh** (default) or Hono(MQTT/Kafka) -> `FMS Consumer` (Rust uEntity) -> `InfluxDB 2.7` -> `Grafana 9.5.14` dashboard (`grafana/dashboards/FMS-Fleet.json`) and `FMS Server` (rFMS 4.0 REST on :8081). Optional Jakarta EE `fleet-analysis-backend` (:8082, fleet stats written back to Influx).
- Evidence: repos/fleet-management/README.md, fms-blueprint-compose*.yaml, components/Cargo.toml (up-rust 0.9.0, up-transport-zenoh 0.9.1, `up-transport-hono-{kafka,mqtt}` crates in-repo).
- Projects: KUKSA (databroker, csv-provider), uProtocol (up-rust), Zenoh (router eclipse/zenoh:1.1.0), Hono (optional), InfluxDB, Grafana; Leda deployment variant in `leda/` (tested with Leda 0.1.0-M3). Docs intro table lists Leda, Kuksa, Hono, Kanto, Paho.
- Dashboards show: speed, engine speed, fuel levels, location, driver working state, RFID driver ID, brake/indicator state, total distance, ambient temperature, "Fleet Stats".

### 2. Service-to-Signal
- Horn client --(uProtocol RPC over Zenoh, COVESA Horn uService)--> `horn-service-kuksa` (Rust, kuksa-rust-sdk) --> Databroker (signal `Vehicle.Body.Horn.IsActive`) <-> `zenoh-kuksa-provider` (from kuksa-incubation **git submodule**) <-> Zenoh topic `Vehicle/Body/Horn/IsActive` <-> `software-horn` (log/sound) or ESP32 `actuator-provider` (zenoh-pico). Dozzle for logs.
- Compose: zenoh 1.6.2, kuksa-databroker 0.6.0, images built locally (`horn-service:latest` etc.). Evidence: repos/service-to-signal/README.md, service-to-signal-compose.yaml.

### 3. Software Orchestration (smart trailer)
- Ankaios variant: workloads (Podman) `service_discovery` (Chariott 0.2.1), `mqtt_broker` (Mosquitto with Agemo config), `dynamic_topic_management` (Agemo pub-sub-service), `digital_twin_vehicle` (Ibeji), `digital_twin_cloud_sync` (Freyja); started on demand: `trailer_connected_provider`, `trailer_properties_provider`, `smart_trailer_application`. BlueChi variant: same workloads as Quadlet `.kube/.yml` files. Evidence: repos/software-orchestration/eclipse-ankaios/config/startupManifest.yaml, eclipse-bluechi/workspace/workloads.
- No KUKSA, no uProtocol; uses the Microsoft-originated Ibeji/Freyja/Chariott/Agemo stack (Eclipse "Ibeji/Freyja" projects). Uses Ankaios 0.5 docs.

### 4. Companion Application (seat adjuster)
- MQTT trigger -> `Seat Adjuster` Velocitas app (Python, vehicle model on VSS) -> Kuksa Databroker (pre-installed in Eclipse Leda) -> mock seat service (Kuksa provider). Deployed to Leda via **Kanto** container manifests (`/data/var/containers/manifests`, `kanto-auto-deployer`); modelled in Eclipse Capella. Repo is **documentation only** (no compose). Written against Leda 0.1.0-M2. Evidence: repos/companion-application/*.md.

### 5. (bonus) E2E Vehicle Signals
- Combines Fleet Management with a motorbike-blinker HW demo: Pi5 with **Ankaios 0.7.0** running Databroker 0.6.0, Mosquitto, `grpc-mqtt-bridge`, `kuksa-can-provider` (val2dbc/dbc2val, CAN IDs 288/289), website; Arduino MCU LED ECU, ThreadX/RFID/joystick input ECUs. `virtual-setup/` replaces the HW with a `virtual-indicator-ui` container. Evidence: repos/e2e-vehicle-signals/README.md, virtual-setup/README.md.

## Maturity summary
| blueprint | maturity | last activity | verdict |
|---|---|---|---|
| fleet-management | demo+, actively maintained (Sep 2026 fixes) | 2026-09-24 | use |
| e2e-vehicle-signals | demo, young | 2026-09-07 | use virtual-setup |
| service-to-signal | demo, slow | 2025-12-04 (issue 2026-10-01) | OK for pattern |
| companion-application | tutorial, outdated Leda M2 | 2026-05-26 | reference only |
| software-orchestration | stale, Ankaios 0.5 | 2025-01-20 | reference only |

## Scaffold fit for Chapter 4 (see [[chapter4-challenge-doctor-whodunit]], [[chapter4-challenge-hack-to-the-future]])
- **Doctor Whodunit (telemetry + fault evidence + dashboards)**: Fleet Management is a near-complete telemetry pipeline (Databroker -> uProtocol/Zenoh -> Influx -> Grafana) minus any fault/DTC path. Add a fault-evidence leg (e.g. [[opensovd-overview]] DTCs, OpenBSW diagnostics -> VSS/Influx, a "snapshot on fault" ring buffer). e2e-vehicle-signals adds a CAN/MCU edge for real "evidence".
- **Hack to the Future (portable feature across targets)**: service-to-signal (feature = uProtocol service, targets = software horn vs ESP32 via Zenoh) and companion-application/Velocitas (vehicle-model-abstracted app) show portability; software-orchestration/Ankaios shows moving workloads between nodes. Chapter 3 `sdv_lab` (uProtocol + Ankaios + CARLA/AAOS, [[chapter3-retrospective]]) is the closest "portable across targets" scaffold.

## Pros / cons
Pros: real compose files with published images, Apache-2.0, VSS/Kuksa as common spine, Rust uProtocol samples, active FMS repo. Cons: forwarder and consumer default to the authorities `fms-forwarder`/`fms-consumer` with the VIN only in the payload, so all trucks share one authority unless each gets `--topic up://<vin-lower>/...` ([[authority-is-the-routing-unit]]); a failed publish is dropped with `warn!`, no buffer ([[fleet-telemetry-batched-at-the-vehicle-keyed-by-vin]]); pinned old versions (Databroker 0.6.0, Grafana 9.5, Zenoh 1.1/1.6 mismatch across repos), docs drift, no common integration (each blueprint uses a different subset), little CI proof of the quickstarts, several repos effectively frozen.
Not suitable when: you need safety/security evidence, production OTA, or a maintained orchestrator demo (software-orchestration).

## Hackathon ideas (blueprint gaps)
1. Fault evidence leg for Fleet Management: DTC/event -> VSS overlay -> Influx annotation -> Grafana panel (Doctor Whodunit).
2. Fix open fleet-management bugs #71 (time unit), #72/#74 (heading/altitude u32/i32 conversion) - small upstreamable PRs.
3. Port Fleet Management Forwarder transport selection to run on [[iceoryx2-overview]] locally + Zenoh bridge.
4. Ankaios manifest for the whole Fleet Management vehicle side (Databroker+csv-provider+forwarder) so it runs on target ECUs (Hack to the Future); e2e-vehicle-signals already has Ankaios 0.7 pattern.
5. Replace the software horn target with a second target (Android/ThreadX/openBSW) for service-to-signal.
6. Refresh software-orchestration for Ankaios 0.7 and add Kuksa instead of Ibeji.
7. Pin kuksa-rust-sdk (service-to-signal#14, open as of 2026-10-01).

Links: [[sdv-blueprints-quickstart]] [[sdv-blueprints-howto]] [[sdv-blueprints-reference]] [[sdv-blueprints-integration-notes]]
