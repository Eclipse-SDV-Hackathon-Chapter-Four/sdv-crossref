---
title: A reading carries what it is worth
type: pattern
cluster: data-modelling
component: none
tags: [quality, validity, age, e2e, j1939, dds, kuksa, timestamp]
status: draft
sources:
  - repos/kuksa-proto/kuksa/val/v2/types.proto (Datapoint)
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/data_entry/enum.md (no "unknown" value)
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/data_entry/data_types_struct.md ("not available" guidance)
  - https://www.omg.org/spec/DDS/1.4/ (SampleInfo: source_timestamp, instance_state, valid_data)
  - https://www.autosar.org/ (E2E protocol: status/result, counter, CRC; unverified details)
  - https://www.sae.org/standards/content/j1939da_202309/ (not available / error indicator, unverified)
last-verified: 2026-10-03
related:
  - "[[the-conversion-rule-is-part-of-the-type]]"
  - "[[coherence-is-a-set-property-declared-in-the-model]]"
  - "[[vss-kuksa-reference]]"
applies-to: [vss-kuksa, iceoryx2, opensovd]
gap-rows: [A8, B10]
---

# A reading carries what it is worth

**Problem.** A frozen sensor keeps a stale `onchange` value forever, and a consumer cannot tell "21.5 degrees" from "21.5 degrees, last updated 40 minutes ago, E2E counter stuck".

**Forces.**
- The model avoids validity values (VSS says: if unknown, do not publish) but consumers still need to know the age.
- Every wire format has its own invalid code (J1939 not-available and error codes, DBC value tables, E2E status).
- Adding fields to every sample costs bytes; omitting them costs safety arguments.

**The rule.** A datum is value plus *what it is worth*: timestamp (age), validity (ok, invalid, absent) and, where relevant, source. Carry them in the datum's envelope, not as extra signals, and translate each wire format's invalid code at the boundary into the same small set. VSS in KUKSA gives only `Datapoint{timestamp, value}` (types.proto, verified); "no value" is the absence of the value, the deliberate VSS answer. So age is available, validity is not.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| KUKSA v2 `Datapoint` | timestamp plus optional value | age and absence only |
| DDS `SampleInfo` | source_timestamp, `valid_data`, instance_state (ALIVE, DISPOSED, NO_WRITERS) | validity and liveness per sample |
| AUTOSAR E2E | per-message CRC, alive counter, status (OK, repeated, wrong sequence, no new data) | verdict from the protection layer, passed up to the application (unverified) |
| J1939 SPN | reserved top range: not available, error indicator, reserved | validity inside the value range |
| VSS struct guidance | "not available" must be included in the value range or an extra item | validity as part of the type |
| OPC UA `StatusCode` per DataValue | quality, plus source and server timestamps | the model-wide quality bits |

**On the Eclipse SDV stack.** [[vss-kuksa-reference]]: freshness watchdog is timestamp-based because `onchange` sensors go silent (gap A8). In iceoryx2 ([[iceoryx2-overview]]) the user header is the natural envelope for `{timestamp, validity, e2e_status}`; [[opensovd-overview]] maps validity to a fault. Plain-signal consumers get validity through the provider: drop the sample, or set `Datapoint.value` absent, when invalid.

**The trap.** Encoding invalidity as an in-band magic number (-1, 255) that propagates as a real reading after conversion.

**For a hackathon team.** A provider translating J1939 "not available" to an absent value and a watchdog that raises a fault from the age. Pitch: "age and validity travel with the number".

**Evidence.** KUKSA Datapoint (read). VSS "unknown" stance (read). Rows for DDS, E2E, J1939 are unverified standard behaviour. The validity gap in KUKSA is stated from types.proto only; kuksa v1 `Metadata`/quality-like fields not checked.
