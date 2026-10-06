---
title: Eclipse ThreadX - overview
type: overview
component: threadx
tags: [sdv, threadx]
status: draft
sources:
  - https://github.com/eclipse-threadx/threadx
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust
  - https://blogs.eclipse.org/node/7908
  - https://github.com/eclipse-threadx/threadx
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# Eclipse ThreadX

## What it is / is NOT
Deeply-embedded **RTOS** (picokernel; ex Azure RTOS ThreadX, donated by Microsoft). Marketed as the first open-source RTOS certified for safety-critical use (challenge text, https://blogs.eclipse.org/node/7908 snippet; which standards/versions: unverified, check threadx.io). Companion repos: **NetX Duo** (IP stack, MQTT/TLS etc.), FileX, USBX, GUIX, LevelX, plus learn-samples. It is NOT Linux/POSIX, not an AUTOSAR stack, and not a framework like [[openbsw-overview]] (OpenBSW can run on an RTOS; combination unverified).

## Maturity / version
MIT license; master + tagged releases like `v6.2-rel` (README); 3.5k stars, 935 forks, 51 open issues (https://github.com/eclipse-threadx/threadx). Cores: Cortex-M0..M85, Cortex-A, RISC-V32, ARC, RX, Xtensa, plus Linux/Win32 simulation ports. Vendor SDKs (ST, NXP, Renesas, Microchip) ship it. Latest tag at today's date: **unverified**; not cloned.

## Chapter 3
- Challenge #5 "To ThreadX and Beyond!": evaluation boards **MXChip AZ3166** given to every participant; integrate ThreadX with other SDV projects via **MQTT and REST** (blogs.eclipse.org/node/7908).
- Team **threadx-rust**: ThreadX + NetX in Rust, async executor on EventFlags (32 tasks), embedded-nal networking, MQTT5 cruise-control override via buttons, publishes temperature as a **uProtocol uMessage**; AZ3166 only; flash with probe-rs; targets thumbv7em-none-eabihf (https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust).
- The OTA-to-MCU element in the brief: the AZ3166 firmware update path is **unverified** from fetched pages; MegaBosses OTA (Symphony+uProtocol+Ankaios) is a related story, see [[symphony-overview]].

## Relevance to Hack to the Future
If the embedded target is an MCU/low-end board, ThreadX is the Eclipse-native RTOS with a certified-safety story; the alternative is [[openbsw-overview]] (C++ BSW on S32K/STM32 or POSIX sim). Check [[chapter4-challenge-hack-to-the-future]] for the actual hardware before choosing.

## Quickstart (not run)
Host-side kernel build with the Linux simulation port or Cortex-M cross build:
```bash
git clone https://github.com/eclipse-threadx/threadx && cd threadx
# prereqs: cmake, ninja, arm-none-eabi-gcc
cmake -Bbuild -GNinja -DCMAKE_TOOLCHAIN_FILE=cmake/cortex_m4.cmake .
cmake --build ./build
```
(README command.) For QEMU: the learn-samples / ports have Cortex-M targets runnable in qemu-system-arm (e.g. mps2-an385 / lm3s6965) - exact recipe **unverified**. For the Rust path on hardware: install targets `thumbv7m-none-eabi thumbv7em-none-eabihf`, `flip-link`, `probe-rs-tools`, cmake, ninja, then `cargo run --release --target thumbv7em-none-eabihf --bin <example>`; Linux needs udev rules; set SSID/password/broker in source.

## Pitfalls
- AZ3166 only in threadx-rust; no board = no demo. Wi-Fi/MQTT credentials hard-coded.
- Toolchain setup (Arm GNU, probe-rs, udev) eats the first hour.
- Executor blocks its thread; limited async.
- Safety certificate applies to a specific release/config, not any build (general caution; verify).

## Pros / cons / when not to use
Pros: tiny, permissive license, certified lineage, NetX Duo network stack, hardware vendor support. Cons: C API; Rust bindings are hackathon-grade; not a platform for AI/Linux workloads; MCU-level debugging. Not for HPC-class Linux nodes.

## Hackathon ideas
1. zenoh-pico on ThreadX/NetX publishing to a Zenoh router ([[zenoh-overview]]).
2. Proper up-rust-lite / uProtocol client for ThreadX ([[uprotocol-overview]]).
3. OTA of MCU firmware driven from Symphony target ([[symphony-overview]]).
4. QEMU CI target so teams without boards can run ThreadX.
5. Embassy-style executor for threadx-rust.

## Observed on 2026-10-03 (verifier)
Quickstart cmake build for cortex_m4, status stays `draft` (not as written: the host has no `arm-none-eabi-gcc`).
- Clone `https://github.com/eclipse-threadx/threadx` depth 1 (93387b0, 2026-10-02).
- Cortex-M4 via the toolchain inside the OpenBSW image `openbsw-sovd-demo-openbsw-ecu` (Arm GNU 14.3.Rel1, gcc 14.3.1; it is not on PATH, add `/opt/arm-gnu-toolchain/bin`): `docker run --rm --user $(id -u):$(id -g) -v $PWD:/src -w /src -e PATH=/opt/arm-gnu-toolchain/bin:/usr/local/bin:/usr/bin:/bin --entrypoint /bin/bash <image> -c 'cmake -Bbuild-m4 -GNinja -DCMAKE_TOOLCHAIN_FILE=cmake/cortex_m4.cmake . && cmake --build build-m4'`.
- Result: 193 objects, `build-m4/libthreadx.a` 265,702 bytes (text 36,589, data 125, bss 1,608; ELF attributes v7E-M Thumb-2). Wall time is about 1 s on 32 cores. CMake prints a harmless "CMAKE_TOOLCHAIN_FILE not used" warning.
- Linux simulation port: `cmake -Bbuild-linux -GNinja -DCMAKE_TOOLCHAIN_FILE=cmake/linux.cmake . && cmake --build build-linux` -> `libthreadx.a` 2,030,272 bytes (host gcc, under 1 s).
- Not run: QEMU image or any sample app.
