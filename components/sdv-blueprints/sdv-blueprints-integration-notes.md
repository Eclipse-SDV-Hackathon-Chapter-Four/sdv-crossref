---
title: SDV Blueprints - Integration notes
type: reference
component: sdv-blueprints
tags: [integration,matrix]
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

# SDV Blueprints - Integration notes

Maturity scale: none / idea / prototype / demo / production. Blueprints are demos at best.

| other project | integrates? | how (protocol / library / adapter) | maturity | evidence |
|---|---|---|---|---|
| VSS / KUKSA | yes (spine of 4 of 5 blueprints) | Databroker 0.6.0 gRPC kuksa.val.v1; FMS VSS overlay (`--metadata vss.json`); csv-provider, kuksa-can-provider, zenoh-kuksa-provider, kuksa-rust-sdk | demo | repos/fleet-management/README.md, repos/service-to-signal/README.md, repos/e2e-vehicle-signals/README.md |
| uProtocol | yes | up-rust 0.9.0 + up-transport-zenoh 0.9.x (Notification in fleet; RPC for COVESA Horn uService); custom Hono Kafka/MQTT transports in-repo | demo | repos/fleet-management/components/Cargo.toml, repos/service-to-signal/components/Cargo.toml |
| Zenoh | yes | router eclipse/zenoh 1.1.0 (fleet) / 1.6.2 (s2s); zenoh-pico on ESP32 | demo | compose files in both repos |
| Ankaios | yes | Podman workloads: software-orchestration (v0.5), e2e-vehicle-signals Pi5 (v0.7.0 `vehicle-signals.yaml`); also Chapter 3 sdv_lab (v0.6.0) | demo | repos/software-orchestration/eclipse-ankaios, repos/e2e-vehicle-signals, repos/sdv_lab/README.md |
| Velocitas | yes | Seat adjuster app from Velocitas template, VSS vehicle model | demo (tutorial, Leda M2) | repos/companion-application/Readme.md |
| Kanto / Leda | yes | Kanto container manifests on Eclipse Leda; fleet-management `leda/` deployment | demo (old versions) | repos/companion-application/deploy-seat-adjuster.md, repos/fleet-management/leda/README.md |
| Symphony | yes, in another blueprint | commercial-sdv-stack (OTA firmware/config; Symphony REST :8082, portal :3000) | demo | https://github.com/eclipse-sdv-blueprints/commercial-sdv-stack (README only read via raw fetch; not cloned) |
| Hono / Mosquitto / Paho | yes | MQTT/Kafka uProtocol transport; MQTT trigger and bridges | demo | fleet-management README, e2e `grpc-mqtt-bridge` |
| ThreadX | yes (placeholder) | `devices/driver-input-ecu-threadx` in e2e-vehicle-signals; submodule `external/challenge-threadx-playRemote` | idea/prototype | repos/e2e-vehicle-signals/README.md |
| Muto | yes, in another blueprint | ros-racer ("Eclipse Muto Integration") | demo | https://github.com/eclipse-sdv-blueprints/ros-racer (README only; not cloned) |
| BlueChi / AutoSD | partial | BlueChi variant of software-orchestration (Quadlet `.kube` files); AutoSD itself not used | prototype | repos/software-orchestration/eclipse-bluechi |
| Ibeji / Freyja / Chariott / Agemo | yes (software-orchestration only) | Chariott service discovery, Agemo pub/sub, Ibeji digital twin, Freyja cloud sync | demo, stale | repos/software-orchestration/eclipse-ankaios/config/startupManifest.yaml |
| InfluxDB / Grafana | yes | fms-consumer -> Influx 2.7; Grafana 9.5.14 provisioned dashboard | demo | fms-blueprint-compose.yaml |
| iceoryx2 | none found | - | none | grep over 5 cloned repos |
| S-CORE | none found | e2e README mentions "Eclipse S-CORE or equivalent" as optional Pi4 high-level control only | idea | repos/e2e-vehicle-signals/README.md |
| OpenSOVD | none found | - | none | grep over 5 cloned repos |
| openDuT | none found | - | none | grep |
| AutoSD | none found | (see BlueChi row) | none | grep |
| OpenBSW | none found | - | none | grep |

## Notes for hackathon teams
- Common contract across blueprints = VSS signal names + Kuksa Databroker 0.6.0. Anything speaking Kuksa gRPC plugs in; that is the cheapest integration seam (CAN provider, MQTT bridge, Zenoh provider, CSV).
- uProtocol over Zenoh is the second seam (fleet forwarder/consumer, horn service). Version-match up-rust/up-transport-zenoh (Chapter 3 pitfall: [[chapter3-retrospective]], repos/sdv_lab/README.md).
- Gaps (no integration found): iceoryx2 local transport, OpenSOVD diagnostics -> Kuksa, S-CORE app on Pi4, openDuT test bench driving a blueprint, OpenBSW as the MCU target (e2e uses Arduino). Each is a plausible hackathon contribution. See [[iceoryx2-overview]], [[opensovd-overview]], [[s-core-overview]], [[opendut-overview]], [[openbsw-overview]], [[autosd-overview]].
