---
title: HackFest repo - OpenBSW-Playground (OpenBSW virtual ECU + OpenSOVD CDA + Grafana)
type: event
component: openbsw
tags: [event, hackfest, openbsw, opensovd, cda, doip, uds, grafana, mdd, reusable]
status: draft
sources:
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground
  - repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/README.md
  - repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/HACKATHON.md
  - repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/doc/demo-architecture.md
  - repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/real-sovd-cda/README.md
  - repos/hackfest-OpenBSW-Playground/doc/sovd-demo/rg6_interop_fixes.rst
  - repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/docker-compose.yaml
last-verified: 2026-10-03
related:
  - "[[hackfest-esslingen-2026]]"
  - "[[openbsw-overview]]"
  - "[[opensovd-overview]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
---

# OpenBSW-Playground (HackFest Esslingen 2026, track "OpenSOVD (CDA) works with OpenBSW")

The most complete and reusable public HackFest result. Repo: https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground (description "Initial DoIP - CDA Test"). Local clone `repos/hackfest-OpenBSW-Playground` @ e22b9d1 (2026-04-28, Tom Fleischmann). Context: [[hackfest-esslingen-2026]].

**What it is**: a self-contained demo where an [[openbsw-overview]] POSIX/FreeRTOS reference ECU serves UDS over DoIP, and an [[opensovd-overview]] Classic Diagnostic Adapter (or a Python stub) turns that into a SOVD REST API, with Grafana on top. **What it is NOT**: production code. The README says "TTL: end of April 2026" and "non productive - JWT tokens are no secret". Treat it as unmaintained since the event.

## Architecture (from doc/demo-architecture.md, docker-compose.yaml)
| Element | Value |
|---|---|
| ECU | `app.sovdDemo.elf`, C++, POSIX + FreeRTOS, lwIP userspace TCP/IP on `tap0`, IP 192.168.0.201, DoIP logical address **0x002A**, port 13400 |
| UDS services | 0x10, 0x14 (new), 0x19 (new; subfunctions 0x01/0x02/0x06), 0x22, 0x2E, 0x28, 0x31, 0x3E, 0x85 |
| Simulated data | DTCs 0x010100 (overtemp), 0x010200 (low battery), 0x010300 (comm fault), 0x010400 (sensor), 0x010500 (brake); DIDs 0xCF01 static, 0xCF02 ADC, 0xCF03 writable, 0xCF10 EngineTemp, 0xCF11 BatteryVoltage, 0xCF12 VehicleSpeed (random walk) |
| Real CDA | Eclipse OpenSOVD CDA (Rust, axum, tokio), submodule pinned at `ce3a566`; IP 192.168.0.10, tester address 0x0EE0; REST `:8080/vehicle/v15/...`; JWT via `POST /vehicle/v15/authorize` (any credentials); health `/health` |
| Stub CDA | `sovd-cda/main.py` (FastAPI + `doipclient`), `/sovd/v1/components/{id}/faults|data`, Grafana helpers `/api/sensors/*`, `/api/faults/*`, catalog in `sovd-cda/catalog.json` |
| Diagnostic DB | MDD (FlatBuffers) `real-sovd-cda/odx-gen/OpenBSW.mdd`, generated from `openbsw_ecu.json` by `generate_mdd.py`; alternative route PDX (`generate_openbsw.py`, odxtools 11) -> `odx-converter` (submodule `b4f516e`) |
| CDA config | `real-sovd-cda/opensovd-cda.toml`: `onboard_tester=false`, `[database] fallback_to_base_variant=true`, `[doip] send_diagnostic_message_ack=false`, `send_timeout_ms=5000`, tester subnet 255.255.0.0 |
| Grafana | `grafana/grafana-oss:latest` + `yesoreyeram-infinity-datasource`; dashboard `grafana/dashboards/openbsw.json` queries `host.docker.internal:8080/vehicle/v15/components/openbsw/...`; datasource has a hardcoded bearer JWT (`grafana/provisioning/datasources/sovd.yaml`) |
| Build | CMake overlay `OpenBSW-SOVD-Demo/CMakeLists.txt` (preset `posix-freertos-sovd`); upstream `openbsw/` submodule pinned at `07b7551` and left **unmodified**; the overlay shadows `UdsSystem.h` and swaps `DoIpServerConnectionHandler.cpp` in the `doip` target |

## Run it (recipe; NOT executed here)
Prerequisites: Linux, Docker, sudo (for TAP) or Docker with NET_ADMIN, CMake + Ninja + GCC, Python 3.10+, `tmux` (only for `--live`). Codespaces extras: `OpenBSW-SOVD-Demo/prepare-gh-codespaces.md`.
```bash
cd repos/hackfest-OpenBSW-Playground
git submodule update --init --depth 1 openbsw OpenBSW-SOVD-Demo/real-sovd-cda/classic-diagnostic-adapter
cd OpenBSW-SOVD-Demo
# A) local, Python stub CDA (fastest):
./demo.sh            # TAP via sudo, builds app.sovdDemo.elf, starts ECU + stub CDA + Grafana, smoke test
curl http://localhost:8080/sovd/v1/components/openbsw-ecu/faults
# B) local, real Eclipse CDA (Rust build in Docker, several minutes the first time):
./demo.sh --real-cda
TOKEN=$(curl -s -XPOST localhost:8080/vehicle/v15/authorize -H 'Content-Type: application/json' \
  -d '{"client_id":"x","client_secret":"y"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
curl -H "Authorization: Bearer $TOKEN" localhost:8080/vehicle/v15/components/openbsw/data/EngineTemp
# C) all in Docker:
docker compose --profile stub-cda up --build     # or --profile real-cda
./demo.sh --stop
```
Expected (from the README): 5 DTCs from `/faults`, live EngineTemp values, Swagger at `:8080/docs` (stub), Grafana at `:3000`. The `access_token` field name is taken from the architecture doc's sequence diagram; unverified against the CDA version.

## Findings that matter beyond the demo (doc/sovd-demo/rg6_interop_fixes.rst)
- **REQ_RG6_001**: the CDA sends `DiagnosticMessagePositiveAck` (0x8002) back to the ECU; OpenBSW's DoIP server answered with Generic NACK 0x01 (unknown payload type). Fixed **only in the overlay** (`openbsw-overlay/libs/doip/src/doip/server/DoIpServerConnectionHandler.cpp`, lines 284-290). This is an upstream OpenBSW contribution waiting to happen.
- **REQ_RG6_002**: the CDA's unconditional ACK confused response parsing, so set `send_diagnostic_message_ack=false`.
- **REQ_RG6_003**: the default 1 s send timeout is too short for lwIP, so use 5000 ms.
- **REQ_RG6_004**: the POSIX ECU stops on SIGTTOU when backgrounded (`Uart::init()` calls `tcsetattr`).
- **REQ_RG6_005**: use standard DoIP, not DOBT (`onboard_tester=false`).
- OpenBSW upstream commit 8d18b1a1 ("Change estd::slice to etl::span in DoIP") broke the overlay, hence the pin to `07b7551` (commit b657100 on `development`).

## Branches
| Branch | What |
|---|---|
| `main` | Event state (e22b9d1) |
| `development`, `feature/release-pipeline` | Release pipeline (vendored licenses, `RELEASING.md`); ECU tests made advisory (`continue-on-error`) |
| `features/jkk_FLUX1000` (f9fdafc, 2026-04-29, Janick Kaltenmark, Softing AG) | Adds a **FLXC1000 "Flux Capacitor" ECU**: `openbsw-overlay/app/{include,src}/systems/Flxc1000UdsSystem.*`, `UdsSystemSelector.h`, `Flxc1000Simulator.*`, MDDs `FLXC1000.mdd`, `FLXCNG1000.mdd`, `FSNR2000.mdd`, base ODX for ISO 14229-5 on ISO 13400-2, a Grafana dashboard `flxc1000.json`, `[security] enabled=false` in the CDA config. DID 0xF200 `FluxCapacitorPowerConsumption`. Unmerged; contains a committed `ecu.log` and `__pycache__` |

## Docs drift (fix before trusting the docs)
- README "Pre-built CDA Binary ... checked into `real-sovd-cda/bin/` via Git LFS", but `real-sovd-cda/bin/README.md` says the binary "is intentionally not stored in this repository".
- HACKATHON.md "Code Map" and Challenges 1-2 point to `../openbsw/executables/referenceApp/...` and `../openbsw/libs/bsw/uds/include/uds/dtc/` as "(new)". Those files live in `OpenBSW-SOVD-Demo/openbsw-overlay/`.
- README "Quick Start (Docker Compose)": `docker compose up --build` "Three services start", but the CDA services are behind `profiles` (`stub-cda` / `real-cda`). Same contradiction in `real-sovd-cda/README.md` ("Default: Python stub CDA").
- HACKATHON.md says the CDA "uses the `doipclient` Python library". That applies to the stub only.

## Chapter 4 relevance
- [[chapter4-challenge-hack-to-the-future]]: the OpenBSW zonal controller can expose its window/fan/alarm state as DIDs/DTCs through this exact stack. The FLXC1000 branch already models a Flux Capacitor ECU.
- [[chapter4-challenge-doctor-whodunit]]: use the DTC simulator pattern for "stuck/stale cell temperature" -> confirmed DTC, read through SOVD as the independent "diagnostic truth". The pytest tiers in `tests/` (unit, ecu, sovd, grafana) give a ready-made verdict harness.

## Repo-level pitfalls
- Submodules are not initialised by a plain clone; the CDA submodule is large.
- Two CDA APIs (stub `/sovd/v1` vs real `/vehicle/v15`). Pick one before writing a client.
- Grafana with the real CDA relies on the hardcoded JWT in the datasource provisioning file; if the CDA's signing secret changes, the panels go blank (inference).

## Verification attempt 2026-10-03: FAILED (as written); passes with 5 fixes
Ran `git submodule update --init --depth 1 openbsw` then `docker compose --profile stub-cda up --build -d` in `OpenBSW-SOVD-Demo`. Compose as committed does not work on current openbsw @07b7551:
```
failed to compute cache key ... "/files/.bash_profile": not found      (build context ../openbsw, Dockerfile expects docker/development)
openbsw-ecu: ioctl(TUNSETIFF): Operation not permitted                 (Dockerfile ends USER build; needs root)
openbsw-ecu: /bin/bash: -G: command not found                          (folded `entrypoint: >` splits the cmake args across lines)
sovd-cda: ECU poll failed: [Errno 111] Connection refused              (lwIP lives on tap0, never bridged to the container's eth0)
openbsw-ecu "unhealthy" forever; sovd-cda never starts                 (healthcheck uses `ss`, lwIP socket is invisible)
```
With an override file (build context `../openbsw/docker/development`, `user: root`, single-line entrypoint, tap0+eth0 bridged via br0, `up -d --no-deps sovd-cda`; see `evidence/verify-run-1.md` and `evidence/verify-run-1-r1-override.yaml`) the demo worked: `curl localhost:8080/sovd/v1/components/openbsw-ecu/faults` returned `count: 5` (0x010100..0x010500) and `/data` returned 6 DIDs; Grafana answered 200 (remapped to :3300 only because :3000 was busy on the test host). Total time about 9 min including the ~3.5 min image build and ~1.5 min ECU compile. Use `./demo.sh` (TAP on the host) if you want the documented path; it was not run (needs sudo).

## Observed on 2026-10-03 (verifier): real CDA profile (`--profile real-cda`)
Status stays `draft`: the real-cda path needs a second override and a locally built CDA.
- The `classic-diagnostic-adapter` submodule is empty and `real-sovd-cda/bin/` holds only a README (no LFS binary, `git lfs ls-files` empty). The CDA was built from `repos/opensovd-cda` (commit e6f4b8f, `cargo build --release --bin opensovd-cda`, 40 s on the reused target dir, 37 MB).
- The Dockerfile's `debian:trixie-slim` runtime is older than the host glibc 2.43, so `playbook/fixes/openbsw-sovd-demo-real-cda.override.yaml` runs the host binary inside `ubuntu:26.04` with the demo's MDD and toml mounted (`export CDA_BIN=<abs path>`).
- Commands: `docker compose -f docker-compose.yaml -f <fixes>/openbsw-sovd-demo.override.yaml -f <fixes>/openbsw-sovd-demo-real-cda.override.yaml --profile real-cda up -d --no-deps openbsw-ecu`, wait for "Socket prepared at port 13400" (10 s, the ECU build dir is baked into the image), then the same with `real-sovd-cda`.
- CDA log: "Routing activated", "Connected to gateway", "ECU connected - setting connectivity to Online ecu_name=openbsw", "CDA fully initialized"; `/health/ready` 204. Warnings seen: variant detection failed (no SESSION state chart), "No SDG found in DB". Harmless.
- Base path is `/vehicle/v15`, and a Bearer token is required (401 otherwise): `POST /vehicle/v15/authorize` with any client_id/secret. `GET /vehicle/v15/components` -> `{"items":[{"id":"openbsw",...}]}`; component state Online, logical_address 0x2a.
- `.../components/openbsw/faults` -> 5 DTCs: 010100 Engine Coolant Temperature Sensor Circuit - Over Temperature (mask 2B), 010400 Sensor Malfunction - General (2B), 010300 CAN/Ethernet Communication Fault (2B), 010500 Brake System Fault (2B), 010200 BattVoltLow (00). `/data` lists 7 DIDs; `/data/BatteryVoltage` -> `{"BatteryVoltage":121}`.
- `/data/Identification` returns an ECU negative response (SID 0x22, NRC 0x31 request out of range; ECU answered `7F 22 31`).
- UDS over DoIP (RUST_LOG=debug, timings ~0.5-1 ms): request `FaultMem_ReportDTCByStatusMask` payload `0xFF` (UDS 19 02 FF); response `59 02 FF 01 01 00 29  01 03 00 2B  01 04 00 2B  01 05 00 2B` (DTC 010100 status 0x29, 010300/010400/010500 status 0x2B; the 010200 entry is reported by the CDA with mask 00). Raw `Sending raw UDS packet` is trace level only.
- Teardown: `docker rm -f real-sovd-cda`, `docker compose ... down -v`; nothing left.

## Observed on 2026-10-03 (verifier): `features/jkk_FLUX1000` (FLXC1000)
## Verification attempt 2026-10-03: FAILED
- Branch (f9fdafc) adds 38 files (+92k lines, mostly generated MDD JSON): `Flxc1000UdsSystem`, `Flxc1000Simulator`, `UdsSystemSelector.h`, `appConfig.h` (ECU logical address 0x1000 under `USE_FLXC1000_ECU`), `TransportConfiguration.h`, FLXC1000/FLXCNG1000/FSNR2000/functional_groups MDDs plus ODX base files, a Grafana `flxc1000.json`, a `--flxc1000` mode in `demo.sh` (real CDA only) and a patched overlay `DoIpServerConnectionHandler.cpp`. It also bumps the `openbsw` submodule from 07b7551 to 9950d75. `docker-compose.yaml` is unchanged, so `-DUSE_FLXC1000_ECU=ON` must be added by an override (`playbook/fixes/openbsw-sovd-demo-flxc1000.override.yaml`).
- Build failure with the pinned-on-main openbsw 07b7551: the branch's overlay `DoIpServerConnectionHandler.cpp` uses `etl::span` and `derived_object_pool::create`, openbsw 07b7551 still has `estd::slice` (6 compile errors, line 288/315/365/493/543/581).
- Commit 9950d75 is not fetchable from github.com/eclipse-openbsw/openbsw ("not our ref"; likely a fork or rewritten history). Upstream main at cda70199 (30 Apr 2026) fails differently: ninja "libs/bsw/middleware/tools/cpp_generator/jinja2cpp.py ... missing", so the overlay CMakeLists needs porting. The ECU was therefore never started, neither with the stub nor with the real CDA.
- What the branch exposes, from its sources (not run): ECU FLXC1000, DIDs 0xF100 Identification, 0xF186 ActiveDiagnosticSession, 0xF190 VIN (writable), 0xF200 FluxCapacitorPowerConsumption (4 bytes); 6 DTCs 0x01E240..0x01E245 ("DTC Code 1..6", `Flxc1000Simulator` toggles status bits randomly). This matches the CDA ecu-sim ECU in [[opensovd-quickstart]].
- Worktree removed; scratch clones deleted.
