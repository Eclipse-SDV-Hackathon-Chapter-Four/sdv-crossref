---
title: Muto declares the ROS stack; the vehicle orchestrator owns the process
type: pattern
cluster: robotics
component: none
tags: [muto, ros2, declarative, ota, ankaios, symphony, mqtt, orchestration]
status: draft
sources:
  - https://projects.eclipse.org/projects/automotive.muto/governance
  - https://github.com/eclipse-muto
  - https://sdv-blueprints.eclipse.dev/docs/ros-racer/
last-verified: 2026-10-03
related:
  - "[[muto-overview]]"
  - "[[ankaios-overview]]"
  - "[[symphony-overview]]"
applies-to: [muto, ankaios, symphony, zenoh]
gap-rows: [C5, C6]
---

# Muto declares the ROS stack; the vehicle orchestrator owns the process

**Problem.** You want to swap a driving algorithm over the air and roll it back, but ROS has no notion of "the desired stack"; a launch file is imperative and local.

**Forces.**
- ROS node graphs are model-shaped (nodes, params, remaps) and benefit from a ROS-aware deployer.
- Vehicles already have a process/container orchestrator with restart, dependency and criticality rules.
- Cloud-side desired state arrives via MQTT/Symphony/Ditto, not DDS.
- Two lifecycle owners for the same process is a bug.

**The rule.** Split the layers: **Muto owns the model** (a stack = nodes, launch context, applicability) and **resolves it into launch actions**; the **orchestrator owns the processes** (start, restart, resources, criticality). Muto's Composer is "a smart launch manager"; its Agent is a transceiver to the twin (Ditto) over MQTT with a Symphony provider; the Dashboard manages devices. What it lacks, as far as the vault could establish: container deployment is "planned", no Ankaios story, no Zenoh story, small community. So put Muto (or a minimal equivalent) *inside* one Ankaios workload that hosts the ROS container, and let Ankaios own restart and dependencies.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Eclipse Muto | stack model, Composer, Agent (MQTT, Ditto, Symphony), ROS Racer blueprint with OTA swap and rollback | declarative ROS stacks |
| Ankaios | state manifest with `workloads:`, `agent`, `dependencies`, `restartPolicy` | process ownership on the vehicle |
| Eclipse Symphony | desired-state targets and providers | cloud-side state, where Muto already has a provider |
| ROS 2 launch / composition | imperative launch description | what Muto replaces with a model |
| Kubernetes operators | controller reconciles a custom resource | the generic form of "model to process" |

**On the Eclipse SDV stack.** The seam is one Ankaios workload per ROS container with the Muto Agent inside; Ankaios `restartPolicy` and `dependencies` handle the container, Muto handles which nodes run in it. Symphony (target = vehicle) pushes the stack model to the Agent, an adapter that already exists in the ROS Racer blueprint. Muto over rmw_zenoh instead of CycloneDDS + MQTT would remove the second bus ([[ros-over-zenoh-needs-a-router-and-a-contract]]). A SOVD or heartbeat status of the stack is not provided. See [[muto-overview]], [[ankaios-overview]], [[symphony-overview]].

**The trap.** Letting Muto restart nodes while Ankaios restarts the container: two owners, a restart storm.

**For a hackathon team.** Run the ROS Racer flow (swap an algorithm, roll back) and show the container under Ankaios with a dependency on the broker; pitch the one-line split above. Do not rebuild Muto. Note this is a freestyle idea, not a gap with a worked solution.

**Evidence.** Muto components and MQTT/Symphony/Ditto: Eclipse project governance page and search summary (verified). "Container deployment planned", no Ankaios/Zenoh: [[muto-overview]] and org README (not re-verified; unverified recency). Ankaios fields: [[ankaios-overview]].
