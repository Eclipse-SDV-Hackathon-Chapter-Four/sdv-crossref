---
title: Eclipse OpenSOVD - overview
type: overview
component: opensovd
tags: [opensovd, sovd, iso17978, diagnostics, uds, doip, odx, rust, s-core]
status: draft
sources:
  - https://projects.eclipse.org/projects/automotive.opensovd
  - https://github.com/eclipse-opensovd
  - repos/opensovd-main/README.md
  - repos/opensovd-main/docs/design/design.md
  - repos/opensovd-main/docs/design/mvp.md
  - repos/opensovd-main/docs/design/adr/001-adr-score-interface.md
  - repos/opensovd-core/README.md
  - repos/opensovd-core/docs/architecture.md
  - repos/opensovd-cda/README.md
  - repos/opensovd-fault-lib/README.md
  - https://github.com/eclipse-opensovd
  - https://www.iso.org/standard/86587.html
  - https://github.com/eclipse-opensovd/opensovd-core/issues
  - https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/
last-verified: 2026-10-03
related:
  - "[[opensovd-quickstart]]"
  - "[[opensovd-howto]]"
  - "[[opensovd-reference]]"
  - "[[opensovd-integration-notes]]"
  - "[[s-core-overview]]"
  - "[[openbsw-overview]]"
  - "[[opendut-overview]]"
  - "[[iceoryx2-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[hackfest-esslingen-2026]]"
---

# Eclipse OpenSOVD - overview

**One line:** an open-source (Apache-2.0, Rust) implementation of **SOVD** (Service-Oriented Vehicle Diagnostics, ISO 17978), the REST/HTTP+JSON successor of UDS-based diagnostics. Today it is two separate, usable pieces: a **SOVD server/gateway** (`opensovd-core`) with a small API surface, and a much more complete **Classic Diagnostic Adapter** (CDA) that exposes UDS-over-DoIP ECUs as SOVD resources. Eclipse project state: **Incubating** ([project page](https://projects.eclipse.org/projects/automotive.opensovd)).

## What SOVD is
- **Standard:** ASAM SOVD (v1.0 2022, v1.1) was moved into ISO as **ISO 17978**. Part 3 (API) was published 2026-03-16, Part 1 (general, definitions) 2026-05-21 ([https://www.iso.org/standard/86587.html](../../https://www.iso.org/standard/86587.html)). The spec text is paywalled. Nothing in the vault quotes it directly, so the resource names below come from the implementations and the OpenSOVD design docs.
- **Idea:** diagnostics as a resource-oriented HTTP API, not byte-level UDS services. A tester (off-board, on-board, or in the cloud) navigates **entities** and their **resource collections**. The JSON is self-describing (with `include-schema`), so a client doesn't need ODX to decode values.
- **Entity types:** `areas` (logical domain/zone), `components` (an ECU or HPC), `apps` (software on a component), `functions` (a cross-entity view, e.g. a functional group); `subareas`/`subcomponents` also exist ([design.md](../../repos/opensovd-main/docs/design/design.md)). Relations between them: `hosts`, `is-located-on`, `contains`, `belongs-to`, `depends-on`.
- **Resource collections per entity:** `data` (identData, currentData, storedData, sysInfo, custom categories; read/write), `faults` (DTC-like entries with status and environment data, read and delete), `operations` (routines and I/O control, sync or async `executions`), `configurations` (coding/parameters), `modes` (session, security access, comm control, DTC setting), `locks` (exclusive access), `bulk-data` (files, flashing), `logs`, `updates`, and `version-info` at the root.
- **Versus UDS:** UDS (ISO 14229) is session-based binary request/response over DoIP (ISO 13400) or CAN. Decoding it needs an ODX description. SOVD wraps or replaces it with HTTPS, OAuth/JWT, and discoverable JSON. For legacy ECUs a **Classic Diagnostic Adapter** translates SOVD calls to UDS using the ECU's ODX.

## What OpenSOVD ships (status 2026-10-03)
| Piece | Repo | Language | State | What it actually does |
|---|---|---|---|---|
| SOVD server library and `opensovd-gateway` binary | [opensovd-core](https://github.com/eclipse-opensovd/opensovd-core) v0.1.1 | Rust (nightly-2026-05-07 pinned) | Early, actively developed. Container image on GHCR | Entity discovery (`areas`/`components`/`apps` plus `hosts`/`contains`/`belongs-to`), `data` (list/categories/groups/read/write with JSON schema), `bulk-data`, `version-info`. **No `faults`, `operations`, `configurations`, `modes`, `locks`, `logs` yet** (verified: `/faults` returns 404; route list in `opensovd-server/src/routes/`). `faults` is issue #156, opened 2026-08-28, no PR. Mock topology via `--mock`. Auth: pluggable `Authenticator`/`Authorizer` traits, JWT (`JwtAuthenticator`) and Rego policies (`RegorusAuthorizer`, regorus), TLS/mTLS. MCP server `opensovd-mcp` for AI agents |
| Classic Diagnostic Adapter (CDA) | [classic-diagnostic-adapter](https://github.com/eclipse-opensovd/classic-diagnostic-adapter) | Rust (axum/aide), MSRV 1.88 | **Most mature component** (S-CORE workshop #103). Tested on real Mercedes, BMW and Porsche cars at the Esslingen HackFest | SOVD -> UDS over **DoIP** (and CAN/ISO-TP via socketcand, feature-gated). Driven by **MDD** files (compact binary form of ODX). Per-ECU `data` (0x22/0x2E), `operations` (0x31 RoutineControl), `configurations` (varcoding class), `faults` (0x19 read, 0x14 clear), `modes` (session 0x10, security 0x27, commctrl 0x28, dtcsetting 0x85), `locks`, `functions` (functional groups), flashing extensions (`x-sovd2uds-download`, `bulk-data`), single-ECU jobs, variant detection, Swagger UI at `/swagger-ui`. Base path `/vehicle/v15/` |
| odx-converter | [odx-converter](https://github.com/eclipse-opensovd/odx-converter) | Kotlin/JVM | Early ("output format may change") | PDX (ODX zip) -> MDD (e.g. 41 MB ODX -> 470 kB). **You must supply the ODX XSD yourself** (copyright) |
| fault-lib + DFM | [fault-lib](https://github.com/eclipse-opensovd/fault-lib) | Rust (Cargo + Bazel) | Prototype | Reporter API for apps (`Reporter`, catalogs in JSON, debounce, enabling conditions) -> **iceoryx2** IPC -> Diagnostic Fault Manager (lifecycle, aging, operation cycles, storage in S-CORE `rust_kvs`) -> `SovdFaultManager` (SOVD-shaped fault records, query over iceoryx2). **Not wired into opensovd-core's HTTP server yet** |
| uds2sovd-proxy | [uds2sovd-proxy](https://github.com/eclipse-opensovd/uds2sovd-proxy) | Rust | README only | Planned: lets legacy UDS testers talk to SOVD |
| cpp-bindings | [cpp-bindings](https://github.com/eclipse-opensovd/cpp-bindings) | - | Empty repo | Planned C++ APIs |
| demo | [demo](https://github.com/eclipse-opensovd/demo) | Kotlin + Rust | Demo ("major parts AI generated", not reviewed) | CDA with a Google OAuth plugin, ECU sim, diag-converter (OCA 2026 talk) |
| mdd-ui, dlt-tracing-lib, mbedtls-rs | - | Rust | Tooling | MDD viewer + MCP; DLT tracing appender; patched Mbed TLS for the CDA |

Sources: [https://github.com/eclipse-opensovd](../../https://github.com/eclipse-opensovd), repo READMEs cloned at the commits in [[opensovd-reference]].

## What it is NOT (yet)
- Not a complete ISO 17978 server. The standalone server (`opensovd-core`) covers discovery, data and bulk-data only. Faults, operations, modes and locks exist **only in the CDA**, and only for UDS ECUs described by MDD.
- Not one integrated stack yet. The CDA and opensovd-core have **different base paths** (`/vehicle/v15` vs `/sovd/v1`), different models and separate code. Convergence is tracked in CDA issue #553 (early). Gateway forwarding from core to the CDA is on the MVP roadmap ("CDA connected to SOVD Server (via Gateway)", 26Q2) but has not landed in `opensovd-core` (no proxy/forwarding route in `opensovd-server/src/routes/`).
- Not safety-qualified. Diagnostics is QM. S-CORE takes the fault-lib safety scope (up to ASIL-B) per ADR-001 ([adr](../../repos/opensovd-main/docs/design/adr/001-adr-score-interface.md)).
- Not a binary distribution for the CDA. No published image ("for legal reasons", testcontainer README). Build from source (about 2 min on 32 cores, see [[opensovd-quickstart]]).
- Not production-secure by default. The CDA's default security plugin **accepts any credentials** unless built with the `auth` feature, and it signs JWTs with the literal key `"secret"` ([default_security_plugin.rs](../../repos/opensovd-cda/cda-plugin-security/src/default_security_plugin.rs)).

## Architecture (target, from design.md)
Fault Library (decentral, in each app) -> IPC -> **Diagnostic Fault Manager** (central, plus Diagnostic DB) -> **SOVD Server** <- **Diagnostic Library** (apps register data/operations) and **Service Apps** (routines such as DTC clear, ECU reset, flash). The **SOVD Gateway** routes to the SOVD Server, the **Classic Diagnostic Adapter** (-> UDS ECUs via DoIP), and other native SOVD ECUs. The **UDS2SOVD Proxy** serves legacy testers. The **SOVD Client** can be off-board, on-board or in the cloud. Example topology: `components/{Hpc1, Ecu1..N}`, `apps/{FaultManager, App1..N, Sovd2Uds, Uds2Sovd}`, `functions/VehicleHealth` ([design.md](../../repos/opensovd-main/docs/design/design.md)).

MVP goal (end of 2026, for S-CORE v1.0): read and clear DTCs via SOVD, report faults via the Fault API into the DFM, reach a UDS ECU via the CDA, trigger a sample diagnostic service, plus a demo vehicle layout in a Docker network ([mvp.md](../../repos/opensovd-main/docs/design/mvp.md)). As of 2026-10-03, read/clear DTC via the **standalone server** is still open (#156). The DTC paths only work through the CDA.

## Maturity and activity
- Project created 2025 (kickoff video, ADR-001 2025-07-21). Weekly Forum on Mondays 11:30 CET. Workstreams for CDA, Core, S-CORE integration and others ([README](../../repos/opensovd-main/README.md); [discussions](https://github.com/eclipse-opensovd/opensovd/discussions)).
- Very active: opensovd-core and the CDA had commits on 2026-10-02/03, and the CDA has 77 open issues.
- People: the OpenSOVD Core workstream lead is among the Chapter 4 coaches ([[chapter4-challenge-doctor-whodunit]]).

## Esslingen HackFest 2026 (28-29 Apr) - what was shown
From the Eclipse blog ([https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/](../../https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/)); details in [[hackfest-esslingen-2026]]:
- **S-CORE x OpenSOVD:** "end-to-end demonstration of S-CORE with OpenSOVD on top of EB corbos Linux using a Raspberry Pi". A 1:10 RC car controlled through S-CORE middleware and made diagnosable via OpenSOVD.
- **Real vehicles:** "communication via the OpenSOVD CDA worked in principle with all available vehicles". Full functionality on Mercedes-Benz, BMW/Porsche still in progress. "Several diagnostic description challenges" were found.
- **OpenBSW x OpenSOVD:** an OpenBSW virtual ECU serves UDS (0x19/0x14/0x22 ...) over DoIP, the CDA translates it to SOVD, and Grafana shows sensors and DTCs. This needed a DoIP ACK-handling overlay in OpenBSW ([https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/tree/main/OpenBSW-SOVD-Demo](../../https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/tree/main/OpenBSW-SOVD-Demo); [[openbsw-overview]]).
- Web UIs and AI-assisted diagnostics (chat + MCP) for OpenSOVD. Diagnostic reports sent to backends. openDuT used for remote access to the CDA ([[opendut-overview]]).

## Relevance to Chapter 4 "Doctor Whodunit"
The challenge wants "diagnostic truth exposed through OpenSOVD" ([[chapter4-challenge-doctor-whodunit]]). Realistic options, best first:
1. **Custom `DataProvider` in an opensovd-core server** (Rust, about 1-2 h): expose the Guardian's fault state as SOVD **data** items (`storedData` category, e.g. `guardian.fault.cell_temp_stale`) plus `currentData` (last cell temperature, freshness age). This works today, but it is not the standard `faults` resource.
2. **Implement `faults` in opensovd-core** (issue #156 already has the design: `FaultProvider` trait and `GET {entity}/faults[/{code}]`). This is a real upstream contribution and scores on "Ecosystem integrability". Feed it from fault-lib/DFM or straight from uProtocol fault events.
3. **Guardian as a UDS ECU behind the CDA** (OpenBSW-style DTCs over DoIP + ODX/MDD): you get standards-compliant `faults` with ISO 14229 status bits, but you have to author ODX/MDD and run DoIP. Too heavy for 2 days unless you start from the OpenBSW-SOVD-Demo.
The evidence factory can treat SOVD as an **independent oracle**: after each openDuT injection, `GET .../faults` (or data) and record DTC status bits and timestamps alongside the uProtocol events. See [[opensovd-howto]].

## Pros / cons
**Pros:** a real standard (ISO 17978) with an open implementation. Rust, fast and small. The CDA is proven on real OEM cars and has broad UDS coverage (sessions, security access, flashing, functional groups). The gateway has a one-command Docker mock and is easy to extend with a `DataProvider`. JSON schema per value. MCP server for AI tooling. Active maintainers, and S-CORE integration is a stated goal.
**Cons:** the standalone server has no faults/operations yet. Two codebases with divergent paths. No CDA binary. ODX/MDD authoring is a barrier (XSD not included, converter needs Java). Nightly Rust for core. The fault-lib/DFM isn't reachable over HTTP. The spec is paywalled, so compliance is hard to check. Default security is demo-grade.
**When not to use:** if you need only signal telemetry, use KUKSA/VSS ([[vss-kuksa-overview]]). If you need hard real-time fault reaction, use S-CORE health/lifecycle; SOVD is QM and off the safety path. If you have no ODX for a legacy ECU, the CDA can't decode anything.

## Hackathon ideas (gaps)
- Implement `faults` (GET list/detail, DELETE) in opensovd-core per #156. Add a fault-lib/DFM -> HTTP bridge.
- A `KuksaDataProvider`: map VSS signals onto SOVD `data` (currentData) for an `apps/guardian` entity. Cross-project, and it doesn't exist yet.
- A **fault timeline** UI or endpoint: poll SOVD faults/data, store transitions with timestamps, render hazard -> fault -> detection -> verdict. The HackFest built web UIs and Grafana dashboards, so reuse the Infinity datasource pattern.
- A gateway route that forwards `/components/{ecu}` to a CDA (MVP roadmap item).
- Python client library or pytest fixtures for SOVD (core has a Rust client and Bruno/pytest tests only).
- An `operations` resource for mitigation commands (e.g. "enter degraded mode") in core.
- Fix small CDA inconsistencies seen during the quickstart (e.g. `href` in `/components` uses `/Vehicle/v15` with a capital V) ([[opensovd-quickstart]]).
