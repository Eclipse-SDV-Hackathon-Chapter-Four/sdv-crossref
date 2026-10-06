---
title: Desired state converges locally; the link only moves intent
type: pattern
cluster: orchestration-criticality
component: none
tags: [desired-state, reconciliation, symphony, ankaios, kubernetes, intermittent-connectivity]
status: draft
sources:
  - repos/ankaios/doc/docs/reference/complete-state.md
  - repos/ankaios/doc/docs/reference/control-interface.md
  - repos/ankaios/doc/docs/reference/orch-comparison.md (reconciliation loop row)
  - repos/ankaios/grpc/doc/swdesign/README.md (ServerGone handling)
  - repos/hc2-challenge-maestro/eclipse-symphony/README.md (Target/Solution/Instance, pull agents, MQTT agent)
  - https://kubernetes.io/docs/concepts/architecture/controller/
  - https://kubeedge.io/docs/ (MetaManager local store, EdgeHub sync)
last-verified: 2026-10-03
related:
  - "[[symphony-overview]]"
  - "[[ankaios-overview]]"
  - "[[muto-overview]]"
applies-to: [ankaios, symphony, muto, kanto]
gap-rows: [C6, C2]
---

# Desired state converges locally; the link only moves intent

**Problem.** A vehicle is in a tunnel when the fleet rolls out a new solution, or the cloud says "run X" while a local safety function says "X must stay off". If control is imperative over the link, a dropped connection leaves the vehicle half-changed.

**Forces.**
- The cloud knows what should run; only the vehicle knows what is safe to start now.
- Imperative commands are lost or replayed when the link flaps; state is idempotent.
- A vehicle must keep running its last accepted state offline.
- Apps sometimes must change state themselves (control interface), which makes two writers.

**The rule.** Send the vehicle a declaration, not a command, and let it converge against its own local state. "Converge" for a vehicle means: the node holds the last accepted desired state durably, reconciles toward it with its own policy (ordering, safety gates, drive state), reports observed state back when a link exists, and never needs the cloud to finish a transition. Define a single owner for each field of desired state: the cloud for "which solution/version", the vehicle for "may we apply it now". Observed state flows up and is an event stream, not a lock.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Kubernetes controllers | observe, diff, act in a loop against declared spec | the reconciliation vocabulary |
| Ankaios | server holds desired `State` (manifest), agents reconcile, apps can read/write `CompleteState` through the control interface; docs list a reconciliation loop; on server loss the agent "remains operational" (swdesign comment) | local convergence with an app-level write path |
| Symphony | Target (device + provider), Solution (components), Instance (solution on targets); providers do the work; MQTT/HTTP agents and pull agents for constrained devices | cloud intent model; pull agent = the vehicle decides when |
| KubeEdge | EdgeCore keeps metadata in local SQLite, EdgeHub syncs when connected | explicit offline autonomy |
| Muto | declarative ROS stack models, agent bridges MQTT, rollback | desired state for a ROS stack |

**On the Eclipse SDV stack.** Ankaios manifest apply (`ank apply`, or a workload with `controlInterfaceAccess` rules writing state) is the in-vehicle declaration; the Symphony Instance is the fleet one, and the missing glue is the Symphony provider for Ankaios (C6): a Target whose provider translates a Solution's components into Ankaios workloads and reports `workloadStates` back. The upstream README lists none; Chapter 3 MegaBosses built a custom adapter (unverified detail, see [[symphony-overview]]). Put the vehicle-side gate in an Ankaios workload that holds the control interface: it accepts a pending desired state, and applies it only in an allowed drive state. Whether an Ankaios agent keeps restarting workloads while the server is unreachable is not stated in the docs read (unverified, test it by stopping `ank-server`). Muto fills the same slot for ROS stacks ([[muto-overview]]).

**The trap.** Treating "the Instance says deployed" as "the vehicle runs it". Desired state is not observed state; show both columns.

**For a hackathon team.** Apply a manifest, cut the link (kill the server or the MQTT broker), change the manifest on the cloud side, restore: show the vehicle converges to the newest declaration and reports the observed state. Pitch: "the vehicle converges, the cloud proposes".

**Evidence.** Control interface and `CompleteState` access: control-interface.md, complete-state.md. Agent stays up on `ServerGone`: grpc swdesign. Symphony constructs and agents: hc2-challenge-maestro/eclipse-symphony/README.md. No Symphony-Ankaios provider in upstream: [[symphony-overview]]. Behaviour under server loss is unverified.
