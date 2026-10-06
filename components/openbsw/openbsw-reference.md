---
title: OpenBSW - Reference
type: reference
component: openbsw
tags: [openbsw, reference, presets, layout]
status: draft
sources:
  - repos/openbsw/CMakePresets.json
  - repos/openbsw/doc/dev/properties.yaml
  - repos/openbsw/Cargo.toml
  - repos/openbsw/docker/development/Dockerfile
last-verified: 2026-10-03
related:
  - "[[openbsw-overview]]"
  - "[[openbsw-quickstart]]"
---

# OpenBSW - Reference

## Links
- Repo https://github.com/eclipse-openbsw/openbsw (commit 9b94994, 2026-10-02) ; docs https://eclipse-openbsw.github.io/openbsw/ (Doxygen, coverage, puncover)
- Playground https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground (commit e22b9d1)
- HackFest blog: https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
- Chapter 3 threadx-rust: https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust
- Snapshots: page snapshots of 2026-10-03 (not published); upstream https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust

## CMake presets (CMakePresets.json)
Run targets: `posix-freertos`, `posix-threadx`, `posix-rust`, `s32k148-freertos-gcc`, `s32k148-freertos-clang`, `s32k148-threadx-gcc`, `s32k148-threadx-clang`, `s32k148-rust-gcc`, `nucleo-g474re-{freertos,threadx}-gcc`, `nucleo-f413zh-{freertos,threadx}-gcc`. Unit-test configs: `tests-{posix,s32k1xx,stm32}-{debug,release}`. Output: `build/<preset>/executables/referenceApp/application/Release/app.referenceApp.elf`. Bazel: `bazel build //...`, `--config=s32k148`.

## Tool versions (doc/dev/properties.yaml)
gcc 11.x, cmake 3.28, Ubuntu 22.04, gcc-arm-none-eabi 14.3.rel1, LLVM-ARM 19.1.1, Rust 1.96.0, S32DS 2.2.

## Source layout
`libs/bsw/*` (modules), `libs/3rdparty` (etl, lwip, freeRtos, threadx, googletest, cmsis, corrosion, printf, cargo-vendor), `platforms/{posix,s32k1xx,stm32}`, `executables/referenceApp` (application, consoleCommands, udsConfiguration, transportConfiguration, lwipConfiguration, rustHelloWorld, platforms/*), `executables/unitTest`, `test/pyTest`, `tools/{UdsTool,can,enet,someip,tracing,...}`, `docker/`.

## Reference-app run levels (doc/dev/learning/uds)
L4 TransportSystem; L5 DoCanSystem, EthernetSystem, StorageSystem; L6 DoipServerSystem (+ SomeIpSystem); L7 UdsSystem. Tasks: TASK_UDS, TASK_CAN, TASK_ETHERNET.

## Network / ID constants
CAN vcan0; UDS request ID 0x7E0, response 0x7E8 (observed at commit 9b94994; the upstream doc's 0x02A/0x0F0 does not answer; corrected 2026-10-03, see [[openbsw-quickstart]]); demo frame 0x558 @1 Hz. ECU IP 192.168.0.201 (POSIX tap0 host side 192.168.0.10), S32K148 192.168.0.200; UDP echo 49444, TCP echo 49555; DoIP 13400; DoIP logical address 0x002A (POSIX) / 0x0600 (other config).

## UDS services present in libs/bsw/uds/include/uds/services
sessioncontrol, ecureset, readdata (0x22), writedata (0x2E), securityaccess, communicationcontrol, controldtcsetting, routinecontrol, testerpresent, inputoutputcontrol, readdtcinformation, cleardiagnosticinformation (dirs exist upstream; the Playground adds its own DTC store/0x19/0x14 as overlay, so upstream DTC support depth is unverified). Upstream has a programming session, a bootloader handover hook and constants for 0x34/0x36, but **no** download/transfer services and **no** bootloader; flashing over SOVD comes from the CDA's `x-sovd2uds-download` ([[the-hpc-is-the-mcus-update-gateway]]).

## Rust crates (Cargo.toml workspace)
rustHelloWorld, openbsw-logger, openbsw_async (embassy-executor 0.7), openbsw_console_out, openbsw_panic_handler; `critical-section`, `log`, `paste`.
