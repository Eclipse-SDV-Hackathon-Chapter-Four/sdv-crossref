---
title: Eclipse Zenoh - overview
type: overview
component: zenoh
tags: [sdv, zenoh]
status: verified
sources:
  - https://zenoh.io
  - https://github.com/eclipse-zenoh/zenoh
  - repos/zenoh/Cargo.toml
  - https://github.com/eclipse-zenoh/zenoh-pico
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# Eclipse Zenoh

## What it is / is NOT
Zenoh is a pub/sub/query protocol and Rust implementation unifying data in motion, at rest and computation (key expressions, publishers, subscribers, queryables, storages). It is a **transport/middleware**, not an orchestrator, not a vehicle-signal model (that is VSS/[[vss-kuksa-overview]]), and not a service-level API like uProtocol (which can *run on* Zenoh, see [[uprotocol-overview]]). Source: https://zenoh.io, repos/zenoh/README.md.

## Maturity / version
- Looked at `eclipse-zenoh/zenoh` commit `173b1220c2ab59cc22c82bfc6c95ac9971ff213b` (2026-10-02), workspace version **1.10.1** (repos/zenoh/Cargo.toml). PyPI `eclipse-zenoh` 1.10.1 installed in the test below.
- Selected as alternate ROS 2 middleware (rmw_zenoh) per Eclipse newsroom (https://newsroom.eclipse.org/news/community-news/?page=5, snippet only). rmw_zenoh needs a router (multicast scouting is off by default; mind `ZENOH_ROUTER_CHECK_ATTEMPTS`), and its key `<domain>/<fqn>/<type>/<hash>` turns a type change into a silent drop ([[ros-over-zenoh-needs-a-router-and-a-contract]]).
- Used at Chapter 3 (listed among technologies, https://blogs.eclipse.org/node/8532 snippet) and as uProtocol transport by the Symphony target example.

## Languages, APIs, transports
Rust core; bindings Python (`eclipse-zenoh`), C (zenoh-c), C++, Kotlin, Java, TypeScript (unverified list: check zenoh.io). Transports: TCP, UDP, QUIC, TLS, WebSocket, unixsock, serial (unverified for each; see repos/zenoh/DEFAULT_CONFIG.json5). Plugins in repos/zenoh/plugins: REST, storage manager. Scouting by UDP multicast gives zero-config peer discovery.

## Modes
- **router** (`zenohd`): routing, storages, plugins; the stable hub.
- **peer**: connects to peers (multicast scouting) and optionally routers; mesh.
- **client**: connects to one router only; light on resources. 

## Ecosystem pieces
- **zenoh-pico**: C library for MCUs (Zephyr, FreeRTOS+TCP, ESP-IDF, Arduino, STM32 ThreadX...), client + peer mode. https://github.com/eclipse-zenoh/zenoh-pico. See [[threadx-overview]].
- **Bridges**: zenoh-plugin-ros2dds / zenoh-bridge-ros2dds (recommended for ROS 2), zenoh-plugin-dds, zenoh-plugin-mqtt (MQTT bridge, exists; details unverified here). https://github.com/eclipse-zenoh/zenoh-plugin-dds
- **Shared memory**: Zenoh has its own SHM transport (feature `shared-memory`, repos/zenoh/zenoh/Cargo.toml L55; examples `z_pub_shm.rs`, `z_sub_shm`, `z_alloc_shm.rs` in repos/zenoh/examples/examples). Separately, the DDS plugin can use iceoryx **v1** (v2.0.5 line) via `dds_shm` feature. Zenoh's SHM is **not** iceoryx2; they do not interoperate directly. Whether an official iceoryx2 <-> Zenoh tunnel ships: I could not verify (search found only iceoryx2-services without tunnel detail) - treat as "idea" and check [[iceoryx2-overview]].
- **uProtocol**: `up-transport-zenoh` crate (https://docs.rs/up-transport-zenoh/), needs a tokio runtime; used with up-rust.

## Quickstart (peer mode, no router; Python)
```bash
python3 -m venv v && v/bin/pip install eclipse-zenoh
# terminal 1: sub.py ; terminal 2: pub.py (see "Observed" below)
```
Router variant: `cargo install zenohd` (long build) or download release binary from https://github.com/eclipse-zenoh/zenoh/releases, run `zenohd`, then examples from `cargo run --example z_sub` / `z_pub` in repos/zenoh (default config connects via scouting). Clients: `-m client -e tcp/127.0.0.1:7447`.

Minimal code:
```python
import zenoh
s = zenoh.open(zenoh.Config())
s.declare_subscriber("demo/hello", lambda x: print(x.payload.to_string()))
s.put("demo/hello", "hi")
q = s.declare_queryable("demo/q", lambda qr: qr.reply("demo/q", "answer"))
for r in s.get("demo/q"): print(r.ok.payload.to_string())
```

### Observed on 2026-10-03
Python 3.14.4, venv, `pip install eclipse-zenoh` -> 1.10.1. Two processes on one host in default peer mode (multicast scouting):
```
got demo/hello hi 0
got demo/hello hi 1
got demo/hello hi 2
reply answer
```
`zenohd` and zenoh-pico were NOT run (no binary installed, did not build).

## Pitfalls
- **Version pinning**: keep router, bridges and clients on the same minor (1.x wire-compatible in principle, but plugins must match the exact zenohd version: plugins are dynamic libs built against a specific zenoh version). Mixing 0.11 and 1.x is incompatible (pre-1.0 API/protocol break; verify per release notes). ROS 2 rmw_zenoh requires a matching zenohd. 
- Multicast scouting often blocked on Wi-Fi / corporate VLANs (unverified; the default Docker bridge passed it here, see Observed below): peers will not find each other; use explicit `-e tcp/<ip>:7447` or a router. Hackathon Wi-Fi: expect this.
- zenoh-pico: tune batch/frag sizes; client mode needs a router (or peer with multicast UDP).
- Docker bridge networks break multicast: not reproduced on the default bridge of one host (corrected 2026-10-03, see the Observed section below); separate compose networks, podman and multi-host are untested, so host network or explicit endpoints stay the safe choice.
- Default config exposes a listener on 7447 without auth - fine for a hackathon, not for a car.

## Pros / cons / when not to use
Pros: one protocol from MCU to cloud, query + storage built in, tiny wire overhead, router-less mesh, multiple bridges. Cons: not an automotive standard by itself, plugin version coupling, SHM story differs from iceoryx2, debugging key-expression routing takes practice. Not for: hard-real-time in-process IPC (use [[iceoryx2-overview]]), signal modelling (use [[vss-kuksa-overview]]).

## Hackathon ideas
1. iceoryx2 <-> Zenoh **gateway** to native Zenoh key expressions. Note: a host-to-host *tunnel* already exists (`iox2-link-tunnel-zenoh`, prototype in iceoryx2 0.10.0, verified locally 2026-10-03, see [[iceoryx2-quickstart]] step 6); it mirrors iceoryx2 services over a Zenoh carrier but does not expose them as plain Zenoh keys for non-iceoryx2 peers. That gateway is the real gap.
2. zenoh-pico on ThreadX/AZ3166 publishing uProtocol uMessages (builds on threadx-rust MQTT example, see [[threadx-overview]]).
3. Zenoh transport for OpenBSW <-> Linux HPC bridge ([[openbsw-overview]]).
4. KUKSA VSS signals exposed as Zenoh key expressions ([[vss-kuksa-overview]]).
5. Zenoh-based Doctor-Whodunit log/trace fan-in ([[chapter4-challenge-doctor-whodunit]]).

## Observed on 2026-10-03 (verifier): router + client mode
Router: Docker image `eclipse/zenoh:1.10.1` exists on Docker Hub (no `cargo install` needed). Client Python is eclipse-zenoh 1.10.1 (vault `.venv`; also `pip install eclipse-zenoh==1.10.1` in python:3.12-slim).
```bash
docker run -d --name zr --network host eclipse/zenoh:1.10.1     # logs "Zenoh can be reached at tcp/..:7447", scout on 224.0.0.224:7446
```
```python
import zenoh
c = zenoh.Config()
c.insert_json5("mode", '"client"')
c.insert_json5("connect/endpoints", '["tcp/127.0.0.1:7447"]')
s = zenoh.open(c)          # use s.close() before exit, otherwise the process may linger
```
- Host client subscriber + host client publisher via the router: subscriber printed `got demo/hello hi 0` .. `hi 3`.
- Same pair in two containers (image `zpy`: python:3.12-slim + eclipse-zenoh 1.10.1) with `--network host` and the router: `hi 0`..`hi 3` received.
- **Pitfall NOT reproduced here (corrected 2026-10-03)**: with NO router, peer mode, two containers on the default Docker bridge discovered each other by multicast scouting and received `hi 0`..`hi 3`; a host peer publishing to a bridge-container peer also worked. So "Docker bridge breaks multicast" does not hold on this Docker 29 host. It still breaks on Wi-Fi/VLANs and rootless/podman setups (untested), so keep the router advice for the event.
Scripts used: `.local-verify/zenoh/sub.py`, `pub.py`.
