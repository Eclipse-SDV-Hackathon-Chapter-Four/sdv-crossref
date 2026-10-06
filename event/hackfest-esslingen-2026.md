---
title: SDV HackFest Esslingen 2026 - what was integrated, what broke, what to reuse
type: event
component: none
tags: [event, hackfest, esslingen, s-core, opensovd, openbsw, opendut, eb-corbos-linux, raspberry-pi, cda, doip, integration-gaps]
status: draft
sources:
  - https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
  - https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/hackfest-docs/blob/main/2026-04-Hackfest-Welcome.pptx.pdf
  - https://github.com/eclipse-opensovd/opensovd/discussions/103
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eb_corbos_toolkit-hackfest/releases
  - https://github.com/eclipse-opendut/opendut/issues/495
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026
  - repos/hackfest-hackfest-docs/2026-04-Hackfest-Welcome.pptx.pdf
  - repos/hackfest-eclipse-score_reference_integration
  - repos/hackfest-eclipse-score_inc_diagnostics
  - repos/hackfest-OpenBSW-Playground
  - repos/hackfest-openDuT-playground
  - repos/hackfest-eb_corbos_toolkit-hackfest
last-verified: 2026-10-03
related:
  - "[[s-core-overview]]"
  - "[[opensovd-overview]]"
  - "[[openbsw-overview]]"
  - "[[opendut-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[chapter4-overview]]"
  - "[[hackfest-score-reference-integration]]"
  - "[[hackfest-score-inc-diagnostics]]"
  - "[[hackfest-openbsw-playground]]"
  - "[[hackfest-opendut-playground]]"
---

# SDV HackFest Esslingen 2026 (28-29 April 2026)

The most recent hands-on event where S-CORE, OpenSOVD, OpenBSW and openDuT were wired together, with real vehicles in the room. Use this note as the evidence base when a Chapter 4 team asks "has anyone made X talk to Y yet?" Repo-level detail is in four sub-notes:
[[hackfest-score-reference-integration]], [[hackfest-score-inc-diagnostics]], [[hackfest-openbsw-playground]], [[hackfest-opendut-playground]].

## TL;DR
1. **Most reusable result: the OpenBSW virtual ECU + OpenSOVD CDA + Grafana demo.** It is public, documented and has a test suite: `repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/`. It is the best starting point for any "diagnose an OpenBSW ECU via SOVD" idea, including [[chapter4-challenge-hack-to-the-future]]. An unmerged branch already contains a Back-to-the-Future-themed **FLXC1000 "Flux Capacitor" ECU**, see [[hackfest-openbsw-playground]].
2. **"S-CORE + OpenSOVD on EB corbos Linux on a Raspberry Pi" was mainly a build integration.** At the HackFest, the OpenSOVD Classic Diagnostic Adapter (CDA, Rust/Cargo) was made to build inside S-CORE's Bazel `reference_integration` through an "adapter module" (`inc_diagnostics`) and cross-compiled for an EB corbos Linux for Safety Applications (EBcLfSA) RPi 4B image. **No public code shows OpenSOVD talking to S-CORE middleware (mw::com/LoLa) over IPC.** At the 20 May workshop the IPC path was still "under discussion" (sources below).
3. **The HackFest Bazel recipe has been superseded.** The HackFest S-CORE branches are a snapshot: the toolchain URL on the org's `hackfest` branch is now 404, and three diverging `inc_diagnostics` branches use two different module names. Since then upstream moved on: `eclipse-score/inc_diagnostics` branch `gateway_cda_int` (Sep 2026) builds `opensovd-cda`, `opensovd-gateway` and a `sovd-client` with Bazel against a CDA that ships its own `MODULE.bazel`. A Chapter 4 team should start there, not from the HackFest branches.
4. **The CDA talks to real cars**: "worked in principle" with Mercedes-Benz, BMW and Porsche, with full functionality on the Mercedes. The open issue is the diagnostic descriptions (ODX/MDD) per vehicle, not the transport.
5. **openDuT delivered remote ECU access.** A CDA folded a real car's mirrors through EDGAR on Raspberry Pis. It also exposed real friction: NetBird session loss, broken CAN setup (fixed in PR #494), vcan missing in the S-CORE image, and Docker missing in the EB image. Frank Märkle wrote the openDuT result overview; relevant to [[chapter4-challenge-doctor-whodunit]].

## Event facts
| Item | Value | Source |
|---|---|---|
| Dates / place | 28-29 Apr 2026, Esslingen University (HS Esslingen), Campus Stadtmitte; talks in CAST lab, hacking in "Alte Mensa" | https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/hackfest-docs/blob/main/2026-04-Hackfest-Welcome.pptx.pdf |
| Participants | about 50 from industry, academia and the SDV community | https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/ |
| Format | **Not a hackathon**: no competing teams, predefined challenges, judging or winners. "Hacking interfaces together. Getting things to run together. Iterating on integration rather than running polished challenges." | blog; slides p.7 |
| Organisers | Christian Heissenberger (Eclipse Foundation), Prof. Johannes Baumgartl, Prof. Dennis Grewe | slides p.2 |
| Talks (day 1) | OpenSOVD (Thilo & Christoph), OpenBSW (Tom), S-CORE (Arvid), openDuT (Michael) | slides p.18 |
| Hardware | Mercedes-Benz (CLA in the slide diagram), BMW (iX3), Porsche; 1:10 RC car and a "robodog"; Raspberry Pi 4B with an MCP2515 CAN shield running EB corbos Linux; openDuT RPis running EDGAR | slides p.19-20; EB release notes |
| Supporters | VdF Alumni + Friends Esslingen e.V., ETAS GmbH | blog |
| Public code | GitHub org `Eclipse-SDV-HackFest-Esslingen-2026`, 6 repos (table at the end) | https://github.com/Eclipse-SDV-HackFest-Esslingen-2026 |

## The shared target architecture (slide 19, "prepared 4 Hackfest")
Transcribed from the welcome deck (repos/hackfest-hackfest-docs/2026-04-Hackfest-Welcome.pptx.pdf p.19). It shows the **intended** wiring. Components marked *prep* were prepared before the event; the rest was the goal.

```
 Diagnostic Client (Tester): SOVD Client
        | <<SOVD>> (discovery via mDNS)                 \ alternative: direct <<SOVD>>
        v                                                v
 +-------------------- Eclipse S-CORE ------------------+     +-- VCI (SOVD Bridge) --+
 | OpenSOVD Gateway Server [prep] --<<SOVD>>------------+---->| SOVD Server           |--<<UDS(DoIP)>>--> Porsche: Diagnostics Server [prep]
 |   |-> OEM Diagnostics Plug-In ---------------------------------------------------------> MB CLA: Diagnostics Server [prep]
 |   |-> OpenSOVD Defect Detection ..> openDuT [prep]                                         (MB CLA ..> openDuT)
 |   '-> OpenSOVD CDA [prep] --<<UDS>>--> Eclipse OpenBSW: UDS Server [prep]
 |                           --<<UDS>>--> BMW iX3: UDS Server [prep]
 +-----------------------------------------------------+   openDuT [prep] --> OpenBSW UDS Server
 Build Tool Chain [prep]
```
What the public repos show was actually built: the **CDA -> OpenBSW UDS server** edge (fully, virtual), **CDA -> real vehicles** (in principle, via openDuT for at least one car), and **CDA built inside S-CORE's Bazel** (build and cross-compile). The **OpenSOVD Gateway Server**, **Defect Detection** (the Fault Library) and **OEM plug-in** boxes have no public HackFest code. The Gateway shows up only later, in `inc_diagnostics@gateway_cda_int` (Sep 2026).

## The four tracks and what each achieved
The slide's four work packages (p.20) map onto the blog's four result sections.

| # | Work package (slide 20) / lead | Blog section | What was achieved (evidence) | Public code | Maturity |
|---|---|---|---|---|---|
| 1 | "Demonstrate that OpenSOVD (CDA) works with OpenBSW" - Tom (Fleischmann, Accenture) | OpenBSW x OpenSOVD | OpenBSW POSIX/FreeRTOS virtual ECU with 5 simulated DTCs and 3 simulated sensor DIDs, served over DoIP; real OpenSOVD CDA (Rust) plus a Python stub CDA; Grafana dashboard; Swagger UI; 4-tier pytest suite; requirements traceability in Sphinx-needs. Two DoIP interop bugs were found and fixed or worked around. | repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/ -> [[hackfest-openbsw-playground]] | **demo** (runs locally / Codespaces) |
| 2 | "S-CORE integration - build openSOVD artefacts" - Oliver (Pajonk, EB) | OpenSOVD x S-CORE | CDA built with Bazel as an S-CORE module (`score_diagnostics` / `score_inc_diagnostics`), added to `known_good.json` and cross-compiled with an EBcLfSA RPi 4B toolchain (`--config=eb-aarch64-rpi4b`). The blog reports an end-to-end demo of "S-CORE with OpenSOVD on top of EB corbos Linux using a Raspberry Pi", web UIs and an AI chat/MCP server for diagnostics. | repos/hackfest-eclipse-score_inc_diagnostics (branches `HackFest_concept`, `hackfest`, `hackfest-opajonk`), repos/hackfest-eclipse-score_reference_integration (branch `hackfest`) -> [[hackfest-score-inc-diagnostics]], [[hackfest-score-reference-integration]]. **UI and MCP code not public** ("planned to be made available upstream") | build **prototype**; runtime demo **unverified** (no public run recipe) |
| 3 | "Deploy & Build on 1:10 vehicle or robodog" - Niklas & Simon | (inside OpenSOVD x S-CORE) | "a prototype in which vehicle functions were controlled using S-CORE as middleware and made diagnosable through OpenSOVD ... an academic 1:10 RC car mock-up". The openDuT notes add: the RC car was driven by `cansend` locally, the S-CORE image was put on the internet, and EDGAR was installed natively on it. | **None public** (no repo in the org) | demo (per blog), **unverified** |
| 4 | "Seamless connection with openDuT" - Michael | openDuT | CDA reached a real car through two EDGAR RPis and folded its mirrors (videos published). Also: virtual-CDA-over-openDuT challenge, a PIN-auth/dark-mode UI concept, two upstream PRs merged (#493, #494), one issue opened (#495). | repos/hackfest-openDuT-playground -> [[hackfest-opendut-playground]] | demo (real car), concept (UI) |
| - | "DEPLOY & TEST" on vehicles: BMW - Anton/Andrey; Mercedes - Jörg & Michael; Porsche - Christoph | OpenSOVD x real vehicles | CDA "worked in principle with all available vehicles"; full functionality on the Mercedes-Benz; BMW/Porsche limited by diagnostic descriptions. At the Ulm workshop: "BMW and Porsche interaction addressed at HackFest; configuration features in pipeline". | none (OEM diagnostic data is not public) | demo (MB), partial (BMW, Porsche) |

Related pre-HackFest branch: `eclipse-score/reference_integration@ankr_poc_integrate_opensovd` (Anton Krivoborodov, BMW, 2026-04-22). It added a `score_opensovd_cda` module from a personal fork (`antonkri/opensovd-core`) and packed `opensovd-cda` into the `linux_x86_64` OCI image (repos/hackfest-eclipse-score_reference_integration, ref `upstream/ankr_poc_integrate_opensovd`, commit 4e07a46). It shows a second, independent attempt to get the CDA into an S-CORE image.

## Exact architecture of the S-CORE + OpenSOVD demo (as far as public evidence goes)
The precise picture, with each claim labelled verified (in code), reported (blog/notes) or unverified.

| Layer | What | Status / evidence |
|---|---|---|
| Hardware | Raspberry Pi 4B with an MCP2515 CAN shield (`dtoverlay=mcp2515-can0,...`) | verified: EB release notes, https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eb_corbos_toolkit-hackfest/releases |
| OS | **EB corbos Linux for Safety Applications (EBcLfSA), "fast-dev" Ubuntu-based image** `fastdev-ubuntu-ebclfsa-rpi4b.tar.gz` (.wic to flash). Release `2.0.0-beta-hackfest` (13 Apr) and `-2` (28 Apr, added `can-utils`, `containerd`, `docker.io`, plus SDK `pkg-config`) | verified: release page |
| OS model | HI (high-integrity) apps must be statically linked, carry an ELF-header checksum (`lisa-elf-enabler`) and be started by the HI init `cflinit`; `crinit` brings up the low-integrity (LI) Linux userland (ssh, gdbserver). Forbidden syscalls are logged (e.g. `clone3`, `madvise`, `ioctl`) | verified for the QEMU fast-dev image: repos/hackfest-eclipse-score_reference_integration/images/ebclfsa_aarch64/README.md. Whether the CDA ran as HI or LI on the Pi is **unverified**; LI is far more likely, because the CDA is tokio/async std Rust and would trip the syscall rules |
| Toolchain | Bazel config `eb-aarch64-rpi4b`: GCC 13 aarch64 sysroot from the EB SDK (`gcc.sdp(... score_ebclfsa_toolchain_raspi_pkg)`), Ferrocene aarch64 Rust toolchain, platform `aarch64-linux-sdk_0.1.0-ebclfsa`; link flags `-static -static-libstdc++ -static-libgcc` | verified: `git -C repos/hackfest-eclipse-score_reference_integration show origin/hackfest:.bazelrc` and `:bazel_common/score_gcc_toolchains.MODULE.bazel` |
| OpenSOVD component | **Classic Diagnostic Adapter only** (`@classic_diagnostic_adapter//cda-main:opensovd_cda`, aliased as `@score_diagnostics//:opensovd_cda`). Pinned upstream commit `ce3a566` on the concept branch; `refs/heads/main` (floating) on the other two branches | verified: `git -C repos/hackfest-eclipse-score_inc_diagnostics show origin/HackFest_concept:extensions/cda_repo.bzl` |
| How OpenSOVD was wired into S-CORE | **Adapter module pattern**: an S-CORE incubation repo downloads the CDA tarball through a `repository_rule`, injects synthetic `BUILD.bazel` files per crate, resolves crates from the CDA's own `Cargo.lock` via `crate_universe`, stubs `build.rs` (no git in the sandbox), pre-fetches mbedTLS 4.0.0, and handles `openssl-sys` (vendored on the concept branch, BCR `openssl` on `hackfest`, SDK pkg-config on `hackfest-opajonk`). `reference_integration` then pulls it in through `known_good.json` and a `local_path_override` | verified: `origin/HackFest_concept:docs/arc.md` (sections 3-8) |
| S-CORE modules in the same build | `known_good.json` target_sw: baselibs, baselibs_rust, communication (mw::com / LoLa), persistency, orchestrator, kyron, lifecycle_health, logging (+ `score_diagnostics` on the HackFest branch). Being in the same Bazel graph does **not** mean these modules were linked into the CDA | verified: repos/hackfest-eclipse-score_reference_integration/known_good.json; `origin/hackfest` diff |
| Processes at runtime | Expected: `opensovd-cda` (axum HTTP server, SOVD REST on :8080 under `/vehicle/v15/...`) as one process on the Pi, talking DoIP (TCP/UDP 13400) to an ECU or vehicle. The RC-car variant added an S-CORE-middleware app driving CAN. **The process list, configs and launch scripts of the Pi demo are not public** | unverified |
| IPC between S-CORE and OpenSOVD | **None evidenced.** Workshop notes (20 May): "IPC communication: planned HTTP-IPC, integration with S-CORE middleware under discussion"; "Async library: Tokio (OpenSOVD) vs Kyron (S-CORE) parallel development" | https://github.com/eclipse-opensovd/opensovd/discussions/103 |
| Clients | Web UI and AI chat + MCP server for diagnostics | reported only (blog); code not public |

Bottom line for teams: "S-CORE + OpenSOVD" at the HackFest meant "the CDA is a Bazel-built S-CORE artefact that runs on the S-CORE target OS". It did **not** mean "S-CORE apps report faults to OpenSOVD over S-CORE IPC". That second step (FaultLib/DiagLib -> SOVD server -> gateway) is what the Ulm workshop prioritised, and it is the gap Chapter 4 [[chapter4-challenge-doctor-whodunit]] ("diagnostic truth exposed through OpenSOVD") runs straight into.

## The OpenBSW virtual ECU + CDA + Grafana stack (summary; detail in [[hackfest-openbsw-playground]])
```
 Browser / curl / Grafana(:3000, Infinity datasource, 192.168.0.100)
          | HTTP :8080  real CDA: /vehicle/v15/... (JWT bearer via POST /vehicle/v15/authorize)
          |             stub CDA: /sovd/v1/...   (no auth, extra /api/sensors|faults for Grafana)
 OpenSOVD CDA (Rust/axum, 192.168.0.10, tester addr 0x0EE0)  -- or --  Python/FastAPI stub (doipclient)
          | DoIP TCP/UDP :13400 (ISO 13400-2), standard DoIP (onboard_tester=false)
 OpenBSW ECU app.sovdDemo.elf (C++, POSIX + FreeRTOS, lwIP over tap0, 192.168.0.201, logical addr 0x002A)
   UDS 0x10/0x14/0x19/0x22/0x2E/0x28/0x31/0x3E/0x85; DTC simulator (5 DTCs), random-walk DIDs 0xCF10-0xCF12
```
- **Zero-patch overlay**: the demo's CMake adds upstream `openbsw/` as a subdirectory, shadows `UdsSystem.h`, adds 0x19/0x14 services, and replaces one DoIP source file in the `doip` target (repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/CMakeLists.txt, doc/demo-architecture.md section 3).
- **Diagnostic description**: an MDD (FlatBuffers) generated from `odx-gen/openbsw_ecu.json` by `generate_mdd.py`, or via PDX with `odxtools` + `odx-converter`.
- **Pinned versions**: openbsw `07b7551` (the commit before the DoIP `estd::slice -> etl::span` API change), CDA `ce3a566`, odx-converter `b4f516e` (`git ls-tree HEAD` in repos/hackfest-OpenBSW-Playground).

## openDuT setup (summary; detail in [[hackfest-opendut-playground]])
- The openDuT team brought Raspberry Pis preinstalled with **EDGAR** (edge agent) and a hosted **CARL** backend. Peers and clusters were managed in the web UI (LEA) or with **CLEO**.
- Challenge 1 ("remote ECU connection"): `PC --eth--> RPi1 EDGAR ==openDuT over WiFi==> RPi2 EDGAR --eth--> Car`, so teams could test against the cars without going outside. Challenge 2: split the CDA's own `testcontainer/docker-compose.yml` (CDA vs ECU-sim) across two PCs joined by openDuT, with EDGAR either on RPis or in Docker. Challenge 3: set up new EDGAR RPis.
- Result: the CDA-to-car link worked (mirrors folded); NetBird sessions dropped; the CAN support bug was fixed upstream (PR #494); EDGAR ran natively on the S-CORE image but needs the `vcan` kernel module.

## Integration challenges and documentation gaps (hackathon ideas)
Each row is an observed pain point with evidence. Most of them make a small, high-value Chapter 4 contribution (Track 2 freestyle, or the "reusable PR/issue" top score on Ecosystem Integrability, see [[chapter4-overview]]).

| # | Gap / challenge | Evidence | Idea for a team |
|---|---|---|---|
| G1 | OpenSOVD <-> S-CORE **runtime** integration (IPC, FaultLib/DiagLib -> SOVD server) did not exist; "HTTP-IPC planned"; Tokio vs Kyron | workshop notes #103 | Prototype an S-CORE app that raises a fault through `inc_diagnostics` `score/mw/diag` and expose it via the SOVD server/gateway; or a mw::com -> SOVD bridge |
| G2 | Bazel build of the CDA was **AI-generated glue in the S-CORE repo** with static toolchain references; "better solution: proper Bazel file within OpenSOVD repo" | workshop notes; `docs/arc.md` sections 8.1-8.8 | Partly done since then (CDA branch `feat/bazel`, see "after" below). Help upstream it and add a CI job |
| G3 | **Ferrocene could not compile CDA deps** (`time-macros 0.2.27` needs nightly `proc_macro_span`); fell back to rustc 1.88 | `origin/HackFest_concept:docs/arc.md` section 8.1 | Check whether this still holds with the current CDA lockfile; open an issue or PR to bump `time` |
| G4 | CDA `build.rs` calls `git`; `mbedtls-sys` downloads mbedTLS at build time; `env!("CARGO_MANIFEST_DIR")` breaks in the sandbox | arc.md sections 8.4-8.6 | Upstream hermetic-build fixes to the CDA (make `build.rs` honour env overrides) |
| G5 | **Diagnostic descriptions** per vehicle (ODX/MDD) were the blocker for BMW and Porsche; "ODX format too large; MDD preferred" | blog; workshop notes | MDD tooling: validator, diff, or generator from a JSON spec (the OpenBSW `generate_mdd.py` is a seed) |
| G6 | **OpenBSW DoIP server NACKed `DiagnosticMessagePositiveAck` (0x8002)** from the CDA, so the CDA had to set `send_diagnostic_message_ack=false`; the default 1 s send timeout was too short for lwIP | repos/hackfest-OpenBSW-Playground/doc/sovd-demo/rg6_interop_fixes.rst | Upstream the ECU-side fix to eclipse-openbsw (the overlay file is ready), and ask the CDA to make the ACK behaviour per-ECU |
| G7 | OpenBSW `main` changed the DoIP API (`estd::slice` -> `etl::span`, upstream commit 8d18b1a1) and broke the overlay, so the demo pins openbsw `07b7551` | commit b657100 message | Port the overlay to current OpenBSW |
| G8 | CDA requires a JWT bearer token even with the `auth` feature off; MDD has an empty `variant_pattern`, so `fallback_to_base_variant=true` is needed | real-sovd-cda/README.md sections 3-4 | Docs PR to the CDA: "minimal config for a new ECU" |
| G9 | Docs drift in the OpenBSW demo: README claims a prebuilt CDA binary in Git LFS (`bin/README.md` says it is not stored); HACKATHON.md points to `../openbsw/...` paths for files that live in `openbsw-overlay/`; README says `docker compose up` starts 3 services, but the compose file needs `--profile stub-cda` or `--profile real-cda` | the files cited | Easy docs PRs; good first Track 2 contribution |
| G10 | openDuT: NetBird session loss (needs EDGAR re-setup), CAN bitrate/sample-point read-back can loop forever, EDGAR without systemd is undocumented, `raspberry-pi-wireless-bootstrap` could not find the rpi-imager AppImage, CLEO accepts a leader outside the cluster (#495, open, good-first-issue) | repos/hackfest-openDuT-playground/result-overview.md; https://github.com/eclipse-opendut/opendut/issues/495 | #495 is a ready-made first PR (the step-by-step guide is in `cleo-apply-fix-leader-in-cluster-not-checked.md`) |
| G11 | S-CORE image lacked Docker and the `vcan` module; the EB image added docker.io only in the day-1 re-release | result-overview.md; EB release `2.0.0-beta-hackfest-2` | Document or provide a "S-CORE target + EDGAR" image recipe |
| G12 | Project-boundary ownership ("where project boundaries end and integration responsibilities begin"); two release paths for OpenSOVD (S-CORE-integrated vs standalone); no integration tests in OpenSOVD | blog "Pains and gains"; workshop notes | Integration test that builds and runs the CDA against the OpenBSW ECU in CI (the playground's tier-2/3 tests are a template) |
| G13 | The web UI and the AI/MCP diagnostics work were never published | blog: "planned to be made available upstream" | An MCP server over the SOVD REST API is a small, demo-friendly build (an unoccupied niche as of 2026-10-03; unverified that nobody has published one since) Note (2026-10-03): opensovd-core already ships `opensovd-mcp`, but with topology tools only; the fault-level tooling is the actual gap ([[gap-register]] A12). |

## Follow-up: S-CORE x OpenSOVD workshop, 20 May 2026, Ulm (MBTI)
The public output is the preliminary notes in https://github.com/eclipse-opensovd/opensovd/discussions/103 (snapshot: https://github.com/eclipse-opensovd/opensovd/discussions/103). No slides or recording were found.
- 24 on-site + 23 online participants (AVL, AlefBits, BMW, EB, ETAS, FEV.io, HiRain, MBTI, LGE, Liebherr, Schaeffler, Traton, Valeo, ZF).
- State reported: FaultLib and DiagLib connected to the SOVD server in sovd-core; the CDA is "mostly working" and is the most advanced component; UDS2SOVD is on hold; no integration tests in OpenSOVD; the SOVD server needs ASIL-QM qualification.
- HackFest result as summarised there: the CDA is imported via a "Bazel proxy repo (inc_diagnostics)" with cross-compilation support; the Bazel files were AI-generated and live in the S-CORE module only.
- **Consensus**: start inside S-CORE's `inc_diagnostics` with a simple use case (build-version readout). **Next step**: integrate into `reference_integration` per design record DR-008-Int (eclipse-score/score PR #2747, merged 2026-06-12).
- The notes link the Chapter 4 hackathon explicitly, so this is the thread to cite in your interview and pitch.

## After the HackFest (May-Sep 2026): where the code went
Verified by `git ls-remote` / shallow fetch on 2026-10-03. Upstream remotes were added to the local clones as `upstream` (reference_integration) and `up` (inc_diagnostics).
| Repo@branch | Date | What | Evidence |
|---|---|---|---|
| eclipse-score/reference_integration@`hackfest-raspi-demo` | 2026-04-15 | Pre-event: adds the `eb-aarch64-rpi4b` config with the RPi SDK from the org's `eb_corbos_toolkit-hackfest` release (URL **still 200**) | `git -C repos/hackfest-eclipse-score_reference_integration show e4a45fd` |
| eclipse-score/reference_integration@`integrate-opensovd-cda` | 2026-05-26 | `bazel_dep(name="classic-diagnostic-adapter")` + `git_override` to CDA commit `0656ae8` (which has its own `MODULE.bazel`) + mbedTLS patches in `patches/diagnostics/` | `git ... show upstream/integrate-opensovd-cda` |
| eclipse-score/inc_diagnostics@`main` | to 2026-09-15 | Diagnostics middleware APIs: `score/mw/diag` (C++ UDS RDBI/WDBI/RoutineControl/DTC, Rust `diag_api`) | `git -C repos/hackfest-eclipse-score_inc_diagnostics log up/main` |
| eclipse-score/inc_diagnostics@`gateway_cda_int` | 2026-09-08 | Bazel targets `//score/opensovd-cda:opensovd-cda` (+ `integration_test`), `//score/opensovd-gateway:opensovd-gateway`, `//score/examples/sovd-client:sovd-client`; deps: CDA `246cdf4`, `mbedtls-rs`, `opensovd_core` `0cb4b25` | `git ... show up/gateway_cda_int:score/opensovd-cda/BUILD` |
| eclipse-opensovd/classic-diagnostic-adapter@`feat/bazel`, `feat/bazel-build` | - | Native Bazel support (not on `main` as of 2026-10-03: `MODULE.bazel` on main returns 404) | `git ls-remote`; curl |

## Reusable starting points for Chapter 4
Ordered by how fast a team gets something green. Paths are local clones; the upstream URL is given where the code is not in a HackFest repo.

| Want to... | Start from | Path | Effort / caveats | Fits |
|---|---|---|---|---|
| Diagnose a (virtual) OpenBSW ECU over SOVD in < 30 min | OpenBSW-SOVD-Demo, stub CDA | repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/ (`./demo.sh`, or `docker compose --profile stub-cda up --build`) | needs `git submodule update --init openbsw`, TAP (sudo, or Docker with NET_ADMIN) | [[chapter4-challenge-hack-to-the-future]] (OpenBSW zonal controller), [[chapter4-challenge-doctor-whodunit]] ("diagnostic truth") |
| Same, with the real Eclipse CDA | `./demo.sh --real-cda` or `docker compose --profile real-cda up --build` | OpenBSW-SOVD-Demo/real-sovd-cda/ (`Dockerfile`, `opensovd-cda.toml`, `entrypoint.sh`) | needs the CDA submodule (`ce3a566`); first Rust build takes minutes; JWT via `POST /vehicle/v15/authorize` | both |
| Describe your own ECU (new DIDs/DTCs) for the CDA | MDD generator | OpenBSW-SOVD-Demo/real-sovd-cda/odx-gen/ (`openbsw_ecu.json` -> `generate_mdd.py` -> `OpenBSW.mdd`; or `generate_openbsw.py` -> PDX -> odx-converter) | needs `protobuf`, `flatbuffers` pip packages; check the MDD schema against the CDA version | both |
| Add a simulated sensor/fault on the ECU | DTC simulator overlay | OpenBSW-SOVD-Demo/openbsw-overlay/app/{include,src}/uds/DtcSimulator.*, ReadIdentifierSimulated.*, systems/UdsSystem.* | HACKATHON.md "Challenge 1/2" (paths in that doc point to `../openbsw/...`; use the overlay paths instead) | Doctor Whodunit (stuck/stale sensor -> DTC) |
| A Back-to-the-Future ECU (Flux Capacitor) | FLXC1000 branch | `git -C repos/hackfest-OpenBSW-Playground show origin/features/jkk_FLUX1000:` + `OpenBSW-SOVD-Demo/openbsw-overlay/app/src/systems/Flxc1000UdsSystem.cpp`, `real-sovd-cda/odx-gen/FLXC1000.mdd`, `grafana/dashboards/flxc1000.json` | unmerged branch (Softing AG contributor, 29 Apr); DID 0xF200 "FluxCapacitorPowerConsumption"; FLXC1000 likely mirrors the CDA's own ecu-sim test ECU (unverified) | [[chapter4-challenge-hack-to-the-future]] stretch goal (Flux Capacitor display) |
| Grafana dashboard over SOVD | provisioning + dashboards | OpenBSW-SOVD-Demo/grafana/{provisioning,dashboards}/ | Infinity datasource with a hardcoded demo JWT; `host.docker.internal` mapping | evidence visualisation |
| Test pyramid for a diagnostics demo | pytest tiers unit / ECU (DoIP/UDS) / SOVD / Grafana (Playwright) | repos/hackfest-OpenBSW-Playground/tests/ | ECU tier is advisory in the release workflow (`.github/workflows/release.yml` ~line 288, `continue-on-error: true`) | "Development Methods" score; Doctor Whodunit verdicts |
| Run the CDA against simulated ECUs across two machines via openDuT | openDuT challenge 2 | repos/hackfest-openDuT-playground/README.md + CDA `testcontainer/docker-compose.yml` (upstream) | needs a CARL backend + 2 EDGARs (RPi or Docker); use a router that allows peer-to-peer traffic | Doctor Whodunit (openDuT fault campaigns) |
| First openDuT upstream PR | CLEO leader-in-cluster check | repos/hackfest-openDuT-playground/cleo-apply-fix-leader-in-cluster-not-checked.md; issue #495 | step-by-step guide included; error type pre-prepared on a branch | Track 2 freestyle |
| Build OpenSOVD components with S-CORE's Bazel | **upstream `inc_diagnostics@gateway_cda_int`** (not the HackFest branches) | https://github.com/eclipse-score/inc_diagnostics/tree/gateway_cda_int (`score/opensovd-cda`, `score/opensovd-gateway`, `score/examples/sovd-client`) | Bazel and S-CORE devcontainer; the first fetch is heavy (>10 min); not run here | Doctor Whodunit (S-CORE listed, role unclear) |
| Understand the adapter-module approach and its traps | concept doc | `git -C repos/hackfest-eclipse-score_inc_diagnostics show origin/HackFest_concept:docs/arc.md` | read-only; the best write-up of Rust-in-Bazel pitfalls | any team bridging Cargo and Bazel |
| Run an S-CORE app on EB corbos Linux (QEMU) | EBcLfSA image integration | repos/hackfest-eclipse-score_reference_integration/images/ebclfsa_aarch64/ (`bazel run --config eb-aarch64 //images/ebclfsa_aarch64:run`) | README still references `scrample_integration/`, which moved (docs drift); about 6 min in a 4-core Codespace per README | HI/LI safety story |
| Real RPi 4B + CAN with EB corbos Linux | EB HackFest release | https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eb_corbos_toolkit-hackfest/releases (`2.0.0-beta-hackfest-2`) | flash the `.wic`; set the MCP2515 overlay in `/boot/config.txt` | hardware stretch |

## Known-broken / open integration gaps (with evidence)
Checked 2026-10-03 unless dated otherwise.

| # | What is broken / open | Evidence | Impact for a team |
|---|---|---|---|
| B1 | Org fork `eclipse-score_reference_integration@hackfest` (5ab03a0) fetches its RPi toolchain from `github.com/opajonk/eb_corbos_toolkit/releases/download/test-tag/fastdev-sdk-ubuntu-ebclfsa-ebcl-qemuarm64.tar.gz`, which returns **HTTP 404** (and despite the "raspi" name it is a qemuarm64 SDK) | `git show origin/hackfest:bazel_common/score_gcc_toolchains.MODULE.bazel`; curl in https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eb_corbos_toolkit-hackfest/releases | `--config=eb-aarch64-rpi4b` cannot fetch; use the upstream `hackfest-raspi-demo` URL (200) |
| B2 | The same branch uses `local_path_override(path="/workspaces/eclipse-score_reference_integration/score_diagnostics")`, an absolute devcontainer path to an unpublished checkout | `git show origin/hackfest:bazel_common/score_modules_target_sw.MODULE.bazel` | Builds only inside that exact devcontainer layout with `score_diagnostics` cloned by hand |
| B3 | The same branch removed `score_autosd10_x86_64_toolchain` from `use_repo`, but `.bazelrc` `build:autosd-x86_64` still references it | `git show origin/hackfest:.bazelrc` lines 59-60 vs the MODULE diff | `--config autosd-x86_64` breaks on that branch |
| B4 | Three divergent `inc_diagnostics` branches: module name `score_inc_diagnostics` (concept) vs `score_diagnostics` (hackfest*); CDA pinned (`ce3a566` + sha256) vs floating `refs/heads/main`; rustc 1.88 vs Ferrocene | `git show origin/<branch>:MODULE.bazel`, `:extensions/cda_repo.bzl` | Not reproducible; floating `main` will drift. Treat as reference only |
| B5 | `hackfest-opajonk` `MODULE.bazel` hard-codes the canonical repo name `@@score_bazel_cpp_toolchains++gcc+score_ebclfsa_toolchain_raspi_pkg` in a `crate.annotation` | `git show origin/hackfest-opajonk:MODULE.bazel` | Only builds as a dependency of that specific reference_integration branch |
| B6 | Ferrocene incompatible with CDA's `time-macros 0.2.27` (nightly `proc_macro_span`) | arc.md section 8.1 | Safety-qualified toolchain story for OpenSOVD is open |
| B7 | No public runtime IPC between S-CORE and OpenSOVD; "HTTP-IPC planned"; Tokio vs Kyron | workshop notes | Any "S-CORE app reports a fault to SOVD" demo is new work |
| B8 | CDA native Bazel support is on `feat/bazel*` branches, not on CDA `main` | `git ls-remote`; `MODULE.bazel` 404 on main, 200 at `0656ae8` | Pin a commit; do not track main |
| B9 | OpenBSW `main` is incompatible with the demo overlay after the DoIP `etl::span` change | commit b657100 (development branch) message | Keep the pinned submodule `07b7551`, or port the overlay |
| B10 | OpenBSW DoIP ACK interop (0x8002/0x8003) fixed only in the demo overlay, not upstream; CDA workaround `send_diagnostic_message_ack=false` | rg6_interop_fixes.rst REQ_RG6_001/002 | Real CDA against stock OpenBSW will hit Generic NACK 0x01 |
| B11 | Real CDA endpoints `Identification` (DID 0xF100) -> NRC 0x31 and `WritableData` -> NRC (needs an extended session) | real-sovd-cda/README.md "Verified Working Endpoints" | Expected NRCs, not a bug; explain to teams |
| B12 | The stub and the real CDA expose **different APIs** (`/sovd/v1/` vs `/vehicle/v15/`, auth vs none, Grafana helper endpoints only on the stub) | real-sovd-cda/README.md "API Differences" | Clients written against the stub do not work against the real CDA |
| B13 | ECU POSIX build stops when backgrounded (`tcsetattr` -> SIGTTOU); demo.sh traps it | REQ_RG6_004 | Launch with stdin from `/dev/null` if you script it yourself |
| B14 | openDuT: NetBird session loss; CAN sample-point read-back mismatch can loop forever; #495 open | result-overview.md; issue #495 | Budget re-setup time; prefer a vcan or virtual path for demos |
| B15 | The S-CORE + OpenSOVD Pi demo, RC-car prototype, web UI and AI/MCP work have **no public code** | org repo list; blog | Cannot be reproduced; ask the OpenSOVD maintainers or the coaches |
| B16 | Docs drift in the playground (LFS binary claim, wrong paths in HACKATHON.md, compose profiles) and in the EBcLfSA README (`scrample_integration/` paths) | the files cited | Small, high-acceptance docs PRs |

## Who to ask (from the slides and commits)
- OpenSOVD x S-CORE build: **Oliver Pajonk** (EB, commits on all S-CORE HackFest branches); Ajitesh Mishra and arsibo (inc_diagnostics commits).
- OpenSOVD: **Thilo Schmitt** (MBTI, workshop host), Christoph (talk); CDA on BMW: Anton Krivoborodov.
- OpenBSW demo: **Tom Fleischmann** (Accenture; the playground README says "TTL: end of April 2026", so treat it as unmaintained); Janick Kaltenmark (Softing AG, FLXC1000 branch).
- openDuT: Michael (talk); **Frank Märkle** (result overview); Reimar Stier (PR merger).

## Repo snapshot (shallow clones, 2026-10-03)
| Local path | Upstream | HEAD (default branch) | Extra refs fetched |
|---|---|---|---|
| repos/hackfest-hackfest-docs | .../hackfest-docs | d86aebc 2026-05-04 | - |
| repos/hackfest-eclipse-score_reference_integration | .../eclipse-score_reference_integration | 3c84382 2026-04-24 (main = upstream main at that date) | origin/hackfest 5ab03a0 (2026-05-19), origin/hackfest_playground_martin (= main), upstream/{hackfest-raspi-demo, integrate-opensovd-cda, ankr_poc_integrate_opensovd, ankr_poc_integrate_opnsovd_in_eb_linux} |
| repos/hackfest-eclipse-score_inc_diagnostics | .../eclipse-score_inc_diagnostics | 3635a79 2025-10-27 (template only) | origin/{HackFest_concept 4158b2d, hackfest c5cacb6, hackfest-opajonk 755cbdf}, up/{main 579ef42, gateway_cda_int b975ed4} |
| repos/hackfest-OpenBSW-Playground | .../OpenBSW-Playground | e22b9d1 2026-04-28 | origin/{development, features/jkk_FLUX1000 f9fdafc, feature/release-pipeline}; submodules **not** initialised |
| repos/hackfest-openDuT-playground | .../openDuT-playground | 421c257 2026-04-30 | - |
| repos/hackfest-eb_corbos_toolkit-hackfest | .../eb_corbos_toolkit-hackfest | 87c741f 2026-03-25 (plain fork of Elektrobit/eb_corbos_toolkit) | the assets live in Releases, not in git |

Nothing was built or run for this note (Bazel fetches exceed the 10-minute budget; the OpenBSW demo needs sudo/TAP or a Docker image build). Status therefore stays `draft`.
