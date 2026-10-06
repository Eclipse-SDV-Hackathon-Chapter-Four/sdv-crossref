---
title: Eclipse OpenBSW - Overview
type: overview
component: openbsw
tags: [embedded, cpp, bsw, uds, doip, can, freertos, threadx, rust]
status: draft
sources:
  - repos/openbsw/README.md
  - repos/openbsw/libs/bsw/doip/doc/index.rst
  - repos/openbsw/Cargo.toml
  - https://eclipse-openbsw.github.io/openbsw/
  - https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust
  - https://eclipse-openbsw.github.io/openbsw/
last-verified: 2026-10-03
related:
  - "[[openbsw-quickstart]]"
  - "[[openbsw-howto]]"
  - "[[openbsw-reference]]"
  - "[[openbsw-integration-notes]]"
  - "[[opensovd-overview]]"
  - "[[threadx-overview]]"
  - "[[hackfest-esslingen-2026]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
---

# Eclipse OpenBSW - Overview

Looked at: eclipse-openbsw/openbsw commit `9b949941497362c11325f7086c2d04509fa206b8` (2026-10-02), shallow clone in `repos/openbsw`; OpenBSW-Playground commit `e22b9d1e778bcdc185b6e6e0c9e8084136ae1021` (2026-04-28) in `repos/OpenBSW-Playground`.

## What it is
An open-source, C++ **embedded basic-software stack for automotive microcontrollers** (Accenture-originated; the repo copyright headers say Accenture; the "ESR Labs" co-authorship is unverified here). It is *not* an AUTOSAR Classic implementation, not a Linux/POSIX middleware, and not an SDV orchestrator: it is the firmware layer that would run on an ECU (repos/openbsw/README.md).
Licence: Apache-2.0. Build systems: CMake presets (primary) and Bazel (docker image ships bazelisk).

## Feature set (README feature table + libs/)
- Modular libs under `libs/bsw`: `async` (+ `asyncImpl`, `asyncFreeRtos`, `asyncThreadX`), `lifecycle`, `logger`, `timer`, `util`, `io`, `storage`, `cpp2can`, `docan` (diagnostics over CAN), `uds`, `transport`/`transportRouterSimple`, `doip`, `cpp2ethernet`, `lwipSocket`, `cpp2someip`, `middleware`, `asyncConsole`/`stdioConsoleInput`.
- **Lifecycle manager** brings components up/down in numbered run levels (reference app: levels 1-7).
- **Console** with extensible commands (`help`, `can`, `lc`, `logger`, `stats`, `storage`): terminal on POSIX, UART on hardware.
- **Targets**: POSIX (Linux, "virtual ECU"), NXP **S32K148** EVB (reference board), STM32 Nucleo G474RE / F413ZH (presets `nucleo-*`). RTOS: **FreeRTOS** or **ThreadX** (`posix-threadx`, `s32k148-threadx-gcc`, `nucleo-*-threadx-gcc`).
- CAN: via SocketCAN on POSIX; UDS over CAN (DoCAN) and over IP.
- Ethernet: lwIP; POSIX uses a TAP device (`tap0`).

## DoIP state
Upstream has a **DoIP server** (ISO 13400-2:2012, version 02): vehicle identification/announcement (UDP 13400) and TCP diagnostic connections routed to the UDS transport router (`libs/bsw/doip/doc/index.rst`). `DoIpServerSystem` is wired into the reference app at run level 6 with logical address 0x002A on POSIX (0x0600 on another config) (`executables/referenceApp/application/src/app/app.cpp:325`, `executables/referenceApp/configuration/include/app/appConfig.h`). No DoIP client; no TLS mentioned as implemented (doc says "can be used on top of TLS", unverified). README feature table marks Ethernet "On current main". An older Eclipse page snippet says TCP/IP+DoIP was "highest priority": now largely delivered. The HackFest found an interop issue: the Playground overlay patches `DoIpServerConnectionHandler.cpp` to handle diagnostic-message positive/negative ACK payload types (0x8002/0x8003) so the OpenSOVD CDA works (repos/OpenBSW-Playground/OpenBSW-SOVD-Demo/README.md). Whether this is upstreamed: unverified (good small contribution).

## Rust
In-repo Rust is **new in 2026**: Cargo workspace with `rustHelloWorld`, `libs/bsw/logger/rust`, `libs/bsw/async/rust` (embassy-executor 0.7 driven by the C++ async runtime), `libs/rust/console_out`, `panic_handler`; presets `posix-rust` and `s32k148-rust-gcc` (Cargo.toml, CMakePresets.json). Rust 1.96 is the documented CI version (doc/dev/properties.yaml). Manual FFI (`extern "C"`), cbindgen used for logger headers. Observed running on POSIX: see [[openbsw-quickstart]].
The "threadx-rust" repo from Chapter 3 (Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust) is a separate ThreadX+NetX Rust project for the MXAZ3166 board and does **not** mention OpenBSW; link to OpenBSW is unverified (https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust). See [[threadx-overview]], [[chapter3-retrospective]].

## HackFest Esslingen 2026 (28-29 Apr)
An OpenBSW team built **OpenBSW-SOVD-Demo** in the OpenBSW-Playground repo: OpenBSW POSIX virtual ECU (UDS over DoIP, 5 simulated DTCs, 3 simulated sensor DIDs) <- OpenSOVD CDA (SOVD REST :8080, Swagger UI) <- Grafana dashboard. See [[hackfest-esslingen-2026]], [[openbsw-howto]], [[opensovd-overview]].

## Maturity
Active (commit 2026-10-02; 449-633 ninja steps indicates a large codebase). CHANGELOG.md top entry is 0.2.0 (2024-11-19), so formal releases lag `main`; README says features land "on current main". Treat `main` as the version.

## Pros / cons
Pros: builds and runs on a laptop in ~15-20 s (32 cores), no hardware; real UDS/DoCAN/DoIP stacks; lifecycle/console/logging idioms resemble production ECU code; Apache-2.0; real S32K148/STM32 targets; Rust+ThreadX options.
Cons: C++ ETL-heavy embedded style, steep for a 2-day hack; no Zenoh/uProtocol/KUKSA/iceoryx integrations upstream; DoIP server only (no client); POSIX ECU needs sudo for vcan/tap; sparse app-level demo content (DemoSystem sends a counter CAN frame); docs reference an older gcc 11/Ubuntu 22.04 baseline while docker uses Ubuntu "resolute".

## When not to use
If a team only needs a data-plane/service demo (use KUKSA/uProtocol/Zenoh with scripts), if nobody on the team writes C++, or if they have no sudo (vcan/TAP can't be created).

## Relevance to Chapter 4
- [[chapter4-challenge-hack-to-the-future]] (child presence): OpenBSW is a natural "embedded controller" for a presence sensor ECU: add a DemoSystem-style component reading GPIO/ADC (on POSIX: simulated), publishing over CAN (vcan) and exposing a DID/DTC via UDS/DoIP; bridge CAN -> KUKSA with a feeder. The demo frame 0x558 -> `Vehicle.Speed` via kuksa-can-provider was reproduced on 2026-10-03 ([[openbsw-howto]], gap B6); a DBC with real presence signals is still open. (corrected 2026-10-06, see [[openbsw-howto]])
- [[chapter4-challenge-doctor-whodunit]] (ECU faults): the Playground demo is almost exactly this: injectable DTCs + sensor DIDs + SOVD REST + Grafana. Reuse it directly.
See [[openbsw-integration-notes]] for the project-by-project table.
