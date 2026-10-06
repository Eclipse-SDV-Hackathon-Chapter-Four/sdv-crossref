---
title: One watchdog per layer, each blind to the others
type: pattern
cluster: safety
component: none
tags: [watchdog, aliveness, heartbeat, systemd, ankaios, supervision, health-management]
status: draft
sources:
  - https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html (WatchdogSec=, Restart=on-watchdog)
  - https://www.freedesktop.org/software/systemd/man/latest/sd_notify.html (WATCHDOG=1, WATCHDOG=trigger)
  - https://www.freedesktop.org/software/systemd/man/latest/systemd-system.conf.html (RuntimeWatchdogSec, /dev/watchdog0)
  - https://docs.kernel.org/watchdog/watchdog-api.html
  - https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_WatchdogManager.pdf (alive, deadline, logical supervision)
  - https://docs.podman.io/en/latest/markdown/podman-run.1.html (--health-cmd, --health-on-failure)
  - repos/ankaios/doc/docs/reference/restart-policy.md
  - repos/s-core-score/docs/requirements/stakeholder/index.rst (health management, external watchdog)
last-verified: 2026-10-03
related:
  - "[[ankaios-overview]]"
  - "[[autosd-overview]]"
  - "[[uprotocol-howto]]"
  - "[[iceoryx2-overview]]"
  - "[[freedom-from-interference-has-three-axes]]"
applies-to: [ankaios, autosd, s-core, uprotocol, iceoryx2, opensovd]
gap-rows: [A9, A8, A10, C4]
---

# One watchdog per layer, each blind to the others

**Problem.** The demo kills the Guardian, Ankaios restarts it, everyone claps. Then the Guardian deadlocks in a loop instead: the process is alive, Ankaios shows `Running`, no heartbeat goes out, and nothing fires. A watchdog only catches failures of the layer it watches, in the way it watches.

**Forces.**
- Each supervisor is cheap; the gaps between them are where hazards live.
- Restarting hides faults unless the restart is itself recorded.
- Liveness ("the process exists") is not progress ("the loop is turning") and not correctness ("the loop took the right path").
- The last-resort supervisor must not depend on the software it supervises.

**The rule.** Stack watchdogs by layer and write down what each one sees:
| Layer | Mechanism | Catches | Blind to |
|---|---|---|---|
| Hardware | `/dev/watchdog0` fed by systemd `RuntimeWatchdogSec` (or an external MCU/PMIC) | kernel hang, PID 1 hang | any single service |
| Supervisor (exit) | Ankaios `restartPolicy`, systemd `Restart=` | process exit/crash | hangs, livelocks, wrong output |
| Supervisor (progress) | systemd `WatchdogSec` + `sd_notify("WATCHDOG=1")` from the cycle; podman `--health-cmd` | stuck main loop | wrong output, stale inputs |
| Application aliveness | heartbeat event with sequence number, checked **on a timer** by an independent monitor | stuck loop, lost transport | wrong output |
| Logical / deadline | checkpoints in order and in time (alive, deadline, logical supervision) | skipped steps, overruns | input data quality |
| Data | freshness and plausibility per input ([[check-plausibility-at-the-consumer-that-decides]]) | stuck/stale sensor | — |
Feed the progress watchdog from the *end* of a successful cycle, never from a separate thread. Every restart is a fault event, not a recovery that erases history.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| systemd | `WatchdogSec` kills+restarts a service that stops pinging; `WATCHDOG=trigger` self-reports; `RuntimeWatchdogSec` feeds the HW watchdog | progress supervision on any Linux box, AutoSD included |
| Linux watchdog API | `/dev/watchdog`: stop writing and the board resets | the last-resort layer |
| AUTOSAR WdgM / Adaptive PHM | alive, deadline and logical supervision of checkpoints | vocabulary for the application layer |
| S-CORE stakeholder reqs | health management (alive/deadline/logical); report unrecoverable errors to an external health monitor, e.g. "stopping the triggering" of an external watchdog | the platform contract |
| iceoryx2 | node-death detection; event `deadline`; health_monitoring example | aliveness without a heartbeat protocol on one host |

**On the Eclipse SDV stack.** Ankaios restarts only on *exit* (`NEVER|ON_FAILURE|ALWAYS` keyed to `ExecutionState`); grep of repos/ankaios finds no liveness or health probe ([[ankaios-overview]]). So "heartbeat loss is a supervised failure" needs a control-interface supervisor that watches heartbeats and calls delete/apply (gap A9), or a podman health check passed through `runtimeConfig` (unverified with Ankaios). On AutoSD, systemd quadlets accept `WatchdogSec` and BlueChi sees unit state ([[autosd-overview]]). uProtocol publish is at-most-once, so the heartbeat monitor tolerates N misses ([[uprotocol-howto]]).

**The trap.** Demonstrating only `ank delete guardian`: the one failure every layer already catches.

**For a hackathon team.** Inject three faults: kill (Ankaios restarts), `SIGSTOP` (only the heartbeat monitor or `WatchdogSec` catches it), and a frozen input (only the data check catches it). Show which layer fired for each. Pitch: "we know which watchdog catches which death, and we tested the gaps".

**Evidence.** systemd semantics from local man pages systemd.service(5), sd_notify(3), systemd-system.conf(5). Ankaios restart semantics: repos/ankaios/doc/docs/reference/restart-policy.md; absence of probes: grep for liveness/healthcheck/readiness in repos/ankaios returned only an unrelated doc line. S-CORE: stkh_req__dependability__health_management, __safe_state. AUTOSAR WdgM from the spec title (not re-read).
