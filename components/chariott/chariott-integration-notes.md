---
title: Chariott / Ibeji / Agemo / Freyja - integration notes
type: reference
component: chariott
tags: [chariott, ibeji, integration]
status: draft
sources:
  - https://github.com/eclipse-chariott
last-verified: 2026-10-03
related:
  - "[[chariott-overview]]"
  - "[[sdv-landscape-overview]]"
---

# Chariott family - integration with other SDV projects

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| Ibeji <-> Chariott | yes | Ibeji registers/discovers via Chariott service discovery (optional) | demo | Ibeji README "Using Chariott" |
| Freyja <-> Ibeji / Agemo / Chariott | yes | Freyja adapters: gRPC digital-twin adapter (Ibeji), managed-subscribe adapter (Agemo), gRPC service discovery adapter (Chariott) | demo | https://raw.githubusercontent.com/eclipse-ibeji/freyja/main/docs/design/README.md |
| SDV Blueprints | idea | chariott-example-applications "incubate early ideas for an eventual blueprint"; software-orchestration blueprint describes the same layers but lists Ankaios/BlueChi only | idea | https://github.com/eclipse-chariott/chariott-example-applications |
| Eclipse Mosquitto / MQTT | yes | Ibeji, Agemo, Freyja MQTT adapters | demo | READMEs |
| VSS / KUKSA | none found | Ibeji uses DTDL; mapping to VSS would be new work | none | Ibeji README |
| iceoryx2 | none found | - | none | - |
| S-CORE | none found | - | none | - |
| OpenSOVD | none found | - | none | - |
| uProtocol | none found | conceptual overlap (service discovery, pub/sub) only | none | - |
| Ankaios | none found | listed as alternative orchestrator in blueprint, no code link | none | software-orchestration README |
| openDuT | none found | - | none | - |
| AutoSD | none found | - | none | - |
| OpenBSW | none found | - | none | - |
