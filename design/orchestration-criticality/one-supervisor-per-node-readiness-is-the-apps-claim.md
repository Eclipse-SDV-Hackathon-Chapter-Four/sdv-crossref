---
title: One supervisor per node; readiness is the app's claim, not the runtime's
type: pattern
cluster: orchestration-criticality
component: none
tags: [lifecycle, ankaios, systemd, quadlet, bluechi, readiness, restart]
status: draft
sources:
  - repos/ankaios/doc/docs/reference/inter-workload-dependencies.md
  - repos/ankaios/doc/docs/reference/restart-policy.md
  - https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html (quadlet generator, Notify=healthy)
  - https://bluechi.readthedocs.io/en/latest/ (BlueChi executes transitions, does not decide desired state)
  - https://www.freedesktop.org/software/systemd/man/latest/sd_notify.html (READY=1)
  - https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
  - repos/hackfest-eclipse-score_reference_integration/showcases/simple_lifecycle/configs/launch_manager_config.json (S-CORE Launch Manager)
last-verified: 2026-10-03
related:
  - "[[ankaios-overview]]"
  - "[[autosd-overview]]"
  - "[[s-core-overview]]"
  - "[[kanto-overview]]"
applies-to: [ankaios, autosd, s-core, kanto]
gap-rows: [C2, C4, C5, A9]
---

# One supervisor per node; readiness is the app's claim, not the runtime's

**Problem.** Two supervisors restart the same process (systemd and Ankaios, or Ankaios and the S-CORE Launch Manager) and fight; or a dependent workload starts because the container is "running" while the app inside is still initialising and the first message is lost.

**Forces.**
- Safety wants one authority that can say "this process is dead, go to the fallback run state".
- Cloud-style orchestrators know containers, not application readiness.
- Boot ordering (systemd) and runtime ordering (Ankaios) look alike but are different graphs.
- A supervisor that restarts blindly hides a crash loop.

**The rule.** Exactly one component owns the start/stop/restart of any given process on a node, and "ready" is something the app asserts through a channel the supervisor listens to. `ADD_COND_RUNNING` in Ankaios means the container's runtime state is running; it says nothing about the app. So either the dependency is a `ADD_COND_SUCCEEDED` init workload that exits 0 only when the real condition holds, or the app publishes its own readiness (sd_notify `READY=1` with quadlet `Notify=healthy`, an Ankaios custom config event, a Launch Manager "Reporting" aliveness cycle) and consumers wait for that. Delete restarts from every layer but one: if Ankaios owns the workload, the quadlet or unit must not be enabled; if systemd owns it, Ankaios must not know the name. Ankaios does not re-apply dependencies on restart (restart-policy.md), so a restarted producer comes back without consumers re-checking it.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| systemd `Type=notify` / `sd_notify READY=1` | the service tells the manager it is ready | readiness as the app's claim |
| Podman quadlet `Notify=healthy` | the generated unit stays "activating" until the container health check passes | closes the gap between container up and app up inside systemd |
| Kubernetes readiness/liveness/startup probes | readiness gates traffic, liveness gates restart, kept as two signals | the vocabulary for splitting "up", "ready", "alive" |
| BlueChi | multi-node systemd controller; executes start/stop/restart, a separate state manager decides | one supervisor (systemd) per node, one cross-node verb layer |
| S-CORE Launch Manager (lifecycle, v0.7+) | JSON components, `depends_on`, `ready_condition`, alive supervision, `ready_recovery_action` restart, run-target `recovery_action` switch | readiness and aliveness are separate, recovery changes the Run State, not just the process |
| Ankaios restart policy (`NEVER`/`ON_FAILURE`/`ALWAYS`) | restart on exit, explicit delete never restarts | simple, no aliveness notion |

**On the Eclipse SDV stack.** Pick the owner per node and write it in the node's manifest header. Ankaios node: `ank-agent` owns app containers; systemd owns only the agent and the OS. AutoSD node: quadlets (`/etc/containers/systemd/*.container`) own containers, BlueChi links root and QM; do not also run Ankaios there unless Ankaios is the only thing that sees the workload ([[autosd-overview]], gap C2 asks exactly who owns lifecycle). S-CORE node: Launch Manager owns processes and Run States; Ankaios, if present, owns the container around the whole S-CORE image, never the processes inside ([[s-core-overview]]). Kanto is one daemon per device with no cluster view ([[kanto-overview]]). For Doctor Whodunit, the Guardian declares readiness by publishing its first heartbeat; a watchdog consumes `workloadStates` (A9) plus the heartbeat, and only the heartbeat counts as ready. Ankaios restart policy `ALWAYS` is the supervisor; the watchdog observes, it does not restart ([[ankaios-overview]]).

**The trap.** Reading `Running(Ok)` as "ready", then adding a second supervisor to "fix" the startup race.

**For a hackathon team.** One manifest with a producer (`restartPolicy: ALWAYS`) and a consumer that depends on a short-lived init workload that waits for the producer's first sample. Show the race with plain `ADD_COND_RUNNING` first, then the fix. Pitch: "running is the runtime's word, ready is the app's".

**Evidence.** Ankaios dependency types and the `Pending(WaitingToStart)` state: inter-workload-dependencies.md; "does not consider inter-workload dependencies when restarting": restart-policy.md. Quadlet generator and `Notify=healthy`: podman-systemd.unit(5). BlueChi "only executes transitions": BlueChi docs overview. Launch Manager config fields: the `simple_lifecycle` launch_manager_config.json in the HackFest reference integration. Claim that no Ankaios health-check or readiness field exists: grep of repos/ankaios/doc/docs found none (checked).
