---
title: A type name is a claim, a layout hash is a proof
type: pattern
cluster: identity-discovery
component: none
tags: [identity, type-hash, ros2, rihs01, iceoryx2, rmw, zero-copy, safety]
status: draft
sources:
  - https://github.com/ros2/rosidl/tree/rolling/rosidl_generator_type_description (RIHS01: SHA-256 over canonical TypeDescription JSON)
  - https://github.com/ros-infrastructure/rep/pull/381 (REP-2016 draft, ROS 2 Interface Type Description)
  - https://github.com/ros2/rmw_dds_common/blob/rolling/rmw_dds_common/src/qos.cpp (`typehash=` in USER_DATA; missing key → zero hash, RMW_RET_OK)
  - https://github.com/ros2/rmw_zenoh/blob/rolling/docs/design.md (key `<domain>/<fqn>/<type_name>/<type_hash>`)
  - https://roscon.ros.org/2023/talks/ROS_2_Types_On-the-wire_Type_Descriptions_and_Hashing_in_Iron_and_onwards.pdf
  - repos/iceoryx2/iceoryx2/src/service/static_config/message_type_details.rs (`is_compatible_to`)
  - repos/iceoryx2/iceoryx2-bb/elementary-traits/src/type_name.rs (`unsafe trait TypeName`)
  - repos/iceoryx2/integrations/ros2/link-adapter/src/translator/plain_struct/mod.rs (LayoutMismatch)
last-verified: 2026-10-03
related:
  - "[[match-on-the-type-descriptor-never-fall-back-to-the-name]]"
  - "[[type-hash-is-the-contract-bridges-must-not-erase-it]]"
  - "[[refuse-loudly-a-mismatch-is-evidence]]"
  - "[[iceoryx2-overview]]"
  - "[[iceoryx2-quickstart]]"
applies-to: [iceoryx2, vss-kuksa, zenoh, s-core]
gap-rows: [B10, B2, B3]
---

# A type name is a claim, a layout hash is a proof

**Problem.** In zero-copy IPC the subscriber reinterprets raw shared memory as its own struct. If producer and consumer disagree on field order but agree on name and size, nothing crashes: the consumer silently reads the wrong field, which is the worst failure a safety function can have.

**Forces.**
- The check must happen at connect time, before the first sample, and cost nothing per sample.
- Cross-language peers (Rust, C++, Python) cannot share a compiler-generated type id.
- Generated code is the norm in ROS 2; hand-written `#[repr(C)]` structs are the norm in iceoryx2.
- A gateway between the two must not weaken the stronger check.

**The rule.** Rank type checks by what they prove and require the strongest one available on any path that decides: **name** (a claim) < **name + size + alignment** (a claim plus a tripwire) < **hash of a canonical structural description** (a proof). ROS 2 since Iron generates `RIHS01_<sha256>` per interface over a canonical JSON TypeDescription including nested types; DDS-based rmws put it in USER_DATA as `typehash=…;`, rmw_zenoh puts it in every data key expression so a different hash simply never matches. iceoryx2 stores `type_name`, size and alignment per service and refuses a mismatch with `IncompatibleTypes`, but `TypeName` is an **`unsafe` user trait** ("the user must guarantee that all types, also definitions in different languages, have the same memory layout"), defaulting to `core::any::type_name`. So iceoryx2's check is a claim plus a tripwire: a reordered field of equal size passes.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ROS 2 RIHS01 (Iron+) | SHA-256 over canonical type description, nested types included | a structural proof, comparable before connecting |
| rmw_zenoh | type hash is a key-expression segment | mismatch cannot match, by construction (and silently) |
| rmw_dds_common | `typehash=` in DDS USER_DATA; absent key parses to a zero hash without error | hash available to tools; refusal left to the caller |
| iceoryx2 0.10 | `type_name` + size + alignment (`<=`) per header and payload | cheap tripwire, `IncompatibleTypes` on open |
| DDS-XTypes | TypeIdentifier hash plus assignability | structural proof with controlled evolution |

**On the Eclipse SDV stack.**
- iceoryx2: give every payload an explicit `#[type_name("vss.Cabin.Seat/v2")]` *and* a `type.hash` service attribute generated from the same source as the struct (VSS via a vss-tools exporter, gap B10, or rosidl). Consumers `require("type.hash", …)`. Observed: Rust vs C++ example → `IncompatibleTypes` because the names differ, not because the layouts were compared ([[iceoryx2-quickstart]]).
- The iceoryx2 ROS 2 link adapter (prototype) maps by ROS type *name* and checks only size and alignment against the rosidl C struct (`LayoutMismatch`); it does not carry RIHS01 across. A static mapping entry should pin the hash ([[type-hash-is-the-contract-bridges-must-not-erase-it]]).
- S-CORE and FEO consume iceoryx2; the same attribute closes the gap there ([[s-core-overview]]).

**The trap.** Reading `IncompatibleTypes` as proof that iceoryx2 checks layouts; it compares a user-asserted name and two numbers.

**For a hackathon team.** Build two Rust binaries with the same `type_name` and swapped `u32` fields: they connect and exchange garbage. Add a `type.hash` attribute from a build script and show the second one refused. Pitch: "the name is what you say, the hash is what you built".

**Evidence.** `is_compatible_to` compares header, `type_name`, `variant`, `size`, and `alignment <=` (message_type_details.rs ~L214). `unsafe trait TypeName` doc comment (type_name.rs ~L17–28). ROS 2 adapter check: plain_struct/mod.rs ~L94–105. rmw_dds_common `parse_type_hash_from_user_data` returns zero hash with `RMW_RET_OK` when the key is missing (qos.cpp ~L694–697). Whether rmw_fastrtps / rmw_cyclonedds refuse on hash mismatch was not found in source (unverified; they appear to expose it in `TopicEndpointInfo` only). rmw_zenoh key format: design.md "Topic and Service name mapping".
