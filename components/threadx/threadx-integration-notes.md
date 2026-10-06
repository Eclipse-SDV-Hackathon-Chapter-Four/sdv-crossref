---
title: Eclipse ThreadX - integration notes
type: integration-notes
component: threadx
tags: [sdv, threadx]
status: draft
sources:
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust
  - https://github.com/eclipse-zenoh/zenoh-pico
  - https://blogs.eclipse.org/node/7908
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# ThreadX - integration notes

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| iceoryx2 | none found | MCU, no shared memory with Linux | none | - |
| S-CORE | none found | - | none | - |
| OpenSOVD | none found | - | none | - |
| VSS/KUKSA | none found | - | none | - |
| uProtocol | yes | threadx-rust publishes uMessage over MQTT5 | prototype | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust |
| Ankaios | none found | - | none | - |
| openDuT | none found | - | none | - |
| AutoSD | none found | - | none | - |
| OpenBSW | none found | alternative embedded base; not combined | none | [[openbsw-overview]] |
| Zenoh | yes (port) | zenoh-pico "STM32 ThreadX" platform | prototype | https://github.com/eclipse-zenoh/zenoh-pico |
| Mosquitto / MQTT | yes | NetX Duo MQTT client; challenge used MQTT and REST | demo | https://blogs.eclipse.org/node/7908 |
| Symphony | unverified | OTA story only via MQTT/REST in Chapter 3 | idea | [[symphony-integration-notes]] |
| Muto | none found | - | none | - |
