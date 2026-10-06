---
title: AutoSD — Integration notes
type: reference
component: autosd
tags: [autosd, centos-automotive-sig, rhivos, aib, bootc, quadlet, qm]
status: draft
sources:
  - https://sigs.centos.org/automotive/
  - https://gitlab.com/CentOS/automotive/sample-images
  - https://gitlab.com/CentOS/automotive/src/automotive-image-builder
  - repos/automotive-image-builder/README.md
  - repos/sample-images/images/
  - repos/eclipse-autosd/README.md
  - repos/hackfest-eclipse-score_reference_integration/images/autosd_x86_64/build/README.md
  - https://sigs.centos.org/automotive/autosd-10/getting-started/quick-start-guide.html
  - https://sig.centos.org/automotive/latest/building/autosd_pi4.html
  - https://sig.centos.org/automotive/latest/features-and-concepts/con_mixed-criticality.html
  - https://projects.eclipse.org/node/33726
last-verified: 2026-10-03
related:
  - "[[autosd-overview]]"
  - "[[autosd-quickstart]]"
  - "[[autosd-howto]]"
  - "[[autosd-reference]]"
  - "[[autosd-integration-notes]]"
  - "[[ankaios-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[s-core-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# AutoSD — Integration notes

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| S-CORE (communication/LoLa, baselibs) | yes | Communication packaged as RPMs in COPR `pingou/score-playground`; image has root+QM partitions, shared `/dev/shm` volume via quadlet drop-in; Bazel `rules_aib` builds AutoSD images from S-CORE | demo | repos/hackfest-eclipse-score_reference_integration/images/autosd_x86_64/build/README.md; repos/inc_os_autosd/README.aib.md |
| Eclipse SDV blueprints (service-to-signal) | planned | Eclipse "Automotive Integration for AutoSD" project: base bootc image, per-blueprint branches; blueprint itself documents docker compose only | idea / prototype | https://projects.eclipse.org/node/33726; repos/eclipse-sdv-autosd/README.md; https://sdv-blueprints.eclipse.dev/docs/service-to-signal |
| Ankaios | partial | COPR RPM spec exists (pingou/ankaios), no end-to-end AutoSD demo found; Ankaios does not ship in eclipse-autosd images; Podman runtime is the Ankaios default and is native on AutoSD | idea | https://download.copr.fedorainfracloud.org/results/pingou/ankaios/srpm-builds/10256969/ankaios.spec ; repos/ankaios/doc/docs/usage/installation.md ; [[ankaios-integration-notes]] |
| KUKSA / VSS | none found (container route works in principle) | would run as quadlet container | none | no AutoSD reference found in repos/ or web search |
| uProtocol / Zenoh | none found directly | service-to-signal uses uProtocol over Zenoh in containers; runs on AutoSD only via the generic container path | idea | https://sdv-blueprints.eclipse.dev/docs/service-to-signal |
| BlueChi (CentOS Automotive SIG) | yes | systemd service orchestration across root/QM, in `eclipse-autosd` base image | demo | repos/eclipse-autosd/aib/image.aib.yml |
| vsomeip (COVESA) | yes | sample apps radio/engine as quadlets sharing `/run/vsomeip` | demo | repos/sample-images/images/container.aib.yml |
| iceoryx2 | none found | shared-memory IPC across QM would need volume mounts like LoLa's `/dev/shm`; not tested | idea | S-CORE LoLa pattern only |
| OpenSOVD | none found | | none | |
| openDuT | none found | | none | |
| OpenBSW | none found | | none | |
| Eclipse Velocitas / Kanto / Muto / Symphony / ThreadX | none found | | none | |

## Core-project notes
- **Ankaios**: biggest practical fit (container orchestrator + podman). Gap: no documented AutoSD recipe; Ankaios would sit next to systemd/quadlet/BlueChi, so decide who owns lifecycle (avoid two supervisors restarting the same container). See [[ankaios-overview]].
- **KUKSA/uProtocol/Zenoh**: ship as OCI images; embed with `container_images` to avoid registry dependency. Ports and sockets across QM need explicit volume/PublishPort config. See [[vss-kuksa-overview]], [[uprotocol-overview]], [[zenoh-overview]].
- **S-CORE**: strongest evidence; note `selinux_mode: permissive` in the demo, i.e. SELinux policy for LoLa is not yet written. See [[s-core-overview]].
- **iceoryx2**: shared-memory transport crossing the root/QM boundary is the interesting open question ([[iceoryx2-overview]]).
- **OpenSOVD, openDuT, OpenBSW**: nothing found; openDuT could use AutoSD VM as a device under test (idea, [[opendut-overview]]).
