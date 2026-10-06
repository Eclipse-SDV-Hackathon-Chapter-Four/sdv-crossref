---
title: Ankaios integration notes
type: reference
component: ankaios
tags: [ankaios, orchestrator, podman, sdv]
status: draft
sources:
  - repos/ankaios/doc/docs/usage/quickstart.md
  - repos/ankaios/doc/docs/usage/tutorial-vehicle-signals.md
  - https://github.com/eclipse-ankaios/ankaios
last-verified: 2026-10-03
related:
  - "[[ankaios-overview]]"
  - "[[ankaios-quickstart]]"
  - "[[ankaios-howto]]"
  - "[[ankaios-reference]]"
  - "[[ankaios-integration-notes]]"
---

# Ankaios integration notes

Ankaios is an orchestrator: it integrates by *running* other projects as containers and exposing a control API, not through protocol bridges.

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| Eclipse KUKSA (databroker, can-provider) | yes | Databroker and providers run as podman workloads with --net=host; Ankaios tutorial feeds VSS speed | demo | repos/ankaios/doc/docs/usage/tutorial-vehicle-signals.md; repos/e2e-vehicle-signals/devices/raspberry-pi5/ankaios/vehicle-signals.yaml |
| Eclipse Symphony | yes | Symphony target provider (Rust crate `symphony`) runs as Ankaios workload, cloud->MQTT->Ankaios control interface | demo | repos/hc3-challenge-mission-update-possible/hpc_variant/README.md; awesome-ankaios.md |
| SDV Blueprints | yes | Software Orchestration, Insurance, E2E Vehicle Signals, Fleet Management blueprints run on Ankaios | demo | repos/software-orchestration/eclipse-ankaios/README.md; repos/e2e-vehicle-signals; repos/ankaios/doc/docs/usage/awesome-ankaios.md |
| Eclipse uProtocol | indirect | uProtocol apps (Rust, cruise-control, sensors) packaged as Ankaios workloads in SDV Lab; Chapter 4 Guardian exchanges uProtocol events under Ankaios supervision | demo | repos/sdv_lab/README.md; repos/hackathon-ch4-dotgithub/profile/README.md:43 |
| Eclipse BlueChi | alternative/adjacent | Same Software Orchestration blueprint has a BlueChi variant; thesis compares Ankaios, BlueChi, K3s | demo | repos/software-orchestration/; awesome-ankaios.md |
| Eclipse Muto | alternative | HC3 "ros_variant" uses Muto instead of Ankaios | prototype | repos/hc3-challenge-mission-update-possible/ros_variant |
| Eclipse LMOS (AI) | yes | talk + repo "arc-with-ankaios" | prototype | awesome-ankaios.md |
| Eclipse ThreadX | idea | privileged container flashes ThreadX board, triggered via Ankaios | idea | hpc_variant/README.md |
| Eclipse openDuT | none found | Chapter 4 plans openDuT fault campaigns against Guardian run under Ankaios, no direct integration code found | idea | repos/hackathon-ch4-dotgithub/profile/README.md:43 |
| AutoSD | partial | COPR RPM spec exists (pingou/ankaios), no end-to-end AutoSD demo found; Ankaios does not ship in eclipse-autosd images; Chapter 4 runs Guardian "on an AutoSD-based runtime, supervised by Ankaios" (claim only) | idea | Chapter 4 README; [[autosd-integration-notes]] |
| iceoryx2 | none found | No Ankaios docs. Possible via shared /dev/shm + --ipc=host between containers | idea | repos/iceoryx2/FAQ.md:458 |
| S-CORE | none found | S-CORE has its own orchestrator (repos/s-core-orchestrator); no Ankaios link found | none | grep of s-core-* repos |
| OpenSOVD | none found | none; idea: expose workload states as SOVD faults via opensovd-fault-lib | idea | grep of opensovd-* repos |
| VSS | yes (via KUKSA) | VSS signals flow through databroker workload | demo | tutorial-vehicle-signals.md |
| OpenBSW | none found | n/a | none | - |
| Zenoh / Velocitas / Kanto | not checked | Kanto is a competing container manager; Velocitas not checked | none | - |

## Notes
- Chapter 3 usage: SDV Lab (v0.6.0) ran ego-vehicle/uProtocol apps and an MQTT service as Ankaios workloads on two nodes (shared notebook + participant notebook), with an example Rust/Python workload using the SDK (repos/sdv_lab/ankaios/example_workloads). "Mission Update Possible" HPC variant: update_trigger (Python SDK) starts the symphony provider workload; Ankaios_Dashboard workload for viewing.
- Chapter 4 Doctor Whodunit (correcting the brief: this is Chapter 4): Ankaios supervises the Battery Thermal Guardian on AutoSD. A plausible design: Guardian workload with `restartPolicy: ALWAYS`, a watchdog workload with SDK + events subscription, fault injectors as ADD_COND_* dependent workloads. See [[chapter4-challenge-doctor-whodunit]], [[chapter3-retrospective]].
- Links: [[vss-kuksa-overview]], [[uprotocol-overview]], [[symphony-overview]], [[opendut-overview]], [[autosd-overview]], [[sdv-blueprints-overview]], [[iceoryx2-overview]], [[s-core-overview]], [[opensovd-overview]], [[kanto-overview]], [[muto-overview]], [[ankaios-overview]].
