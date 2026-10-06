---
title: The type hash is the contract; a bridge must carry it or admit it dropped it
type: pattern
cluster: robotics
component: none
tags: [ros2, rihs01, type-hash, vss, iceoryx2, bridge, schema-evolution]
status: draft
sources:
  - https://roscon.ros.org/2023/talks/ROS_2_Types_On-the-wire_Type_Descriptions_and_Hashing_in_Iron_and_onwards.pdf
  - https://docs.ros.org/en/rolling/p/type_description_interfaces/srv/GetTypeDescription.html
  - https://github.com/ros2/rmw_zenoh
  - https://discourse.openrobotics.org/t/rmw-iceoryx2-v0-1-0-release/40996
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[iceoryx2-overview]]"
  - "[[vss-kuksa-overview]]"
applies-to: [iceoryx2, vss-kuksa, zenoh, uprotocol]
gap-rows: [B2, B10]
---

# The type hash is the contract; a bridge must carry it or admit it dropped it

**Problem.** A ROS 2 message `Foo` gains a field. Old and new nodes still "speak Foo", but their bytes differ; a bridge to VSS or to a fixed-layout shared-memory service maps by name and quietly mis-reads.

**Forces.**
- ROS 2 messages are variable-size, serialized (CDR) and may hold strings and sequences; shared-memory layouts are fixed.
- Evolution must be detectable, not assumed compatible.
- VSS is a signal model with units and ranges, not a message model.
- Bridges are cheap to write and expensive to trust.

**The rule.** Identity of a layout is its **hash**, not its name. ROS 2 (Iron onward) gives each interface a RIHS01 hash, SHA-256 over a canonical description of the type and its nested types, discoverable and retrievable via `GetTypeDescription`; rmw_zenoh puts it into the key expression `<domain>/<fqn>/<type>/<hash>`, so a changed type does not match and **is silently dropped** (the README lists Humble vs newer as incompatible for this reason). A bridge is *honest* when it either carries the source hash into the destination (service attribute, key suffix, header field) and refuses on mismatch, or states in its manifest which fields it maps. It is *hiding* a mismatch when it maps by field name into VSS leaf paths and defaults the missing ones.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| REP-2011 / RIHS01 | hash of type description, carried in discovery | detect drift before the first sample |
| rmw_zenoh key expressions | hash is part of the key | mismatch = no delivery, not corruption |
| rmw_iceoryx2 v0.1.0 (Dec 2024) | pub/sub of self-contained types only; no serialization, services or host-to-host yet | fixed layout is the precondition for zero-copy |
| Protobuf/FlatBuffers evolution rules | additive, field-number-stable changes | compatibility by construction, not by hash |
| vss-tools exporters (ros2interface, protobuf, ddsidl) | VSS tree to message definitions | one-way generation (see gap B10) |

**On the Eclipse SDV stack.** [[iceoryx2-overview]] already refuses a mismatched type name and size; add the RIHS01 (or a hash of the generated struct) as a service **attribute**, as in [[instance-in-the-name-type-in-the-hash]], and the ROS-to-iceoryx2 bridge becomes honest: a ROS message is eligible only if it is bounded (fixed arrays, bounded strings). VSS enters one level up ([[vss-kuksa-overview]]): VSS paths carry unit and range, which ROS msgs do not, so a ROS-to-VSS mapper must hold that metadata itself. B10 (vss-tools to `#[repr(C)]`) is the other direction and is the reason the layout hash can be derived from the vspec.

**The trap.** Treating "same name, same package" as "same type" and mapping by field name; the bridge works until a field is inserted.

**For a hackathon team.** Add a field to a message, show rmw_zenoh (or your bridge) refusing the old publisher by hash instead of delivering garbage. Pitch: "mismatch is a refusal, not a surprise".

**Evidence.** Hash exposure and key expression: rmw_zenoh README and design doc (verified). rmw_iceoryx2 limits: release post (verified, as of Dec 2024, may have moved on). What exactly is inside the hash (field names and types included; comments and default values excluded) is from memory of REP-2011: unverified (docs.ros.org blocked).
