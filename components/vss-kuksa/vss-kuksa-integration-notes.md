---
title: VSS + KUKSA integration notes
type: reference
component: vss-kuksa
tags: [vss, kuksa, integration, uprotocol, ankaios, zenoh, opensovd, blueprints]
status: draft
sources:
  - repos/service-to-signal/service-to-signal-compose.yaml
  - repos/hc3-ArBytesMoral/compute/ankaios.yaml
  - repos/ankaios/doc/docs/usage/tutorial-vehicle-signals.md
  - repos/fleet-management/components/fms-forwarder/src/vehicle_abstraction/kuksa.rs
  - repos/e2e-vehicle-signals/README.md
  - repos/hackathon-ch4-dotgithub/profile/README.md
  - https://sdv-blueprints.eclipse.dev/docs/service-to-signal
  - https://sdv-blueprints.eclipse.dev/docs/e2e-demo-blueprint/signal-mapping
  - https://github.com/eclipse-kuksa/kuksa-incubation
  - https://eclipse.dev/velocitas/docs/concepts/development_model/val/
  - https://projects.eclipse.org/projects/automotive.leda/releases/0.1.0/plan
  - https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[opensovd-overview]]"
  - "[[s-core-overview]]"
  - "[[iceoryx2-overview]]"
  - "[[opendut-overview]]"
  - "[[autosd-overview]]"
  - "[[openbsw-overview]]"
  - "[[sdv-blueprints-overview]]"
  - "[[zenoh-overview]]"
  - "[[velocitas-overview]]"
  - "[[kanto-overview]]"
  - "[[symphony-overview]]"
  - "[[muto-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# VSS + KUKSA integration notes

Method: grepped every clone in `repos/` for `kuksa|databroker|vehicle_signal_specification|VSS` (2026-10-03) and ran a web search on the rest. "none found" means no evidence in the cloned repos or the web search. It is not proof that nothing exists.

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| [[uprotocol-overview]] uProtocol | partial | Service-to-Signal blueprint: a COVESA Horn uService over uProtocol (up-transport-zenoh-rust) is backed by the VSS signal `Vehicle.Body.Horn.IsActive` in a KUKSA databroker through the "horn-service-kuksa" component and the kuksa-incubation zenoh-kuksa-provider. No generic up-kuksa bridge found. up-spec has no VSS/KUKSA text (only an SVG hit). | demo | repos/service-to-signal/service-to-signal-compose.yaml:37-80 (databroker 0.6.0 on port 55556); https://sdv-blueprints.eclipse.dev/docs/service-to-signal |
| [[s-core-overview]] S-CORE | none found | n/a. 0 hits in repos/s-core-score and repos/s-core-reference_integration. A VSS-based vehicle API on top of S-CORE communication would be new work. | none | grep of repos/s-core-* |
| [[opensovd-overview]] OpenSOVD | none found | No VSS→SOVD mapping exists. 0 hits in repos/opensovd-core, -cda, -demo, -main. Possible adapter: expose selected VSS signals as SOVD `data` resources and map `Vehicle.Diagnostics.DTCList` to SOVD faults. | idea | grep of repos/opensovd-*; Chapter 4 text pairs OpenSOVD ("diagnostic truth") with VSS-level fault injection |
| [[ankaios-overview]] Ankaios | yes | Databroker runs as a podman workload with `ADD_COND_RUNNING` dependencies for providers. There is an official tutorial (speed-provider/consumer images) and a Chapter 3 winner manifest. | demo | repos/ankaios/doc/docs/usage/tutorial-vehicle-signals.md (uses old `ghcr.io/eclipse/kuksa.val/databroker:0.4.1`); repos/ankaios/tools/tutorials/vehicle_signals/; repos/hc3-ArBytesMoral/compute/ankaios.yaml (`kuksa-databroker:0.6.0`); repos/e2e-vehicle-signals/README.md:3 ("Kuksa Databroker 0.6.0 running as an Eclipse Ankaios 0.7.0 workload") |
| [[opendut-overview]] openDuT | partial (challenge-level) | The Chapter 4 Doctor Whodunit text says openDuT replays fault campaigns including "stuck or implausible VSS signals". There is no openDuT code referencing KUKSA (0 hits in repos/opendut, repos/opendut-playground). The likely mechanism is a provider-side or network-level fault injector in front of the databroker. | idea | https://opendut.eclipse.dev/; Eventbrite link in frontmatter |
| [[autosd-overview]] AutoSD | none found | No KUKSA package or sample in repos/eclipse-autosd, sample-images, inc_os_autosd, automotive-image-builder. Running the databroker container under podman on AutoSD should work (static musl binary, distroless image), but this was not tested. Only an AGL Yocto recipe was found. | none | grep of repos/*autosd*, repos/sample-images; https://layers.openembedded.org/layerindex/recipe/396481 |
| [[iceoryx2-overview]] iceoryx2 | none found | n/a. A possible idea is an iceoryx2 provider for zero-copy local signal fan-out. | none | grep of repos/iceoryx2; https://github.com/eclipse-iceoryx/iceoryx2:49 |
| [[openbsw-overview]] OpenBSW | none found | n/a. The realistic path is CAN frames from OpenBSW to kuksa-can-provider (DBC↔VSS) to the databroker. | none | grep of repos/openbsw (only an unrelated "vss" in a printf CMake comment) |
| [[sdv-blueprints-overview]] SDV Blueprints | yes | Fleet Management: fms-forwarder reads VSS from the databroker via kuksa-rust-sdk v2. The compose file uses `quay.io/eclipse-kuksa/kuksa-databroker:0.6.0` and `quay.io/eclipse-kuksa/csv-provider:0.4.5`. Service-to-Signal: see the uProtocol row. E2E vehicle signals: VSS-aligned names plus kuksa-can-provider `0.4.4`. Companion Application: Leda + Velocitas + KUKSA. Software-orchestration lists `automotive.kuksa` in `.sdv-blueprint.json`. | demo | repos/fleet-management/components/fms-forwarder/src/vehicle_abstraction/kuksa.rs:20; repos/fleet-management/fms-blueprint-compose.yaml:161,179; repos/e2e-vehicle-signals/devices/raspberry-pi5/ankaios/vehicle-signals.yaml; repos/e2e-vehicle-signals/README.md; repos/software-orchestration/.sdv-blueprint.json:12 |
| [[zenoh-overview]] Zenoh | yes | `zenoh-kuksa-provider` (kuksa-incubation) forwards configurable VSS signals between databroker gRPC and Zenoh key expressions. Lets ESP32/zenoh-pico devices join. | prototype/demo | repos/service-to-signal/service-to-signal-compose.yaml:68-80; https://github.com/eclipse-kuksa/kuksa-incubation |
| [[velocitas-overview]] Velocitas | yes | Vehicle-app SDKs (Python/C++) use the databroker as the "Vehicle Abstraction Layer" with a generated VSS model. Low release activity (Python SDK v0.15.7, 2024-07-03). Which gRPC API the latest SDK targets is unverified, so check before use with databroker 0.7.x. | demo (stale) | https://eclipse.dev/velocitas/docs/concepts/development_model/val/ ; https://github.com/eclipse-velocitas/vehicle-app-python-sdk/releases |
| [[kanto-overview]] Kanto | partial | Bundled next to the databroker in Eclipse Leda (Kanto container management). Fleet-management ships Leda/Kanto container manifests for the databroker and csv-provider. | demo (Leda largely inactive, unverified) | repos/fleet-management/leda/data/var/containers/manifests/databroker.json; Leda plan link in frontmatter |
| [[symphony-overview]] Symphony | none found | n/a | none | web search only |
| [[muto-overview]] Muto | none found | n/a | none | web search only |
| Android (AAOS) | yes | kuksa-android-sdk (Alpha) and kuksa-android-companion app (F-Droid). `vspec export vhal` (vss-tools 6.1) generates VHAL mapping, Java and AIDL. | prototype | repos/vss-tools/CHANGELOG.md; https://github.com/eclipse-kuksa |
| ROS 2 | yes (tooling) | `vspec export ros2interface` generates .msg/.srv from VSS (vss-tools 6.0+). Chapter 3 team A-kiki used VSS with ROS 2 and Zenoh. | prototype | repos/vss-tools/src/vss_tools/cli.py:61; repos/hc3-A-kiki |

## Chapter history
- Chapter 3 (2025): 1st place **ArBytesMoral** ran the databroker 0.6.0 under Ankaios, wrote an MQTT→KUKSA provider in Rust with kuksa-rust-sdk (main branch), and combined it with uProtocol/Zenoh (repos/hc3-ArBytesMoral/compute/). **A-kiki** used VSS names over Zenoh/WebSocket with ROS 2. The SDV Lab challenge listed "Kuksa (VSS)" as a technology (https://blogs.eclipse.org/post/christian-heissenberger/unveiling-2025-sdv-hackathon-challenges-ideas-impact-%E2%80%93-faster). See [[chapter3-retrospective]].
- Chapter 4 (2026): KUKSA is in the project list of the hackathon org README (repos/hackathon-ch4-dotgithub/profile/README.md:49). The challenges name uProtocol for events, so KUKSA is optional and serves as the signal-state layer. See [[chapter4-challenge-doctor-whodunit]] and [[chapter4-challenge-hack-to-the-future]].

## Suggested reference wiring for Chapter 4 teams
`sensor sim / CSV / CAN provider → KUKSA databroker (VSS state, v2) → guardian service (subscribes) → uProtocol event (fault / heartbeat / mitigation) → OpenSOVD (DTC + data) ; Ankaios runs all of it as workloads ; openDuT injects stuck or late signals in front of the databroker.`
Gap to fill: the KUKSA→uProtocol and VSS→SOVD adapters do not exist as reusable components.
