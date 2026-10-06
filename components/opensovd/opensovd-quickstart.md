---
title: OpenSOVD - quickstart (gateway mock + CDA with ECU simulator)
type: quickstart
component: opensovd
tags: [opensovd, quickstart, sovd, cda, docker, curl]
status: verified
sources:
  - repos/opensovd-core/README.md
  - repos/opensovd-core/opensovd-cli/gateway/README.md
  - repos/opensovd-core/opensovd-mocks/README.md
  - repos/opensovd-cda/README.md
  - repos/opensovd-cda/testcontainer/first_steps.md
  - repos/opensovd-cda/testcontainer/docker-compose.yml
  - repos/opensovd-cda/testcontainer/ecu-sim/src/main/kotlin/webserver/WebserverRoutes.kt
last-verified: 2026-10-03
related:
  - "[[opensovd-overview]]"
  - "[[opensovd-howto]]"
  - "[[opensovd-reference]]"
---

# OpenSOVD - quickstart

There are two independent recipes. **A** takes about 2 minutes and needs only Docker. **B** takes about 10 minutes and needs Rust plus Docker. Both were run on 2026-10-03 (Ubuntu 26.04, Docker, 32 cores). Exact output is at the bottom.

## Prerequisites
- Docker (A and B), `curl`, `jq`.
- B also needs: Rust via rustup (CDA MSRV 1.88; stable 1.98 worked), `cmake`, `clang`/`gcc`, `perl`, `pkg-config`, `libssl-dev` (mbedtls-sys and openssl are built). The ECU simulator image builds with Gradle **inside** Docker, so you don't need a local JDK.
- Free ports: 7690 (A), 20002 and 8181 (B).

## A. SOVD gateway with mock topology (opensovd-core)
```bash
docker run -d --rm --name opensovd-qs -p 7690:7690 ghcr.io/eclipse-opensovd/opensovd-gateway --mock
B=http://127.0.0.1:7690/sovd
curl -s $B/version-info | jq                                   # SOVD 1.1.0, vendor OpenSOVD 0.1.1-dev
curl -s $B/v1/ | jq                                            # root: areas/components/apps links
curl -s $B/v1/components | jq                                  # ecu, gateway
curl -s $B/v1/components/ecu | jq                              # capabilities: data, belongs-to, hosts
curl -s $B/v1/components/ecu/data | jq                         # 8 items (voltage, temperature, sw.*, hw.*)
curl -s "$B/v1/components/ecu/data/voltage?include-schema=true" | jq
curl -s $B/v1/components/ecu/data-categories | jq
curl -s $B/v1/components/gateway/hosts | jq                    # apps hosted on gateway
curl -s $B/v1/areas/powertrain/contains | jq
curl -s $B/v1/apps/engine_control/data/app.status | jq
docker stop opensovd-qs
```
Expected: JSON like `{"id":"voltage","data":{"value":12.6}}`. Mock entities: areas `powertrain`, `network`; components `ecu`, `gateway`; apps `engine_control`, `diagnostics`, `ota_manager` ([mocks README](../../repos/opensovd-core/opensovd-mocks/README.md)).
**Not available here:** `/faults`, `/operations`, `/modes`, `/locks` all return **404 with an empty body**. The mock data is read-only: a PUT returns 400 `"read only"`.

Without Docker: `cd repos/opensovd-core && cargo run -p opensovd-gateway -- --mock`. The first run downloads the pinned nightly toolchain from `rust-toolchain.toml`.

## B. Classic Diagnostic Adapter + ECU simulator (UDS over DoIP, real faults)
The upstream path ([first_steps.md](../../repos/opensovd-cda/testcontainer/first_steps.md)) has you run the whole integration-test suite first, only to generate `testcontainer/cda-test-config.toml`. This shortcut skips that. It runs the CDA binary on the host and the Kotlin ECU simulator in a Docker bridge network. DoIP vehicle discovery (UDP broadcast) works across the host bridge interface.

```bash
cd repos/opensovd-cda                                    # clone under the vault's repos/
cargo build --release --locked -p opensovd-cda           # ~1m41s on 32 cores (cold); binary target/release/opensovd-cda (~37 MB)
CDA=$(pwd)/target/release/opensovd-cda

# ECU simulator image (gradle build inside docker, ~2-3 min)
docker build -f testcontainer/ecu-sim/docker/Dockerfile -t opensovd-ecu-sim:local testcontainer/ecu-sim

# Network with the same subnet as upstream compose; the sim adds extra IPs (needs privileged/NET_ADMIN)
docker network create --subnet 172.42.0.0/16 opensovd-net
docker run -d --rm --name opensovd-ecusim --network opensovd-net --privileged --cap-add NET_ADMIN \
  -e USE_MULTIPLE_IPS=true -e SIM_NETWORK_INTERFACE=eth0 -p 8181:8181 opensovd-ecu-sim:local
until curl -sf http://127.0.0.1:8181/ >/dev/null; do sleep 2; done

# CDA: tester address = host IP on that bridge (172.42.0.1); MDDs from the repo
mkdir -p /tmp/cda-run && cp testcontainer/odx/*.mdd /tmp/cda-run/ && cd /tmp/cda-run
$CDA -d /tmp/cda-run -t 172.42.0.1 \
  --listen-address 127.0.0.1 --listen-port 20002 &
```
Wait about 2 s until the log shows `ECU connected - setting connectivity to Online ecu_name="flxc1000"`. Then:
```bash
B=http://127.0.0.1:20002/vehicle/v15
TOKEN=$(curl -s -X POST $B/authorize -H 'Content-Type: application/json' \
  -d '{"client_id":"test","client_secret":"secret"}' | jq -r .access_token)
H="Authorization: Bearer $TOKEN"
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:20002/health/ready      # 204
curl -s $B/components -H "$H" | jq                                              # flxc1000, fsnr2000, flxcng1000
curl -s $B/components/flxc1000 -H "$H" | jq .variant                            # state Online
curl -s $B/components/flxc1000/data -H "$H" | jq '[.items[].id]'
curl -s $B/components/flxc1000/data/VINDataIdentifier -H "$H" | jq              # UDS 0x22 F190
curl -s $B/components/flxc1000/faults -H "$H" | jq                              # UDS 0x19
# inject a DTC in the simulator (sim control API, not SOVD): testFailed+confirmed = 0x09
curl -s -X PUT http://127.0.0.1:8181/FLXC1000/dtc/Standard -H 'Content-Type: application/json' \
  -d '{"id":"01E240","statusMask":"09"}'
curl -s $B/components/flxc1000/faults/01E240 -H "$H" | jq                       # detail + environment_data
# clear DTCs: needs a lock first (else 409 lock-required)
curl -s -X POST $B/components/flxc1000/locks -H "$H" -H 'Content-Type: application/json' -d '{"lock_expiration":60}'
curl -s -X DELETE $B/components/flxc1000/faults -H "$H" -w '%{http_code}\n'      # 204 (UDS 0x14)
curl -s -X PUT $B/components/flxc1000/modes/session -H "$H" -H 'Content-Type: application/json' -d '{"value":"extended"}'
curl -s -X POST $B/components/flxc1000/operations/SelfTest/executions -H "$H" -H 'Content-Type: application/json' -d '{}'
# Swagger UI: http://127.0.0.1:20002/swagger-ui ; OpenAPI: http://127.0.0.1:20002/openapi.json
```
Teardown: `kill %1; docker stop opensovd-ecusim; docker network rm opensovd-net`.

Upstream alternative (heavier): `cargo test --package integration-tests --features integration-tests` once, then `cd testcontainer && docker compose build && docker compose up`. This builds the CDA in Docker with cargo-chef ([first_steps.md](../../repos/opensovd-cda/testcontainer/first_steps.md)). Not run here.

## Pitfalls seen
- **Protocol name mismatch.** With the default `--protocol-name UDS_Ethernet_DoIP_DOBT`, 3 of the 6 test MDDs (JGWT5000, HOVR4000, TMCC3000) are skipped with `Protocol UDS_Ethernet_DoIP_DOBT not found in database`. With `UDS_Ethernet_DoIP` the same three fail. In both cases flxc1000, fsnr2000 and flxcng1000 load. The sim's VAMs for the skipped ECUs then log `UnknownECU`. This is harmless.
- **Before the ECUs are found**, every ECU resource returns **503** `{"vendor_code":"communication-not-ready","message":"Variant detection has not concluded"}`. Typical causes: wrong `--tester-address` (must be an IP on the interface facing the ECUs), or a firewall blocking UDP 13400 broadcast.
- **Auth is demo-only.** Any `client_id`/`client_secret` returns a token (the default build has no `auth` feature). The token is an HS256 JWT with key `"secret"` and `exp` 2000000000. Without `auth` the CDA decodes incoming JWTs with `jsonwebtoken::dangerous::insecure_decode` (no signature check), and opensovd-core's `JwtAuthenticator` sets `validate_aud = false` ([[verify-offline-against-a-pinned-root]]). `GET /components` even worked **without** a token.
- **href casing.** `GET /components` returned `href` values with `/Vehicle/v15/...` (capital V), while the real routes are `/vehicle/v15`. Clients that follow hrefs on a case-sensitive server may break. Candidate for an upstream issue.
- **Fault filter.** `?status[confirmedDtc]=true` still returned all six DTCs, including ones with mask `00`. The list seems to merge the ODX-known DTCs with the ECU-reported ones. Filter on `.status.mask` client-side, or check this with the maintainers. Unverified whether this is a bug.
- The CDA writes storage into its working directory (`Local storage initialized root=.`), so run it from a scratch dir.
- No published CDA image or binary ("for legal reasons", testcontainer README). The HackFest OpenBSW demo checked in a prebuilt binary via Git LFS ([https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/tree/main/OpenBSW-SOVD-Demo](../../https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/tree/main/OpenBSW-SOVD-Demo)).

## Observed on 2026-10-03
Recipe A (image `ghcr.io/eclipse-opensovd/opensovd-gateway:latest`, digest `sha256:21ca941f...`):
```
{"sovd_info":[{"version":"1.1.0","base_uri":"http://127.0.0.1:7690/sovd/v1","vendor_info":{"version":"0.1.1-dev","sha1":"bde7a78","build_date":"2026-09-25","name":"OpenSOVD"}}]}
{"id":"","name":"","areas":"http://127.0.0.1:7690/sovd/v1/areas","components":"http://127.0.0.1:7690/sovd/v1/components","apps":"http://127.0.0.1:7690/sovd/v1/apps"}
{"items":[{"id":"ecu","name":"Engine Control Unit","translation_id":"ecu.name","href":"http://127.0.0.1:7690/sovd/v1/components/ecu","tags":["powertrain","critical"]},{"id":"gateway",...}]}
{"id":"ecu","name":"Engine Control Unit","translation_id":"ecu.name","variant":{"variant":"v2","manufacturer":"ACME"},"data":".../components/ecu/data","belongs-to":".../components/ecu/belongs-to","hosts":".../components/ecu/hosts"}
{"id":"voltage","data":{"value":12.6}}
{"items":[{"item":"currentData"},{"item":"identData"}]}
GET /v1/components/ecu/faults -> HTTP/1.1 404 Not Found (content-length: 0)
PUT /v1/components/ecu/data/voltage -> 400 {"error_code":"error-response","message":"read only"}
GET /v1/components/ecu/bulk-data -> {"error_code":"vendor-specific","vendor_code":"provider-not-available","message":"Component has no bulkdata"}
```
Recipe B (CDA commit e6f4b8f built with cargo 1.98.1 in 1m41s; ecu-sim image built locally):
```
health/ready 204
{"name":"FLXC1000_App_0101","is_base_variant":false,"state":"Online","logical_address":"0x1000"}
["VINDataIdentifier","ActiveDiagnosticSessionDataIdentifier","Identification","FluxCapacitorPowerConsumption"]
{"id":"vindataidentifier","data":{"VIN":"SCEDT26T8BD005261"}}
{"id":"fluxcapacitorpowerconsumption","data":{"PowerConsumption":10}}
operations: ["CalibrateSensors","SelfTest","TimeCircuits","Clear_Diagnostic_User_Memory"]
modes: session, security, commctrl, dtcsetting ; configurations: []
after sim PUT 01E240 mask 09:
{"item":{"code":"01E240","scope":"FaultMem","fault_name":"DTC Code 1","severity":0,"status":{"test_failed":true,...,"confirmed_dtc":true,...,"mask":"09"}},"environment_data":{"extended_data_records":{"data":{}},"snapshots":{"data":{}}}}
DELETE faults without lock -> 409 {"message":"Required lock is missing","error_code":"vendor-specific","vendor_code":"lock-required"}
POST locks -> {"id":"eab36778-...","owned":true,"x-sovd2uds-isexclusive":true} ; DELETE faults -> 204 ; sim fault memory now []
PUT modes/session extended -> {"id":"session","value":"Extended"}
POST operations/SelfTest/executions -> {"parameters":{"RoutineId":4097}}
Without ECU sim: ECU resources -> 503 communication-not-ready
```
