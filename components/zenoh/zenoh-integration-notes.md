---
title: Eclipse Zenoh - integration notes
type: integration-notes
component: zenoh
tags: [sdv, zenoh]
status: draft
sources:
  - https://docs.rs/up-transport-zenoh/
  - https://github.com/eclipse-uprotocol/symphony-target-example-rust
  - https://github.com/eclipse-zenoh/zenoh-plugin-dds
  - https://github.com/eclipse-zenoh/zenoh-pico
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# Zenoh - integration notes

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| iceoryx2 | yes (prototype) | iceoryx2 ships a link tunnel with a Zenoh carrier (`iox2-link-tunnel-zenoh`, crate `iceoryx2-integrations-zenoh-link-tunnel-cli` 0.10.0) that mirrors iceoryx2 services between hosts; verified locally 2026-10-03 ([[iceoryx2-integration-notes]], [[iceoryx2-quickstart]] step 6). The Zenoh DDS plugin separately uses iceoryx v1 for DDS SHM. Still missing: a gateway exposing iceoryx2 services as native Zenoh key expressions | prototype | https://github.com/eclipse-zenoh/zenoh-plugin-dds ; [[iceoryx2-overview]] |
| S-CORE | none found | S-CORE's production IPC is LoLa (mw::com, its own shared-memory implementation); iceoryx2 is used only by the S-CORE orchestrator (cross-process events, removed from the platform in v0.9 but repo exists) and as one FEO communication backend; no Zenoh evidence seen | none | [[s-core-integration-notes]]; [[iceoryx2-integration-notes]] |
| OpenSOVD | none found | Could carry diagnostics over Zenoh; nothing found | none | - |
| VSS/KUKSA | none found | Possible: key expr per VSS path | idea | [[vss-kuksa-overview]] |
| uProtocol | yes | `up-transport-zenoh` crate (Rust, tokio) | prototype/demo | https://docs.rs/up-transport-zenoh/ |
| Ankaios | none found | Workloads could use Zenoh themselves | none | - |
| openDuT | none found | - | none | - |
| AutoSD | none found | zenohd is a plain Linux/RPM-able binary; not verified in AutoSD | none | - |
| OpenBSW | none found | zenoh-pico on MCU would be the path | idea | https://github.com/eclipse-zenoh/zenoh-pico |
| Symphony | yes | Symphony Target example talks uProtocol over Zenoh or MQTT5 | demo | https://github.com/eclipse-uprotocol/symphony-target-example-rust |
| ThreadX | yes (port) | zenoh-pico supports STM32 ThreadX | prototype | https://github.com/eclipse-zenoh/zenoh-pico |
| ROS 2 (rmw_zenoh) | yes | rmw_zenoh, zenoh-plugin-ros2dds | production | https://github.com/ros2/rmw_zenoh ; https://github.com/eclipse-zenoh/zenoh-plugin-ros2dds |
| Muto | no | Muto itself uses MQTT/CycloneDDS in ROS Racer; no Zenoh use found | none | https://sdv-blueprints.eclipse.dev/docs/ros-racer/ |
| MQTT / DDS | yes | Router plugins/bridges | production-ish | zenoh-plugin-dds repo |
