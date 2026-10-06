---
title: openDuT - how-to recipes (fault campaigns, virtual ECU, board, vehicle)
type: howto
component: opendut
tags: [opendut, fault-injection, can, ethernet, doctor-whodunit, hack-to-the-future]
status: draft
sources:
  - repos/opendut/doc/src/user-manual/cleo/commands.md
  - repos/opendut/doc/src/user-manual/test-execution.md
  - repos/opendut/doc/src/user-manual/edgar/setup.md
  - repos/opendut/doc/src/architecture/network/index.md
  - repos/opendut-playground/README.md
last-verified: 2026-10-03
related:
  - "[[opendut-overview]]"
  - "[[opendut-quickstart]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# openDuT how-to

Everything marked **design** is my proposal (not found in openDuT docs, untested). Everything else cites docs.

## Declarative setup with CLEO (repeatable)
`opendut-cleo apply file.yaml` takes `PeerDescriptor` (interfaces, devices, executors) and `ClusterDescriptor` (leader-id, devices) YAML; `opendut-cleo create uuid` generates IDs (cleo/commands.md). Sample file in upstream repo: `.ci/cargo-ci/src/packages/carl/cargo-ci-carl-push-samples.yaml` (path from playground; unverified in current tree). Commit the YAML to git = reproducible topology.

Imperative CAN flow: `create peer` -> `create network-interface --type can --name vcan0` -> `create device` -> `generate-setup-string`; then cluster create + deploy.

## Run a test as an executor
Container executor on a peer, started when the cluster is **deployed**; write results to `/results/`, then `touch /results/.results_ready`; EDGAR zips and uploads to `--results-url` (WebDAV; testenv has `http://nginx-webdav/`). `opendut-cleo create container-executor --peer-id .. --engine docker|podman --image .. --devices .. --results-url ..` (test-execution.md). Redeploy (undeploy+deploy) re-triggers.

## Doctor Whodunit: repeatable fault campaigns (design)
Challenge text claims openDuT "replays repeatable fault campaigns" at three levels ([[chapter4-challenge-doctor-whodunit]]; source is a search snippet, verify on the official page). openDuT supplies the **plumbing and repeatability of topology/execution**, not the fault logic. Suggested mapping:
1. **Message level (delayed / duplicated / dropped)**: run an executor container with `--devices` on the cluster Ethernet/CAN interface (`br-opendut`, `br-vcan-opendut`/`can0`) with NET_ADMIN, apply `tc qdisc add dev <if> root netem delay 200ms loss 5% duplicate 3%` for ethernet. For CAN use `can-utils`: `canplayer -I campaign.log`, `cangen`, `cansend`, `cangw` rules. Note: `can_gw` is already required by EDGAR.
2. **Signal level (stuck / implausible VSS)**: put a feeder (e.g. a CAN->KUKSA feeder, or a script writing to KUKSA databroker) on the leader side; the campaign file lists `{t, signal, value|freeze}`. Replay deterministically from a seed + timeline.
3. **Device level (sensor dropout)**: `ip link set can0 down/up` on the EDGAR host (or unplug via cluster undeploy/deploy: removes the device from the network), or pause the sensor container.
4. **Evidence**: executor writes JSONL of injected faults with timestamps into `/results/`; collector joins with Ankaios/uProtocol/SOVD logs. Use `.results_ready`.
Repeatability tips: pin versions (CARL 0.10.2), keep cluster/peer YAML in git, run `cleo apply` + deploy from a script, fixed seeds, NTP/chrony on all peers (timestamps across WG tunnel are not synchronized by openDuT; unverified).
Caveat: no built-in scheduler or trace store; GRE+WireGuard adds latency/jitter so timing-precise replay should be done on the DuT-side host rather than across the tunnel.

## Hack to the Future: virtual ECU + embedded board + real car (design, grounded in HackFest)
Topology: each target hangs off one EDGAR peer; one cluster joins their devices.
- **Virtual ECU** (e.g. OpenBSW posix build, [[openbsw-overview]]): run EDGAR in Docker (`.ci/docker/edgar/docker-compose.yml`, host network, root) on the PC; create `vcan0` and point the ECU's SocketCAN at it; register `vcan0` as CAN interface/device. For UDP/Ethernet ECUs use a veth/bridge attached as an Ethernet interface (unverified; docs only show real interfaces and vcan).
- **Embedded board / Pi**: flash image with EDGAR (Raspberry Pi Imager flow, playground challenge 3), or install native EDGAR (works on S-CORE image: needs `vcan`, cannelloni; runs without systemd per HackFest note). Board's CAN via USB-CAN or MCP2515 as `can0`.
- **Real vehicle**: Pi + CAN/Ethernet adapter on OBD/DoIP port; at HackFest a CDA connection to a car via openDuT worked and folded mirrors (result-overview.md). Keep-alive of the car via script failed; plan for wake-up/keep-alive handled on the Pi side. Safety: use read-only diagnostics unless you own the car.
- Switch DuT dynamically: change cluster membership via LEA/CLEO (playground "bonus goal").
Cluster joins all devices on one L2/CAN domain; leader peer is the hub for CAN (v0.10.2 notes: only follower port per peer).

## Troubleshooting order
`ip link` (wt0, br-opendut, gre-*, br-vcan-opendut) -> `netbird status --detail` -> `journalctl -u opendut-edgar` -> redeploy cluster -> re-run EDGAR setup (edgar/troubleshooting.md).
