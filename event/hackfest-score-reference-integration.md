---
title: HackFest repo - eclipse-score_reference_integration (S-CORE + CDA on EB corbos Linux / RPi 4B)
type: event
component: s-core
tags: [event, hackfest, s-core, opensovd, bazel, eb-corbos-linux, ebclfsa, raspberry-pi, cross-compile, known-good]
status: draft
sources:
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eclipse-score_reference_integration
  - https://github.com/eclipse-score/reference_integration
  - repos/hackfest-eclipse-score_reference_integration
  - repos/hackfest-eclipse-score_reference_integration/images/ebclfsa_aarch64/README.md
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eb_corbos_toolkit-hackfest/releases
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eb_corbos_toolkit-hackfest
last-verified: 2026-10-03
related:
  - "[[hackfest-esslingen-2026]]"
  - "[[hackfest-score-inc-diagnostics]]"
  - "[[s-core-overview]]"
  - "[[opensovd-overview]]"
  - "[[autosd-overview]]"
---

# eclipse-score_reference_integration (HackFest fork) - S-CORE x OpenSOVD on EBcLfSA / Raspberry Pi

Fork of S-CORE's `reference_integration` (the single Bazel workspace that integrates all S-CORE modules from `known_good.json` and builds images for Linux x86_64, QNX, AutoSD and EB corbos Linux for Safety Applications). Local clone `repos/hackfest-eclipse-score_reference_integration`; `main` = 3c84382 (2026-04-24, identical to upstream at that date). HackFest work is on branch **`hackfest`** (5ab03a0); `hackfest_playground_martin` has no extra commits. Upstream remote `upstream` added for the related branches. Context: [[hackfest-esslingen-2026]]; component background: [[s-core-overview]].

## What the `hackfest` branch changes (`git diff main origin/hackfest -- . ':!MODULE.bazel.lock'`)
| Commit | Date | Change |
|---|---|---|
| f50e3a9 "add score_diagnostics" | 2026-04-28 | `known_good.json` += `score_diagnostics` -> `Eclipse-SDV-HackFest-Esslingen-2026/eclipse-score_inc_diagnostics.git` @ `88fd660`, `code_root_path //src/...` |
| 7c3093c | 2026-04-28 | `rules_rust` 0.61.0 -> **0.69.0** |
| 14b728e "Add local toolchain for cross-compilation and quick iterations on it and integrate score_diagnostics module" | 2026-05-19 | `.bazelrc` `build:eb-aarch64-rpi4b` (GCC EBcLfSA raspi toolchain + `@ferrocene_aarch64_ebclfsa` + platform `aarch64-linux-sdk_0.1.0-ebclfsa`); `gcc.sdp(score_ebclfsa_toolchain_raspi_pkg)` + `gcc.toolchain(score_ebclfsa_raspi_toolchain)` with explicit sysroot include/lib flags and `-static`; `score_bazel_cpp_toolchains` 0.5.0 -> 0.5.1; `bazel_dep(score_diagnostics)` + `local_path_override(path="/workspaces/eclipse-score_reference_integration/score_diagnostics")`; `rust_coverage_score_diagnostics` report target |
| 5ab03a0 | 2026-05-19 | lockfile |

Note: commits 14b728e/5ab03a0 come three weeks **after** the event. They are the cleaned-up state, not necessarily what ran on 29 April.

## Hardware/OS of the demo
- **Raspberry Pi 4B + MCP2515 CAN shield**, running EB corbos Linux for Safety Applications "fast-dev" (Ubuntu-based) from the org's `eb_corbos_toolkit-hackfest` releases: `2.0.0-beta-hackfest` (2026-04-13) and `2.0.0-beta-hackfest-2` (2026-04-28, + `can-utils`, `containerd`, `docker.io`; SDK + `pkg-config`). Assets: `fastdev-ubuntu-ebclfsa-rpi4b.tar.gz` (flash the `.wic`), `fastdev-sdk-ubuntu-ebclfsa-rpi4b.tar.gz`, SPDX SBOM. CAN overlay in `/boot/config.txt`: `dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25` (beta-2), or `8000000,interrupt=12` (beta-1), depending on wiring.
- The git content of `eb_corbos_toolkit-hackfest` itself is just a fork of `Elektrobit/eb_corbos_toolkit` @ 87c741f (CMake app-dev workspace, `hello-world`/`hello-safety` apps, presets `fastdev-{li,hi}-qemuarm64`, devcontainer image on `artifactory.elektrobit.com`). The HackFest value is in its **Releases**.
- OS rules for safety apps (from `images/ebclfsa_aarch64/README.md`): HI apps statically linked, ELF-header checksum via `lisa-elf-enabler`, started by HI init `cflinit`; LI userland via `crinit` (ssh on 2222 in QEMU, root/`linux`); disallowed syscalls (`clone3`, `madvise`, `ioctl`) are logged.

## Related branches in upstream eclipse-score/reference_integration
| Branch | Commit | Author | What |
|---|---|---|---|
| `hackfest-raspi-demo` | e4a45fd 2026-04-15 | Oliver Pajonk | Pre-event version of the RPi toolchain, pointing at the org release `2.0.0-beta-hackfest/fastdev-sdk-ubuntu-ebclfsa-rpi4b.tar.gz` (sha256 `7e253dfd...`, **URL still 200**) |
| `ankr_poc_integrate_opensovd` | 4e07a46 2026-04-22 | Anton Krivoborodov (BMW) | `bazel_dep(score_opensovd_cda)` from `antonkri/opensovd-core` @ c85fa71; packs `@score_opensovd_cda//:opensovd-cda` into the `linux_x86_64` OCI image at `/usr/bin/opensovd_cda_bin` |
| `ankr_poc_integrate_opnsovd_in_eb_linux` | = main@43c8aa4 | - | empty placeholder |
| `integrate-opensovd-cda` | 6a67d10 2026-05-26 | Oliver Pajonk | `bazel_dep(name="classic-diagnostic-adapter")` + `git_override` commit `0656ae8` (CDA with native `MODULE.bazel`) + `patches/diagnostics/00{2,3,4}-cda-mbedtls-*.patch` (002/004 commented out, "only relevant for cross-compilation") |

## Recipes (NOT executed here; Bazel first fetch exceeds the 10-minute budget)
S-CORE on EBcLfSA in QEMU (upstream-supported, from the README; ~6 min on a 4-core Codespace per README):
```bash
cd repos/hackfest-eclipse-score_reference_integration   # main
# inside the S-CORE devcontainer (ghcr.io/eclipse-score/devcontainer)
./score_starter        # menu; or directly:
bazel --output_base=build/eb-aarch64 run --config eb-aarch64 //images/ebclfsa_aarch64:run
```
CDA cross-compiled for the RPi (reconstructed from the branch; **will fail on B1-B2 below** unless fixed):
```bash
git checkout origin/hackfest
git clone https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eclipse-score_inc_diagnostics score_diagnostics
git -C score_diagnostics checkout hackfest-opajonk
# devcontainer must mount the repo at /workspaces/eclipse-score_reference_integration
# replace the 404 toolchain URL with the one from upstream branch hackfest-raspi-demo (and its sha256/strip_prefix)
bazel build --config=eb-aarch64-rpi4b @score_diagnostics//:opensovd_cda     # target name per BUILD alias; unverified
# deployment to the Pi (scp to the LI userland) is not documented anywhere public
```

## Known-broken on the `hackfest` branch
- **B1** Toolchain URL `https://github.com/opajonk/eb_corbos_toolkit/releases/download/test-tag/fastdev-sdk-ubuntu-ebclfsa-ebcl-qemuarm64.tar.gz` returns **404** (2026-10-03). Despite the "raspi" naming it was a qemuarm64 SDK.
- **B2** `local_path_override` to the absolute path `/workspaces/eclipse-score_reference_integration/score_diagnostics`.
- **B3** `use_repo` no longer lists `score_autosd10_x86_64_toolchain`, but `.bazelrc` lines 59-60 (`build:autosd-x86_64`) still reference it, so the AutoSD config breaks on this branch ([[autosd-overview]] users beware).
- **B4** The `known_good.json` entry points at the HackFest fork commit `88fd660`, while the actual build uses the local override (which may be on another branch).
- Docs drift in upstream too: `images/ebclfsa_aarch64/README.md` documents `//images/ebclfsa_aarch64/scrample_integration:*` targets, but the folder now holds only `BUILD`, `README.md`, `build/`, `docs/` (the run target is `//images/ebclfsa_aarch64:run`).
- Main README "Known Issues": `score/mw/com` label inconsistencies (`@//third_party`), coverage only on Ubuntu 22.04, `starpls.bzl` uses curl outside Bazel (proxy trouble).

## For Chapter 4 teams
- Need S-CORE on a real board with CAN in two days? The EB RPi 4B image + SDK release is the only published S-CORE-ready RPi image in this material. Treat it as **beta, development-only** ("not a production image" per README).
- Need the CDA in an S-CORE image? Follow upstream `integrate-opensovd-cda` (reference_integration) or `gateway_cda_int` ([[hackfest-score-inc-diagnostics]]), and pin commits.
- `known_good.json` + `scripts/known_good/*.py` + gita workspace (README "Workspace support") is the intended way to hack on several S-CORE modules at once.
