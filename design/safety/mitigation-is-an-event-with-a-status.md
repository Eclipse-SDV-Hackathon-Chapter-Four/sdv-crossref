---
title: A mitigation is an event with a status, not a side effect
type: pattern
cluster: safety
component: none
tags: [degraded-mode, mitigation, limp-home, minimal-risk-condition, sovd, operations, uprotocol]
status: draft
sources:
  - https://www.iso.org/standard/68385.html (ISO 26262-3:2018, functional safety concept: warning and degradation, emergency operation) (catalogue id unverified)
  - https://www.sae.org/standards/content/j3016_202104/ (SAE J3016: minimal risk condition, fallback)
  - https://unece.org/transport/documents/2021/03/standards/un-regulation-no-157-automated-lane-keeping-systems-alks (UN R157: minimal risk manoeuvre)
  - https://www.autosar.org/fileadmin/standards/R22-11/AP/AUTOSAR_SWS_StateManagement.pdf (function group states)
  - https://www.asam.net/standards/detail/sovd/ (ASAM SOVD / ISO 17978: operations, executions, modes)
  - "[[opensovd-reference]] (operations not implemented in core; CDA maps 0x31)"
last-verified: 2026-10-03
related:
  - "[[evidence-is-a-linked-record-not-a-log]]"
  - "[[deciding-on-a-bad-state-is-wrong-not-degraded]]"
  - "[[opensovd-overview]]"
  - "[[uprotocol-howto]]"
applies-to: [opensovd, uprotocol, ankaios, vss-kuksa]
gap-rows: [A10, A1, A5]
---

# A mitigation is an event with a status, not a side effect

**Problem.** The Guardian detects a runaway trend and "limits charging" by writing a KUKSA target value. Did the charger accept it? Did it take effect in time? Was it later released? The evidence shows a detection and then nothing, so the verdict cannot say whether the hazard was actually mitigated.

**Forces.**
- Detection is cheap to show; effect is what the safety goal needs.
- Actuators are other people's software; a request is not an outcome.
- Several faults may request overlapping mitigations; releases must not cancel each other.
- Diagnostics wants to start, observe and stop mitigations from outside (workshop, test bench).

**The rule.** Model each mitigation as a first-class, addressable object with a lifecycle: `requested → active → (completed | failed | timed_out) → released`, a deadline, the triggering fault id, the degraded mode it puts the function into, and the observed effect (e.g. charge current actually below limit). Emit every transition as an event; the verdict checks the *effect*, not the request. Use a small closed vocabulary of modes, ordered by severity: `normal → notify → limit` (limit-charge, limit-power) `→ limp-home → safe-stop`; a mode only escalates automatically, de-escalation needs the fault healed plus a hold time.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 26262-3 | warning and degradation concept; emergency operation until safe state | modes are part of the functional safety concept, not UI |
| SAE J3016 / UN R157 | minimal risk condition, minimal risk manoeuvre as defined fallback behaviours | a named terminal mode with entry criteria |
| AUTOSAR Adaptive State Management | function groups with declared states and requested transitions | modes as explicit, requestable state |
| ASAM SOVD / ISO 17978 | `operations/{op}/executions` with 202 + status polling, start/stop; `modes` resources | the diagnostic interface for a running mitigation |
| AUTOSAR DEM | operation cycles, healing, aging | rules for when a degraded mode may be left |

**On the Eclipse SDV stack.** The challenge names three event classes: heartbeat, fault, **mitigation** ([[chapter4-challenge-doctor-whodunit]]); no schema exists (gap A10). Proposal: uProtocol topic `/8003` mitigation with `{mitigation_id, fault_id, mode, action, status, deadline_ms, observed}` and the same `traceparent` as the fault ([[uprotocol-howto]]). Expose it as SOVD `operations/limit-charge/executions/{id}` so the status is queryable; OpenSOVD core has no `operations` yet (only the CDA maps UDS 0x31), so this is an unlisted gap next to A1 ([[opensovd-reference]]). Effect check: read `Vehicle.Powertrain.TractionBattery.Charging.*` back from KUKSA ([[vss-kuksa-overview]]).

**The trap.** Logging "mitigation sent" and calling the test passed.

**For a hackathon team.** One mitigation (limit-charge) with four statuses, a fake charger that sometimes refuses, and a verdict that fails when the effect is missing. Pitch: "we prove the hazard was mitigated, not that we asked nicely".

**Evidence.** SOVD operations/modes semantics and OpenSOVD core status from [[opensovd-reference]] (rows 56, 71, 120, 122). The mode ladder is this card's proposal. Standards from public abstracts (clause-level wording unverified). Evidence for a new gap: SOVD `operations` in opensovd-core is missing and not a gap-register row.
