---
title: Eclipse Velocitas - integration notes
type: reference
component: velocitas
tags: [velocitas, integration]
status: draft
sources:
  - https://github.com/eclipse-velocitas
  - https://github.com/eclipse-autowrx
last-verified: 2026-10-03
related:
  - "[[velocitas-overview]]"
  - "[[sdv-landscape-overview]]"
---

# Velocitas - integration with other SDV projects

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| VSS / KUKSA | yes (core) | SDK vdb layer over KUKSA databroker gRPC (`kuksa.val.v1`); model generated from VSS by vehicle-model-generator; runtime image databroker 0.5.0 | demo (stale pin) | https://raw.githubusercontent.com/eclipse-velocitas/devenv-runtimes/main/manifest.json |
| Kanto | yes | `runtime-kanto`, `deployment-kanto` components | demo | Velocitas quickstart |
| autowrx / playground | yes | playground prototypes export to Velocitas; `sdv-runtime` image ships Python SDK 0.14.1 | demo (observed 2026-10-03) | [[autowrx-overview]] |
| Eclipse Leda | yes | Velocitas vApps deployed on Leda via Kanto | demo | https://eclipse-leda.github.io/leda/docs/app-deployment/ |
| uProtocol | partial | repo `pkg-velocitas-uprotocol` (stale since 2024-09-20) | idea | https://github.com/eclipse-velocitas |
| Ankaios | none found | would need a deployment component; apps are plain containers so it works manually | idea | - |
| iceoryx2 | none found | - | none | - |
| S-CORE | none found | - | none | - |
| OpenSOVD | none found | - | none | - |
| openDuT | none found | - | none | - |
| AutoSD | none found | containers could run on AutoSD via podman (unverified) | none | - |
| OpenBSW | none found | - | none | - |
| SDV Blueprints | partial | blueprints reuse KUKSA more than Velocitas; companion-application targets Leda | prototype | https://github.com/eclipse-sdv-blueprints |
