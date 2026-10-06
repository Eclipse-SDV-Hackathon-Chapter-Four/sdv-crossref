---
title: SDV Blueprints - Quickstart
type: quickstart
component: sdv-blueprints
tags: [quickstart,docker,compose,ankaios]
status: draft
sources:
  - https://sdv-blueprints.eclipse.dev
  - https://github.com/eclipse-sdv-blueprints
  - repos/fleet-management/README.md
  - repos/service-to-signal/README.md
  - repos/software-orchestration/README.md
  - repos/companion-application/Readme.md
  - repos/e2e-vehicle-signals/README.md
  - repos/sdv_lab/README.md
  - https://api.github.com/orgs/eclipse-sdv-blueprints/repos?per_page=100
last-verified: 2026-10-03
related:
  - "[[sdv-blueprints-overview]]"
  - "[[chapter4-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[zenoh-overview]]"
  - "[[kanto-overview]]"
  - "[[velocitas-overview]]"
  - "[[symphony-overview]]"
  - "[[chapter3-retrospective]]"
---

# SDV Blueprints - Quickstart (run in <15 min)

> Status: **not executed** on 2026-10-03 (the host's Docker was in use for another project; commands below are taken from the repos' READMEs/compose files and are unverified by a run). A verifier should run recipe A first.

Prerequisites: Docker Engine + compose v2, ~4 GB free RAM, internet to pull images (ghcr.io, quay.io, docker.io). Free ports: 3000 (Grafana), 8081 (rFMS), 8082 (analysis), 8086 (Influx), 8080 (Dozzle).

## A. Fleet Management (Zenoh transport) - ~5 min
```sh
git clone --depth 1 https://github.com/eclipse-sdv-blueprints/fleet-management && cd fleet-management
docker compose -f ./fms-blueprint-compose.yaml -f ./fms-blueprint-compose-zenoh.yaml up --detach
docker compose -f ./fms-blueprint-compose.yaml -f ./fms-blueprint-compose-zenoh.yaml ps
```
Expected (per README): Grafana at http://127.0.0.1:3000 (login `sdv`/`sdv`) with the FMS-Fleet dashboard filling; rFMS:
```sh
curl -s "http://127.0.0.1:8081/rfms/vehicleposition?latestOnly=true" | jq
```
Fleet-analysis API: http://127.0.0.1:8082/fleet-analysis/api. Stop: `docker compose ... down -v`.
Pitfalls: a README mentioned elsewhere (e2e repo) suggests `docker swarm init` if networks fail (unverified); images are `:main` tags so behaviour changes under you; open bugs #71/#72 mean position time/heading/altitude may look wrong.

## B. Service-to-Signal - ~7 min (builds Rust images locally; may exceed 10 min on cold cache)
```sh
git clone --recurse-submodules --depth 1 https://github.com/eclipse-sdv-blueprints/service-to-signal && cd service-to-signal
docker compose -f service-to-signal-compose.yaml up --detach
docker logs -f horn-client      # requests
docker logs -f software-horn    # horn state changes
```
Dozzle UI: http://localhost:8080. **Pitfall**: without `--recurse-submodules` (or `git submodule update --init`) `components/kuksa-incubation` is empty and the zenoh-kuksa-provider build fails (we confirmed the submodule dir is empty after a plain shallow clone). Shallow clone + submodules: run `git submodule update --init --depth 1`.

## C. Software Orchestration (Ankaios 0.5 devcontainer) - ~10 min
```sh
git clone --depth 1 https://github.com/eclipse-sdv-blueprints/software-orchestration && cd software-orchestration/eclipse-ankaios
docker build -t ankaios-orchestration:0.1 -f .devcontainer/Dockerfile .   # add --build-arg TARGETARCH=amd64 if no buildx
docker run -it --privileged -p 25551:25551 --user ankaios --name ankaios_orchestration \
  --workdir /workspaces/software-orchestration \
  -v $PWD:/workspaces/software-orchestration \
  -v $PWD/../scenarios/smart_trailer/scripts/start_trailer_applications_ankaios.sh:/usr/local/bin/start_trailer_applications.sh \
  ankaios-orchestration:0.1
# inside: run_blueprint.sh ; second terminal: ank get workloads ; start_trailer_applications.sh
```
Expected: 5 workloads `Running(Ok)` (digital_twin_cloud_sync, digital_twin_vehicle, dynamic_topic_management, mqtt_broker, service_discovery), then smart_trailer_* after the trailer step. Pitfall: privileged container, Podman inside Docker; the README references `.devcontainer/` and `startupState.yaml` - the clone has `config/startupManifest.yaml` (`.devcontainer/` exists in the clone; README says startupState.yaml but the file is `config/startupManifest.yaml` - name drift).

## D. E2E Vehicle Signals, virtual setup (no hardware) - ~8 min
```sh
git clone --depth 1 https://github.com/eclipse-sdv-blueprints/e2e-vehicle-signals && cd e2e-vehicle-signals
git submodule update --init --recursive        # external/fleet-management
./virtual-setup/start-virtual-setup.sh          # ./virtual-setup/stop-virtual-setup.sh to stop
```
Then open http://localhost:8091 (Indicator input/actor UI replacing the Arduino ECUs) and http://localhost:8090 (demo website); Grafana :3000 as in recipe A. Databroker inside the Docker network is `databroker:55556`, host `localhost:55555` (virtual-setup/README.md).

## E. Companion Application
No runnable repo: follow the docs (Velocitas template repo in a VSCode devcontainer + Eclipse Leda 0.1.0-M2 in QEMU/Docker + `kanto-cm`). Allow > 1 h; not a 15 min recipe.

## Observed on 2026-10-03
Only static checks: repos cloned; compose files and manifests read; `kuksa-incubation` submodule empty after shallow clone; `eclipse-sdv-blueprints.github.io` = 404, `sdv-blueprints.eclipse.dev` = 200.

## Verification attempt 2026-10-03: FAILED (recipes A, B, D as written)
Run on Docker 29 without swarm, with host port 3000 occupied. Details in `evidence/verify-run-1.md`.
- **A**: `Network fleet-management_fms-backend Error ... This node is not a swarm manager` (compose networks are `driver: overlay`). Needs `docker swarm init`, or a bridge-network override. With bridge networks (and Grafana remapped off :3000) all 9 services ran, the "FMS Fleet" dashboard exists, and `curl :8081/rfms/vehicleposition?latestOnly=true` returned **404 with an empty body**. The working path is **`/rfms/vehiclepositions`** (plural): it returned the VIN YV2E4C3A5VB180691 with speed values. `:8082/fleet-analysis/api` returned 404.
- **B**: `docker compose up` fails building `horn-service-kuksa` (cargo exit 101, E0308 `http::uri::Uri` / `prost_types::Timestamp` mismatch) because there is no `Cargo.lock` and `kuksa-rust-sdk = "0.2.0 "` now resolves to 0.2.2. With `kuksa-rust-sdk = "=0.2.0"` in a scratch copy plus bridge networks it works: `software-horn` logs `activating horn signal` / `deactivating horn signal`, `horn-client` logs `Activate Horn returned message: status {}`. Also needs the overlay-network workaround.
- **D**: `./virtual-setup/start-virtual-setup.sh` is not executable (`Permission denied`; run with `bash`), then fails on the same overlay-network error. With a merged bridge-network compose passed via `FLEET_COMPOSE_FILE` and `FLEET_TRANSPORT_COMPOSE_FILE`, `curl -I :8091` and `:8090` both returned `HTTP/1.0 200 OK`.
- C and E were not run.
