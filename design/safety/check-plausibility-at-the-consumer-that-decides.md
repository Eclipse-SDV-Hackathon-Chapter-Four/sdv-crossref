---
title: Check plausibility at the consumer that decides
type: pattern
cluster: safety
component: none
tags: [plausibility, freshness, stuck-at, rate-of-change, cross-check, debounce, dtc, fault-lib]
status: draft
sources:
  - https://www.iso.org/standard/68387.html (ISO 26262-5:2018 Annex D; sensor range, correlation, rationality checks) (catalogue id and table wording unverified)
  - https://ww2.arb.ca.gov/our-work/programs/obd-on-board-diagnostic-program (CARB OBD II, 13 CCR 1968.2: circuit, out-of-range, rationality monitoring)
  - https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_DiagnosticEventManager.pdf (counter- and time-based debouncing)
  - repos/opensovd-fault-lib/src/common/src/debounce.rs (DebounceMode)
  - repos/opensovd-fault-lib/tests/integration/src/helpers.rs (CabinTempSensorStuck, HoldTime debounce)
  - https://covesa.github.io/vehicle_signal_specification/ (VSS min/max/unit metadata)
last-verified: 2026-10-03
related:
  - "[[deciding-on-a-bad-state-is-wrong-not-degraded]]"
  - "[[vss-kuksa-overview]]"
  - "[[opensovd-overview]]"
  - "[[one-watchdog-per-layer-each-blind-to-the-others]]"
applies-to: [vss-kuksa, opensovd, uprotocol, iceoryx2]
gap-rows: [A8, A2, A1, A10]
---

# Check plausibility at the consumer that decides

**Problem.** The provider promises valid data, the broker validates `min`/`max`, so the Guardian trusts every value. A frozen sensor sends 31.2 °C forever with fresh timestamps, inside range, and passes every check that exists. Range checks find broken wires; they do not find a lying sensor.

**Forces.**
- Producers know the sensor physics (noise floor, ADC codes); consumers know what the decision needs.
- Checking twice costs CPU; checking only at the producer means trusting a black channel.
- Constant values are sometimes real (stable temperature, coarse resolution), so "unchanged" alone is not "stuck".
- Glitches must not raise faults; real faults must not be debounced past the FTTI.

**The rule.** The consumer that takes the safety decision runs its own checks on every input, each producing a named fault reason, debounced into a confirmed fault:
- **Freshness:** age = now − source timestamp, checked on a timer; plus a producer sequence counter (timestamp freshness alone is defeated by a provider that re-stamps a frozen value).
- **Range:** physical min/max from the model (VSS `min`/`max`, unit).
- **Rate of change:** |Δvalue/Δt| bounded by physics (a cell cannot heat 50 K in 100 ms; nor can it hold to 0.000 K for 10 minutes while current flows).
- **Stuck-at:** zero variance over a window *while* a correlated quantity (pack current, neighbour cells) changes.
- **Cross-sensor consistency:** Max ≥ Average ≥ Min; one cell vs the median of its neighbours.
Producers may run the same checks earlier (and should report circuit/ADC faults only they can see), but the consumer's checks are the safety mechanism. Each failing check → fault reason → debounce (count- or time-based, bounded by FTTI) → confirmed fault → policy transition.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 26262-5 Annex D | sensor valid range, sensor correlation, rationality check, input comparison/voting as diagnostic measures with typical coverage | the names an assessor expects |
| CARB OBD II comprehensive component monitoring | circuit, out-of-range and *rationality* monitors per input | 30 years of "in range but implausible" practice |
| AUTOSAR DEM | counter-based and time-based debouncing, pre-failed/failed states | glitch filtering with a defined confirmation time |
| OpenSOVD fault-lib | `DebounceMode::{CountWithinWindow, HoldTime, EdgeWithCooldown}`, reporter- vs manager-side debounce, `ComplianceTag::SafetyCritical`; its tests already model `CabinTempSensorStuck` | the ready Eclipse home for the confirmed fault |
| VSS | `min`, `max`, `unit` per leaf | range metadata the checker can load instead of hard-coding |

**On the Eclipse SDV stack.** Read `Vehicle.Powertrain.TractionBattery.Temperature.{Max,Average,Min,CellTemperature}` over kuksa.val.v2 with each `Datapoint.timestamp` ([[vss-kuksa-overview]], gap A8). Report confirmed faults through fault-lib to the DFM over iceoryx2 (exists), then out through SOVD `/faults` (gaps A2, A1, [[opensovd-overview]]); mirror each reason as a uProtocol fault event (A10). Use the reason names from [[reference-architecture-doctor-whodunit]] (stale, counter gap, counter repeat, …) plus `range`, `rate`, `stuck`, `cross`.

**The trap.** Detecting "stuck" by timestamp age only, when the frozen provider keeps re-sending the same value with a fresh timestamp.

**For a hackathon team.** Five checks, one function each, one CSV per check that trips it, a table of reason → detection latency. Pitch: "every way a temperature can lie has a named check, a test vector and a measured latency".

**Evidence.** fault-lib types from repos/opensovd-fault-lib/src/common/src/{debounce.rs,fault.rs} and README test list. Annex D measure names from public summaries (SAE 2017-01-0015 abstract, presencis.com summary); table numbers unverified. CARB 1968.2 monitor classes from prior knowledge (unverified against the regulation text). The "re-stamped frozen value" case sharpens the reference architecture's "timestamps, not value change" rule: both are needed.
