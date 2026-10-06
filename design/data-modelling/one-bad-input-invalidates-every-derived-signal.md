---
title: One bad input invalidates every derived signal
type: pattern
cluster: data-modelling
component: none
tags: [quality, validity, derived-signal, dag, propagation, not-available, kuksa, vss]
status: draft
sources:
  - repos/kuksa-proto/kuksa/val/v2/types.proto (Datapoint: timestamp plus optional value)
  - https://www.omg.org/spec/DDS/1.4/ (SampleInfo valid_data, unverified detail)
  - https://reference.opcfoundation.org/Core/Part8/v105/docs/ (OPC UA Part 8: StatusCode for derived/aggregated values, unverified)
  - https://www.autosar.org/ (NOT_AVAILABLE / INVALID signal states, unverified)
last-verified: 2026-10-03
related:
  - "[[a-reading-carries-what-it-is-worth]]"
  - "[[detect-silence-with-a-clock-not-with-data]]"
  - "[[check-plausibility-at-the-consumer-that-decides]]"
  - "[[vss-kuksa-reference]]"
applies-to: [vss-kuksa, iceoryx2]
gap-rows: [A13, A8, B11]
---

# One bad input invalidates every derived signal

**Problem.** A team derives "battery heating rate" from a temperature sensor and "thermal runaway suspected" from the rate. The sensor freezes; the derivative of a constant is zero; the state machine reports "all calm" with a fresh timestamp. Nobody set a flag, so the derived signals look perfect.

**Forces.**
- Derived signals multiply quickly (filters, rates, aggregates, state machines), each written by a different person.
- Setting a validity flag by hand in every node is forgotten in exactly one node.
- Some derivations can tolerate a missing input (a mean over four cells), most cannot.
- The derived value must still be published when invalid, or consumers cannot tell "invalid" from "silent".

**The rule.** Quality is a *propagated* property of the derived-signal graph, not a per-signal flag set by hand. Each derived signal declares its inputs; the runtime computes its quality as the worst quality of its required inputs and its age as the age of its oldest input, before the derivation function runs. A node may declare an input optional with an explicit degraded rule (n of m), and that is the only way to improve on the worst input. Invalid outputs are published as absent values with the reason, never as a computed number. The source states are the small set from [[a-reading-carries-what-it-is-worth]]: ok, invalid, not available, stale.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| AUTOSAR signal states | NOT_AVAILABLE and INVALID as reserved values that a gateway passes on | invalidity survives a hop (unverified detail) |
| OPC UA Part 8 aggregates | a derived value carries a StatusCode computed from the inputs' qualities | quality as a function of inputs (unverified) |
| DDS `SampleInfo.valid_data` | per-sample validity alongside the data | validity travels with the sample (unverified detail) |
| KUKSA v2 `Datapoint` | timestamp plus optional value; absent value is the only "not valid" | the carrier for invalid outputs ([[vss-kuksa-reference]]) |
| Spreadsheet / reactive dataflow | a cell referencing an error cell is an error | the propagation rule everyone already knows |

**On the Eclipse SDV stack.** A derived-signal node subscribes over kuksa.val.v2, holds `{value, timestamp, quality}` per input and publishes derived VSS paths (an overlay branch) as a provider; invalid outputs go out with an absent `Datapoint.value` ([[vss-kuksa-reference]]). In iceoryx2 the user header carries the propagated quality so a zero-copy consumer sees it without a lookup ([[iceoryx2-overview]]). The A8 freshness watchdog becomes the leaf rule of the graph (stale input → stale output), and [[detect-silence-with-a-clock-not-with-data]] supplies the stale verdict. Gap A13 is this runtime; B11's DBC drafter can emit the input lists.

**The trap.** A derivative or a filter of a stale input looks like a valid zero or a valid constant, and it carries the derivation's fresh timestamp.

**For a hackathon team.** Twenty lines: a dict of `derived: [inputs]`, a worst-of quality function, and one demo where freezing a temperature sensor turns the runaway detector grey instead of green. Pitch: "our detector cannot say calm about data it does not have".

**Evidence.** KUKSA `Datapoint` shape read in `types.proto` (via [[a-reading-carries-what-it-is-worth]]). AUTOSAR, OPC UA and DDS rows are standard behaviour not checked against the spec text (unverified). The propagation runtime is P (unverified): nothing in the vault implements it.
