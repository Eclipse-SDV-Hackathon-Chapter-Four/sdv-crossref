---
title: Eclipse Symphony - integration notes
type: integration-notes
component: symphony
tags: [sdv, symphony]
status: draft
sources:
  - https://github.com/eclipse-uprotocol/symphony-target-example-rust
  - https://sdv-blueprints.eclipse.dev/docs/ros-racer/
  - https://blogs.eclipse.org/post/christian-heissenberger/meet-2025-sdv-hackathon-finalists-and-winners-%E2%80%93-and-explore-their-code
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# Symphony - integration notes

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| iceoryx2 | none found | - | none | - |
| S-CORE | none found | - | none | - |
| OpenSOVD | none found | - | none | - |
| VSS/KUKSA | none found | - | none | - |
| uProtocol | yes | Target Provider uService contract over uProtocol (Zenoh or MQTT5) | demo | https://github.com/eclipse-uprotocol/symphony-target-example-rust |
| Ankaios | yes (hackathon) | MegaBosses OTA: Symphony + uProtocol + Ankaios; exact adapter unverified; no Ankaios provider in README | demo | blogs.eclipse.org post "Meet 2025 SDV Hackathon finalists" |
| openDuT | none found | - | none | - |
| AutoSD | none found | - | none | - |
| OpenBSW | none found | - | none | - |
| Muto | yes | MQTT bridge Muto agent <-> Symphony; ROS Racer blueprint | demo | https://sdv-blueprints.eclipse.dev/docs/ros-racer/ |
| Zenoh | indirect | via uProtocol Zenoh transport | demo | [[zenoh-integration-notes]] |
| ThreadX | indirect | Chapter 3 ThreadX challenge used MQTT/REST; direct Symphony link unverified | idea | [[threadx-integration-notes]] |
| Eclipse Ditto / Mosquitto | yes | MQTT provider / bridge | demo | ROS Racer doc |
