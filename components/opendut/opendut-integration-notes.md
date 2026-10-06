---
title: openDuT - integration notes
type: reference
component: opendut
tags: [opendut, integration]
status: draft
sources:
  - repos/opendut-playground/README.md
  - repos/opendut-playground/result-overview.md
  - https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
  - https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
last-verified: 2026-10-03
related:
  - "[[opendut-overview]]"
  - "[[opendut-howto]]"
  - "[[opensovd-overview]]"
  - "[[s-core-overview]]"
---

# openDuT integration notes

openDuT is a transport/orchestration layer for L2/CAN; integration with others = "connect their wires/containers through it", not API-level.

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| OpenSOVD (Classic Diagnostic Adapter) | yes | CDA reaches a real car's ECUs/DoIP over an openDuT Pi; virtual CDA testcontainer split across two PCs via openDuT (challenge 2) | demo | playground README; result-overview.md (mirrors folded); HackFest blog |
| S-CORE | partial | EDGAR installed natively on the S-CORE image (needs vcan; no systemd); S-CORE image used with RC car CAN | prototype | result-overview.md |
| iceoryx2 | none found | - (host-local IPC; could sit inside a container behind a CAN/Eth bridge) | none | no mention in repos/opendut (grep not exhaustive) |
| VSS / KUKSA | none found | idea: CAN feeder to KUKSA on peer; Chapter 4 text mentions "stuck VSS signals" | idea | Chapter 4 challenge snippet (eventbrite); no code |
| uProtocol | none found | idea: uP over Zenoh/MQTT over openDuT Ethernet cluster | none | - |
| Ankaios | none found | idea: Ankaios nodes in different sites joined via cluster Ethernet; Chapter 4 stack lists Ankaios + openDuT together | idea | Chapter 4 snippet |
| AutoSD | none found | idea: AutoSD image with native EDGAR (RPM/podman; EDGAR supports podman executors) | none | - |
| OpenBSW | none found | idea: posix virtual ECU on vcan bridged by EDGAR | idea | see [[openbsw-overview]] |
| Eclipse SDV HackFest Esslingen (event) | yes | see [[hackfest-esslingen-2026]] | demo | playground |
