---
title: HackFest repo - openDuT-playground (remote ECU access, virtual CDA, results)
type: event
component: opendut
tags: [event, hackfest, opendut, edgar, cleo, netbird, can, cda, raspberry-pi]
status: draft
sources:
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/openDuT-playground
  - repos/hackfest-openDuT-playground/README.md
  - repos/hackfest-openDuT-playground/result-overview.md
  - repos/hackfest-openDuT-playground/opendut_authupdate.md
  - repos/hackfest-openDuT-playground/cleo-apply-fix-leader-in-cluster-not-checked.md
  - https://github.com/eclipse-opendut/opendut/issues/495
last-verified: 2026-10-03
related:
  - "[[hackfest-esslingen-2026]]"
  - "[[opendut-overview]]"
  - "[[opensovd-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
---

# openDuT-playground (HackFest Esslingen 2026, track "Seamless connection with openDuT")

Repo: https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/openDuT-playground. Local clone `repos/hackfest-openDuT-playground` @ 421c257 (2026-04-30, Frank Märkle, "Add result overview"). Docs only, no code. Context: [[hackfest-esslingen-2026]]; component background: [[opendut-overview]].

## Setup provided at the event (README.md)
- Raspberry Pis preinstalled with the openDuT edge software (**EDGAR**) plus a hosted openDuT backend (**CARL**). Access via the web UI or **CLEO** (CLI).
- **Challenge 1, remote ECU connection** (`assets/overview-challenge-a.png`): `PC --Ethernet--> RPi1 (EDGAR) ==openDuT over WiFi==> RPi2 (EDGAR) --Ethernet--> Car`. Goal: other teams test against the cars without going outside. Bonus: one Pi inside and dynamically re-cluster to different cars.
- **Challenge 2, virtual CDA over openDuT** (`assets/overview-challenge-b.png`): `PC1 CDA -> EDGAR ==openDuT over WiFi or relay==> EDGAR -> PC2 ECU-Sim`, splitting the CDA's `testcontainer/docker-compose.yml` (https://github.com/eclipse-opensovd/classic-diagnostic-adapter/blob/main/testcontainer/docker-compose.yml). Goal 1: via RPis; Goal 2: EDGAR in Docker on the PCs. Use the provided router, because the guest WiFi likely blocks PC-to-PC traffic; bonus: relay across different networks.
- **Challenge 3**: set up new edge devices (Raspberry Pi Imager -> boot -> create peer in CARL -> "User Manual -> EDGAR -> Setup").

## Results (result-overview.md, verbatim points condensed)
| Result | Detail / evidence |
|---|---|
| CDA -> car via openDuT works | "Were able to fold mirrors from inside." Videos: https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/openDuT-playground/releases/tag/video (3 mp4 files, 29 Apr 15:00) |
| Pis initially misconfigured | "Avoidable user error", linked to issue #495 |
| Keeping the car awake by script | "did not work" |
| EDGAR lost connection (NetBird) | Happened both with the CDA and in a local container setup; re-setup of EDGAR fixes it; "Might be due to recent inlining of NetBird process" |
| RC car | Controlled via `cansend` locally; S-CORE image connected to the internet; **Docker could not be set up on the S-CORE image**; EDGAR installed natively on the S-CORE image, which needs the `vcan` kernel module and runs without systemd ("should improve documentation") |
| Pi flashing tool | `raspberry-pi-wireless-bootstrap` could not find the rpi-imager AppImage in PATH |
| EDGAR CAN support broken | Fixed in PR #494 (merged 2026-04-29: `ip link` parameter order); open: "CAN Sample Point read via `ip link show` does not necessarily match what we set -> Can put us into infinite loop" |
| UI / auth | THEO dev mode was broken, fixed in PR #493 (merged 2026-04-29). PIN-per-device auth concept and a dark theme (`opendut_authupdate.md`, Abhishek Vijay Potekar & Raihan Soniwala); not finished |
| CLEO bug | `opendut-cleo apply` accepts a leader peer that is not in the cluster. Issue **#495, open, good-first-issue** (2026-10-03); fix in `opendut-carl/src/manager/cluster_manager/create_cluster_descriptor.rs` with `CreateClusterDescriptorError::LeaderNotInCluster`; guide in `cleo-apply-fix-leader-in-cluster-not-checked.md` |

Note: the "S-CORE image" in these results is most likely the EB corbos Linux RPi image from the S-CORE track (inference: EB's re-release `2.0.0-beta-hackfest-2` on 28 Apr added `docker.io`, `containerd` and `can-utils`; see https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eb_corbos_toolkit-hackfest/releases).

## Reusable for Chapter 4
- [[chapter4-challenge-doctor-whodunit]] asks openDuT to "replay repeatable fault campaigns" including "device-level sensor dropout". Challenge 2 above (CDA <-> ECU-sim split across an openDuT link) is the closest published precedent for putting a network/device fault between a diagnostic tester and an ECU.
- #495 is a ready, guided first PR for a Track 2 team.
- Tip: budget for NetBird re-setup and CAN bitrate pitfalls; prefer `vcan` for demos; bring a router that allows peer-to-peer traffic.

## Gaps / ideas
- Document EDGAR on non-systemd, minimal targets (S-CORE/EB images), including the `vcan` requirement.
- Make the CAN sample-point check tolerant (avoid the infinite loop).
- A keep-alive/TesterPresent helper for real cars over openDuT (the script attempt failed).
- Finish the PIN-auth concept in CARL/LEA.
