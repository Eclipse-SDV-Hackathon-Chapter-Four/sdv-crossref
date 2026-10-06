---
title: Eclipse Muto - integration notes
type: integration-notes
component: muto
tags: [sdv, muto]
status: draft
sources:
  - https://github.com/eclipse-muto
  - https://sdv-blueprints.eclipse.dev/docs/ros-racer/
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# Muto - integration notes

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| iceoryx2 | none found | (CycloneDDS iceoryx SHM possible via ROS 2, not Muto-specific) | none | - |
| S-CORE | none found | - | none | - |
| OpenSOVD | none found | - | none | - |
| VSS/KUKSA | none found | - | none | - |
| uProtocol | none found | - | none | - |
| Ankaios | none found | container deployment "planned" in Muto README | idea | https://github.com/eclipse-muto |
| openDuT | none found | - | none | - |
| AutoSD | none found | - | none | - |
| OpenBSW | none found | - | none | - |
| Symphony | yes | MQTT bridge in Muto Agent | demo | ROS Racer blueprint |
| Eclipse Ditto | yes | digital twin per device, MQTT | demo | project page |
| Zenoh | none found (in Muto) | ROS 2 could use rmw_zenoh; ROS Racer uses CycloneDDS | idea | [[zenoh-overview]] |
| ThreadX | none found | - | none | - |
| SDV blueprints | yes | ROS Racer | demo | [[sdv-blueprints-overview]] |
