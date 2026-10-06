---
title: Eclipse autowrx / digital.auto playground - overview, quickstart (inline)
type: overview
component: autowrx
tags: [autowrx, digital-auto, playground, dreamkit, vss, prototyping, adjacent]
status: verified
sources:
  - https://github.com/eclipse-autowrx
  - https://github.com/eclipse-autowrx
  - https://playground.digital.auto
  - https://github.com/eclipse-autowrx/sdv-runtime
last-verified: 2026-10-03
related:
  - "[[autowrx-integration-notes]]"
  - "[[vss-kuksa-overview]]"
  - "[[velocitas-overview]]"
  - "[[sdv-landscape-overview]]"
---

# Eclipse autowrx (digital.auto playground) and dreamKIT

## What it is
- **autowrx**: open-source web platform (monorepo: React/Vite/TypeScript frontend, Node/Express + MongoDB backend, Socket.IO; MIT) behind https://playground.digital.auto. Browse a VSS-based vehicle API catalogue, write a prototype in the browser (Python / C++ / Rust), run it against a runtime and show live signals, present "customer journeys". Source: https://raw.githubusercontent.com/eclipse-autowrx/autowrx/main/README.md
- **sdv-runtime**: Docker image (arm64/amd64) = KUKSA databroker + VSS + Velocitas Python SDK + mock provider + "kit manager" that registers the runtime with the playground server, so code written in the browser runs in your container (https://github.com/eclipse-autowrx/sdv-runtime).
- **dreamKIT**: PoC hardware kit (NXP S32G Goldbox + Jetson AGX Orin + touchscreen, CAN/Ethernet); playground apps deploy via Socket.IO "within seconds" (https://github.com/eclipse-autowrx/dreamKIT, v1.0.0 2025-06-06, last commit 2025-10-03).

## What it is NOT
Not a production runtime, not safety-relevant, not a simulator by itself (signals come from a mock provider or your feeder), not an orchestrator. Prototypes are QM-class apps.

## Maturity / state in 2026
- autowrx: **very active**. CalVer releases almost daily (v2026.10.02 on 2026-10-02; Sep 2026 notes: Tailwind v4 migration, plugin/templates, `generate_vehicle_model` carries VSS spec, XSS fix) https://github.com/eclipse-autowrx/autowrx/releases . 18 repos; platform-plugins, platform-services, sample Replit plugin, learning-journey (Jan 2026) hint at an AI/plugin direction (names only, unverified).
- sdv-runtime: latest tag v1.2.0 (2025-09-04) but commits 2026-08/09 (vulnerability fixes, kit-manager safety); image on ghcr rebuilt 2026-09-25 (observed).
- dreamKIT: stable, slow (last push Oct 2025).
- Eclipse state: Incubating (proposal https://projects.eclipse.org/proposals/eclipse-autowrx).
- **Important**: the playground and kit server (`https://kit.digitalauto.tech`) are hosted services; availability of that SaaS is a risk for a 2-day event.

## How teams used it in hackathons
- BCX2022 hack challenge "Passenger Welcome": prototype in digital.auto, transfer to Velocitas/KUKSA/Leda (https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-passenger-welcome).
- Chapter Two "Play by Wire": create a prototype in digital.auto to define the VSS API of a vehicle-input game (Pong with KUKSA, Forza UDP proxy); hardware Arduino/RPi4/ThreadX board; Ankaios for deployment (https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challenge-play-by-wire).
- 2025 challenge announcements (Virtual SDV Lab, Mission: Update Possible) do not mention it (https://blogs.eclipse.org/node/8424); nothing found for Chapter 4 - check [[chapter4-overview]].
- Pattern: use it first 2 hours for "what signals do we need?" + demo UI, then move logic to Velocitas/KUKSA containers.

## Quickstart (inline) - OBSERVED on 2026-10-03
Prerequisites: Docker, internet (to reach kit.digitalauto.tech), free port.
```bash
docker run -d --name coach-sdv-runtime -e RUNTIME_NAME="coach-test-20261003" \
  -p 55599:55555 ghcr.io/eclipse-autowrx/sdv-runtime:latest      # 55555 = databroker gRPC
docker logs coach-sdv-runtime | tail
```
Observed (image 160 MB, created 2026-09-25): `Starting Kuksa Databroker 0.4.4`, `Populating metadata from file '/home/dev/ws/vss.json'`, `Listening on 0.0.0.0:55555`, `TLS is not enabled`, `Authorization is not enabled`, `Created mock datapoints ... mock provider is now running`, `RunTime display name: Runtime-coach-test-20261003`, `Connecting to Kit Server: https://kit.digitalauto.tech`, `Kuksa connected True`, KitManager heartbeats. Inside: kuksa_client 0.4.3, velocitas_sdk 0.14.1. Remaining manual step (not done): open https://playground.digital.auto, choose a prototype, pick runtime "Runtime-<name>" in the run panel.
Self-host the platform (from README, not run): MongoDB `docker run -d --name autowrx-mongodb -p 27017:27017 mongo:4.4.6-bionic`; `cd backend && yarn install && yarn dev` (port 3200); `cd frontend && yarn install && yarn dev` (port 3210).

## Pitfalls
1. Needs outbound internet to the SaaS kit server; set `SYNCER_SERVER_URL` for a self-hosted manager (instance-setup repo).
2. Databroker 0.4.4 / VSS 4.0 inside the runtime: old `kuksa.val.v1` API and VSS-4 paths; a VSS 5/6 model will not match. Keep `-p 55555` mapping if you use `kuksa-client` from the host.
3. Runtime name must be unique per team (it is a global id on the shared server); use `RUNTIME_PREFIX`.
4. Container is fail-fast on Kit-Manager exit; use `--restart=always`.
5. No auth/TLS by default - fine for a lab LAN only.
6. Mock provider is "with modification to the source code": do not assume it equals upstream kuksa-mock-provider.

## Pros / cons / when not to use
Pros: zero-install start in a browser, VSS-first, great for ideation and demos, active upstream, bridges to Velocitas and dreamKIT.
Cons: dependency on hosted server, old databroker inside, prototype-grade runtime, limited to VSS signals + MQTT-style services.
Not for: real-time, safety, uProtocol/Zenoh-native designs, or offline venues without a self-hosted instance.

## Hackathon ideas
1. Offline kit: compose file with autowrx + MongoDB + local kit manager for venues with poor Wi-Fi (verify `instance-setup`).
2. Playground widget showing an OpenSOVD diagnostic or an iceoryx2 signal feed (platform-plugins).
3. VSS 5/6 + databroker v2 update of sdv-runtime.
4. dreamKIT CAN provider with `dbc_overlay.vspec` (README mention) driving a real CAN simulator.

## Observed on 2026-10-03 (verifier)
Re-ran the quickstart `docker run` exactly as written; container healthy after 6 s, all expected lines appeared within 9 s:
```
Starting Kuksa Databroker 0.4.4
Populating metadata from file '/home/dev/ws/vss.json'
Listening on 0.0.0.0:55555
RunTime display name: Runtime-coach-test-20261003
Connecting to Kit Server: https://kit.digitalauto.tech
Kuksa connected True
Connected to Kit Server
```
Scope: only the databroker/runtime start was verified; the playground.digital.auto pairing step and the self-host recipe were not run.
