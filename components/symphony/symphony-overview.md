---
title: Eclipse Symphony - overview
type: overview
component: symphony
tags: [sdv, symphony]
status: draft
sources:
  - https://github.com/eclipse-symphony/symphony
  - https://github.com/eclipse-uprotocol/symphony-target-example-rust
  - https://blogs.eclipse.org/post/christian-heissenberger/meet-2025-sdv-hackathon-finalists-and-winners-%E2%80%93-and-explore-their-code
  - https://github.com/eclipse-symphony/symphony
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# Eclipse Symphony

## What it is / is NOT
Cloud-to-edge **orchestration control plane** (Microsoft origin). Three constructs: Unified Object Model, Orchestration API, Providers (https://projects.eclipse.org/node/26912 snippet). Core objects: **Target** (a device/endpoint with provider config), **Solution** (what to deploy: components), **Instance** (solution applied to targets). Providers do the actual deployment (Docker, Kubernetes, Helm, Azure IoT Edge, MQTT, HTTP...). It is NOT a container runtime (that is [[ankaios-overview]] / Kanto [[kanto-overview]]) and NOT a messaging layer.

## Maturity / version
- README references **0.48.28** for install (https://github.com/eclipse-symphony/symphony). MIT. ~1000+ commits, ~159 open issues (fetched page; the page showed community-call dates from early 2025, so activity level in late 2026 is **unverified** - check commit history before betting a team on it). Go codebase (unverified from fetch; check repo).
- Not cloned (conventions: only zenoh). 

## Ankaios and Chapter 3
- The fetched README does not list an Ankaios provider. Chapter 3 team **MegaBosses** (Porto) built an end-to-end OTA with Symphony + uProtocol + Ankaios (blog above). How exactly (custom provider vs. a uProtocol target in front of Ankaios) is **unverified** - read their repo from the blog post.
- Eclipse uProtocol ships `symphony-target-example-rust`: a remote Target implementing the "Target Provider uService contract" over uProtocol (Zenoh or MQTT5), simulating ECU firmware versions/updates (https://github.com/eclipse-uprotocol/symphony-target-example-rust). This is the reference pattern for "Symphony manages a vehicle target through uProtocol".
- Chapter 3 challenges mention Ankaios, Symphony, Chariott in "Sunken Kitchen" (https://blogs.eclipse.org/node/7908 snippet).

## Quickstart (from README; NOT run here)
```bash
# Install maestro CLI (see README for platform one-liner), needs Docker
maestro up        # brings up a Symphony API + sample scenario
```
Prereqs: Docker; Linux/WSL/macOS. Expect a local Symphony REST API and sample targets/solutions/instances. Verifier: record real output. Nothing was executed (task scope: write-up).

## Pitfalls
- Heavy: K8s/Azure-flavoured docs; the SDV usage is a small slice. Budget time to find the right provider docs.
- Maturity/activity uncertain; version churn (0.48.x).
- Custom provider for Ankaios may need Go work or a uProtocol target.

## Pros / cons / when not to use
Pros: real fleet-level desired-state model, many providers, MQTT/HTTP targets easy to fake, pairs with Muto (MQTT bridge, ROS Racer blueprint). Cons: big, K8s-centric, unclear current momentum, steep concept count. Do not use if a team just needs to start containers on one box (use Ankaios directly).

## Hackathon ideas
1. Symphony provider (or uProtocol target) for Ankaios - clean up MegaBosses' work into something reusable.
2. Symphony target for an MCU (zenoh-pico / ThreadX, [[threadx-overview]]) - OTA of firmware version.
3. Symphony -> Muto fleet rollout of a ROS stack ([[muto-overview]]).
4. Hack to the Future: Symphony Instance describing HPC + MCU software set ([[chapter4-challenge-hack-to-the-future]]).

## Verification attempt 2026-10-03 (verifier): PARTIAL, `maestro up` not run
`maestro` is not installed (release 0.49.4 ships `maestro_linux_amd64.tar.gz`; not tried, it expects a k8s/minikube flow). Docker path instead: `ghcr.io/eclipse-symphony/symphony-api:latest` (1.08 GB on disk, 294 MB pulled). Plain `docker run` exits ("open -l: no such file") because `CONFIG` is unset; the no-Kubernetes config works:
```bash
docker run -d --name symph -e CONFIG=/symphony-api-no-k8s.json -e LOG_LEVEL=Info -p 28082:8082 ghcr.io/eclipse-symphony/symphony-api:latest   # 28082 because 8082 is taken
curl localhost:28082/v1alpha2/greetings        # HTTP 200 "Hello from Symphony K8s control plane (S8C)"
curl -X POST localhost:28082/v1alpha2/users/auth -H 'Content-Type: application/json' -d '{"username":"admin","password":""}'   # accessToken
curl -H "Authorization: Bearer $TOK" localhost:28082/v1alpha2/targets/registry   # HTTP 200 []
```
Idle RSS about 15 MiB. No version endpoint; logs say `"ver":"unknown"`; latest GitHub release is 0.49.4 (note above says 0.48.x). The jobs manager logs "Token creation error: unable to read from volume" (harmless in no-k8s mode). symphony-target-example-rust was not built (skipped). Status stays `draft`.
