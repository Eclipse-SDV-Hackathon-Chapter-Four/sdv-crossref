---
title: A function moving between nodes is a placement change, not a model edit
type: pattern
cluster: orchestration-criticality
component: none
tags: [placement, manifest, vss, ankaios, hpc, rt, cadence]
status: draft
sources:
  - repos/ankaios/doc/docs/reference/glossary.md (agent field names the node)
  - repos/ankaios/doc/docs/architecture.md (workload communication out of scope)
  - https://www.autosar.org/standards/adaptive-platform (AUTOSAR Adaptive execution manifest / machine manifest, separate from the service model)
  - https://covesa.github.io/vehicle_signal_specification/ (VSS has no placement)
last-verified: 2026-10-03
related:
  - "[[ankaios-overview]]"
  - "[[symphony-overview]]"
  - "[[reference-architecture-hack-to-the-future]]"
  - "[[instance-in-the-name-type-in-the-hash]]"
applies-to: [ankaios, symphony, vss-kuksa, iceoryx2, zenoh]
gap-rows: [C8, C5]
---

# A function moving between nodes is a placement change, not a model edit

**Problem.** The brake-light function moves from the RT MCU to the HPC for a second hardware variant, and someone edits the signal tree, the topic names and three configs. Ankaios knows `agent: hpc`; the signal model knows nothing about nodes; nothing says who produces what.

**Forces.**
- The signal model (VSS, types) must stay the same across variants.
- Direction (publish or consume) is a per-node fact, not a model fact.
- Cadence and producer count are safety-relevant (one producer per signal set).
- Workload placement (Ankaios) and signal placement are different artefacts that must not drift.

**The rule.** Keep a third artefact between the model and the orchestrator: a **placement manifest** that says, per signal set, which node produces it, at which cadence, with which validity policy. Each node's provider config and subscribe/publish direction is generated from it: a node that is not the producer subscribes. Moving a function is then a one-line edit of `producer:` and a re-apply of the workload manifest; the model and the consumers do not change. Validate: exactly one producer per set, cadence declared, every consumer node has a route.

```yaml
sets:
  - set: Vehicle.Cabin.Lights.Brake      # type: from the model
    producer: {node: rt-mcu, cadence_ms: 10}
    consumers: [hpc, gateway]
```

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| AUTOSAR Adaptive manifests | service interface model separate from machine and execution manifests | same split: model, then where and how it runs |
| Ankaios `agent:` field | per workload node name | what runs where, nothing about signals |
| Kubernetes nodeSelector / affinity | placement as data separate from the workload spec | placement as a constraint, not code |
| DDS QoS plus deployment XML (OMG DDS) | cadence/deadline are QoS, not type | cadence belongs next to the producer declaration |
| Symphony Target/Instance | which solution on which target | fleet-level placement, still no signals |

**On the Eclipse SDV stack.** Ankaios workload manifest answers "which container on which agent" ([[ankaios-overview]]); Symphony answers "which solution on which target" ([[symphony-overview]]). Neither says "which node produces `Vehicle.Speed` every 10 ms" (gap C8). The generator emits, per node, the Ankaios workload set, the KUKSA provider or iceoryx2 service config, and the Zenoh key mapping for the cross-node hop ([[instance-in-the-name-type-in-the-hash]] for the instance and type split). Hack-to-the-Future's RT/HPC split ([[reference-architecture-hack-to-the-future]]) is the natural demo: flip `producer:` and show the same consumer binary unchanged.

**The trap.** Encoding the producing node in the signal path or type, so a placement change becomes a model migration.

**For a hackathon team.** A 40-line script: read the YAML, emit two Ankaios manifests and two provider configs, and a validator that rejects two producers for one set. Demo by moving one function between nodes live. Pitch: "move a function by editing one line".

**Evidence.** Gap C8 and its definition: synthesis/gap-register.md. Ankaios `agent` and the statement that communication between workloads is out of scope: architecture.md. AUTOSAR Adaptive manifest split: standard AUTOSAR behaviour (primary spec access is gated; unverified here).
