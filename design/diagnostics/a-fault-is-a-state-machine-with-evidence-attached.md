---
title: A fault is a state machine with evidence attached
type: pattern
cluster: diagnostics
component: none
tags: [dtc, uds, 0x19, dem, aging, freeze-frame, faults, sovd]
status: draft
sources:
  - https://www.iso.org/standard/72439.html (ISO 14229-1, UDS: 0x19 ReadDTCInformation, 0x14 ClearDiagnosticInformation, DTC status byte; number unverified)
  - https://www.asam.net/standards/detail/sovd/ (ASAM SOVD, origin of ISO 17978)
  - https://www.autosar.org/standards/classic-platform (AUTOSAR CP SWS Diagnostic Event Manager: event, debounce, operation cycle, aging; not fetched this session)
  - https://github.com/eclipse-opensovd/fault-lib (src/common/src/fault.rs LifecycleStage, src/dfm_lib/src/aging_manager.rs, operation_cycle.rs)
  - https://github.com/eclipse-opensovd/classic-diagnostic-adapter (docs/03_architecture/02_sovd-api, Faults section)
  - "[[opensovd-reference]] (CDA fault JSON, DFM SovdFault)"
last-verified: 2026-10-03
related:
  - "[[opensovd-overview]]"
  - "[[opensovd-integration-notes]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[let-the-standard-timestamp-your-evidence]]"
applies-to: [opensovd, s-core, openbsw, vss-kuksa]
gap-rows: [A1, A2, A4, A5, A8, E7]
---

# A fault is a state machine with evidence attached

**Problem.** A team stores "fault: cell temp stale" as a boolean or a log line. A tester cannot tell if it is happening now, happened this drive, was cleared, or aged out, and nobody can see what the system looked like when it fired.

**Forces.**
- A fault must latch (a flickering sensor must not erase the finding) yet also heal (a car with a year-old fault is useless).
- Time in diagnostics is measured in *operation cycles* (ignition, drive), not wall-clock.
- Evidence (freeze frame) must be captured at the failing edge, not when someone asks.
- Three code bases spell the same bits differently.

**The rule.** Model a fault as an eight-bit status register plus counters plus snapshots, and let clients filter on bits, never on prose. The UDS status byte (ISO 14229-1, read with 0x19, clear with 0x14) is: bit0 testFailed, 1 testFailedThisOperationCycle, 2 pendingDTC, 3 confirmedDTC, 4 testNotCompletedSinceLastClear, 5 testFailedSinceLastClear, 6 testNotCompletedThisOperationCycle, 7 warningIndicatorRequested. Pending means failed this cycle and not yet confirmed; confirmed latches until aging or clear. Environment data is attached: a freeze frame (snapshot at failure) and extended records (occurrence, aging counters). Healing is the failing test passing for N cycles; aging then drops confirmed.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 14229-1 (UDS) 0x19/0x14 | status byte, mask filter, snapshot and extended-data records | the canonical bit semantics and read/clear services |
| AUTOSAR Dem | Event (debounced pass/fail, PREPASSED/PREFAILED/PASSED/FAILED) mapped to a DTC with an origin memory, operation cycles, aging, freeze frame class | the event-to-DTC split: many events may map to one DTC, so reporters never know DTC numbers |
| ASAM SOVD / ISO 17978 `faults` | list, read with environment data, delete one or all, filter by status | the same register over HTTP/JSON |
| OpenSOVD fault-lib / DFM | `LifecycleStage` NotTested/PreFailed/Failed/PrePassed/Passed with a checked transition table; `ResetTrigger` PowerCycles / OperationCycles / StableFor / ToolOnly; `aging_counter`, `healing_counter` | the Dem shape in Rust, over iceoryx2 |
| OpenSOVD CDA | `GET /faults?status[confirmedDtc]=true` or `status[mask]=09`; detail with `include-snapshot`, `include-extended-data` | the working read path for real UDS ECUs |
| SAE J1979 / ISO 15031-5 | emission DTCs with pending/confirmed/MIL | the regulated subset of the same register |

**On the Eclipse SDV stack.**
- Reporter side: [[opensovd-overview]] fault-lib `Reporter` raises a *descriptor-keyed event* (Dem-like); debounce and enabling conditions live in the catalog, so a Guardian in Python or Rust reports "stale Temperature.Cell" and never a DTC number.
- DFM: `aging_manager.rs` and `operation_cycle.rs` implement the cycle logic; operation cycles come from an `OperationCycleProvider` (sources Ecu, Hpc, Manual). Aging windows are held in RAM only, so a DFM restart resets the in-progress window (counters persist in S-CORE `rust_kvs`).
- Read side: today only the CDA serves `/components/{ecu}/faults`; core has none ([[opensovd-reference]], issue #156). A `FaultProvider` in core must return the CDA JSON shape (snake_case flags plus `mask`).
- Hackathon wiring: a Guardian that watches `Vehicle.Powertrain.TractionBattery.Temperature.*` raises the event; the snapshot carries the last values and their ages ([[vss-kuksa-overview]]).

**The trap.** Reinventing the register in your own JSON. The CDA writes `test_failed`, the Dem-style DFM writes `confirmedDTC`, and the CDA filter keys are `confirmedDtc`: pick the UDS bit order and one spelling at the edge, and keep the hex `mask` as the join key.

**For a hackathon team.** One fault with a debounced pass/fail edge, a mask returned as hex, a snapshot with two signal values and their timestamps, and a clear that resets it. Pitch line: "our fault is a state machine with evidence, and the mask is the same byte a workshop tester already understands."

**Evidence.** Bit order matches the CDA sample in [[opensovd-reference]] (`mask:"09"` = testFailed + confirmedDTC). Transition table and aging caveat quoted from `repos/opensovd-fault-lib/src/common/src/fault.rs` and `src/dfm_lib/src/aging_manager.rs`. Filter keys from CDA `docs/03_architecture/02_sovd-api/02_sovd-api.rst`. The three spellings finding extends gap E7 and CDA issue #553 (shared model); the Dem details are from memory of the SWS (unverified against the current release).
