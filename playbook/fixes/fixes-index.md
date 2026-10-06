# Known-good fixes for recipes that fail as written (verified 2026-10-03)

Pass each override as an extra `-f` to `docker compose`. Full verification log: `evidence/verify-run-1.md`. Context: [[known-broken-recipes]]. (This file is named fixes-index.md to keep vault basenames unique.)

| File | Fixes | Use with |
|---|---|---|
| `openbsw-sovd-demo.override.yaml` | build context, root user, single-line entrypoint, tap0↔eth0 bridge | `repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo` (`--profile stub-cda`), then `up -d --no-deps sovd-cda` because the healthcheck never passes |
| `openbsw-sovd-demo-real-cda.override.yaml` | real-cda profile: no CDA submodule or LFS binary, glibc too new for the trixie runtime; runs a locally built `opensovd-cda` in ubuntu:26.04 (`export CDA_BIN=...`) | add as third `-f` with `--profile real-cda`; `up -d --no-deps openbsw-ecu` then `real-sovd-cda`; API under `/vehicle/v15` with Bearer token |
| `openbsw-sovd-demo-flxc1000.override.yaml` | adds `-DUSE_FLXC1000_ECU=ON` to the ECU entrypoint | branch `features/jkk_FLUX1000` only; build still FAILS (openbsw pin 9950d75 unfetchable) |
| `fleet-management-bridge.override.yaml` | overlay → bridge networks (no swarm needed) | `repos/fleet-management` Recipe A, and `e2e-vehicle-signals` via `FLEET_COMPOSE_FILE` |
| `service-to-signal-bridge.override.yaml` | overlay → bridge networks | `repos/service-to-signal` (also pin `kuksa-rust-sdk = "=0.2.0"` in `components/horn-service-kuksa/Cargo.toml`) |
| `opendut-edgar-docker-notes.md` | EDGAR container: needs `OPENDUT_EDGAR_IMAGE_VERSION=0.10.2` and `OPENDUT_BACKEND_IP=127.0.0.1`; peer still does not join (no override file) | `repos/opendut/.ci/docker/edgar` |

If host port 3000 is taken, add a Grafana remap override: `services: {grafana: {ports: !override ["3300:3000"]}}`.
