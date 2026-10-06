---
title: Additive changes keep the id, anything else mints a new one
type: pattern
cluster: data-modelling
component: none
tags: [evolution, versioning, deprecation, protobuf, flatbuffers, avro, sovd, vss]
status: draft
sources:
  - https://protobuf.dev/programming-guides/proto3/#updating
  - https://flatbuffers.dev/schema/
  - https://avro.apache.org/docs/current/specification/#schema-resolution
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/basics.md (Deprecation)
  - repos/vss-tools/docs/id.md and docs/diff.md
  - https://github.com/eclipse-opensovd/opensovd (x-sovd-applicability, see opensovd-reference)
last-verified: 2026-10-03
related:
  - "[[derive-ids-from-layout-not-from-prose]]"
  - "[[enum-discriminants-are-the-type]]"
  - "[[opensovd-reference]]"
applies-to: [vss-kuksa, iceoryx2, opensovd]
gap-rows: [B10]
---

# Additive changes keep the id, anything else mints a new one

**Problem.** A producer adds a field and half the consumers crash; or a producer changes a unit and no one notices because the name stayed.

**Forces.**
- Fleets run mixed versions for years.
- Old data must stay readable; new producers must not force simultaneous upgrades.
- "Minor" edits are decided by whoever is in a hurry.

**The rule.** An id survives only changes that every old reader tolerates: append a field or enum value, add an optional attribute, change a description, mark deprecated. Anything that changes the layout, meaning (unit, scale), or discriminant binding mints a new id; the old id stays served for the deprecation window. Put the rule in a tool that diffs two models, not in review habits.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Protobuf | add fields and enum values safely; never change numbers; `reserved` for removed | the additive rule and the tombstone |
| FlatBuffers | table fields append-only, `deprecated` keeps the slot; structs cannot change; do not change defaults | the layout constraint in a zero-copy format |
| Avro | writer/reader schema resolution with defaults and aliases | explicit compatibility check (unverified detail) |
| VSS `deprecation: v6.1 - ...` | moved/removed noted with version; served during the window (removed in second minor or next major) | the deprecation protocol |
| vss-tools `id --validate-static-uid`, `vspec diff` | BREAKING: name, datatype, type, unit, allowed, min, max; non-breaking: description, deprecation, added or deleted attribute | a mechanical breaking-change detector with `fka` for renames |
| SOVD `x-sovd-applicability` and DTDL `;version` | variants and published immutable versions | version versus variant: same id family, different applicability (unverified for SOVD detail) |

**On the Eclipse SDV stack.** Run `vspec export id --validate-static-uid` plus `vspec diff` in CI on the overlay set ([[vss-kuksa-howto]]); gate service-attribute changes on the same verdict. Remember the vss-tools asymmetry: min/max are breaking, `enum` is not hashed. [[opensovd-reference]] lists applicability for variants.

**The trap.** Conflating version with variant: a different supplier's unit is a variant (new signal, same family), not version 2.

**For a hackathon team.** One CI step printing BREAKING versus NON-BREAKING for a model edit. Pitch: "the pipeline decides whether the id changes".

**Evidence.** Protobuf rules fetched; FlatBuffers partly fetched; VSS deprecation rules and id tables read. Avro and SOVD applicability details unverified.
