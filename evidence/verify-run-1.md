# Verify run 1 (2026-10-03, verifier)

Host: Docker 29 / compose v5.3.1, no sudo, no swarm. Foreign containers were already running and were NOT touched: `weft-telemetry-grafana-1` holds host port 3000 (and 9090), `dp711-remote` holds 8000, `sumo-*` hold 18080/18081/4600/19000.
Override files used (kept in this dir or scratchpad): `evidence/verify-run-1-r1-override.yaml` (recipe 1). No tracked file in any clone was edited; only `git submodule update --init` and build outputs (`target/`) were produced.

## Summary
| # | Recipe | As written | With fixes | Wall time |
|---|---|---|---|---|
| 1 | OpenBSW-SOVD-Demo, `docker compose --profile stub-cda up --build -d` | FAIL (4 independent bugs) | PASS: 5 DTCs | 9m22s total incl. 4 attempts (final build ~3.5m + ECU compile ~1.5m) |
| 2 | sdv-blueprints Recipe A fleet-management | FAIL (overlay network needs swarm; port 3000 busy; documented rFMS path 404) | PASS | 1m30s |
| 3 | Recipe D e2e-vehicle-signals virtual setup | FAIL (script not executable; swarm overlay; port 3000 busy) | PASS (:8091 and :8090 = 200) | ~1m |
| 4 | Recipe B service-to-signal | FAIL (cargo build breaks: dependency drift, no Cargo.lock) | PASS only with `kuksa-rust-sdk = "=0.2.0"` pin in a scratch COPY | 8m19s |
| 5 | autowrx sdv-runtime `docker run` | PASS exactly as written | n/a | 9s |
| 6 | zenoh router variant | SKIPPED: note gives no Docker image (says `cargo install zenohd` / release binary, and says it was not run); per instructions not attempted | | |
| 7 | opensovd-howto recipe 8 (dfm_bin + tst_app) | PASS exactly as written | n/a | 31s (13.6s cold build) |

## 1. OpenBSW-Playground (event/hackfest-openbsw-playground.md)
Commands: `git submodule update --init --depth 1 openbsw` (4s, OK, @07b7551); `cd OpenBSW-SOVD-Demo && docker compose --profile stub-cda up --build -d`.
Failures and fixes (all applied in `evidence/verify-run-1-r1-override.yaml`, passed as a 2nd `-f`):
1. Build fails immediately: `failed to compute cache key ... "/files/.bash_profile": not found`. Compose uses `context: ../openbsw` but openbsw's Dockerfile (`docker/development/Dockerfile`) COPYs `files/...` relative to `docker/development`. Fix: `build: {context: ../openbsw/docker/development, dockerfile: Dockerfile}`.
2. Container exits 127: `ioctl(TUNSETIFF): Operation not permitted`; the (new) Dockerfile ends with `USER build`, but `ip tuntap` needs root. Fix: `user: root`.
3. Same exit 127 with `-G: command not found`, `-DCMAKE_...: command not found`: the `entrypoint: >` folded scalar keeps newlines on the more-indented cmake args, so the bash command is split. Fix: single-line entrypoint.
4. Design bug: kernel `tap0` and Docker `eth0` both own 192.168.0.201 but the DoIP stack is lwIP in userspace on tap0; `eth0` is not connected to `tap0`, so sovd-cda gets `[Errno 111] Connection refused` on 13400. Fix: in the entrypoint replace `ip address add 192.168.0.201/24 dev tap0` with `ip addr flush dev eth0; ip link add br0 type bridge; ip link set tap0 master br0; ip link set eth0 master br0; ip link set br0 up`.
5. Healthcheck `ss -tlnp | grep -q :13400` can never pass (lwIP userspace socket is invisible to `ss`), so `depends_on: service_healthy` never starts sovd-cda (`dependency failed to start: container openbsw-ecu is unhealthy`). Workaround: `docker compose ... up -d --no-deps sovd-cda`.
6. Port 3000 busy on this host (foreign Grafana): remapped grafana to 3300 (host specific, not a repo bug).
Observed:
```
openbsw-ecu: RefApp: [TCP: INFO: Socket prepared at port 13400   (after [355/358] build, app.sovdDemo.elf)
sovd-cda: UDS TX: 1902ff
sovd-cda: UDS RX: 5902ff010100290102002a01030028010400280105002b
GET /sovd/v1/components/openbsw-ecu/faults -> 200 {"availability_mask":"0xFF","count":5,"items":[0x010100 P0100 ... 0x010500 C0500 Brake System Fault]}
GET /sovd/v1/components/openbsw-ecu/data -> {"count":6,...0xCF01 StaticData, 0xCF02 ADC_Value ...}
grafana (remapped :3300) /api/health -> database ok, version 13.0.2
```
Teardown: `docker compose ... down -v`; no containers/networks left. Result: FAIL as written, PASS with fixes (5 DTCs).

## 2. SDV Blueprints Recipe A (fleet-management, repos/fleet-management)
Command: `docker compose -f ./fms-blueprint-compose.yaml -f ./fms-blueprint-compose-zenoh.yaml up --detach`.
As written: `Network fleet-management_fms-backend Error ... This node is not a swarm manager` (networks are `driver: overlay`). `docker swarm init` was NOT run (would change host Docker state). Fix: extra -f file setting both networks to `driver: bridge` (`attachable: !reset null`) plus grafana host port 3300 (3000 busy).
Observed (after ~70s):
```
9 containers Up (databroker, csv-provider, fms-forwarder, fms-consumer, fms-server, fms-zenoh-router, fleet-analysis-backend, grafana, influxDB healthy)
GET :3300/api/health -> 200 ; /api/search (sdv:sdv) -> [{"title":"FMS Fleet","uri":"db/fms-fleet"...}]
GET :8081/rfms/vehicleposition?latestOnly=true -> HTTP/1.1 404 Not Found (empty body)   <- path in note and README is wrong
GET :8081/rfms/vehiclepositions?latestOnly=true -> 200 {"vehiclePositionResponse":{"vehiclePositions":[{"vin":"YV2E4C3A5VB180691","tachographSpeed":2.09765625,"triggerType":{"triggerType":"TIMER"}...
GET :8081/rfms/vehicles -> {"vehicleResponse":{"vehicles":[{"vin":"YV2E4C3A5VB180691"}]}}
GET :8082/fleet-analysis/api -> 404 ; :8082/ -> 404 (Payara up, path not confirmed)
```
The route in `components/fms-server/src/lib.rs` is `/rfms/vehiclepositions` (plural); the server's own welcome text says singular. Down: `down -v`, clean. Result: FAIL as written, PASS with fixes and the corrected path.

## 3. Recipe D (repos/e2e-vehicle-signals)
Commands: `git submodule update --init --recursive` (6s OK), `./virtual-setup/start-virtual-setup.sh`.
As written: `Permission denied` (file mode 100644 in git, not executable; run with `bash ...`). Then same swarm error as recipe 2 (fleet compose overlay networks). Fix: rendered a merged bridge-network, grafana:3300 compose via `docker compose config` and passed it through the script's `FLEET_COMPOSE_FILE` / `FLEET_TRANSPORT_COMPOSE_FILE=<services: {}>` env vars. Also noticed: script line `up --detach"$@"` lacks a space (breaks if any arg passed).
Observed:
```
[start-virtual] All services started.  (24s; 13 containers Up incl. mosquitto, grpc-mqtt-bridge, virtual-indicator-ui, pi5-demo-website)
curl -I :8091 -> HTTP/1.0 200 OK  Server: SimpleHTTP/0.6 Python/3.12.15
curl -I :8090 -> HTTP/1.0 200 OK  Server: SimpleHTTP/0.6 Python/3.12.15
grafana (remapped :3300) -> 302
```
Teardown: `stop-virtual-setup.sh -v` (with same env); left two fleet-management_* networks, removed with `docker network rm`. Result: FAIL as written, PASS with fixes.

## 4. Recipe B service-to-signal
Commands: `git submodule update --init --recursive` (kuksa-incubation populated), `docker compose -f service-to-signal-compose.yaml up --detach`.
As written FAIL: `horn-service-kuksa` image build: `cargo build --package horn-service-kuksa` exit 101, two E0308 errors (`connections.rs:25 expected http::uri::Uri, found Uri`; `:32 expected prost_types::protobuf::Timestamp, found prost_types::Timestamp`). Cause: no `Cargo.lock` committed and `kuksa-rust-sdk = "0.2.0 "` floats to 0.2.2, which depends on http 1.x / prost-types 0.14, while the crate pins http 0.2 / prost-types 0.12. Overlay networks would also have failed (swarm).
Fix tried in a scratch copy (clone untouched): `kuksa-rust-sdk = "=0.2.0"` plus bridge network override. Build 2m, `up` OK.
```
software-horn: [INFO software_horn] activating horn signal / deactivating horn signal  (repeating)
horn-client: Starting the client for the COVESA Horn service over uProtocol
horn-client: Activating horn for 1500 milliseconds with a sequenced horn
horn-client: Activate Horn returned message: status {}
```
Result: FAIL as written (build), PASS with the pin. Torn down, clean.

## 5. autowrx (components/autowrx/autowrx-overview.md)
Command exactly as in the note (`docker run -d --name coach-sdv-runtime -e RUNTIME_NAME=coach-test-20261003 -p 55599:55555 ghcr.io/eclipse-autowrx/sdv-runtime:latest`). Within 9 s:
```
Starting Kuksa Databroker 0.4.4
Populating metadata from file '/home/dev/ws/vss.json'
Listening on 0.0.0.0:55555
RunTime display name: Runtime-coach-test-20261003
Connecting to Kit Server: https://kit.digitalauto.tech
Kuksa connected True
Connected to Kit Server
container status: Up 6 seconds (healthy)
```
PASS. `docker rm -f` done.

## 6. zenoh: skipped (no Docker image in the note; note itself says zenohd was never run). For reference the eclipse/zenoh:1.6.2 image did run as the router in recipe 4 and eclipse/zenoh:1.1.0 in recipe 2.

## 7. opensovd-howto recipe 8 (repos/opensovd-fault-lib)
Commands exactly as in the note (after pre-building with `cargo build -p dfm_bin -p fault_lib --features fault_lib/testutils --example tst_app`, 13.6 s).
```
dfm_bin: Loaded catalog 'hvac' ... (2 faults) / 'ivi' ... (2 faults)
dfm_bin: Starting DFM with query server (4 faults across 2 catalogs) / DFM ready
dfm_lib::fault_lib_communicator: Received new fault ID: Text("hvac.blower.speed_sensor_mismatch")
error: get_value could not find key: hvac   (x2, harmless as noted)
tst_app: End Basic fault library example      exit 0, ~4 s
```
PASS. dfm_bin stopped, /tmp/dfm-store removed.
