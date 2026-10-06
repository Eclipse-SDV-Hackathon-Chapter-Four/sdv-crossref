---
title: Eclipse S-CORE quickstart
type: quickstart
component: s-core
tags: [s-core, quickstart, orchestrator, iceoryx2, bazel, cargo, raspberry-pi]
status: verified
sources:
  - repos/s-core-orchestrator/README.md
  - repos/s-core-orchestrator/examples/README.md
  - repos/s-core-orchestrator/rust-toolchain.toml
  - repos/s-core-reference_integration/README.md
  - repos/s-core-reference_integration/score_starter
  - repos/s-core-reference_integration/.devcontainer/devcontainer.json
  - repos/s-core-reference_integration/images/ebclfsa_aarch64/README.md
  - https://github.com/eclipse-score/devcontainer
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eclipse-score_reference_integration
last-verified: 2026-10-03
related:
  - "[[s-core-overview]]"
  - "[[s-core-howto]]"
  - "[[iceoryx2-overview]]"
---

# Eclipse S-CORE quickstart

Three paths, fastest first. Only **Path A** was executed on 2026-10-03. Paths B-D are copied from the repo READMEs and were not run (no full Bazel builds were allowed).

## Path A (verified, ~2 min): Orchestrator + iceoryx2 IPC with plain Cargo, no Bazel

This is the fastest realistic way to run S-CORE code on a laptop. The orchestrator also builds with Cargo; its README documents both Cargo and Bazel CI (repos/s-core-orchestrator/README.md). Caveat: the orchestrator was **removed from the platform in v0.9**, so this is a demo of the S-CORE runtime ideas (Kyron + iceoryx2), not of the current integrated stack.

**Prerequisites:**
- Linux x86_64 (aarch64 should work but is unverified)
- git, a C toolchain, rustup with a **stable toolchain >= 1.88**
- The README also lists `protobuf-compiler libclang-dev`. They were not needed for these examples on this machine; libclang was already present.

```bash
git clone --depth 1 https://github.com/eclipse-score/orchestrator.git
cd orchestrator
# PITFALL: rust-toolchain.toml pins 1.85.0, but Cargo.lock pulls time@0.3.47, which needs rustc 1.88.
# Override with a newer toolchain:
rustup toolchain install stable
cargo +stable build --locked --example basic --example inter_process_event_sender --example inter_process_event_receiver
cargo +stable run --locked --example basic
# IPC demo (two terminals): receiver first, then sender
cargo +stable run --locked --example inter_process_event_receiver
cargo +stable run --locked --example inter_process_event_sender
```

### Observed on 2026-10-03

Host: x86_64, 32 cores, rustc stable 1.98.1; repo commit 749c11371a9d.

- `cargo build` with the pinned 1.85.0 toolchain fails immediately:
  ```
  error: rustc 1.85.0 is not supported by the following packages:
    time@0.3.47 requires rustc 1.88.0
    time-core@0.1.8 requires rustc 1.88.0
  ```
- `cargo +stable build --locked ...`: `Finished dev profile ... in 22.41s` (crates already downloaded by the failed attempt). The `target/` directory is about 670 MB.
- `cargo +stable run --example basic` prints a cyclic program (3 iterations, 1 s timer) and exits:
  ```
  INFO ThreadId(04) basic::common: Start of 'test2_sync_func' function.
  ...
  INFO ThreadId(05) basic: Program finished running.
  INFO ThreadId(01) basic: Exit.
  ```
- The IPC pair worked across two processes (iceoryx2 Event service):
  ```
  sender:   INFO inter_process_event_sender: Forward collision is imminent...
  receiver: INFO inter_process_event_receiver: Applying brake...
  ```
  Shared-memory artifacts appear as `/tmp/iceoryx2/orch_node*.event` and `/dev/shm/iox2_*`.

## Path B (not run, heavy): reference integration, Linux x86_64 in Docker via Bazel

**Prerequisites** (repos/s-core-reference_integration/README.md):
- `sudo apt-get install -y protobuf-compiler libclang-dev lcov qemu-system-x86`
- Docker
- bazelisk. `.bazelversion` = **8.6.0**. Running `bazel version` here downloaded and started 8.6.0 without trouble.

```bash
git clone --depth 1 https://github.com/eclipse-score/reference_integration.git
cd reference_integration
./score_starter                 # interactive menu
# or directly:
./score_starter -r linux-x86_64
# == bazel --output_base=build/linux-x86_64 run --config linux-x86_64 //images/linux_x86_64:run
```

What this does:
- Builds all showcases with the downloaded GCC 12.2 and Ferrocene toolchains.
- Packs them, plus the `datarouter` logging daemon, into an Ubuntu 22.04 OCI image (`score_showcases:latest`).
- Starts the image in Docker (images/linux_x86_64/BUILD).

Inside, the `cli` lets you pick showcases. The shipped examples are:
- communication sender/receiver (`com-api-example`)
- simple lifecycle (launch_manager + supervised apps, about 15 s)
- persistency, logging, kyron, time, config_management

Example configs: showcases/standalone/*.score.json and showcases/simple_lifecycle/simple_lifecycle.score.json.

**Expected cost (unverified estimate):**
- First build: tens of minutes and several GB in the Bazel output base. `MODULE.bazel.lock` alone is 2 MB of pinned deps.
- Each `--config` uses its own `--output_base=build/<name>`, so **every platform re-downloads its toolchains**.
- For comparison, the EB corbos README reports about **6 min** on a 4-core Codespace with a warm disk cache.

## Path C (not run): devcontainer / GitHub Codespaces, EB corbos aarch64 in QEMU

The reference integration has a devcontainer (`ghcr.io/eclipse-score/devcontainer:v1.11.0`, needs `/dev/kvm` and docker-in-docker; see .devcontainer/devcontainer.json). The EB corbos README recommends Codespaces with a **4-core** machine:

```bash
bazel build --config=eb-aarch64 //images/ebclfsa_aarch64:run
```

Expected tail:
```
Waiting for QEMU to be ready... (3/60)
QEMU is accessible
...
INFO: Build completed successfully, 2020 total actions
```
(repos/s-core-reference_integration/images/ebclfsa_aarch64/README.md). This is the platform the HackFest Esslingen demo ran on: EB corbos + OpenSOVD on a Raspberry Pi.

## Path D: Raspberry Pi

- **QNX 8.0 on RPi 4/5:**
  - `bazel build --config=qnx-aarch64 //images/qnx_aarch64:image` requires a **licensed QNX SDP 8.0** and the QNX RPi BSP.
  - You must also replace `startup-virt` with the BSP's startup binary in images/qnx_aarch64/build/init.build.
  - Login is `ssh root@<ip>`, and the CLI autostarts.
  - Source: repos/s-core-reference_integration/README.md.
  - Not realistic in 2 days without existing QNX credentials (`SCORE_QNX_USER`/`SCORE_QNX_PASSWORD`).
- **EB corbos on RPi:** shown at HackFest Esslingen 2026 (https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and). Exact steps are not published in the HackFest fork (unverified). Ask the S-CORE/EB mentors.
- **Raspberry Pi OS 64-bit + Path A:** probably the fastest way to get something running on a Pi, since iceoryx2 and Kyron are plain Rust. Unverified.

## HackFest Esslingen fork: simpler?

No. https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/eclipse-score_reference_integration is an **older snapshot** of upstream (commit 2026-04-24, Bazel 8.4.2, devcontainer v1.3.0). It still contains an `orchestration_persistency` showcase and a `qnx_x86_64`/`autosd_x86_64`/`ebclfsa_aarch64` image set, with the same `./score_starter` flow (repos/s-core-hackfest-reference_integration/README.md). Use upstream `main` unless you need to reproduce the HackFest state exactly.

## Observed on 2026-10-03 (verifier): Path B

- Command (same target as `./score_starter -r linux-x86_64`, run as `bazel build` first so the TTY-bound `docker run -it` came after): `bazel --bazelrc=<limits> --output_base=build/linux-x86_64 build --config linux-x86_64 //images/linux_x86_64:run`, limits `--local_ram_resources=8192 --local_cpu_resources=12 --jobs=12` (deprecated flag names still work in Bazel 8.6.0).
- Build: **130 s** ("2431 total actions", critical path 75 s). The output base was partly warm from an earlier killed attempt (1.7 GB in `build/` before), so a cold build is longer.
- Disk: `~/.cache/bazel` 10 G -> 11 G; `build/linux-x86_64` 1.7 G -> 4.2 G.
- Memory: host available 14.7 GB before, lowest sampled 13.5 GB (about 1 GB used by the build). Bazel stopped with `bazel shutdown`; no server left.
- `bazel run ...:run`: image loaded, `score_showcases:latest` (333 MB on disk). The final `docker run --rm -it` fails with "cannot attach stdin to a TTY-enabled container" when there is no terminal, so use a real terminal for the `cli` menu (the cli menu itself was not exercised).
- Inside the image, `/showcases/bin/system_time` ran and printed unix time ticks. `com-api-example` run bare panics with "Config file not found: ./score/mw/com/example/com-api-example/etc/mw_com_config.json" (pass `--service-instance-manifest` or start it through the `cli`).
- Host packages: protobuf-compiler, libclang-dev, qemu-system-x86 present; **lcov is missing** (only needed for coverage; the build did not need it). QEMU boot was not attempted (Path C, not requested).
- Upstream `inc_diagnostics@gateway_cda_int` step: SKIPPED.
