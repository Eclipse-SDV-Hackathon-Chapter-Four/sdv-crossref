---
title: Eclipse SDV Working Group landscape - master project list
type: overview
component: sdv-landscape
tags: [landscape, master-list, capability-map, activity, dormant]
status: draft
sources:
  - https://projects.eclipse.org/api/projects?working_group=sdv
  - https://projects.eclipse.org/api/projects?working_group=sdv
  - https://eclipsesdv.org/projects/
last-verified: 2026-10-03
related:
  - "[[kanto-overview]]"
  - "[[velocitas-overview]]"
  - "[[autowrx-overview]]"
  - "[[sommr-overview]]"
  - "[[chariott-overview]]"
  - "[[sdv-blueprints-overview]]"
---

# Eclipse SDV WG - master project list (2026-10-03)

## Method and caveats
- Project list: `projects.eclipse.org/api/projects?working_group=sdv` (37 projects, all pages). https://eclipsesdv.org/projects/ (sdv.eclipse.org/projects redirects there) lists 35: it omits **Hephaestus** and **SDV Landscape**.
- Eclipse lifecycle state: every project is "Incubating" except Ankaios, BlueChi and iceoryx ("Regular"/mature). **No project in the WG list is marked archived** - but several are dormant.
- Activity: "last push" = latest push to any non-dotfile repo of the project's GitHub org (GitHub org repository pages, 2026-10-03) or GitLab last_activity for GitLab-hosted ones. Pushes include dependabot and website commits, so this overstates real development. `n/N` = repos pushed in last 90 days / repos.
- Levels: **High** = active repo pushed in the last 2 weeks and several repos in 90 days; **Medium** = pushed in the last 90 days, few repos; **Low** = last push 90 days to 12 months ago; **Dormant** = no push for more than 12 months; **Archived** = formally archived.
- Releases are the `latest_release_name` in the Eclipse API (often empty; GitHub tags may be newer).

## Master list
| Project (slug) | Purpose (one line) | Last push / n of N | Activity | Flags |
|---|---|---|---|---|
| Ambient Light Services | AUTOSAR-interface ambient-light showcase stack | 2023-12-13 (GitLab) | **Dormant** | dormant |
| Ankaios ([[ankaios-overview]]) | Workload/container orchestrator for automotive HPCs, server+agent, Rust; v1.0.2 | 2026-10-02, 5/5 | High | |
| ArchE | MBSE architecture modelling tool | 2025-11-24, 0/1 | Low | |
| Automotive API Framework | Decouple application logic from basic software stack | 2026-09-03, 2/3 | Medium | |
| AutoSD integration ([[autosd-overview]]) | Run/test SDV projects and blueprints on CentOS Automotive SIG/AutoSD | 2026-10-02, 1/2 | Medium | |
| autowrx ([[autowrx-overview]]) | digital.auto playground, browser prototyping on VSS | 2026-10-02, 3/18 (daily releases) | High | |
| BlueChi | Multi-node systemd service controller (C, D-Bus); v1.2.2 | 2026-08-25, 2/7 | Medium | |
| CANought | Kanto extension: CAN translator + uProtocol C++ client/server | 2025-04-22, 0/5 | **Dormant** | dormant |
| Chariott ([[chariott-overview]]) | Intent-brokering/service discovery middleware (Microsoft) | 2025-04-13, 0/3 | **Dormant** | not archived |
| SDV Developer Console (DCO) | Software lifecycle integration console | 2023-12-13 (GitLab) | **Dormant** | dormant |
| eCAL | High-performance pub/sub IPC middleware; v6.0.2; 1k stars | 2026-10-01, 4/21 | High | |
| Heimlig | HSM firmware in Rust | 2025-01-15, 0/1 | **Dormant** | dormant |
| Hephaestus | Contributor onboarding / tooling for SDV projects (fork of opensovd-core used as reference) | 2026-09-25, 2/2 | Medium | not on eclipsesdv.org list |
| Ibeji ([[chariott-overview]]) | In-vehicle digital twin (DTDL, Rust; Microsoft) | 2024-09-09 (examples; core 2024-07-15), 0/3 | **Dormant** | not archived |
| iceoryx ([[iceoryx2-overview]]) | Zero-copy shared-memory IPC; iceoryx2 is the active line | 2026-10-02, 4/9 | High | |
| KUKSA ([[vss-kuksa-overview]]) | Vehicle abstraction: VSS databroker, providers, clients; 0.6.1 | 2026-10-01, 12/19 | High | |
| Leda | Reference SDV distro (Yocto, Kanto, Velocitas, KUKSA); 0.1.0 | 2026-07-09, 1/11 | Medium | |
| Leda Incubator | Experimental Leda contributions (self-update agent, OTel, cloud connector repos) | within eclipse-leda org, unverified separately | Medium (unverified) | |
| LMOS | Multi-agent AI platform (non-vehicle core) | 2026-10-02, 5/13 | Medium | off-topic for SDV hackathons |
| Muto ([[muto-overview]]) | Dynamic, model-driven ROS stack composition | 2026-09-08, 2/15 | Medium | |
| Open Vehicle API | Vehicle abstraction interface for signal/event functions | 2026-08-18 (core 2026-08-13), 2/4 | Medium | |
| OpenBSW ([[openbsw-overview]]) | Embedded basic software stack for MCUs (C++) | 2026-10-02, 1/4 | High | |
| openDuT ([[opendut-overview]]) | Automated test/validation of automotive software, HIL bench orchestration | 2026-09-25 (opendut 2026-09-21), 3/6 | Medium | |
| OpenSOVD ([[opensovd-overview]]) | Service-Oriented Vehicle Diagnostics (ISO 17978) | 2026-10-03, 9/13 | High | |
| OpenXilEnv | Lightweight SIL/HIL environment | 2026-10-01, 1/2 | Medium | |
| p3com | Pluggable portable pub/sub API | 2023-05-19, 0/1 | **Dormant** | dormant |
| Pullpiri | K8s-model orchestrator for vehicles (Rust) | 2026-09-28, 3/3 | Medium | |
| S-CORE ([[s-core-overview]]) | Safe Open Vehicle Core stack for HPCs | 2026-10-03, 29/29 | High | |
| SDV Blueprints ([[sdv-blueprints-overview]]) | Reference end-to-end implementations | 2026-09-24, 5/11 | Medium | |
| SDV Landscape | Visual catalogue of SDV projects at Eclipse | 2026-07-27, 1/4 | Low | meta (documents this list) |
| SDV-LVL | Terminology/taxonomy of SDV capability levels | 2025-06-13, 0/1 | **Dormant** | docs-only |
| Symphony ([[symphony-overview]]) | End-to-end workload orchestration across cloud/edge | 2026-09-30, 1/3 | Medium | |
| ThreadX ([[threadx-overview]]) | Certified RTOS; v6.4.2 | 2026-10-02, 11/14 | High | |
| TSF | Trustable Software Framework (risk/evidence method) | 2026-09-29 (GitLab) | Medium | |
| uProtocol ([[uprotocol-overview]]) | Transport-agnostic layered messaging (Rust/C++/Java/Python) | 2026-10-01, 28/29 | High | |
| Velocitas ([[velocitas-overview]]) | Vehicle app SDK, templates, devcontainer toolchain | 2026-09-21 (Java SDK; Python SDK 2025-07-03), 1/20 | Low | maintenance mode |
| Zenoh ([[zenoh-overview]]) | Pub/sub/query/storage protocol; 1.9.0 | 2026-10-02, 23/28 | High | |

Not in the WG list but relevant:
| Project | Purpose | State |
|---|---|---|
| Eclipse Kanto ([[kanto-overview]]) | Edge container management + cloud connect (Hono/Ditto), Go | Incubating; v1.0.0 2024-06; code frozen since mid-2024, docs touched 2026-04; **Low/Dormant** |
| Eclipse SommR ([[sommr-overview]]) | SOME/IP in Rust | **Archived** (Eclipse + GitHub), repo empty |

## Flags summary
- **Formally archived** (in/near WG): SommR (not in WG list anymore). In Eclipse GitHub orgs only minor repos are archived (Velocitas devenv-runtime-local/k3d, Kanto suite-bootstrapping).
- **Dormant (>12 months, not archived)**: Ambient Light Services, CANought, Chariott, DCO, Heimlig, Ibeji (+Freyja/Agemo), p3com, SDV-LVL. Treat as unmaintained.
- **Low/maintenance**: Velocitas, ArchE, SDV Landscape, Kanto.
- **Core hackathon set, all High**: S-CORE, OpenSOVD, uProtocol, Zenoh, iceoryx2, KUKSA, Ankaios, OpenBSW, ThreadX; openDuT and AutoSD Medium.

## Capability-map grouping (input for synthesis/capability-map.md)
- Orchestration/lifecycle: Ankaios, BlueChi, Pullpiri, Symphony, Kanto (low), Muto (ROS).
- Communication/middleware: Zenoh, uProtocol, iceoryx(2), eCAL, p3com (dormant), Open Vehicle API, SommR (archived).
- Vehicle abstraction/data: KUKSA/VSS, Ibeji/Chariott (dormant), Automotive API Framework.
- Dev toolchain/prototyping: Velocitas, autowrx, Hephaestus, DCO (dormant), Leda.
- Base software/safety: S-CORE, OpenBSW, ThreadX, Heimlig (dormant), AutoSD.
- Diagnostics/test: OpenSOVD, openDuT, OpenXilEnv.
- Reference/process: Blueprints, SDV-LVL, TSF, ArchE, SDV Landscape.

## Pros / cons of using this list
It is the full Eclipse list, so it includes docs-only and showcase projects; activity levels are a proxy. Verify a project's real maintainers before building a team plan on it.

## Integration with the core set
See each component's `*-integration-notes`; for the dormant ones the answer is "none found" almost everywhere, which is itself a landscape finding. Also an ecosystem-wide gap: nothing integrates iceoryx2 with Kanto, Velocitas or the Chariott family.

## Hackathon ideas
1. Auto-generate this table nightly (GitHub org + GitLab API script in `scripts/`) so the capability map stays honest.
2. Bridges between active projects and dormant-but-useful designs (CANought CAN translator to uProtocol; Ibeji DTDL to VSS).
3. Add the missing "Kanto vs Ankaios vs BlueChi vs Pullpiri" decision matrix to the playbook.
