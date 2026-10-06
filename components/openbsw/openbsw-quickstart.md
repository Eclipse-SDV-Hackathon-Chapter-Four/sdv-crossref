---
title: OpenBSW - Quickstart (POSIX virtual ECU)
type: quickstart
component: openbsw
tags: [openbsw, quickstart, posix, cmake]
status: verified
sources:
  - repos/openbsw/doc/dev/learning/setup/setup_posix_build.rst
  - repos/openbsw/doc/dev/learning/can/index.rst
  - repos/openbsw/doc/dev/learning/uds/index.rst
  - repos/openbsw/doc/dev/learning/ethernet/index.rst
last-verified: 2026-10-03
related:
  - "[[openbsw-overview]]"
  - "[[openbsw-howto]]"
---

# OpenBSW - Quickstart (POSIX virtual ECU)

Verified: build + run only (no sudo available, so vcan/tap parts were NOT executed; they are from the docs).

## Prerequisites
gcc/g++ (docs: >=11, tested 15.2.0), cmake >= 3.28 (tested 4.2.3), ninja, make. No git submodules needed (3rd-party FreeRTOS/ThreadX/lwIP/etl/googletest are vendored in `libs/3rdparty`). Optional: rustc/cargo (tested 1.98.1) for Rust preset; `can-utils` for candump/cansend; docs say Rust 1.96.

## Build (FreeRTOS on POSIX)
```bash
git clone --depth 1 https://github.com/eclipse-openbsw/openbsw && cd openbsw
cmake --preset posix-freertos
cmake --build --preset posix-freertos --parallel
# -> build/posix-freertos/executables/referenceApp/application/Release/app.referenceApp.elf
```
Docker alternative (README): `DOCKER_UID=$(id -u) DOCKER_GID=$(id -g) docker compose run --build development` then the same cmake commands inside (image includes arm-none-eabi gcc 14.3, LLVM-ET 19.1.1, bazelisk). Not run here.

## Run
```bash
build/posix-freertos/executables/referenceApp/application/Release/app.referenceApp.elf
```
Console is the same terminal: type `help`. Ctrl-C exits.

## Optional: CAN and UDS over CAN (needs sudo, from docs)
```bash
sudo ip link add dev vcan0 type vcan && sudo ip link set vcan0 mtu 16 && sudo ip link set up vcan0   # or tools/can/bring-up-vcan0.sh
candump vcan0 &
cansend vcan0 7E0#0322CF0100000000     # UDS 0x22 ReadDataByIdentifier DID 0xCF01; request 0x7E0, response on 0x7E8 (upstream doc says 0x02A/0x0F0, which does not answer at commit 9b94994; corrected 2026-10-03, see the observed section below)
```
App sends a counter frame ID 0x558 every second (DemoSystem). Docs show a "Flow control timeout" warning after the response: expected in that example.

## Optional: Ethernet / DoIP (needs sudo, from docs)
```bash
./tools/enet/bring-up-ethernet.sh      # creates tap0 (192.168.0.10/24) + VLAN tap0a0 (192.168.2.10)
build/.../app.referenceApp.elf         # ECU IP 192.168.0.201; DoIP port 13400, logical addr 0x002A
ping 192.168.0.201; telnet 192.168.0.201 49555   # TCP echo; UDP echo on 49444
```
DoIP tester: not in upstream docs; use the Playground CDA (see [[openbsw-howto]]) or any DoIP client (e.g. python doipclient, unverified).

## Rust and ThreadX variants
`cmake --preset posix-rust && cmake --build --preset posix-rust`; `posix-threadx` likewise.

## Observed on 2026-10-03
Host: Linux 7.0.0-31, 32 cores, gcc 15.2.0, cmake 4.2.3, ninja, rustc 1.98.1. Commit 9b94994.
- `posix-freertos`: configure + build 449 steps, **real 11.0 s** (user 2m22s); ELF 1,233,144 bytes.
- `posix-rust`: 454 steps, **real 15.5 s**. Output includes "Hello Rust!", "Hello from Rust!", "Rust add(3, 4) = 7", then alternating "Rust async task A/B: tick N".
- `posix-threadx`: 633 steps, **real 20.1 s**, links OK (not run).
- Run (no vcan, no tap): prints `hello`, lifecycle logs (levels 1-7) as "0: RefApp: LIFECYCLE: INFO: Initialize level 1" ..., and two non-fatal errors:
  - `ETHERNET: CRITICAL: TapEthernetDriver start failed!`
  - `CAN: ERROR: [SocketCanTransceiver] Failed to ioctl socket (node=vcan0, error=-1)`
  App keeps running. Piping `help` on stdin printed the console command list: can (info, send), help, lc (reboot, poweroff, level, udef, pabt, dabt, assert), logger (level), stats (cpu, stack, all), storage (write, fill, read).
- Output contains ANSI colour codes; the clock counter in log lines is ms since start.

## Observed on 2026-10-03 (verifier): CAN over vcan0
Host had `vcan0` UP mtu 16 (`./test_setup.sh`), `tap0` absent (needs root, DoIP-over-tap skipped). Binary: `repos/openbsw/build/posix-freertos/.../app.referenceApp.elf` (reused). Logs: `.local-verify/candump1.log`, `candump2.log`, `app1.log`, `app2.log`.
- No `Failed to ioctl socket` error in the log; CAN and DoCAN start. Only `TapEthernetDriver start failed!` remains (no tap0), the app keeps running.
- Frame `0x558` [4 bytes] every 1.000 s (`00 00 00 00`, `00 00 00 01`, ... big-endian counter in the last byte; CAN id and counter both from `CanDemoListener`).
- **Corrected: the doc's `02A#...` / `0x0F0` addressing does NOT work at this commit (9b94994).** `cansend vcan0 02A#0322CF0100000000` got no response (twice). The DoCAN channel uses OBD addressing: request `0x7E0`, response `0x7E8` (`executables/referenceApp/application/src/systems/DoCanSystem.cpp`, `include/config/DoCanConfig.h`; extended addressing 0x600/0x601 is also configured, tester id 0xF4, no reply to my unframed-ext test).
- `cansend vcan0 7E0#0322CF0100000000` -> `7E8#101B62CF01010200` (multi-frame first frame: 0x62 positive, DID CF01, 0x1B bytes; the ECU waits for flow control, so a candump-only test shows the "Flow control timeout" warning; use `isotpsend`/`isotprecv` or `cansend 7E0#30...` for the rest).
- `7E0#0322CF0200000000` -> `7E8#0762CF0200000002` (positive, DID CF02 = `00 00 00 02`).
- `7E0#0210010000000000` (DiagnosticSessionControl default) -> `7E8#06500100 3201F4CC` = `50 01 00 32 01 F4` positive; session 03 (extended) also `50 03 00 32 01 F4`.
- `7E0#023E000000000000` TesterPresent -> `7E8#027E00CCCCCCCCCC`.
- Round trip latency about 1-2 ms.
