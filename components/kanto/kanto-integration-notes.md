---
title: Eclipse Kanto - integration notes
type: reference
component: kanto
tags: [kanto, integration]
status: draft
sources:
  - https://github.com/eclipse-kanto/kanto
  - https://github.com/eclipse-velocitas
last-verified: 2026-10-03
related:
  - "[[kanto-overview]]"
  - "[[sdv-landscape-overview]]"
---

# Kanto - integration with other SDV projects

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| Eclipse Leda | yes | Kanto is the container runtime/manager of the Leda SDV.EDGE stack (kanto-auto-deployer, sdv-kanto-ctl) | demo | https://eclipse-leda.github.io/leda/docs/general-usage/sdv-introduction/ |
| Velocitas | yes | `runtime-kanto` / `deployment-kanto` components deploy databroker, MQTT, services as Kanto containers | demo | Velocitas quickstart; `.velocitas.json` in vehicle-app-python-template |
| KUKSA / VSS | indirect | KUKSA databroker image (0.5.0) run as a Kanto container by Velocitas runtime-kanto | demo | https://raw.githubusercontent.com/eclipse-velocitas/devenv-runtimes/main/manifest.json |
| uProtocol | partial | CANought: `up-cpp-server`/`up-cpp-client` for a CAN translator (dormant since 2025-04) | prototype | https://github.com/eclipse-canought |
| Eclipse Hono / Ditto | yes | suite-connector MQTT to Hono/Ditto; Azure/AWS connectors | production (v1.0.0, non-automotive) | https://projects.eclipse.org/projects/iot.kanto |
| Ankaios | none found | functional alternative (orchestrator); no bridge | none | https://github.com/eclipse-kanto/kanto |
| iceoryx2 | none found | - | none | - |
| S-CORE | none found | - | none | - |
| OpenSOVD | none found | - | none | - |
| openDuT | none found | - | none | - |
| AutoSD | none found | AutoSD uses podman/systemd/BlueChi, not Kanto | none | [[autosd-overview]] |
| OpenBSW | none found | - | none | - |
| SDV Blueprints | none found | not in blueprint READMEs checked (fleet-management, software-orchestration, e2e-vehicle-signals, carmate) | none | grep 2026-10-03 |
