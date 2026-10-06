---
title: Eclipse Velocitas - overview, quickstart (inline)
type: overview
component: velocitas
tags: [velocitas, vehicle-app, sdk, devcontainer, kuksa, python, cpp, adjacent]
status: draft
sources:
  - https://github.com/eclipse-velocitas
  - https://github.com/eclipse-velocitas
  - https://eclipse.dev/velocitas/docs/
last-verified: 2026-10-03
related:
  - "[[velocitas-integration-notes]]"
  - "[[vss-kuksa-overview]]"
  - "[[kanto-overview]]"
  - "[[autowrx-overview]]"
  - "[[sdv-landscape-overview]]"
---

# Eclipse Velocitas

## What it is
An end-to-end toolchain for *vehicle apps*: (1) language SDKs (Python, C++; Java and Rust/Kotlin experimental) that give a typed VSS "vehicle model" API (`vehicle.Cabin.Seat.Row1.DriverSide.Position.get()`), (2) project templates (GitHub "Use this template"), (3) the `velocitas` CLI which pins packages (`.velocitas.json`), (4) devcontainer + local/Kanto "runtimes" that start KUKSA databroker, Mosquitto and demo services, (5) CI workflows. The SDK talks to the KUKSA databroker over gRPC and optionally MQTT / gRPC services. Sources: https://github.com/eclipse-velocitas, https://eclipse.dev/velocitas/docs/.

## What it is NOT
- Not a signal store or runtime (that is [[vss-kuksa-overview]]) and not an orchestrator (see [[ankaios-overview]], [[kanto-overview]]).
- Not a safety/real-time framework: apps are QM, Python/C++ containers.

## Maturity and state in 2026 (verified 2026-10-03)
| Repo | Latest tag | Last commit | Notes |
|---|---|---|---|
| vehicle-app-python-sdk | v0.15.7 (2025-07-03) | 2025-07-03 | README still says "alpha"; 12 open issues, oldest 2023 |
| vehicle-app-cpp-sdk | v0.7.1 (2025-12-15) | 2025-12-15 | Conan 2 migration May 2025, then security bumps |
| vehicle-app-python-template | v0.1.2 (2024-03) | 2025-07-07 | SDK/base-image refresh |
| vehicle-app-cpp-template | - | 2026-01-05 | dependabot / urllib3 |
| cli | v0.13.2 (2025-04-11) | 2025-09-20 | npm deps only |
| vehicle-app-java-sdk | 0.1.2 (2025-03) | 2026-09-21 | commits 2026-09-15..21: **VSS 6.0 support**, Sonatype switch, single maintainer |
| velocitas-docs | - | 2025-02-13 | docs "last modified February 13, 2025" |
Eclipse project: Incubating, only formal release 0.1.0 (2023-05-12).
**Verdict: maintenance mode.** Bosch-driven security/dependency upkeep; no feature work on Python/C++ since mid-2025; the only 2026 life is the Java SDK. Archived: devenv-runtime-local, devenv-runtime-k3d (2023). It still works, but is frozen against an older KUKSA (see pitfalls).

## Quickstart (inline; from official docs, devcontainer NOT run here - needs VS Code)
Prerequisites: VS Code + Dev Containers extension, Docker (docker-in-docker, `--privileged`), GitHub account, ~10 GB disk, good bandwidth.
1. https://github.com/eclipse-velocitas/vehicle-app-python-template -> "Use this template" (or C++ template, or `velocitas create -n MyApp -l python -e seat-adjuster` from vehicle-app-template).
2. `git clone <your repo> && cd <repo> && code .` -> "Reopen in Container" (first build: minutes). On failure: `Dev-Containers: Rebuild Container Without Cache`.
3. F1 -> Tasks: Run Task -> `Local Runtime - Up`. Expected (from docs):
```
$ velocitas exec runtime-local up
> mqtt-broker running
> vehicledatabroker running
> seatservice running
> feedercan running
✅ Runtime is ready to use!
```
4. Run/debug the sample app (F5 "Python app debug", or the task `Run VehicleApp`); Kanto variant: task `Kanto Runtime - Up`. Debugging only works with the Local runtime.
5. No-IDE shortcut for the databroker part only: see [[autowrx-overview]] `sdv-runtime` container (verified run 2026-10-03, bundles Velocitas Python SDK 0.14.1 + databroker 0.4.4).
Quickstart doc: https://raw.githubusercontent.com/eclipse-velocitas/velocitas-docs/main/content/en/docs/tutorials/quickstart/quickstart.md

## Pitfalls (checklist)
1. **Devcontainer is heavy**: big image pull, docker-in-docker + `--privileged`; fails on Docker rootless/podman, Apple-silicon emulation, corporate proxy (dedicated "behind proxy" doc), small VMs. Pre-pull/build before the event; Codespaces is the fallback (do not mix browser and local VS Code sessions).
2. **Version pinning is by design and is now stale**: template pins `devenv-runtimes v4.1.0`, `cliVersion v0.13.2`; runtime pins `kuksa-databroker 0.5.0`, `mosquitto 2.0.14`, `seat_service 0.4.0` (devenv-runtimes manifest.json). Current KUKSA release line is 0.6.x with the newer `kuksa.val.v2` API (https://projects.eclipse.org/projects/automotive.kuksa lists 0.6.1); the SDK speaks the older `kuksa.val.v1`. Do not "just bump" the databroker image; pin and stay consistent. Do not let teams run `latest` images.
3. SDK alpha: open issues "Examples outdated", "Outdated/incomplete example instructions", "Seat Adjuster Dockerfile not buildable stand-alone" (python-sdk issues).
4. Generated vehicle model must match the VSS version served by the databroker (generation by `vehicle-model-generator`); mismatch gives silent unknown-path errors.
5. `GITHUB_API_TOKEN` env var is read by the devcontainer for package download; rate limits hit shared hackathon networks.
6. Python SDK requires Python >= 3.10.

## Pros / cons / when not to use
Pros: fastest path from VSS idea to a containerised app; typed model; templates + CI; playground (autowrx) can export to it; widely used in earlier hackathons (BCX2022 passenger-welcome used Velocitas + KUKSA + Leda; https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-passenger-welcome).
Cons: maintenance mode, pinned to old KUKSA, heavy tooling, MQTT/gRPC-only (no uProtocol/Zenoh in core; `pkg-velocitas-uprotocol` repo stale since 2024-09).
Skip it if: you only need to read/write signals (use `kuksa-client` / databroker gRPC directly), need Rust-first (Rust SDK stale since 2025-03), or have a hard 2-day limit and no pre-built image.

## Hackathon ideas
1. Port the Python SDK's databroker layer to `kuksa.val.v2` (small, high-value PR).
2. Velocitas + uProtocol: revive `pkg-velocitas-uprotocol` against current up-rust/up-python ([[uprotocol-overview]]).
3. A slim non-devcontainer path: Dockerfile + Makefile that builds the template app against a pinned databroker (take-home).
4. Run the sample app under [[ankaios-overview]] instead of Kanto (manifest generator for AppManifest.json).
