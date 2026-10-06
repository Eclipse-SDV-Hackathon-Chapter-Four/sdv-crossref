---
title: Let the standard timestamp your evidence (subscriptions and triggers)
type: pattern
cluster: diagnostics
component: none
tags: [sovd, sse, cyclic-subscriptions, triggers, timeline, evidence, polling]
status: draft
sources:
  - https://www.asam.net/standards/detail/sovd/ (cyclic-subscriptions, triggers resources)
  - https://www.iso.org/standard/86587.html (ISO 17978-3; resource catalogue as in [[opensovd-reference]])
  - https://html.spec.whatwg.org/multipage/server-sent-events.html (SSE)
  - https://github.com/eclipse-opensovd/opensovd-core/issues/156 (faults; subscriptions have no issue cited in the vault)
  - https://www.rfc-editor.org/rfc/rfc9110
last-verified: 2026-10-03
related:
  - "[[opensovd-reference]]"
  - "[[a-fault-is-a-state-machine-with-evidence-attached]]"
  - "[[logs-are-bulk-data-and-evidence-has-an-address]]"
applies-to: [opensovd, uprotocol, vss-kuksa]
gap-rows: [A5, H1, H2]
---

# Let the standard timestamp your evidence

**Problem.** A fault timeline (hazard, fault, detection, verdict) is built from client polling, so its resolution is the poll period and its clock is the tester's laptop. Disputes about "what came first" are unresolvable.

**Forces.**
- Evidence needs timestamps from the source, not from the observer.
- Polling is simple, works today, and loses transitions between samples.
- Subscriptions and triggers are in the standard but not in OpenSOVD core.
- Event hooks must be able to do more than notify: log, or issue a command.

**The rule.** Get the timeline from the server: a *cyclic subscription* streams `{timestamp, payload, error}` over SSE at a rate, and a *trigger* fires on a condition (EnterRange, LeaveRange, OnChange, OnChangeTo) and can emit an SSE event, a log entry, or a further SOVD command (for example, writing a fault or starting an operation). A timeline is the ordered merge of: trigger events (edges), subscription samples (context), fault `first_occurrence`/`last_occurrence`, and client-side receipt times kept as a separate column so clock skew is visible.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 17978 `cyclic-subscriptions` | POST creates (201 + Location); GET the subscription with `Accept: text/event-stream` | server-timestamped stream per resource |
| ISO 17978 `triggers` | condition on a data resource fires event, log or command | detection as a resource, not as client code |
| UDS 0x2A ReadDataByPeriodicIdentifier, 0x86 ResponseOnEvent | ECU-side periodic and event-driven reporting | the legacy ancestors of both |
| AUTOSAR Dem | freeze frame at the failing edge, FDC counter | capture-at-edge discipline |
| W3C Server-Sent Events | `id:` and `Last-Event-ID` reconnect | gap-free resume |
| OpenSOVD fault-lib | `first_occurrence`, `last_occurrence`, `IpcTimestamp` on `FaultRecord` | source-side timestamps on faults today |

**On the Eclipse SDV stack.**
- Core has neither resource (gap H1, H2); the CDA has neither ([[opensovd-reference]] coverage table). Do not wait: implement the *poll* path with the right bookkeeping.
- Poll recipe: read `/faults` (or the Guardian `x-guardian-` data) every 250-500 ms, store `(client_recv_ts, server_ts_if_any, mask, counters)` per fault, emit a timeline row only on a change of mask or counter. Join with uProtocol events and openDuT campaign markers by time ([[chapter4-challenge-doctor-whodunit]]).
- Server-side upgrade (H1): a `SubscriptionProvider` over the existing `DataProvider::read` with an axum SSE handler. Trigger (H2) can be built on the same loop evaluating a condition and writing to a `FaultProvider`.

**The trap.** Treating the poll response time as the event time: the timeline then shows detection before the cause whenever the tester's clock is ahead.

**For a hackathon team.** Poll with change-detection and two timestamp columns, render hazard to verdict as a table; if time remains, add a 60-line SSE cyclic subscription. Pitch line: "we use the standard's own evidence hook and show the server's clock".

**Evidence.** Subscription and trigger semantics are from the catalogue in [[opensovd-reference]] (standard text paywalled; unverified at clause level). `first_occurrence`/`last_occurrence` are in `SovdFault` per [[opensovd-reference]]. 0x2A/0x86 are standard UDS services (unverified in this session).
