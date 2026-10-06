---
title: Deciding on a bad state is wrong, not degraded
type: pattern
cluster: safety
component: none
tags: [signal-policy, hold-last, substitute, safe-state, ftti, e2e, doctor-whodunit]
status: draft
sources:
  - https://www.iso.org/standard/68383.html (ISO 26262-1:2018: fault tolerant time interval, safe state, emergency operation)
  - https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_COM.pdf (reception deadline monitoring, ComRxDataTimeoutAction NONE/REPLACE/SUBSTITUTE)
  - https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_E2EProtocol.pdf (E2E check status per sample)
  - repos/s-core-score/docs/requirements/stakeholder/index.rst (stkh_req__dependability__safe_state)
  - https://globalautoregs.com/rules/225 (UN GTR No. 20 warning budget)
last-verified: 2026-10-03
related:
  - "[[reference-architecture-doctor-whodunit]]"
  - "[[check-plausibility-at-the-consumer-that-decides]]"
  - "[[mitigation-is-an-event-with-a-status]]"
  - "[[vss-kuksa-overview]]"
applies-to: [vss-kuksa, uprotocol, opensovd, s-core]
gap-rows: [A8, A10]
---

# Deciding on a bad state is wrong, not degraded

**Problem.** A cell-temperature sensor freezes. The Guardian keeps using the last value "to stay available", reports green, and the thermal warning chain is silently disarmed: the exact hazard the challenge describes. Hold-last felt like graceful degradation; it was a wrong decision with a confident face.

**Forces.**
- Availability pushes towards using *something*; integrity pushes towards using nothing.
- Short gaps (one lost frame) are normal; long gaps are faults.
- The time a safety goal tolerates a fault (FTTI) is fixed by physics; for thermal runaway the regulatory warning budget is minutes, the detection budget seconds.
- Different signals play different roles: a decider input, a display value, a logged value.

**The rule.** Give every input signal an explicit, written policy chosen by its **role**, never one global default:
1. **Reject** — the value is unusable; the decision that needs it is not taken, and the function goes to its safe reaction (warn, limit). Default for any input to a safety decision.
2. **Hold last, bounded** — reuse the previous value for at most *H*, where *H* + detection time + reaction time < FTTI; carry the age with it; after *H* it becomes *reject*. Only for inputs whose staleness cannot hide the hazard.
3. **Degrade / substitute** — use a declared substitute (redundant sensor, model estimate, conservative constant such as "assume hottest plausible") *and flag the output as degraded*. A substitute must be conservative in the hazard's direction.
Each policy transition is a fault event. Document per signal: role, policy, *H*, substitute, FTTI, rationale.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 26262 | FTTI, safe state, emergency operation, warning and degradation concept | the timing argument that bounds *H* |
| AUTOSAR COM deadline monitoring | per-signal timeout action: keep (NONE), REPLACE with init value, SUBSTITUTE with configured value | per-signal policy is configuration, not code |
| AUTOSAR E2E | per-sample status (OK, REPEATED, WRONGSEQUENCE, NODATA, ERROR) plus a windowed state machine (VALID/INVALID/NODATA) | "bad" is classified before it is used |
| S-CORE stakeholder reqs | platform safe state = "error reported" to the external health monitor | the platform reports; the *application* owns the functional safe reaction |
| UN GTR 20 | occupant warning ahead of a thermal event | why "reject → warn" is the conservative direction for the Guardian |

**On the Eclipse SDV stack.** KUKSA delivers `Datapoint{timestamp, value}` over kuksa.val.v2; `onchange` sensors go silent when frozen ([[vss-kuksa-overview]], gap A8). Put the policy table next to the VSS overlay as metadata (e.g. a `x-policy: reject` comment or a sidecar YAML keyed by VSS path), and emit the transition as a uProtocol fault event with `{signal, policy, age_ms, reason}` (schema gap A10). SOVD makes it auditable: the fault appears under `/components/guardian/faults` ([[opensovd-overview]]).

**The trap.** A global "use last known value on timeout" in the subscriber helper, applied to the one input that guards against a frozen sensor.

**For a hackathon team.** A three-row policy table (max cell temp: reject; average temp: hold 2 s; ambient temp: substitute 45 °C, degraded) and a campaign that freezes each; the evidence shows three different, documented reactions. Pitch: "we did not degrade, we refused to decide on a lie, and warned".

**Evidence.** AUTOSAR COM/E2E names from the cited R22-11 specs (PDFs not re-fetched; values from prior knowledge, unverified against R22-11 text). S-CORE safe-state wording quoted from repos/s-core-score/docs/requirements/stakeholder/index.rst. This card extends the two-word rule in [[reference-architecture-doctor-whodunit]] with a third policy (substitute, flagged) and the FTTI bound on *H*.
