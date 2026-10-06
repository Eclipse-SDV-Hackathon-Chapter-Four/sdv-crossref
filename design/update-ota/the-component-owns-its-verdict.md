---
title: The component owns its verdict; the orchestrator polls and never infers
type: pattern
cluster: update-ota
component: none
tags: [health, verdict, watchdog, rollback, greenboot, readiness, orchestrator, trial]
status: draft
sources:
  - https://github.com/fedora-iot/greenboot-rs (required.d / wanted.d health checks, red/green)
  - https://source.android.com/docs/core/ota/ab (markBootSuccessful, update_verifier)
  - https://docs.u-boot.org/en/latest/api/bootcount.html (userspace resets bootcount)
  - https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ (liveness vs readiness)
  - https://www.freedesktop.org/software/systemd/man/latest/sd_notify.html (READY=1, WATCHDOG=1)
last-verified: 2026-10-03
related:
  - "[[trial-boot-then-commit-reboot-is-owed]]"
  - "[[one-supervisor-per-node-readiness-is-the-apps-claim]]"
  - "[[a-campaign-commits-all-or-rolls-back-all]]"
applies-to: [ankaios, opensovd, autosd, symphony, s-core]
gap-rows: [H3, A9, C4]
---

# The component owns its verdict; the orchestrator polls and never infers

**Problem.** After an update the orchestrator sees the container running, the ECU answering TesterPresent, the HTTP port open, and commits. The function inside is broken (wrong calibration, a dead sensor path), and the old bank is released.

**Forces.**
- Only the component knows what "working" means for it.
- The orchestrator must decide in bounded time, even if the component hangs.
- A component that crashes before speaking must not count as healthy.
- Verdicts must be readable through the same diagnostic surface as everything else.

**The rule.** After a reset or activation each component exposes a post-reset health state it computes itself: `verifying` → `healthy` or `unhealthy` (with a reason). The orchestrator polls that state and treats it as the only input to commit; process state, reachability and "no error so far" are never promoted to a verdict. Every trial has a deadline: no verdict by then is a negative verdict, and a hardware or bootloader watchdog enforces it even if the orchestrator is dead. A component that cannot evaluate itself declares a fixed observation window instead, and says so.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| greenboot / greenboot-rs | scripts in `required.d` must pass for a green boot; `wanted.d` may fail; red boots reboot then roll back; watchdog-triggered boots checked | the verdict is a set of component-owned checks |
| Android A/B | `update_verifier` checks dm-verity, then `markBootSuccessful()`; unmarked slots fall back after retries | commit only on an explicit positive call |
| U-Boot bootcount | application code must reset `bootcount`; silence means fallback | the watchdog form of "no verdict is a failure" |
| Kubernetes probes | liveness (restart me) is not readiness (serve me) | process alive is not the same claim as function ready |
| systemd `sd_notify` | `READY=1` and `WATCHDOG=1` sent by the service itself | readiness and aliveness are the app's claims |

**On the Eclipse SDV stack.** Ankaios's `ADD_COND_RUNNING` reports runtime state, not health ([[one-supervisor-per-node-readiness-is-the-apps-claim]]); an update agent under Ankaios should read a verdict the workload publishes (a control-interface config entry or a uProtocol message) instead. In SOVD terms the verdict is a `data` resource per entity (say `data/x-update-health`) and the `/updates/{id}/status` of H3 waits in "awaiting verdict" until it is `healthy` or the deadline passes ([[opensovd-reference]]). On AutoSD the node verdict is greenboot's, which can include a check that reads the component verdicts ([[autosd-overview]]). At fleet level the verdict per vehicle feeds the canary error budget, as COOTA did in Chapter 3 with telemetry ([[chapter3-retrospective]], [[a-campaign-commits-all-or-rolls-back-all]]).

**The trap.** Letting the orchestrator infer health from "running" or "reachable", which commits every update that fails functionally.

**For a hackathon team.** A Guardian-style workload that publishes `verifying` for 10 s, then `healthy` only if its input signal is fresh; the update agent polls it, commits on `healthy`, rolls back on `unhealthy` or after 30 s of silence. Show both paths by killing the signal. Pitch: "the car commits only what says it works".

**Evidence.** greenboot-rs README, Android A/B page, U-Boot bootcount page (fetched 2026-10-03). Kubernetes and sd_notify are standard behaviour of the linked docs (sd_notify page not re-fetched; HTTP 418 to the checker). Ankaios condition semantics: [[one-supervisor-per-node-readiness-is-the-apps-claim]]. The `x-update-health` resource name is a proposal, not an OpenSOVD or ISO 17978 name.
