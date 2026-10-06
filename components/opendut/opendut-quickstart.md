---
title: openDuT - quickstart (CARL + EDGAR locally)
type: quickstart
component: opendut
tags: [opendut, docker-compose, theo, netbird, keycloak]
status: verified
sources:
  - repos/opendut/doc/src/user-manual/carl/setup.md
  - repos/opendut/doc/src/user-manual/edgar/setup.md
  - repos/opendut/doc/src/user-manual/edgar/docker.md
  - repos/opendut/doc/src/development/testenv/setup/theo-setup-docker.md
  - repos/opendut/.ci/deploy/localenv/docker-compose.yml
  - repos/opendut/.ci/docker/edgar/docker-compose.yml
last-verified: 2026-10-03
related:
  - "[[opendut-overview]]"
  - "[[opendut-howto]]"
  - "[[opendut-reference]]"
---

# openDuT quickstart

**Status:** localenv stack executed on 2026-10-03, see "Observed on 2026-10-03 (verifier)" at the end; the EDGAR-in-Docker join FAILED there.

## Fastest path A: "localenv" compose (CARL + NetBird + Keycloak), then EDGAR in Docker
Prereqs: Docker + Compose v2, user in `docker` group, Linux host (EDGAR container uses `network_mode: host`).

```sh
git clone --depth 1 https://github.com/eclipse-opendut/opendut.git && cd opendut
# 1. hostnames (127.0.0.1 for local use)
sudo tee -a /etc/hosts <<'H'
127.0.0.1 opendut.local
127.0.0.1 auth.opendut.local
127.0.0.1 netbird-api.opendut.local
127.0.0.1 netbird-relay.opendut.local
127.0.0.1 signal.opendut.local
127.0.0.1 nginx-webdav.opendut.local
127.0.0.1 opentelemetry.opendut.local
127.0.0.1 monitoring.opendut.local
H
# 2. provision secrets, copy them out, start everything (from doc user-manual/carl/setup.md)
export OPENDUT_REPO_ROOT=$(git rev-parse --show-toplevel)
L=$OPENDUT_REPO_ROOT/.ci/deploy/localenv
docker compose --file $L/docker-compose.yml --env-file $L/.env.development up --build provision-secrets
rm -rf $L/data/secrets/
docker cp opendut-provision-secrets:/provision/ $L/data/secrets/
docker compose --file $L/docker-compose.yml --env-file $L/.env.development --env-file $L/data/secrets/.env up --detach --build
```
Expected (from docs, unverified): containers for CARL, Keycloak, NetBird mgmt/signal/relay, Postgres, Traefik, Grafana/Loki/Prometheus/Alloy running; LEA at https://opendut.local (self-signed CA; trust it, CA location unverified), Keycloak at https://auth.opendut.local. Credentials are generated into `data/secrets/.env`. CARL image default `ghcr.io/eclipse-opendut/opendut-carl:0.10.2`.

Then:
1. In LEA (or CLEO) create a Peer, attach a network interface (e.g. `vcan0` kind can, or eth) and a Device, copy the **Setup-String**.
2. Run EDGAR in Docker (experimental):
```sh
cd .ci/docker/edgar
export OPENDUT_EDGAR_SETUP_STRING=<setup string>
export OPENDUT_BACKEND_IP=<ip>   # only if DNS names do not resolve
docker compose up
```
For CAN on host: `sudo modprobe vcan; sudo modprobe can_gw max_hops=2; sudo ip link add dev vcan0 type vcan; sudo ip link set vcan0 up`.
3. Create a cluster of 2 devices, choose a leader, **deploy**. Test CAN: `candump -d can0` on leader, `cansend can0 01a#01020304` on the other.

Native EDGAR instead (Pi / S-CORE image): download from LEA (Downloads) or `curl https://$CARL_HOST/api/edgar/$ARCH/download --output opendut-edgar.tar.gz`; `tar xf`; `export OPENDUT_EDGAR_SERVICE_USER=root` (for CAN); install `can-utils` and cannelloni; `./opendut-edgar setup managed` and paste setup string (edgar/setup.md). `--skip-can` to skip CAN.

## Path B: THEO test environment (all-in-docker incl. several EDGARs)
Developer-oriented; needs Rust toolchain and building a distribution (can take long, do not start in a hackathon unless prepared):
```sh
cargo ci distribution            # or download a release into target/ci/distribution/x86_64-unknown-linux-gnu/
cargo theo testenv start         # in the VM, or on host with docker compose
cargo theo testenv cluster start # starts several EDGAR containers and a cluster
```
Browser container "OpenDuT Browser" at http://localhost:3000 has certs preinstalled (test mode). VM variant uses Vagrant+VirtualBox+Ansible (setup/theo-setup-vm-linux.md). Dev mode: `cargo theo dev start`, `cargo theo dev carl`, `cargo lea`.

## Path C (recommended for 2-day events): use an organiser-hosted CARL
At HackFest the organisers hosted CARL and handed out Pis with EDGAR; teams only did EDGAR + CLEO/LEA ([[hackfest-esslingen-2026]]). Ask whether Chapter 4 provides this; then you only need the EDGAR steps above.

## Pitfalls (with sources)
- Needs working DNS/hosts for all `*.opendut.local` names, and trust of the generated CA; EDGAR must reach CARL, Keycloak, NetBird, OTel (edgar/setup.md).
- Keycloak re-provisioned after NetBird => 403 on `/api/groups`; fix `cargo theo testenv destroy` then start (testenv/known-issues.md).
- NetBird session lost; re-run EDGAR setup (playground result-overview.md). Check `/opt/opendut/edgar/netbird/netbird status --detail`, `ip link` for `wt0`, `br-opendut`, `gre-*`, `br-vcan-opendut` (edgar/troubleshooting.md).
- CAN without cannelloni/vcan/can_gw fails ("cannelloni: No such file"); without CAN setup use `--skip-can` and tell users (edgar/setup.md).
- EDGAR container is root + host network (issue #459 in compose comments).
- Upgrade CARL one version at a time, back up DB (CHANGELOG).
- Ping/L2 test between EDGARs: `ip address add 192.168.123.101/24 dev br-opendut` on one, `.102` on other, ping.
- Check wiring/ECU first before blaming openDuT (edgar/troubleshooting.md).
- Disk: Docker images are large; `docker system prune` hints in known-issues.md.

## Observed on 2026-10-03 (verifier)
Host: Docker 29, 60 GB RAM (13 GB available), repos/opendut at a2447d8 (unmodified), hosts and vcan0 pre-applied (`./test_setup.sh`: missing: 0). Ports 80/443/8080/8081 were free, no remap and no override file needed. Logs in `.local-verify/opendut/`.
Commands: exactly Path A steps 2 (`up --build provision-secrets`, 46 s; `rm -rf data/secrets; docker cp opendut-provision-secrets:/provision/ data/secrets/`; `up --detach --build`).
- **No Rust compile.** `--build` only builds small local images (keycloak, keycloak-init, netbird-management, cleo, nginx-webdav, tempo, otel-collector, provision-secrets); CARL is the prebuilt `ghcr.io/eclipse-opendut/opendut-carl:0.10.2`. Wall time from start to all healthy: about 10.5 min (628 s, mostly image pulls and builds).
- **Containers: 17 in `ps -a`**, 15 running (all with healthcheck healthy), 2 exited 0 by design (provision-secrets, grafana-users): alloy, carl, cleo, grafana, keycloak, keycloak-init, keycloak-postgres, loki, netbird-management, netbird-relay, netbird-signal, otel-collector, prometheus, tempo, traefik. nginx-webdav is built but not started.
- **Memory** (`docker stats --no-stream`): about 1.55 GB total, keycloak 862 MB, netbird-management 94 MB, grafana 111 MB, loki 84 MB, otel 81 MB, alloy 73 MB, carl 32 MB. Host available RAM stayed at 12-13 GB.
- **Images** (size): opendut-carl 710 MB, keycloak 805, keycloak-init 801, netbird-management 317, nginx-webdav 408, otel-collector 453, cleo 145, tempo 174, provision-secrets 130, grafana 1.14 GB (plus grafana-oss 1.47 GB), postgres:16 642 MB, alloy 672, prometheus 503, traefik 241, loki 175, netbird signal 63 and relay 62. About 8 GB total.
- `curl -k https://opendut.local` gives **200** (LEA); `curl -k https://auth.opendut.local` gives **302** (Keycloak redirect to its login).
- CLEO runs inside the stack (container `opendut-cleo`, already authenticated): `docker exec opendut-cleo opendut-cleo create peer --name verifier-peer`, `... create network-interface --peer-id <id> --type vcan --name vcan0`, `... generate-setup-string <id>` (positional id, not `--peer-id`). Setup-String is about 2.3 kB.
- **EDGAR in Docker: peer did NOT go Online (stayed Disconnected).** `docker pull ghcr.io/eclipse-opendut/opendut-edgar:0.10.2` (the compose default tag `0.10.0-alpha` does not match CARL 0.10.2, so set `OPENDUT_EDGAR_IMAGE_VERSION=0.10.2`), `OPENDUT_BACKEND_IP=127.0.0.1` (without it extra_hosts maps opendut.local to 0.0.0.0), then `docker compose up`. EDGAR setup tasks all succeeded and it reached CARL ("CARL has version 0.10.2"), but the bundled netbird-client then looped every 30 s with `failed creating connection to Management Service ... context deadline exceeded`. Its `netbird/config.json` held ManagementURL `api.netbird.io:443` (the NetBird default, not netbird-api.opendut.local), so the container never got the local management URL. Cause not isolated (setup ran with `--skip-service-run`; the EDGAR service that normally receives the peer config from CARL never logged a CARL peer stream). Treat EDGAR-in-Docker as unverified/broken, see [[opendut-edgar-docker-notes]].
- Teardown: `docker compose down -v` for both stacks; no opendut containers left, other 10 containers untouched; images kept (1.3 TB free). Total run 868 s.
