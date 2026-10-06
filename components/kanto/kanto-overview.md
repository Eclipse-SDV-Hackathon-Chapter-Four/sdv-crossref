---
title: Eclipse Kanto - overview, quickstart (inline)
type: overview
component: kanto
tags: [kanto, container-management, edge, hono, ditto, go, adjacent]
status: draft
sources:
  - https://github.com/eclipse-kanto/kanto
  - https://github.com/eclipse-kanto
  - https://projects.eclipse.org/projects/iot.kanto
  - https://eclipse.dev/kanto/docs/getting-started/install/
last-verified: 2026-10-03
related:
  - "[[kanto-integration-notes]]"
  - "[[ankaios-overview]]"
  - "[[velocitas-overview]]"
  - "[[sdv-blueprints-overview]]"
  - "[[sdv-landscape-overview]]"
---

# Eclipse Kanto

## What it is
Modular IoT/edge software stack written in Go: OCI container management on constrained devices, an MQTT "suite connector" to cloud IoT back ends (Eclipse Hono / Ditto, Bosch IoT Suite, plus Azure and AWS connectors), software update manager, file upload/backup, system metrics, local digital twins (Vorto-based). Apache-2.0 / EPL-2.0. Sources: https://github.com/eclipse-kanto/kanto, https://projects.eclipse.org/projects/iot.kanto, https://eclipse.dev/kanto/docs/.

## What it is NOT
- Not a multi-node orchestrator: one container-management daemon per device, no cluster scheduler (contrast [[ankaios-overview]]).
- Not a vehicle abstraction or signal layer (use [[vss-kuksa-overview]]).
- Not (any more) formally listed in the SDV WG project list: the Eclipse API for working_group=sdv returns CANought (`iot.kanto.canought`, CAN extensions for Kanto) but not Kanto itself (https://projects.eclipse.org/api/projects?working_group=sdv).

## Maturity and state (is it still maintained?)
- Eclipse state: Incubating (projects.eclipse.org/projects/iot.kanto).
- Releases: every component tagged v1.0.0 on 2024-06-10 (GitHub API). No release since.
- Code activity: container-management last commit 2024-06-28, suite-connector 2024-05-28, update-manager 2024-06-26; meta-kanto (Yocto layer) 2025-01-24; software-update 2025-02-16.
- The main `kanto` repo had commits on 2026-04-07, but they are documentation only (Yocto image for Raspberry Pi) (https://github.com/eclipse-kanto/kanto/commits/main). 27 stars, 27 open issues.
- Not archived on GitHub (only `suite-bootstrapping` is).
- Verdict: **maintenance mode / low activity**. Stable v1.0.0 code, docs still touched in 2026, but no feature or dependency work visible for ~2 years (Go deps will be stale; security bumps unverified). Treat as "works, do not expect fixes".

## Relation to Ankaios
Same niche (container workload manager for edge/vehicle computers), different design. Kanto: per-device daemon on containerd + cloud-first (Hono/Ditto, OTA via cloud). Ankaios: server/agent, declarative manifest, multi-node, vehicle-first, active (v1.0.2, daily commits; see [[ankaios-overview]]). No integration code found either way; they are alternatives, not layers. The Blueprint "software-orchestration" implements Ankaios and BlueChi, not Kanto (https://api.github.com/orgs/eclipse-sdv-blueprints/repos?per_page=100 ; https://raw.githubusercontent.com/eclipse-sdv-blueprints/software-orchestration/main/README.md).

## Where Kanto still appears in the SDV ecosystem
- **Eclipse Leda**: core SDV.EDGE stack uses Kanto for container management (Leda docs: Kanto Auto Deployer, sdv-kanto-ctl) https://eclipse-leda.github.io/leda/docs/general-usage/sdv-introduction/
- **Velocitas**: `runtime-kanto` and `deployment-kanto` components deploy the KUKSA databroker, MQTT broker and services as Kanto containers (Velocitas quickstart, template `.velocitas.json`) - see [[velocitas-overview]].
- **SDV Blueprints**: no Kanto mention in the READMEs of fleet-management, software-orchestration, e2e-vehicle-signals, carmate (grep, 2026-10-03). The Leda-based `companion-application` blueprint runs on Leda and therefore implicitly on Kanto (unverified). See [[sdv-blueprints-overview]].
- CANought: CAN translator + uProtocol C++ client/server (`eclipse-canought/up-cpp-*`), last push 2025-04-22.

## Quickstart (inline; docs-derived, NOT executed - needs sudo)
Prerequisites: Debian/Ubuntu-style host (x86_64 deb for v1.0.0; arm packages on the Releases page), sudo, internet.
```bash
curl -fsSL https://github.com/eclipse-kanto/kanto/raw/main/quickstart/install_ctrd.sh | sh      # containerd
wget https://github.com/eclipse-kanto/kanto/releases/download/v1.0.0/kanto_1.0.0_linux_x86_64.deb && \
  sudo apt install ./kanto_1.0.0_linux_x86_64.deb
systemctl status suite-connector.service container-management.service software-update.service \
  file-upload.service file-backup.service system-metrics.service kanto-update-manager.service
```
Expected per docs: all services "active (running)". Note `suite-connector` will loop/retry until provisioned for a cloud (Hono/Ditto) - for a purely local container demo only `container-management.service` matters (unverified). Then try `sudo kanto-cm --help` and `sudo kanto-cm list` (CLI name from docs/search results; exact subcommands unverified - read `--help`).
Yocto route: https://github.com/eclipse-kanto/meta-kanto and the Raspberry Pi doc added 2026-04.

## Pros / cons / when not to use
Pros: small Go footprint, containerd-based, cloud connectivity and OTA already there, Yocto layer, used by Leda and Velocitas runtime.
Cons: effectively dormant, single-node, cloud-centric defaults, little hackathon community, no uProtocol/Zenoh path.
Do not use when you need multi-node orchestration, safety-oriented lifecycle, or active upstream support: use [[ankaios-overview]].

## Pitfalls
- Version pin is v1.0.0 deb (June 2024); newer distros / containerd versions may misbehave (unverified).
- suite-connector needs cloud provisioning; the other six services start independently.
- Docs pages move (several deep links 404 on 2026-10-03: use the site navigation).

## Hackathon ideas
1. Kanto-to-Ankaios migration recipe: translate a Kanto container JSON to an Ankaios manifest (small script, high value for anyone moving off Kanto).
2. Wire Kanto suite-connector to a local Eclipse Ditto/Hono compose and expose the twin of a Velocitas app.
3. Update the CANought `up-cpp-server` to current uProtocol (see [[uprotocol-overview]]) and bridge CAN to Zenoh/uProtocol.
4. Fill the gap register: "who maintains Kanto?" - ask on kanto-dev list before building on it.
