---
title: One type source, generated bindings, one pinned library version
type: pattern
cluster: ipc-e2e
component: none
tags: [type-safety, abi, cross-language, iceoryx2, dds-xtypes, codegen, versioning, rust, cpp, python]
status: draft
sources:
  - repos/iceoryx2/iceoryx2/src/service/static_config/message_type_details.rs (TypeDetail, is_compatible_to)
  - repos/iceoryx2/FAQ.md ("Unable To Connect Due To IncompatibleTypes")
  - https://www.omg.org/spec/DDS-XTypes/1.3/PDF (§7.6.3.4 TypeConsistencyEnforcementQosPolicy)
  - https://docs.ros.org/en/rolling/Concepts/Advanced/About-Type-Hashes.html (RIHS01)
  - repos/up-spec/up-l1/iceoryx2.adoc (dsn~up-transport-iceoryx2-protocol-version~1)
  - repos/up-transport-iceoryx2-rust/Cargo.toml
last-verified: 2026-10-03
related:
  - "[[type-hash-is-the-contract-bridges-must-not-erase-it]]"
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[zero-copy-pays-only-for-fixed-layout-payloads]]"
  - "[[iceoryx2-howto]]"
  - "[[iceoryx2-quickstart]]"
  - "[[uprotocol-howto]]"
applies-to: [iceoryx2, uprotocol, vss-kuksa, s-core, zenoh]
gap-rows: [B10, B5, E5, E9]
---

# One type source, generated bindings, one pinned library version

**Problem.** A Rust producer, a C++ consumer and a Python dashboard each declare "the same" struct by hand. On a good day they refuse to connect. On a bad day they connect, because name, size and alignment match while two `f32` fields are swapped, and the Guardian reads pack voltage as temperature.

**Forces.**
- Three languages and three toolchains, and the struct has to be identical to the byte.
- Pre-1.0 middleware breaks its own wire format between minor releases.
- Developers silence a connection error by making names match, not layouts.
- Over the network a schema can evolve. Shared memory cannot evolve in place.

**The rule.** Write the type **once** (vspec, IDL, `.fbs`, or one Rust crate with `#[repr(C)]`), **generate** every language binding from it, put a **layout hash** where the middleware compares names, and **pin one middleware version** across every process that shares memory. Know exactly what your middleware checks. iceoryx2 compares only `type_name`, variant, `size` and `alignment` for the payload and the user header (`is_compatible_to`). It does not compare fields, order, units or meaning. Different iceoryx2 versions fail with `VersionMismatch`. That is the correct failure, so never work around it.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| iceoryx2 static config | type name + size + alignment per service; `IncompatibleTypes`, `VersionMismatch` | a cheap gate that is not a layout proof |
| DDS XTypes §7.6.3.4 | `DISALLOW_TYPE_COERCION` (same type) vs default `ALLOW_TYPE_COERCION` (reader assignable from writer) | an explicit choice between strict and evolvable |
| ROS 2 RIHS01 | SHA-256 over the canonical type description, carried in discovery | name ≠ type; the hash is the contract ([[type-hash-is-the-contract-bridges-must-not-erase-it]]) |
| AUTOSAR ARXML → RTE generation | one model, generated per-ECU code | the automotive original of "one source, generated bindings" |
| FlatBuffers / protobuf schemas | `flatc`/`protoc` for every language | a single schema with generated readers |

**On the Eclipse SDV stack.**
- iceoryx2: a shared type crate (the [[iceoryx2-howto]] advice) covers Rust only. For C++ generate a header (cbindgen), and for Python generate `ctypes.Structure` classes from the same crate or vspec. Set the type name to `<path>@<layout-hash>` with `#[type_name]` / `IOX2_TYPE_NAME`, so a field reorder becomes `IncompatibleTypes` instead of silent corruption. Observed on 2026-10-03: the Rust and C++ examples fail with `IncompatibleTypes`, and PyPI 0.10.0 against `main` fails with `VersionMismatch` ([[iceoryx2-quickstart]]).
- uProtocol shows the pinning trap in a spec. up-l1 iceoryx2 says transports "**MUST** use version `0.6.1` of the iceoryx2 protocol", while up-transport-iceoryx2-rust pins 0.7. Because iceoryx2 refuses mismatched versions, neither can talk to a 0.10 application (B5, E9).
- VSS as the type source: B10 (a vspec → `#[repr(C)]` exporter) is the generator this pattern needs.

**The trap.** Setting `IOX2_TYPE_NAME` by hand to "fix" `IncompatibleTypes` between hand-written structs. That turns off the only check and leaves the layout unproven.

**For a hackathon team.** Write one `.rs` type crate, generate the C++ header with cbindgen and the Python ctypes class with a 40-line script, and put a SHA-256 of the generated header into the type name. Reorder a field to show `IncompatibleTypes`. Pitch: "one type source; a reordered field cannot connect".

**Evidence.** `is_compatible_to` was read in `message_type_details.rs` lines 214–224 (fields: name, variant, size, alignment). The XTypes text is from §7.6.3.4.1. The uProtocol version requirement is quoted from `up-l1/iceoryx2.adoc`. The up-transport pin is from [[iceoryx2-overview]] and Cargo.toml. That the generated-header hash approach catches reorders is by design and was not demonstrated here.
