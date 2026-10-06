---
title: Kill, restart and delete are first-class test actions; workload states are the evidence
type: pattern
cluster: orchestration-criticality
component: none
tags: [fault-injection, chaos, ankaios, workload-state, evidence, restart-latency, sovd]
status: draft
sources:
  - repos/ankaios/doc/docs/reference/events.md (subscribe to workloadStates.*.*.*.state)
  - repos/ankaios/doc/docs/reference/restart-policy.md
  - repos/ankaios/doc/docs/reference/inter-workload-dependencies.md (Failed, Pending, Stopping states)
  - repos/ankaios/doc/docs/usage/tutorial-events.md
  - https://principlesofchaos.org/
  - https://litmuschaos.io/docs/
last-verified: 2026-10-03
related:
  - "[[ankaios-overview]]"
  - "[[one-supervisor-per-node-readiness-is-the-apps-claim]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
applies-to: [ankaios, opensovd, autosd, opendut]
gap-rows: [A9, C7, C4]
---

# Kill, restart and delete are first-class test actions; workload states are the evidence

**Problem.** A fault campaign kills processes with ad-hoc `podman kill`, and afterwards nobody can prove what the supervisor saw, when, or how long recovery took.

**Forces.**
- The orchestrator is already the authority on workload state; a second observer disagrees.
- Different actions test different things: `kill` tests restart policy, `delete` tests dependency teardown (explicit delete is never restarted), `stop agent` tests the lost state.
- Evidence must be timestamped and attributable to the action.
- Injecting faults needs authorisation, or any workload can kill any other.

**The rule.** Model injection as an action of the orchestrator's own API, not a side channel, and record the orchestrator's state stream as the oracle. Each campaign step is `{action, target, t0}`; the evidence is the sequence of state transitions (`Running`, `Failed(ExecFailed)`, `Pending(WaitingToStart)`, `Running`, ...) with timestamps, and **restart latency** is `t(Running again) - t(Failed)`; a better metric is `t(app ready) - t(Failed)`, using the app's own readiness claim ([[one-supervisor-per-node-readiness-is-the-apps-claim]]). Run the same campaign with different restart policies (`NEVER`, `ON_FAILURE`, `ALWAYS`) to compare.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Principles of Chaos | hypothesis about steady state, inject, observe | the experiment shape |
| LitmusChaos / Chaos Mesh (Kubernetes) | faults as declarative experiments, results as resources | injection as an API object |
| Ankaios control interface and events | a workload subscribes to `workloadStates.*.*.*.state` and receives `alteredFields` | the state stream is the evidence source |
| Ankaios restart policy | `ON_FAILURE`, `ALWAYS` restart on exit, explicit delete does not | which actions get a restart |
| UDS/SOVD DTCs | a fault is a record with status and time | workload state mapped to a fault record |

**On the Eclipse SDV stack.** A control-interface workload (Python SDK, authorised by `controlInterfaceAccess` allow rules) is both injector and observer: it subscribes to state events, applies `ank delete`/`apply` equivalents or kills the container, and logs the transitions (gap A9, and C7 for the dashboard with kill/restart buttons). Publish each transition as a SOVD fault via A1/A4 so the diagnostic server shows "Guardian failed at t, restarted at t+x". For Doctor Whodunit, add an agent-stop case (state `Failed(Lost)`) and a delete case (no restart) beside the kill case ([[chapter4-challenge-doctor-whodunit]]). On AutoSD with BlueChi the equivalent injection is `bluechictl stop/restart` and the journal is the evidence (C4).

**The trap.** Measuring "container running again" and calling it recovered: the app may not be ready, and the Guardian's alerts are silent until it is.

**For a hackathon team.** A 60-line SDK script that runs kill, delete, restart-policy variants against the Guardian and prints a table of state transitions with latencies; hand the table to the jury. Pitch: "we inject through the orchestrator and the orchestrator is our witness".

**Evidence.** Event subscription and wildcard mask: events.md. State names: inter-workload-dependencies.md, restart-policy.md, glossary and tests (`Failed(Lost)`, `Succeeded(Ok)` in the Ankaios docs). Restart latency figures are not published upstream (none found); measure yourself. A gap nobody listed: a per-campaign evidence format combining workload states and readiness claims.
