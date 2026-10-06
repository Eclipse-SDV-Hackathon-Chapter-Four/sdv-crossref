---
title: Pick the control plane by who must decide offline: a decision table
type: pattern
cluster: orchestration-criticality
component: none
tags: [control-plane, symphony, ankaios, kanto, muto, bluechi, kubernetes, kubeedge, decision]
status: draft
sources:
  - repos/hc2-challenge-maestro/eclipse-symphony/README.md
  - repos/hc2-challenge-maestro/eclipse-bluechi/README.md
  - repos/ankaios/doc/docs/reference/orch-comparison.md
  - repos/hc3-challenge-mission-update-possible/hpc_variant/README.md
  - https://eclipse.dev/kanto/docs/
  - https://sdv-blueprints.eclipse.dev/docs/ros-racer/
  - https://kubeedge.io/docs/
last-verified: 2026-10-03
related:
  - "[[symphony-overview]]"
  - "[[ankaios-overview]]"
  - "[[kanto-overview]]"
  - "[[muto-overview]]"
  - "[[desired-state-converges-locally-when-the-link-drops]]"
applies-to: [symphony, ankaios, kanto, muto, autosd]
gap-rows: [C6, C2, C5]
---

# Pick the control plane by who must decide offline: a decision table

**Problem.** A team wires Symphony to a vehicle and discovers the vehicle needs a local agent anyway; another starts from Kanto and finds a cloud-shaped model and a dormant upstream.

**Forces.**
- A fleet plane (many vehicles, rollouts) and a vehicle plane (start order, restart, safety gates) have different owners and failure modes.
- Cloud-first stacks assume connectivity; vehicle-first stacks assume a local authority.
- Domain-specific planes (ROS stacks) have their own composition model.

**The rule.** Two planes, one seam. The **cloud plane** declares intent for a fleet (Symphony Instance, Kubernetes/KubeEdge, Kanto's Hono/Ditto path). The **vehicle plane** owns what runs on this node and in what order (Ankaios, or systemd/quadlet/BlueChi on AutoSD, or S-CORE Launch Manager). The seam is a provider or agent that turns intent into local desired state and reports observed state back. Choose each plane by the questions below, and do not let the cloud plane talk to containers directly.

| Question | Answer to pick | Why |
|---|---|---|
| Must the vehicle act with no cloud? | vehicle plane required: Ankaios or systemd+BlueChi | local authority |
| Several nodes, one declarative API in the vehicle? | Ankaios (BlueChi if you stay on systemd) | multi-node, dependency ordering; BlueChi only executes transitions |
| Only systemd units on AutoSD? | quadlets + BlueChi | no extra runtime |
| Fleet rollout, targets, staged deploys? | Symphony (needs the Ankaios provider, gap C6) | Target/Solution/Instance |
| Already cloud-centric with Hono/Ditto, one device? | Kanto, accepting maintenance mode (last tagged 2024) | per-device daemon, cloud-first |
| ROS 2 stack composition and swap? | Muto (Symphony hook optional) | model-driven ROS stacks |
| Full Kubernetes API in vehicle? | k3s/KubeEdge (heavier; no dependency types per Ankaios's comparison) | ecosystem, not footprint |

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Symphony providers and agents | target provider, MQTT/HTTP remote agent, pull agent (Piccolo) | the seam in code: agent per device |
| Mission Update Possible HPC variant | Symphony in cloud, MQTT, Ankaios control-interface workload in the vehicle | a working seam, custom |
| KubeEdge | cloud core plus EdgeCore with local store | Kubernetes-shaped offline autonomy |
| Kanto | container-management daemon plus suite connector to Hono/Ditto | cloud-first single device |
| Muto | ROS stacks, agent, composer; Symphony or Ditto cloud side | domain-specific plane |

**On the Eclipse SDV stack.** The unfilled cell is C6: Symphony provider for Ankaios (upstream lists none; Chapter 3 had a custom adapter, Ankaios exploring Symphony's Python SDK PoC per the Symphony README). Pullpiri is an additional Symphony provider target (listed in the Maestro README; not researched). Detail in [[symphony-overview]], [[ankaios-overview]], [[kanto-overview]], [[muto-overview]]. Pair with [[desired-state-converges-locally-when-the-link-drops]].

**The trap.** Choosing the plane for the pitch deck (cloud logo) and discovering that the vehicle plane has no owner when the modem drops.

**For a hackathon team.** Do not build both planes: pick Ankaios locally and fake the cloud with an MQTT publisher of a manifest. One slide with the table above and the sentence "cloud proposes, vehicle disposes".

**Evidence.** Kanto activity and cloud focus: [[kanto-overview]] (GitHub API data from that note). Symphony provider/agent list: Maestro Symphony README. Ankaios vs K3s feature table: orch-comparison.md. KubeEdge local metadata: kubeedge.io page (offline reconnect details not confirmed, unverified).
