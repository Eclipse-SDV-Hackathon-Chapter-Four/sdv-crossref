---
title: OpenSOVD - integration notes
type: synthesis
component: opensovd
tags: [opensovd, integration, s-core, openbsw, kuksa, vss, uprotocol, ankaios, opendut, autosd, iceoryx2, doctor-whodunit]
status: draft
sources:
  - repos/opensovd-main/docs/design/adr/001-adr-score-interface.md
  - repos/opensovd-main/docs/design/mvp.md
  - repos/opensovd-fault-lib/Cargo.toml
  - repos/opensovd-fault-lib/README.md
  - repos/opensovd-core/examples/server/systemd/systemd.rs
  - https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/tree/main/OpenBSW-SOVD-Demo
  - https://github.com/eclipse-opensovd/opensovd-core/issues
last-verified: 2026-10-03
related:
  - "[[opensovd-overview]]"
  - "[[opensovd-howto]]"
  - "[[s-core-overview]]"
  - "[[openbsw-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[opendut-overview]]"
  - "[[autosd-overview]]"
  - "[[iceoryx2-overview]]"
  - "[[sdv-blueprints-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[hackfest-esslingen-2026]]"
---

# OpenSOVD - integration notes

Grep check on 2026-10-03: across the five cloned OpenSOVD repos, there are **no mentions** of kuksa, uprotocol, ankaios, opendut, autosd, zenoh or openbsw. The only hits for "vss" are inside "kvs". The only other-project dependencies in code are **iceoryx2** (fault-lib) and **S-CORE persistency** (`rust_kvs` in dfm_lib).

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| S-CORE | yes | Fault library is the agreed interface (ADR-001); DFM stores into S-CORE `rust_kvs` (persistency); S-CORE plans to consume OpenSOVD via `inc_diagnostics` and reference_integration; "http-ipc" planned between libs and SOVD server | demo | ADR-001; `src/dfm_lib/Cargo.toml`; HackFest: "S-CORE with OpenSOVD on top of EB corbos Linux using a Raspberry Pi", RC car via S-CORE middleware made diagnosable; discussion #103 |
| OpenBSW | yes | OpenBSW virtual ECU (POSIX/FreeRTOS) as UDS server over DoIP :13400 -> OpenSOVD CDA (MDD generated from JSON) -> SOVD REST -> Grafana; needed an OpenBSW DoIP ACK-handling overlay and added 0x19/0x14 DTC services | demo | Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/OpenBSW-SOVD-Demo; HackFest blog |
| openDuT | yes | openDuT provides network connectivity (Pi / remote peer) between the CDA and real vehicles' DoIP or a split testcontainer; also a fault-injection layer for Chapter 4 | demo | [[opendut-integration-notes]] (openDuT-playground, HackFest blog) |
| iceoryx2 | yes | fault-lib Reporter -> DFM transport and DFM query server use iceoryx2 (git rev eba5da4) | prototype (ran locally: dfm_bin + tst_app, 2026-10-03) | repos/opensovd-fault-lib/Cargo.toml; [[opensovd-howto]] recipe 8 |
| VSS / KUKSA | none found | idea: a `DataProvider` that reads KUKSA databroker signals and exposes them as SOVD `currentData` on an app/component entity; stale-signal detection could raise SOVD faults | idea | no code or issue found; design.md mentions "semantic interoperability" only; project proposal says it collaborates with COVESA (unverified detail) |
| uProtocol | none found | idea: bridge uProtocol fault/heartbeat/mitigation events (Doctor Whodunit) into fault-lib Reporter or a SOVD `FaultProvider`; SOVD itself stays HTTP | idea | none |
| Ankaios | none found | idea: run gateway/CDA/DFM as Ankaios workloads (gateway image is distroless, port 7690); expose workload states as SOVD data/faults | idea | none; [[ankaios-integration-notes]] lists the same idea |
| AutoSD | none found | idea: run on AutoSD as containers or systemd service; core ships a `systemd` example with `sd-notify` readiness (`examples/server/systemd`) | idea | repos/opensovd-core/examples/server/systemd/systemd.rs |
| Grafana (non-SDV) | yes | Infinity datasource polling SOVD REST | demo | OpenBSW-SOVD-Demo |
| DLT (COVESA, non-Eclipse) | yes | CDA `dlt-tracing` feature; `dlt-tracing-lib` repo | prototype | repos/opensovd-cda/cda-tracing/Cargo.toml |
| MCP / AI agents | yes | `opensovd-mcp` (topology tools); `mdd-ui` MCP for MDD files; HackFest AI chat demo | prototype | opensovd-cli/mcp/README.md; HackFest blog |

## Notes per pairing
- **S-CORE:** OpenSOVD is S-CORE's diagnostics answer. The MVP is timed for S-CORE v1.0 at the end of 2026 ([mvp.md](../../repos/opensovd-main/docs/design/mvp.md)). Safety split: S-CORE owns the safety-relevant fault-lib scope (up to ASIL-B), OpenSOVD stays QM. Open questions from workshop #103: integrate FaultLib or DiagLib first, Bazel config, dual release. The workshop named the Friedrichshafen hackathon as a collaboration opportunity. See [[s-core-overview]].
- **OpenBSW:** this is the most reproducible "real UDS ECU" for a hackathon. Pitfall: the upstream DoIP server didn't handle diagnostic message ACK payloads 0x8002/0x8003 the way the CDA needed, and the demo replaces `DoIpServerConnectionHandler.cpp` (lines 284-290). Check whether that has gone upstream before relying on vanilla OpenBSW. Unverified as of 2026-10-03. See [[openbsw-overview]].
- **KUKSA/VSS -> SOVD mapping (gap):** VSS describes vehicle signals, SOVD describes diagnostic resources per entity. A natural mapping is VSS branch -> SOVD `area`/`component`, leaf sensor -> `data` item (category `currentData`), and attributes -> `identData`. Nobody has built it. It's a good 2-day contribution ([[vss-kuksa-overview]]).
- **Doctor Whodunit wiring (suggested, not built):** Guardian on AutoSD under Ankaios. Fault/heartbeat/mitigation go over uProtocol. A small bridge either writes into an opensovd-core `DataProvider` ([[opensovd-howto]] recipe 1) or reports through fault-lib to the DFM (recipe 8). openDuT injects faults. The evidence collector polls SOVD as the independent oracle and joins it with openDuT campaign timestamps ([[chapter4-challenge-doctor-whodunit]]). Package it as an SDV Blueprint ([[sdv-blueprints-overview]]).
