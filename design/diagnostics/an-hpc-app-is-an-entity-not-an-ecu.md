---
title: An HPC app is an entity, not an ECU: faults flow in through a library
type: pattern
cluster: diagnostics
component: none
tags: [sovd, hpc, apps, hosts, ankaios, fault-lib, dfm, iceoryx2, s-core]
status: draft
sources:
  - https://github.com/eclipse-opensovd/opensovd (docs/design/design.md topology, adr/001-adr-score-interface.md)
  - https://github.com/eclipse-opensovd/fault-lib
  - https://github.com/eclipse-opensovd/opensovd-core (Topology, App, Component entities)
  - https://eclipse-ankaios.github.io/ankaios/ (control interface, complete state, workload states)
  - https://github.com/eclipse-score/inc_diagnostics
  - "[[ankaios-integration-notes]]"
last-verified: 2026-10-03
related:
  - "[[opensovd-integration-notes]]"
  - "[[ankaios-integration-notes]]"
  - "[[one-backend-trait-many-backends]]"
  - "[[a-fault-is-a-state-machine-with-evidence-attached]]"
applies-to: [opensovd, ankaios, s-core, iceoryx2]
gap-rows: [A2, A3, A9, A4, H11]
---

# An HPC app is an entity, not an ECU: faults flow in through a library

**Problem.** A container crashes on an HPC. There is no UDS ECU, no DID table, no 0x19. Teams either fake an ECU or write ad-hoc JSON, and the supervisor that knows the crash (the orchestrator) never tells the diagnostic stack.

**Forces.**
- SOVD has `apps` for software and `components` for compute units; UDS only knows ECUs.
- The app must report fast and cheaply (no HTTP in a control loop), so IPC to a manager is needed.
- The orchestrator owns lifecycle truth; the app owns semantic truth ("stale sensor").
- Safety scope (S-CORE up to ASIL-B for fault-lib) differs from QM diagnostics.

**The rule.** Model software as entities and let two producers feed them: the app reports *semantic faults* through a library, the orchestrator reports *lifecycle states*. `components/Hpc1` `hosts` apps; each `apps/X` `is-located-on` Hpc1; faults come from a central fault manager fed over IPC; `functions/VehicleHealth` `depends-on` the manager for the cross-entity view. Orchestrator states (Pending, Starting, Running, Succeeded, Failed, Stopping, Removed, Unknown) are *data* on the app (current state, restart count) and a fault only when policy says so (a mandatory workload leaving Running).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ASAM SOVD entity model | `areas`, `components`, `apps`, `functions`, relations `hosts`, `contains`, `is-located-on`, `belongs-to`, `depends-on` | the vocabulary for HPC software |
| OpenSOVD design.md | Diagnostic Library registers apps; FaultManager serves `faults/` (does not aggregate other apps); Service Apps for routines | the target architecture |
| fault-lib / DFM | `Reporter` -> iceoryx2 -> DFM (aging, cycles, `rust_kvs`) -> `SovdFaultManager`; ADR-001: fault-lib is the S-CORE interface | the report path, working locally (`dfm_bin` + `tst_app`) |
| S-CORE inc_diagnostics (`score/mw/diag`) | S-CORE-side API planned to feed OpenSOVD; "http-ipc" for now | the S-CORE entry (README still template per vault) |
| AUTOSAR Adaptive Diagnostic Management | diagnostic server per application, event reporting by SWC | the same idea in Adaptive |
| Ankaios control interface | workload states in `CompleteState`, event subscription | the lifecycle truth source |

**On the Eclipse SDV stack.**
- Missing glue (gaps A2/A3): nothing exposes the DFM over HTTP; no S-CORE app reports to OpenSOVD at runtime ([[hackfest-esslingen-2026]] G1/B7). Smallest chain: Guardian uses fault-lib `Reporter` -> DFM -> a bridge reading `SovdFaultManager` (iceoryx2 query) -> `FaultProvider` in core ([[opensovd-integration-notes]]).
- A9: an Ankaios control-interface app subscribes to `workloadStates` and publishes `apps/guardian/data/x-ankaios-state` and, on `Failed`, a fault via the same Reporter ([[ankaios-integration-notes]]).
- Compose the entity tree: `components/Hpc1` hosts `apps/Guardian`, `apps/FaultManager`; the CDA appears as `apps/Sovd2Uds`.
- Cycles: wire Ankaios start/stop to the DFM `OperationCycleProvider` (source `Hpc`) so aging is meaningful.

**The trap.** Promoting every orchestrator event to a DTC: a restart loop then fills fault memory and ages out the one real fault.

**For a hackathon team.** Kill the Guardian container, show `apps/guardian/data` flip to `Failed` and one fault appear with a timestamp, restart it and watch healing count. Pitch line: "software is an entity; the orchestrator and the app each tell their half".

**Evidence.** Topology and relation table: `repos/opensovd-main/docs/design/design.md`. DFM chain verified in the vault ([[opensovd-integration-notes]], recipe 8 in [[opensovd-howto]]). Ankaios state list from [[ankaios-reference]] (exact list unverified). S-CORE `inc_diagnostics` README is a template per [[opensovd-reference]].
