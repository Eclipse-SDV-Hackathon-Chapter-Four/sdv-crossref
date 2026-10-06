---
title: Eclipse SommR - integration notes
type: reference
component: sommr
tags: [sommr, integration, archived]
status: draft
sources:
  - https://projects.eclipse.org/projects/automotive.sommr
last-verified: 2026-10-03
related:
  - "[[sommr-overview]]"
  - "[[sdv-landscape-overview]]"
---

# SommR - integration with other SDV projects

SommR is archived with an empty repository; every row below is "none" unless a document claims intent.

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| Eclipse Leda / Velocitas / KUKSA | idea | BCX2022 challenge text: "Digital.Auto, Velocitas, Kuksa and Leda, and, if applicable SommR"; no implementation | idea | https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-passenger-welcome |
| iceoryx2 | none found | - | none | - |
| S-CORE | none found | - | none | - |
| OpenSOVD | none found | SOVD is HTTP/REST over Ethernet, not SOME/IP | none | - |
| VSS / KUKSA | none found | a SOME/IP-to-databroker provider would be new work | none | - |
| uProtocol | none found | uProtocol has transports (zenoh, mqtt5, socket), none for SOME/IP in the repos listed | none | https://github.com/eclipse-uprotocol |
| Ankaios | none found | - | none | - |
| openDuT | none found | - | none | - |
| AutoSD | none found | - | none | - |
| OpenBSW | none found | OpenBSW is MCU-side (Ethernet/CAN); no SOME/IP link found | none | - |
