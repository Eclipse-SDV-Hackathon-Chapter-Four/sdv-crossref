---
title: Desired state is a ledger, reported state is evidence, and the gap is the work
type: pattern
cluster: fleet-cloud
component: none
tags: [desired-state, reported-state, symphony, ditto, ankaios, convergence, intermittent]
status: draft
sources:
  - https://eclipse.dev/ditto/2020-11-11-desired-properties.html
  - https://github.com/eclipse-symphony/symphony
  - https://github.com/eclipse-uprotocol/symphony-target-example-rust
  - repos/hc3-COOTA/campaign/fleet-1-target.json
  - components/ankaios/ankaios-overview.md
last-verified: 2026-10-03
related:
  - "[[desired-state-converges-locally-when-the-link-drops]]"
  - "[[a-twin-is-last-known-state-not-a-bus]]"
  - "[[symphony-overview]]"
  - "[[ankaios-overview]]"
applies-to: [symphony, ankaios, chariott, uprotocol]
gap-rows: [C6, C8]
---

# Desired state is a ledger, reported state is evidence, and the gap is the work

**Problem.** The cloud says "run v2", the vehicle was in a tunnel, and nobody knows afterwards whether v2 runs, failed, or was never asked. A fire-and-forget command has no memory.

**Forces.**
- The vehicle is offline most of the day and must act on its own when it returns.
- Operators need intent recorded before delivery.
- The vehicle must report what it actually runs, not what it was told.
- Two writers (operator, vehicle) on one record cause lost updates.

**The rule.** Two records per vehicle with two single writers: the backend writes `desired`, the vehicle writes `reported`, and a loop on the vehicle side diffs them. Ditto stores both on a Feature (`desiredProperties` next to `properties`); Symphony stores Solution + Instance + Target as desired state and its target providers reconcile; Ankaios holds the in-vehicle desired state in `ank-server` and workload states as reported. The reconciliation loop runs locally, tolerates the link being down, and reports with a generation number so the backend can tell "applied" from "stale". The cross-cluster note [[desired-state-converges-locally-when-the-link-drops]] covers the in-vehicle half.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Eclipse Ditto | desiredProperties beside properties, searchable and eventful | intent that survives offline vehicles |
| Eclipse Symphony | Solution, Instance, Target; providers; campaigns/activations | cloud desired state, MQTT/uProtocol target |
| Eclipse Ankaios | server holds desired state, agents report workloadStates | on-vehicle convergence |
| Kubernetes controllers | spec versus status, level-triggered reconcile | the shape all of these copy |
| Sparkplug NCMD | command on Node Control topic, state from NBIRTH | request and report on MQTT |

**On the Eclipse SDV stack.**
- Chapter 3 chain: Symphony API, MQTT topics `coa-request`/`coa-response`, a "Symphony Target Provider" workload run by Ankaios, which applies the manifest ([[chapter3-retrospective]]). The reconcile loop is the provider; there is no upstream Ankaios provider (gap C6).
- COOTA's Targets use `providers.target.mqtt` with one broker and fixed request/response topics and `forceRedeploy: true`, i.e. level-triggered with no per-vehicle topic; per-VIN topics (`fleet/<vin>/coa-request`) are the fix ([[one-key-scheme-from-mcu-to-cloud]]).
- Ankaios workload states into the twin is the reported leg ([[ankaios-overview]]: control interface, `workloadStates` events); Symphony target status is the cloud's view of it.
- Placement is the missing third record (C8): who produces which signals, kept next to desired.

**The trap.** Reporting "applied" when the command was acknowledged rather than when the workload state reads running (Ankaios `Running`, not `Pending`).

**For a hackathon team.** Pull the network cable, change `desired` to v2, reconnect, and show reported flipping to v2 with a timestamp and generation. Pitch: "intent is recorded; evidence is reported".

**Evidence.** Ditto desired properties: eclipse.dev/ditto blog (search result, definition quoted). Symphony objects: [[symphony-overview]]. COOTA target file and shared topics: repos/hc3-COOTA/campaign/fleet-1-target.json. Ankaios states: components/ankaios. Symphony's own reconcile semantics not verified (unverified).
