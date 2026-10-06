---
title: A campaign commits all or rolls back all, and reports to the twin
type: pattern
cluster: fleet-cloud
component: none
tags: [campaign, ota, atomic, canary, rollback, symphony, evidence, twin]
status: draft
sources:
  - repos/hc3-COOTA/README.md
  - repos/hc3-COOTA/campaign/campaign.json
  - repos/hc3-challenge-mission-update-possible/README.md
  - https://github.com/eclipse-symphony/symphony
  - https://datatracker.ietf.org/doc/html/rfc9019
last-verified: 2026-10-03
related:
  - "[[desired-is-a-ledger-reported-is-evidence]]"
  - "[[a-twin-is-last-known-state-not-a-bus]]"
  - "[[chapter3-retrospective]]"
applies-to: [symphony, ankaios, uprotocol, opensovd]
gap-rows: [H3, H4, H5, H6, C6]
---

# A campaign commits all or rolls back all, and reports to the twin

**Problem.** A campaign touches many ECUs in a vehicle and many vehicles in a fleet. Half-applied is worse than not applied: the vehicle runs a combination nobody tested, and the backend cannot tell.

**Forces.**
- ECUs have different bank, rollback and verify capabilities.
- Vehicles are reachable at different times; "all vehicles at once" never happens.
- The operator needs a stop rule (error budget) and an audit trail.
- A trial must stay revertible until the whole set is verified.

**The rule.** Two levels, each with its own atomicity. Inside a vehicle: stage every ECU in trial, verify all, then commit all or roll back all (an ECU that cannot revert, such as HSM keys, never joins a revertible set, H6). Across the fleet: a campaign is staged (canary, then expand), each stage gated by telemetry and an error budget, and each vehicle reports `trial`, `committed`, `rolled-back` and the cause back to its twin. Commit is the only irreversible step and is the only point where the security version rises (H4).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| IETF SUIT (RFC 9019 family) | signed manifest naming components, conditions, dependencies | one manifest, many ECUs, signed |
| Eclipse Symphony campaigns | stages, activations, stage selectors, `selfDriving` | fleet-level staging engine |
| A/B bank updates (Uptane, Android A/B) | trial boot, health check, commit or fall back | per-ECU revertibility |
| COOTA (Chapter 3) | canary 0.5 percent, watch telemetry, auto rollback | the closed loop, in demo form |
| Ditto/Hono state | per-vehicle report records | the audit trail |

**On the Eclipse SDV stack.**
- Chapter 3 build: Symphony campaign JSON with stages `test-stage-entry` and `wait-stage`, `providers.stage.http` posting a Target, an Ankaios workload per vehicle ([[chapter3-retrospective]]). The README promises canary and automatic rollback; the demo shows deploy and rollback first, monitoring second (ranking notes in the retrospective).
- Missing: signed per-ECU manifests (H5), the trial/commit split (H3), `security_version` (H4), and a report leg into a twin. Chapter 3 teams (P-OTA-VEZ) listed "atomic install, rollback, audit trail" as unfinished issues.
- Where the report lands: Ditto `reported` feature, or an Influx event with `vin`, `campaign`, `stage`, `state` tags, next to telemetry ([[fleet-telemetry-batched-at-the-vehicle-keyed-by-vin]]).
- Trigger evidence: a campaign stage should capture the fault snapshot that made it stop; same evidence record as the fault leg.

**The trap.** Reporting success when the Symphony stage returns, not when the vehicle verified its new combination.

**For a hackathon team.** Three simulated vehicles, one campaign; make vehicle 2 fail its health check and show vehicles 1 and 3 reverting too, with a single reason in the dashboard. Pitch: "all or nothing, and the twin knows why".

**Evidence.** COOTA flow and campaign JSON: repos/hc3-COOTA. Challenge scope: repos/hc3-challenge-mission-update-possible/README.md. H3-H6 rows: [[gap-register]]. Symphony stage semantics beyond the shown JSON unverified. SUIT scope from RFC 9019 abstract (not re-fetched).
