---
title: The namespace is the instance, the launch file is the placement
type: pattern
cluster: robotics
component: none
tags: [ros2, composition, namespaces, remapping, launch, placement]
status: draft
sources:
  - https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Composition.html
  - https://docs.ros.org/en/rolling/Tutorials/Intermediate/Composition.html
  - https://docs.ros.org/en/jazzy/p/composition_interfaces/
  - https://github.com/eclipse-ankaios/ankaios
  - https://github.com/eclipse-uprotocol/up-spec
last-verified: 2026-10-03
related:
  - "[[ankaios-overview]]"
  - "[[uprotocol-overview]]"
  - "[[muto-overview]]"
  - "[[instance-in-the-name-type-in-the-hash]]"
applies-to: [ankaios, uprotocol, muto, zenoh]
gap-rows: [C8, C5]
---

# The namespace is the instance, the launch file is the placement

**Problem.** Two identical arms, two identical cameras, or a trailer's second brake controller are started from the same code. If the code hard-codes names, the second copy collides; if the instance leaks into the code, you rebuild per instance.

**Forces.**
- One binary (type) must run many times (instances).
- Where a node runs (process, container, host) must be changeable without touching its code.
- Names must stay stable for consumers across a re-placement.
- Co-locating nodes should be allowed to be zero-copy, but must not change semantics.

**The rule.** A ROS 2 node is a *component* (type) with relative names; the **namespace and remappings** supply the instance; the **launch file or container** supplies the placement. A node that publishes `joint_states` becomes `/left_arm/joint_states` and `/right_arm/joint_states` by namespace alone, and a remap re-wires one consumer without a rebuild. A composable node can be loaded into a running container through the `composition_interfaces/LoadNode` service (or `ComposableNodeContainer` in launch), so moving a node between processes is a placement decision that changes neither its name nor its interfaces, only latency (intra-process).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ROS 2 composition | component libraries, container loads them at runtime via `LoadNode`/`UnloadNode` | placement without code change |
| ROS 2 namespaces, remapping, `__ns` / `__node` | relative names rewritten at start | instances from one binary |
| Ankaios state manifest | `workloads:` map with `agent`, `runtime`, `dependencies` | placement declared per workload ([[ankaios-overview]]) |
| uProtocol UUri | `authority` + `ue_id` (type low 16 bits, instance high 16 bits) + version + resource | the same type/instance split in the address |
| Eclipse Muto Composer | stack model that launches nodes ("a smart launch manager") | placement as a deployable model ([[muto-overview]]) |

**On the Eclipse SDV stack.** The three vocabularies line up: ROS namespace = UUri `ue_instance` (and authority for a whole robot); launch file / composable container = an Ankaios workload with an `agent:` field. An Ankaios manifest that starts one container per ROS namespace gives you a vehicle-side launch file, but Ankaios sees a container, not nodes; the node-level view ("which node produces which topic at which rate") is still the missing placement manifest, [[ankaios-overview]] / gap C8. Ankaios manifests for ROS stacks do not exist upstream (C5).

**The trap.** Putting the instance in the node name in code (`left_arm_driver`), so the second arm needs a fork; or assuming composition is only an optimisation and then discovering that intra-process delivery ignores some QoS and is not visible to a tap on the wire.

**For a hackathon team.** Start the same driver node twice under two namespaces from one launch file, then once as a composable node in one container, and show that the consumer's topics did not change. Pitch: "one binary, namespaced instances, placement in a file".

**Evidence.** Composition and `LoadNode` service: composition docs above. UUri bit layout: [[uprotocol-overview]]. Ankaios manifest fields: [[ankaios-overview]]. The claim that no upstream Ankaios manifest for ROS exists is from [[muto-overview]] ("container deployment planned"); not otherwise searched.
