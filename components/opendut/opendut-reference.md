---
title: openDuT - reference
type: reference
component: opendut
tags: [opendut, reference, versions]
status: draft
sources:
  - repos/opendut
  - repos/opendut-playground
  - https://opendut.eclipse.dev/
last-verified: 2026-10-03
related:
  - "[[opendut-overview]]"
  - "[[opendut-quickstart]]"
---

# openDuT reference

## Repos / links
- Main: https://github.com/eclipse-opendut/opendut, shallow clone `repos/opendut` @ a2447d876905d3293577f360af877229ca989017 (2026-07-17).
- HackFest playground: https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/openDuT-playground, `repos/opendut-playground` @ 421c257bf13b1c9887cf0b0763d6afdc42f21982 (2026-04-30). Releases: tag `video` (mirror-folding videos).
- Docs: https://opendut.eclipse.dev/ ; User manual /book/user-manual/ ; dev testenv /book/development/testenv/ ; Matrix room #automotive.opendut:matrix.eclipse.org ; Cannelloni fork https://github.com/eclipse-opendut/cannelloni/releases/
- Issues of note: #459 (EDGAR container non-root), #493 (testenv dev mode, PR), #494 (CAN PR), #495 (cleo apply leader check), #518 (CAN). Not fetched individually; referenced from CHANGELOG/playground.

## Versions
Released v0.10.2 (2026-06-11), v0.10.1 (2026-06-03), v0.10.0 (2026-04-02). Workspace `0.11.0-alpha`. Images: ghcr.io/eclipse-opendut/opendut-carl:0.10.2. Pinned third-party: NetBird 0.64.5, Traefik v3.6.8, Postgres 14.15, Grafana 12.3.
v0.10.2 changed CARL API `CanConnection` to single `port` (rolling upgrade: deprecated field 4 kept one cycle).

## Crates (repos/opendut)
opendut-carl, opendut-edgar, opendut-lea, opendut-cleo, opendut-model, opendut-auth, opendut-vpn (NetBird), opendut-telemetry, opendut-util, opendut-viper (VIPER runtime, Python bindings), tests, `.ci/cargo-ci` (`cargo ci`, `cargo theo`, `cargo carl`, `cargo cleo`, `cargo lea`).

## Interfaces
- CARL gRPC (doc/src/development/carl-grpc-api.md), protobuf in opendut-carl API crates.
- CLEO YAML kinds `PeerDescriptor`, `ClusterDescriptor` (version v1).
- Config: `/etc/opendut/carl.toml` or env vars (TOML keys joined by `_`, e.g. `NETWORK_BIND_HOST`); EDGAR env `OPENDUT_EDGAR_*`; log level `OPENDUT_LOG`.
- EDGAR archs: x86_64-unknown-linux-gnu, armv7-unknown-linux-gnueabihf, aarch64-unknown-linux-gnu.
- Domains: opendut.local, auth., netbird-api., netbird-relay., signal., nginx-webdav., opentelemetry., monitoring. (+ .env.development).
- mTLS client auth optional (`docker-compose.override.mtls.yml`).
- Host requirements for CAN: can-utils, cannelloni, kernel `vcan`, `can_gw max_hops=2`, `ip_gre`/`gre`.

## Languages
Rust (all components), WASM plugins for EDGAR setup (`plugins/*.wasm`), Python-like VIPER tests, Ansible/Vagrant for testenv.
