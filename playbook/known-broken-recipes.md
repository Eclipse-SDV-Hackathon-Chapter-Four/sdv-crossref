---
title: Known-broken recipes and their fixes (verified 2026-10-03)
type: playbook
component: none
tags: [verification, fixes, blueprints, openbsw, opensovd]
status: verified
sources:
  - evidence/verify-run-1.md (verifier log, 7 recipes, 2026-10-03)
  - playbook/fixes/
last-verified: 2026-10-03
related:
  - "[[hackfest-openbsw-playground]]"
  - "[[sdv-blueprints-quickstart]]"
  - "[[pitfalls-top20]]"
  - "[[reference-architecture-doctor-whodunit]]"
  - "[[reference-architecture-hack-to-the-future]]"
---

# Known-broken recipes and their fixes

Seven upstream recipes were run exactly as documented on a stock Docker 29 host without swarm, podman or sudo. Four fail as written. All four pass with the override files in `playbook/fixes/`. Using these files saves you the first afternoon.

| Recipe | As written | With fix | Time |
|---|---|---|---|
| OpenBSW-SOVD-Demo (`--profile stub-cda`) | FAIL, five independent bugs | PASS: `/faults` returns 5 DTCs, `/data` 6 DIDs | ~9.5 min incl. ECU compile |
| OpenBSW-SOVD-Demo (`--profile real-cda`) | FAIL: CDA submodule empty, no LFS binary; trixie runtime older than host glibc | PASS with `openbsw-sovd-demo-real-cda.override.yaml` + locally built CDA: 5 DTCs over real DoIP, base path `/vehicle/v15` + Bearer token | ~1 min after CDA build (40 s) |
| OpenBSW-SOVD-Demo FLXC1000 branch (`features/jkk_FLUX1000`) | FAIL: overlay needs openbsw 9950d75 (not fetchable); 07b7551 gives 6 compile errors, upstream main breaks the overlay CMake | no fix found | - |
| ThreadX cortex_m4 quickstart | no `arm-none-eabi-gcc` on host | PASS using the toolchain in the OpenBSW image; libthreadx.a 265,702 B | ~1 s |
| fleet-management Recipe A | FAIL: overlay networks need swarm; documented rFMS path 404 | PASS | 1.5 min |
| e2e-vehicle-signals virtual setup | FAIL: script not executable; overlay networks | PASS, UIs on :8091 and :8090 | ~1 min |
| service-to-signal | FAIL: Rust build breaks (dependency drift, no Cargo.lock) | PASS with `kuksa-rust-sdk = "=0.2.0"` | 8 min |
| autowrx sdv-runtime | PASS | — | 9 s |
| OpenSOVD fault-lib recipe 8 (`dfm_bin` + `tst_app`) | PASS | — | 31 s |
| zenoh router via Docker | skipped, the note gives no image | — | — |

## OpenBSW-SOVD-Demo ([[hackfest-openbsw-playground]])

Five bugs at the pinned openbsw submodule `07b7551`:

1. Build context: compose uses `context: ../openbsw` but the Dockerfile copies `files/...` relative to `docker/development`. Error: `"/files/.bash_profile": not found`.
2. The Dockerfile ends with `USER build`; `ip tuntap` needs root. Error: `ioctl(TUNSETIFF): Operation not permitted`.
3. `entrypoint: >` folded scalar splits the cmake arguments onto separate bash commands (`-G: command not found`).
4. Design bug: lwIP runs in userspace on `tap0`, but the CDA connects via the container's `eth0`; they are never bridged, so DoIP port 13400 is refused. Fix: bridge `tap0` and `eth0` into `br0`.
5. The `ss`-based healthcheck cannot see a userspace socket, so `depends_on: service_healthy` never lets `sovd-cda` start. Workaround: `docker compose ... up -d --no-deps sovd-cda`.

All five are in `playbook/fixes/openbsw-sovd-demo.override.yaml`. Observed with the fix:

```
openbsw-ecu: RefApp: [TCP: INFO: Socket prepared at port 13400
sovd-cda: UDS TX: 1902ff
sovd-cda: UDS RX: 5902ff010100290102002a01030028010400280105002b
GET /sovd/v1/components/openbsw-ecu/faults -> 200 {"count":5, items 0x010100 P0100 ... 0x010500 C0500 Brake System Fault}
```

Upstream contributions these imply: fix the compose file and healthcheck in the HackFest playground (or its successor), and document the bridge requirement. See [[gap-register]] E2.

## SDV Blueprints ([[sdv-blueprints-quickstart]])

- **All three repos declare `driver: overlay` networks**, which require `docker swarm init`. Use the bridge overrides in `playbook/fixes/`. Upstream fix: ship a non-swarm compose variant.
- fleet-management: the documented rFMS path `/rfms/vehicleposition` returns 404; the route is `/rfms/vehiclepositions` (plural) and returned VIN `YV2E4C3A5VB180691`. The server's own welcome text is wrong. Upstream fix: README and welcome text.
- e2e-vehicle-signals: `virtual-setup/start-virtual-setup.sh` is committed without the executable bit (run `bash start-virtual-setup.sh`) and has `up --detach"$@"` without a space, which breaks if any argument is passed. Pass the bridge override through `FLEET_COMPOSE_FILE`.
- service-to-signal: no `Cargo.lock` and `kuksa-rust-sdk = "0.2.0 "` (note the trailing space) floats to 0.2.2, which pulls http 1.x and prost-types 0.14 against pinned http 0.2 / prost-types 0.12 (two E0308 errors in `connections.rs`). Fix: `kuksa-rust-sdk = "=0.2.0"` in `components/horn-service-kuksa/Cargo.toml`. Upstream: commit a Cargo.lock (open issue service-to-signal#14 already asks for the pin).

Each of these is a 30-minute freestyle PR with a verified reproduction. See [[gap-register]] E3 and E15.

## Not broken (reproduced exactly)

- autowrx `sdv-runtime`: "Starting Kuksa Databroker 0.4.4", "Kuksa connected True" within 9 s ([[autowrx-overview]]).
- OpenSOVD fault-lib: `dfm_bin` logs "DFM ready", `tst_app` exits 0 ([[opensovd-howto]]).
- Earlier the same day, during the component research: iceoryx2, uProtocol, VSS/KUKSA, OpenSOVD recipes A and B, OpenBSW POSIX build, S-CORE Cargo path, Zenoh Python ([[pitfalls-top20]] lists them as verified).

## Zenoh / uStreamer / Symphony ([[zenoh-overview]], [[uprotocol-howto]], [[symphony-overview]]), 2026-10-03
- Symphony `docker run ghcr.io/eclipse-symphony/symphony-api` with no env exits at once: add `-e CONFIG=/symphony-api-no-k8s.json` (map host 28082 -> 8082). See [[symphony-docker-no-k8s]].
- uStreamer + stock mosquitto container: add a config with `listener 1883` and `allow_anonymous true`, else the MQTT connection is refused. The streamer already is a Zenoh router on 7447; do not also run `zenohd` there.
- Docker bridge multicast: not broken on this host (see zenoh-overview), keep the router for Wi-Fi.

## openDuT localenv + EDGAR in Docker ([[opendut-quickstart]]), 2026-10-03
- Localenv compose passes as written (17 containers, ~10.5 min, ~1.6 GB RAM, LEA 200). No override needed.
- EDGAR-in-Docker fails: compose default image tag 0.10.0-alpha vs CARL 0.10.2 (set `OPENDUT_EDGAR_IMAGE_VERSION=0.10.2`), `OPENDUT_BACKEND_IP=127.0.0.1` required, and even then netbird-client targets api.netbird.io and the peer stays Disconnected. See [[opendut-edgar-docker-notes]].
