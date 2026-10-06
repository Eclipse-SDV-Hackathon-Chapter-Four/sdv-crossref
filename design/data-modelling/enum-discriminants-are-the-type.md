---
title: Enum discriminants are part of the type, names are not
type: pattern
cluster: data-modelling
component: none
tags: [vss, enum, allowed, protobuf, flatbuffers, discriminant]
status: draft
sources:
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/data_entry/enum.md and allowed.md
  - repos/vss-tools/src/vss_tools/model.py (enum checks) and exporters/id.py
  - repos/vss-tools/docs/avro.md and docs/ddsidl.md
  - https://protobuf.dev/programming-guides/proto3/#enum
  - https://protobuf.dev/programming-guides/proto3/#updating
  - https://flatbuffers.dev/schema/
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-reference]]"
  - "[[additive-only-then-remint-identity]]"
  - "[[derive-ids-from-layout-not-from-prose]]"
applies-to: [vss-kuksa, iceoryx2, uprotocol]
gap-rows: [B10]
---

# Enum discriminants are part of the type, names are not

**Problem.** `allowed: ['FORWARD','BACKWARD']` becomes `enum {FORWARD, BACKWARD}` in DDS IDL with positions 0 and 1. Someone inserts `NEUTRAL` in the middle, and every stored sample silently changes meaning.

**Forces.**
- Strings are self-describing but unbounded; integers are fixed-size but meaningless without the table.
- Zero-copy and CAN need integers; humans need names.
- Unknown values must be handled, not crashed on.

**The rule.** The number-to-meaning binding is the type; the names are documentation. Pin discriminants explicitly, never derive them from list order, never reuse a retired number, and treat adding a value as additive only for open (tolerant) consumers. VSS 6.1 `enum` does this: integer base type, `'KEY': value` dict, values unique, keys `[A-Z][A-Z_0-9]*`, no `allowed`/`min`/`max` alongside. VSS `allowed` is the older, order-free string set; exporters that need an integer invent one (vss-tools DDS IDL emits `enum` by list position, Avro puts `UNKNOWN` at position 0 as default).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| VSS 6.1 `enum` | named, pinned integers; recommends no "unknown" value (publish nothing) | explicit discriminants in the model |
| Protobuf proto3 | zero value first, open enums, `reserved` numbers and names, renumbering unsafe | the retirement rule |
| FlatBuffers | enum has explicit underlying type and values; unknown values legal on the wire; changing defaults is unsafe | fixed-size enum in a zero-copy table |
| Avro | enum symbol order matters; schema `default` symbol for unknown (reader) | the "unknown" escape hatch |
| J1939 / DBC value tables | value tables per signal, with reserved "error" and "not available" codes | an enum that includes its own validity values |

**On the Eclipse SDV stack.** [[vss-kuksa-reference]], two measured facts: the databroker 0.7.1 does not enforce `enum` (it accepted `99` for a 6.1 enum signal, observed there) but does enforce `allowed`; and vss-tools `vspec export id` hashes `allowed` but has no `enum` term in `exporters/id.py` (code reading, not run), so rebinding an enum value can keep the same static id. Exporter B10 should emit `#[repr(u8)]` enums with discriminants copied from the VSS `enum` dict, and refuse a model that uses `allowed` strings for a fixed-layout signal.

**The trap.** Treating enum rebinding as a harmless edit of labels, while stored and in-flight values keep their numbers.

**For a hackathon team.** Show two builds with a swapped enum value and a consumer that refuses the second via a discriminant-table hash in the service attributes.

**Evidence.** enum.md, allowed.md, model.py checks, Avro and DDS IDL docs read. Protobuf rules fetched. FlatBuffers enum/union rules and Avro default semantics only partly fetched (unverified detail).
