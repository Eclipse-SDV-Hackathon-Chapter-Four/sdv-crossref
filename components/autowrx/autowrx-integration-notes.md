---
title: Eclipse autowrx - integration notes
type: reference
component: autowrx
tags: [autowrx, integration]
status: draft
sources:
  - https://github.com/eclipse-autowrx
last-verified: 2026-10-03
related:
  - "[[autowrx-overview]]"
  - "[[sdv-landscape-overview]]"
---

# autowrx / playground / dreamKIT - integration with other SDV projects

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| VSS / KUKSA | yes (core) | sdv-runtime bundles databroker 0.4.4 + VSS 4.0 + mock provider + kuksa-syncer; playground reads/writes via databroker | demo (run 2026-10-03) | https://github.com/eclipse-autowrx/sdv-runtime |
| Velocitas | yes | code runs with Velocitas Python SDK 0.14.1; export to Velocitas templates | demo | sdv-runtime README; velocitas quickstart tab "digital.auto" |
| SDV Blueprints | yes | carmate blueprint uses AutoWRX; autowrx org has `sdv-blueprints`, `digital.auto-RIVOS-blueprint` repos | prototype | https://github.com/eclipse-sdv-blueprints/carmate |
| Eclipse Leda | yes | hackathon "Passenger Welcome": digital.auto + Velocitas + KUKSA + Leda | demo (2022) | https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-passenger-welcome |
| Ankaios | indirect | Chapter Two Play by Wire suggests Ankaios for deployment of playground-defined APIs | idea | https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challenge-play-by-wire |
| Kanto | none found | - | none | - |
| uProtocol | none found | - | none | - |
| iceoryx2 | none found | - | none | - |
| S-CORE | none found | - | none | - |
| OpenSOVD | none found | - | none | - |
| openDuT | none found | - | none | - |
| AutoSD | none found | - | none | - |
| OpenBSW | none found | dreamKIT docs mention connecting AUTOSAR ECUs over CAN/SOME-IP, not OpenBSW | none | https://github.com/eclipse-autowrx/dreamKIT |
