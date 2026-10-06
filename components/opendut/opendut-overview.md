---
title: Eclipse openDuT - overview
type: overview
component: opendut
tags: [opendut, test-infrastructure, vpn, can, ethernet, hil, sil]
status: draft
sources:
  - repos/opendut/README.md
  - repos/opendut/CHANGELOG.md
  - repos/opendut/doc/src/architecture/network/index.md
  - repos/opendut/doc/src/architecture/carl/index.md
  - repos/opendut-playground/result-overview.md
  - https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
  - https://opendut.eclipse.dev/
last-verified: 2026-10-03
related:
  - "[[opendut-quickstart]]"
  - "[[opendut-howto]]"
  - "[[opendut-reference]]"
  - "[[opendut-integration-notes]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[hackfest-esslingen-2026]]"
  - "[[chapter3-retrospective]]"
---

# Eclipse openDuT - overview

Repo: https://github.com/eclipse-opendut/opendut, docs: https://opendut.eclipse.dev/ (book at /book/). Looked at commit a2447d8 (2026-07-17), see [[opendut-reference]].

## What it is
"Test Electronic Control Units around the world in a transparent network" (repos/opendut/README.md). A framework to run automotive tests in a "reliable, repeatable and observable way" over a distributed network of real (HIL) and virtual (SIL) devices under test (DuT). Apache-2.0, Rust workspace, Eclipse Automotive project, EU-funded.

Mental model: **a remote wire**. A DuT (ECU, Pi, container) is plugged into a small edge machine; openDuT makes DuTs on different edge machines appear to sit on the same Ethernet segment / CAN bus, over the internet, without changing the DuT.

## Components (all in the repo workspace)
| Name | Role | Evidence |
|---|---|---|
| CARL | Backend server: stores peers/devices/clusters, gRPC API, serves LEA, hands configuration to EDGARs | doc/src/architecture/carl/index.md, doc/src/development/carl-grpc-api.md |
| EDGAR | Agent on the edge host (x86_64, armv7 Pi, aarch64). Fetches config from CARL, sets up NetBird client, GRE tunnel + bridge `br-opendut` (Ethernet), Cannelloni + `br-vcan-opendut` (CAN), runs container "executors" | doc/src/user-manual/edgar/*, architecture/network |
| LEA | Web UI (Rust/Leptos, OIDC login) | opendut-lea/Cargo.toml |
| CLEO | CLI `opendut-cleo`: create/list/describe/delete, `apply` YAML descriptors, generate setup string | doc/src/user-manual/cleo/commands.md |
| THEO | Dev/test-env tool (`cargo theo`), Vagrant VM or plain Docker | doc/src/development/testenv/index.md |
| VIPER | Embedded Python-flavoured test-suite runtime (opendut-viper); CARL analyses, EDGAR runs suites | doc/src/architecture/viper/index.md |
| NetBird + Keycloak + Traefik + Postgres + Grafana/Loki/Prometheus/Alloy | Third-party stack run by docker compose ("localenv") | .ci/deploy/localenv/docker-compose.yml |

Concepts: **Peer** (an EDGAR host, with network interfaces), **Device** (a DuT attached to a peer interface), **Cluster** (set of devices + a leader peer; "deploy" activates the network), **Executor** (container run on a peer when cluster is deployed, results zipped and PUT to WebDAV via `/results/` + `.results_ready`). Source: user-manual/test-execution.md, cleo/commands.md.

## Transport
- Ethernet: GRE tunnels (VLAN capable) inside WireGuard (NetBird); WG MTU raised to 1542; fragmentation possible if DuT sends full 1500 MTU. (architecture/network/index.md)
- CAN: Cannelloni between EDGARs, local bridge to physical or `vcan` interfaces; needs kernel modules `vcan`, `can_gw` (max_hops=2) and root service user. (user-manual/edgar/setup.md, edgar/docker.md)
- Control: gRPC (CARL), OIDC (Keycloak), OpenTelemetry to monitoring stack.

## Version / maturity
- Latest release in CHANGELOG: **v0.10.2 (2026-06-11)**; repo main workspace is `0.11.0-alpha`. v0.10.1 (2026-06-03) was largely fixes from HackFest Esslingen (CAN, LEA). Pre-1.0: "do not skip versions when upgrading CARL" (CHANGELOG.md).
- (A WebFetch of the GitHub releases page printed 2024 dates; ignored as contradicting CHANGELOG.)

## What it is NOT
- Not a fault-injection tool. grep of docs/code finds no netem/fault-injection/replay feature (only VIPER test runtime). Fault campaigns must be built on top (see [[opendut-howto]]).
- Not a simulator, not a signal/data broker, not a CI runner, not a CAN-trace recorder/replayer (candump/canplayer are separate tools).
- Not lightweight: a self-hosted backend is ~12+ containers.

## Use at HackFest Esslingen 2026 ([[hackfest-esslingen-2026]])
Source: https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/openDuT-playground and blog above.
- Organisers prepared Raspberry Pis with EDGAR plus a shared openDuT backend. Challenges: (1) remote ECU connection for CDA to cars, (2) virtual CDA split in two halves joined via openDuT (Docker EDGARs), (3) set up Pi edge devices.
- Results: CDA connected to a car through openDuT, mirrors folded from inside (videos on the playground release `video`). Keep-car-alive script failed. EDGAR lost NetBird session (also in local container setup; re-setup fixes; suspected relation to NetBird process inlining). RC car controlled via cansend; EDGAR installed natively on S-CORE image (needed `vcan`; works without systemd). CAN support was broken (PR #494, issue #518, fixed in v0.10.1/0.10.2). Testenv dev mode broken (PR #493). Pi misconfig (issue #495 related). rpi-imager AppImage not found by `raspberry-pi-wireless-bootstrap`.
- Team ideas: PIN-based device access per cluster (unfinished), dark theme in LEA. Gap found: `cleo apply` accepts leader not in cluster (issue #495 per playground file).

## Chapter 3 (2025)
openDuT's role there is unverified by me. Note: "Doctor Whodunit" appears to be a **Chapter 4** (Oct 2026) challenge, not Chapter 3; see [[chapter4-challenge-doctor-whodunit]] and [[chapter3-retrospective]].

## Pros / cons
Pros: transparent L2 (and CAN) connectivity across NAT; works with Pis; real-car proof at HackFest; web UI + CLI + YAML; hardware-agnostic; container executors with result upload; active (fixes within weeks of HackFest).
Cons: heavy stack (NetBird, Keycloak, Postgres, Traefik, OTel), hostnames/certs/DNS (`*.opendut.local`) and OIDC are mandatory; kernel-module and root requirements for CAN; NetBird session loss; pre-1.0 with breaking migrations; docs gaps acknowledged at HackFest; no built-in fault injection or time-deterministic replay.

## When NOT to use in a 2-day hackathon
- All components run on one laptop and you only need local traffic (use vcan/docker network/`tc netem` directly).
- Team has no Linux host with root and kernel modules (macOS/Windows laptops: only via VM).
- You lack ~1h of time budget and someone who has set it up before; use the shared backend if the organisers offer one (as at HackFest).
- You need hard real-time or timestamp-accurate replay (WireGuard/GRE/Cannelloni add latency/jitter, no timing guarantees documented).

## Hackathon ideas
1. Fault-injection executor: container image run via openDuT executor that wraps `tc netem` / `canplayer` / `cangen` / `can-utils` on the bridge interfaces to drop, delay, duplicate frames, driven by a YAML "campaign" and results uploaded to WebDAV (fits [[chapter4-challenge-doctor-whodunit]]).
2. Validate leader-in-cluster in CARL (known gap, `create_cluster_descriptor.rs`) (tracked as openDuT issue #495, labelled good-first-issue, see [[hackfest-esslingen-2026]]), good first contribution.
3. PIN/ownership for devices in LEA (unfinished HackFest idea); dark theme.
4. EDGAR health: detect lost NetBird session and auto re-register.
5. Docs: EDGAR on S-CORE image / without systemd; CAN kernel-module checklist.
6. Bridge openDuT cluster CAN to KUKSA via a CAN feeder (idea; no evidence of existing integration), see [[opendut-integration-notes]].
