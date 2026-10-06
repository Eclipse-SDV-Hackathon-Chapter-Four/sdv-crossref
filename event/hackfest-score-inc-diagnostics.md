---
title: HackFest repo - eclipse-score_inc_diagnostics (OpenSOVD CDA as an S-CORE Bazel adapter module)
type: event
component: s-core
tags: [event, hackfest, s-core, opensovd, cda, bazel, rust, ferrocene, crate_universe, adapter-module]
status: draft
sources:
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eclipse-score_inc_diagnostics
  - https://github.com/eclipse-score/inc_diagnostics
  - repos/hackfest-eclipse-score_inc_diagnostics
  - https://github.com/eclipse-opensovd/opensovd/discussions/103
last-verified: 2026-10-03
related:
  - "[[hackfest-esslingen-2026]]"
  - "[[hackfest-score-reference-integration]]"
  - "[[s-core-overview]]"
  - "[[opensovd-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
---

# eclipse-score_inc_diagnostics (HackFest fork) - building the OpenSOVD CDA inside S-CORE

Fork of S-CORE's diagnostics incubation repo, used in the track "S-CORE integration - build openSOVD artefacts" (lead Oliver Pajonk, EB). Local clone `repos/hackfest-eclipse-score_inc_diagnostics`. `main` (3635a79, 2025-10-27) is the untouched S-CORE C++/Rust module template; **all HackFest work is on three branches**. Upstream `eclipse-score/inc_diagnostics` was fetched as remote `up`. Context: [[hackfest-esslingen-2026]]; consumer: [[hackfest-score-reference-integration]].

## The idea: "Adapter Module" (docs/arc.md on `HackFest_concept`)
Read with `git -C repos/hackfest-eclipse-score_inc_diagnostics show origin/HackFest_concept:docs/arc.md`.
- Goal: make an external Cargo project (the [[opensovd-overview]] CDA) buildable with the S-CORE toolchain and integrable into `reference_integration` **without forking or modifying it**.
- `extensions/cda_repo.bzl`: a `repository_rule` downloads a fixed-commit CDA tarball (sha256), writes a synthetic `BUILD.bazel` per crate, and keeps the upstream `Cargo.lock` (`crate.from_cargo(name="cda_crates", ...)` over 16 manifests).
- Public surface: `//src:opensovd_cda -> @classic_diagnostic_adapter//cda-main:opensovd_cda` and `//src:cda_lib` (concept branch). The `hackfest*` branches expose `//:opensovd_cda` instead.
- Integration path: `known_good.json` entry + `bazel_dep` + `git_override` in reference_integration (sections 5.1-5.3); showcase target in an image was planned (5.3), not done.
- Alternatives rejected: fork (governance), publishing the CDA to the S-CORE registry (needs upstream Bazel), git submodule (not hermetic).

## Implementation findings (arc.md section 8) - the reusable knowledge
| # | Problem | Workaround |
|---|---|---|
| 8.1 | Ferrocene cannot build `time-macros 0.2.27` (nightly `proc_macro_span`) | Use standard rustc **1.88.0** via `rules_rust` (`rust.toolchain(edition="2024", versions=["1.88.0"])`) |
| 8.2 | `all_crate_deps()` omits intra-workspace deps | Hand-maintained `_LIB_EXTRA_DEPS` per crate |
| 8.3 | Starlark `.format()` "silently drops" `load()` lines with `@` labels | Build BUILD text by string concatenation (the doc's claim; the root cause is unverified, possibly brace escaping) |
| 8.4 | `cda-main/build.rs` runs `git` | Replace with a stub emitting fixed `BUILD_DATE` / `GIT_COMMIT_HASH=ce3a566` |
| 8.5 | `mbedtls-sys/build.rs` downloads mbedTLS 4.0.0 | Pre-fetch in the repository_rule (sha256 `2f3a47f7...`), `MBEDTLS_SKIP_PATCH=1` |
| 8.6 | `env!("CARGO_MANIFEST_DIR")` is the compile-time path | Patch to `std::env::var("CARGO_MANIFEST_DIR")` |
| 8.8 | `openssl-sys` wants host OpenSSL via pkg-config | `crate.annotation(crate="openssl-sys", build_script_env={OPENSSL_VENDORED:"1", OPENSSL_STATIC:"1"})` (OpenSSL 3.5.4 from `openssl-src`) |
Open after the HackFest (8.7): S-CORE Bazel registry entry, `known_good.json` entry upstream, CI for upstream bumps.

## Branches (HackFest fork)
| Branch | HEAD | Author(s) | Module name | CDA source | Rust | OpenSSL |
|---|---|---|---|---|---|---|
| `HackFest_concept` | 4158b2d 2026-04-28 | arsibo | `score_inc_diagnostics` 0.1.0 | pinned `ce3a566c...` + sha256 `1c830c4c...` | rustc 1.88 (`rules_rust` 0.63) | vendored |
| `hackfest` | c5cacb6 2026-04-29 | Ajitesh Mishra, Oliver Pajonk | `score_diagnostics` | **`refs/heads/main` (floating)** | `rules_rust` 0.69; `.bazelrc` registers Ferrocene x86_64 + `ferrocene_aarch64_ebclfsa`; `eb-aarch64` config; devcontainer `ghcr.io/eclipse-score/devcontainer:v1.4.1` | BCR `openssl` 3.5.5.bcr.4 via `OPENSSL_DIR` |
| `hackfest-opajonk` | 755cbdf 2026-05-19 | Oliver Pajonk | `score_diagnostics` | **floating main** | `register_toolchains(@score_toolchains_rust//toolchains/ferrocene:all)` | cross pkg-config into the EB RPi SDK sysroot, hard-coded canonical repo name `@@score_bazel_cpp_toolchains++gcc+score_ebclfsa_toolchain_raspi_pkg` ("enable CDA cross compilation, especially by fixing the openssl-sys crate") |
`reference_integration@hackfest` pins this repo at `88fd660` ("fix module name"), a commit shared by both `hackfest*` branches, and overrides it with a `local_path_override`. See [[hackfest-score-reference-integration]].

Whether the Ferrocene path actually compiled the CDA on the `hackfest*` branches (given finding 8.1) is **unverified**; no build logs are public.

## What upstream did next (remote `up`, eclipse-score/inc_diagnostics)
- `up/main` (579ef42, 2026-09-15): S-CORE diagnostics middleware APIs in `score/mw/diag/` (C++ `uds/` ReadDataByIdentifier, WriteDataByIdentifier, RoutineControl, generic service, NRCs, mocks + tests; Rust `api/diag_api.rs`, `uds.rs`; "Add DTC C++ API for diag_lib" #26). This is the **DiagLib** side the Ulm workshop discussed.
- `up/gateway_cda_int` (b975ed4, 2026-09-08, Frank Scholter Peres, MB): consumes the CDA as a **native Bazel module** (`bazel_dep(name="classic-diagnostic-adapter", version="0.1.0")` + `git_override` commit `246cdf4`; `mbedtls-rs` from eclipse-opensovd; `opensovd_core` commit `0cb4b25`) and builds:
  - `//score/opensovd-cda:opensovd-cda` (+ `:integration_test` using `opensovd-client`, sample TOML, `mdd/functional_groups.mdd`)
  - `//score/opensovd-gateway:opensovd-gateway` (opensovd-core server/providers/models)
  - `//score/examples/sovd-client:sovd-client`
  So the adapter-module glue from the HackFest has effectively been replaced by upstream Bazel support in the CDA (branches `feat/bazel*` in classic-diagnostic-adapter, "PR 488" per the commit message). This matches the workshop's "better solution: proper Bazel file within OpenSOVD repo".

## For Chapter 4 teams
- Want OpenSOVD inside an S-CORE build? Start from **`up/gateway_cda_int`**, not from the HackFest branches. Expect a heavy first Bazel fetch (>10 min, not run here). Prerequisites: the S-CORE devcontainer.
- Want to show "an S-CORE app reports a fault to SOVD"? The pieces exist separately (`score/mw/diag` DiagLib API; opensovd-core server/gateway), but **no published glue connects them over IPC**. That is new work and a strong demo for [[chapter4-challenge-doctor-whodunit]] ("diagnostic truth exposed through OpenSOVD").
- Want to bring another Cargo project into S-CORE Bazel? arc.md section 8 is the checklist of traps.

## Pitfalls
- Floating CDA `main` on two branches makes builds drift; the hard-coded canonical repo name ties `hackfest-opajonk` to one consumer.
- The module name differs between branches (`score_inc_diagnostics` vs `score_diagnostics`).
- The section 8.8 text of arc.md is in German.
