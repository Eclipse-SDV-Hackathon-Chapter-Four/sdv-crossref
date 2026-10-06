---
title: OpenBSW - How-to recipes
type: howto
component: openbsw
tags: [openbsw, howto, uds, doip, sovd, grafana, pitfalls]
status: draft
sources:
  - repos/OpenBSW-Playground/OpenBSW-SOVD-Demo/README.md
  - repos/OpenBSW-Playground/OpenBSW-SOVD-Demo/HACKATHON.md
  - repos/openbsw/doc/dev/learning/
  - https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
last-verified: 2026-10-03
related:
  - "[[openbsw-overview]]"
  - "[[openbsw-quickstart]]"
  - "[[openbsw-integration-notes]]"
  - "[[opensovd-overview]]"
---

# OpenBSW - How-to recipes

Status draft: recipes below come from docs/READMEs; only the plain POSIX build/run was executed (see [[openbsw-quickstart]]).

## Run the HackFest virtual-ECU + OpenSOVD CDA + Grafana demo
Repo: https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground (commit e22b9d1, 2026-04-28; README says "TTL: end of April 2026", "non productive", contact Thomas.Fleischmann@accenture.com; repo may vanish, so fork it). Layout: top-level `openbsw` submodule + `OpenBSW-SOVD-Demo/`.
```bash
git clone --recurse-submodules https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground
cd OpenBSW-Playground/OpenBSW-SOVD-Demo
./demo.sh            # builds ECU, starts ECU + CDA, runs smoke test (needs sudo for TAP, tmux optional)
./demo.sh --live     # + tmux status/log split;  ./demo.sh --stop
# or: docker compose up --build   (openbsw-ecu @192.168.0.201:13400, sovd-cda :8080, grafana :3000)
curl http://localhost:8080/sovd/v1/components
curl http://localhost:8080/sovd/v1/components/openbsw-ecu/faults
curl http://localhost:8080/sovd/v1/components/openbsw-ecu/data/CF10
# Swagger: http://localhost:8080/docs ; Grafana: http://localhost:3000
```
Build only: `cmake --preset posix-freertos-sovd && cmake --build build/posix-freertos-sovd` -> `app.sovdDemo.elf`.
Content: 5 simulated DTCs (engine overtemp, low battery, comm fault, sensor malfunction, brake), 3 random-walk sensor DIDs (engine temp, battery V, speed); UDS 0x19 (sub 0x01/0x02/0x06), 0x14, 0x22 added via overlay (no patch of upstream); two CDAs: real OpenSOVD CDA (Rust, needs MDD file; prebuilt 26 MB binary via **Git LFS**, so `git lfs` must be installed) or a Python/FastAPI stub with hardcoded DIDs. Grafana uses the Infinity datasource and `host.docker.internal:8080`.
Not executed by me (Docker present, but needs TAP/sudo and large submodules).

## Add a console command / system
Study `executables/referenceApp/application/src/systems/DemoSystem.cpp` (1 Hz CAN frame 0x558) and `consoleCommands/`. A new feature = a "System" class registered via `lifecycleManager.addComponent("name", sys.create(TASK_X), level)` in `app.cpp`. Docs: `doc/dev/learning/{lifecycle,console,commands,logging}`.

## Add a UDS DID (e.g. "child present")
In `UdsSystem` add a `ReadIdentifierFromMemory`/custom job like `_read22Cf01(0xCF01, data)`; for live values follow the Playground's `ReadIdentifierSimulated`. Test over CAN: `cansend vcan0 02A#0322<DID hi><DID lo>00000000`. Test over DoIP: via CDA.

## Test with pytest
`test/pyTest` (`pip install -r requirements.txt`, `pytest --target=posix`), target config `target_posix.toml`. `tools/UdsTool` is a Python UDS CLI used by those tests.

## Pitfalls (from docs and observation)
- `vcan0` and `tap0` need root; without them the app still runs but logs `CAN: ERROR ... Failed to ioctl socket` and `TapEthernetDriver start failed!` (observed).
- WSL: stock kernel lacks SocketCAN; custom kernel needed (doc/dev/learning/setup/setup_wsl_socketcan.rst).
- `tap0` must be removed before testing the S32K148 on same host (`sudo ip tuntap del dev tap0 mode tap`). The vault's `./test_setup.sh --apply` creates tap0 and its VLAN `tap0a0` as upstream's `tools/enet/bring-up-ethernet.sh` does; `./test_setup.sh --remove` deletes both.
- Docs state gcc 11/Ubuntu 22.04/cmake 3.28 baseline; Docker image is pinned to a newer Ubuntu and arm-none-eabi-gcc 14.3.rel1 + LLVM-ET 19.1.1: for S32K148/STM32 builds use the Docker image rather than apt toolchains.
- Console input is read from stdin; log timestamps are ms since start and are interleaved with the prompt.
- DoIP interop: upstream server ignored/rejected diagnostic-message ACK payloads from the CDA (Playground patch). If a DoIP client misbehaves, check this first.
- Rust preset needs a recent rustc (docs pin 1.96) and uses vendored cargo deps (`libs/3rdparty/cargo-vendor`); no network needed.
- Known open issues (GitHub, 2026-10-03): #612 flaky tests under slow CI (wall clock), #613 defunct `bspCharInputOutputMock` target, #511 warning on s32k148-freertos-gcc.
- Real hardware (S32K148EVB) needs NXP S32 Design Studio/GDB server, TJA1101 daughter board for Ethernet, and on some boards a resistor depopulated (doc/dev/learning/ethernet). Not feasible in 2 days without a board.

## Hackathon ideas
1. "Child presence ECU": new `PresenceSystem` (simulated sensor via console command `presence set 1`), CAN frame on vcan + DID + DTC "sensor fault"; bridge CAN->KUKSA (see [[vss-kuksa-overview]]). 
2. Doctor Whodunit: extend Playground DTC simulator with injectable faults via console, show in Grafana via SOVD ([[opensovd-overview]]).
3. Upstream the DoIP ACK fix / a DoIP client test / DoIP over TLS.
4. Rust task on the embassy-executor glue that reads a simulated sensor and posts to CAN.
5. Zenoh/uProtocol gateway process on Linux that reads vcan0 (no OpenBSW change) ([[zenoh-overview]], [[uprotocol-overview]]).
6. openDuT: expose the TAP/vcan to a test rig ([[opendut-overview]]).

## 9. CAN to KUKSA feeder on vcan0
Files: `components/openbsw/examples-can-feeder/` (`openbsw-demo.dbc`, `mapping.json`, `can-provider.ini`). The ECU sends `0x558` (4 bytes, big-endian counter) once a second; the DBC signal is `SG_ Counter : 7|32@0+`, mapped to `Vehicle.Speed` (float).
```bash
cd components/openbsw/examples-can-feeder
docker run -d --name vf-databroker --network host ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1 --insecure --port 55587
# ECU (own terminal, needs a tty): repos/openbsw/build/posix-freertos/executables/referenceApp/application/Release/app.referenceApp.elf
docker run -d --name vf-can --network host -v $PWD:/config:ro \
  ghcr.io/eclipse-kuksa/kuksa-can-provider/can-provider:0.5.0 --config /config/can-provider.ini grpc://127.0.0.1:55587
.venv/bin/python -c "from kuksa_client.grpc import VSSClient; c=VSSClient('127.0.0.1',55587); c.connect(); print(c.get_current_values(['Vehicle.Speed']))"
```
Pitfalls: the databroker address must be the positional `grpc://host:port` argument; `ip`/`port` in `[general]` of the ini are ignored (provider tried 55555 and failed with "Connection refused"). `use_socketcan = True` plus `port = vcan0` is needed; `dbc2val = True`, `val2dbc = False`.

## Observed on 2026-10-03 (verifier)
Docker 29 (root daemon), vcan0 present. `--network host` alone was enough: no `--cap-add NET_ADMIN`, no `--privileged`. Provider log: `Using CAN frame ID whitelist=[{'can_id': 1368,...}]`, `Vehicle.Speed is already registered with type FLOAT`, `Update datapoint requests sent to kuksa.val so far: 4`. kuksa-client reads: `Vehicle.Speed = 22.0` at 16:34:40, `25.0` at 16:34:43 (counter value, +1 per second). Works with databroker 0.7.1 (v2 API) and can-provider 0.5.0. Fallback python-can script not needed. Run dir: `.local-verify/can-feeder/`.
