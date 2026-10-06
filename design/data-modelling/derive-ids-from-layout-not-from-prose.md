---
title: Derive ids from layout, not from prose
type: pattern
cluster: data-modelling
component: none
tags: [id, hash, vss, static-uid, ros2, dds, fnv, identity]
status: draft
sources:
  - repos/vss-tools/docs/id.md
  - repos/vss-tools/src/vss_tools/utils/idgen_utils.py and exporters/id.py
  - https://docs.ros.org/en/rolling/Concepts/Advanced/About-Type-Hashes.html
  - https://github.com/ros2/rosidl/tree/rolling/rosidl_generator_type_description
  - https://www.omg.org/spec/DDS-XTypes/ (TypeIdentifier equivalence hashes)
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[additive-only-then-remint-identity]]"
  - "[[a-unit-is-identity-a-range-is-policy]]"
applies-to: [vss-kuksa, iceoryx2]
gap-rows: [B10]
---

# Derive ids from layout, not from prose

**Problem.** A typo fix in a description re-mints every id, or an enum rebinding does not. Either way the id no longer answers "can I read these bytes".

**Forces.**
- Ids must be computable by independent parties without a registry.
- Prose (descriptions, display names, comments) changes constantly and carries no wire meaning.
- 32-bit ids collide; compactness costs safety.

**The rule.** Hash exactly what a reader needs to decode and interpret the bytes: canonical name, node kind, datatype and layout, unit, enum discriminant table, scale and offset. Exclude descriptions, comments, display names, defaults and ranges. Use a stable canonical serialisation, a wide hash, and a collision check; keep an explicit `fka` or alias to move names without re-minting.

What VSS does today (`vspec export id`, vss-tools 6.1, read from `idgen_utils.py`): FNV-1 32-bit over `"<fqn>: unit: , datatype: , type:" + allowed + min + max`, lower-cased unless `--case-sensitive`/strict. So included: path, unit, datatype, type, `allowed`, `min`, `max`. Excluded: description, default, comment, deprecation (docs: non-breaking), and, from code reading, the 6.1 `enum` dict. `fka` hashes the old name; `constUID` overrides; a collision exits fatally. The probability quoted in id.md is 0.0197 percent for about 1300 signals.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| VSS `vspec export id` | 4-byte FNV-1 over metadata; validation against a prior file, `fka`, `constUID` | static ids from the model, with a breaking/non-breaking report |
| ROS 2 type hash (REP 2011) | SHA-256 over the canonical type description including referenced types | wide, layout-only identity carried in discovery |
| DDS XTypes TypeIdentifier | equivalence hash of the structure (unverified detail) | structural identity independent of names of modules |
| Protobuf field numbers | the number, not the name, is the wire identity | names free, numbers frozen |
| Git/Nix content addressing | identity is the hash of content | no registry |

**On the Eclipse SDV stack.** The B10 exporter ([[vss-kuksa-howto]] section 9, [[iceoryx2-overview]]) should compute its own 128-bit layout hash and put it in service attributes; reuse `staticUID` only as a human-stable alias. Note the gap with vss-tools: `min`/`max` are in the hash (a range change is flagged BREAKING in id.md) and enum values are not. For safety consumers the opposite is wanted: ranges out, enum discriminants in. The databroker's own numeric ids are load-time and unstable ([[vss-kuksa-reference]]).

**The trap.** Hashing human text and treating the id as a version.

**For a hackathon team.** Show a diff table: edit a description (id same), change a unit (id changes), rebind an enum (id changes), tighten a range (id same).

**Evidence.** Hash inputs: idgen_utils.py and id.py. Breaking/non-breaking table: id.md. ROS 2 type hash page was blocked by an anti-bot wall when fetched; the rosidl README confirms a SHA-256 over fully expanded type descriptions, exclusions not stated there (unverified).
