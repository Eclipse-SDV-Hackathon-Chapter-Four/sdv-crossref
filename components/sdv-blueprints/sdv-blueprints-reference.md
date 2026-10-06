---
title: SDV Blueprints - Reference
type: reference
component: sdv-blueprints
tags: [reference,repos,versions]
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

# SDV Blueprints - Reference

## Links
- Site: https://sdv-blueprints.eclipse.dev (docs, per-blueprint pages); org: https://github.com/eclipse-sdv-blueprints ; project management repo `blueprints`.
- Chapter 3 lab: https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/sdv_lab (cloned: repos/sdv_lab @849444a, 2025-10-01).
- Source snapshots: https://sdv-blueprints.eclipse.dev, ...-github-org.md, ...-sdv-lab-readme.md

## Component/version matrix (from compose/manifests, 2026-10-03)
| blueprint | key images/versions | languages |
|---|---|---|
| fleet-management | kuksa-databroker 0.6.0, csv-provider 0.4.5, eclipse/zenoh 1.1.0, influxdb 2.7, grafana 9.5.14, fms-{forwarder,consumer,server}:main, up-rust 0.9.0, up-transport-zenoh 0.9.1 | Rust, Java (Jakarta EE 11) |
| service-to-signal | zenoh 1.6.2, kuksa-databroker 0.6.0, up-rust 0.9.0, up-transport-zenoh 0.9.0, dozzle | Rust, C++/zenoh-pico (ESP32) |
| software-orchestration | Ankaios 0.5, Chariott 0.2.1, Agemo 0.1.2, Ibeji 0.1.1, Freyja, Mosquitto, Podman 4.6 | Rust |
| companion-application | Leda 0.1.0-M2, Velocitas, Kuksa, Kanto | Python, Capella |
| e2e-vehicle-signals | Ankaios 0.7.0, Databroker 0.6.0, kuksa-can-provider 0.4.4, Mosquitto | Python, Arduino C++, Rust |

## APIs and ports
Fleet Management: Grafana 3000, rFMS HTTP 8081 (`/rfms/vehicleposition`), analysis 8082 (`/fleet-analysis/api`), Influx 8086, Databroker gRPC 55555. service-to-signal: Dozzle 8080, Databroker gRPC (kuksa.val.v1), Zenoh router. Ankaios: server 25551. E2E virtual: 8091 UI, 8090 website, 1883 MQTT.

## Activity / issues (2026-10-03)
See https://api.github.com/orgs/eclipse-sdv-blueprints/repos?per_page=100. Open issue counts: fleet-management 17, software-orchestration 11 (issue #28 undocumented in-vehicle dependencies), companion-application 10, service-to-signal 4, e2e-vehicle-signals 2, carmate 2.

## Licensing
fleet-management Apache-2.0; service-to-signal EPL-2.0; companion-application: none detected by GitHub API (unverified).
