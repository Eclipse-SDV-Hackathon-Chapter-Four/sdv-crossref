---
title: New types are a software change; new instances are not
type: pattern
cluster: safety
component: none
tags: [open-world, closed-world, type-hash, impact-analysis, deciders, observers, trailer]
status: draft
sources:
  - https://www.iso.org/standard/68384.html (ISO 26262-8:2018 clause 8 change management, clause 7 configuration management) (catalogue id unverified)
  - https://www.omg.org/spec/DDS-XTypes/ (type identity and assignability in discovery)
  - https://docs.ros.org/en/rolling/Concepts/Advanced/About-Type-Hashes.html
  - repos/s-core-score/docs/features/frameworks/feo/index.rst ("runtime static" topics, statically typed messages)
  - https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_E2EProtocol.pdf (Data ID binds a message to its type and source)
  - "[[iceoryx2-reference]] (service attributes, type name and size matching)"
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[decide-once-per-cycle-in-a-fixed-order]]"
  - "[[record-at-the-seam-replay-with-the-original-clock]]"
  - "[[iceoryx2-overview]]"
  - "[[opensovd-overview]]"
applies-to: [iceoryx2, s-core, vss-kuksa, opensovd, uprotocol, zenoh]
gap-rows: [B10, C8, A5, A10]
---

# New types are a software change; new instances are not

**Problem.** A second battery pack (or a trailer battery) appears at runtime. If the Guardian accepts whatever shows up, a new, unvalidated layout feeds a safety decision. If every new pack needs a rebuild, the platform cannot grow. Either the safety argument or the openness breaks.

**Forces.**
- A safety argument covers code paths that were analysed and tested; an unknown layout is an unanalysed path.
- Instances (pack 2, trailer 7) appear in the field; recertifying per instance is impossible.
- Observers (evidence, dashboards, diagnostics) must see everything, including what nobody compiled against.
- The type check must happen before the first byte is used, not after a crash.

**The rule.** Split consumers by role. **Deciders** are closed-world: they open ports only for types (layout hashes) in their build-time list and refuse anything else before reading a sample; a new *type* therefore needs a new build, impact analysis and re-verification, i.e. it is a software change under change management. A new *instance* of a known type (pack 2) is configuration: same code path, same tests, new name; the decider may accept it if the instance set and its limits are bounded by a validated rule (e.g. "up to 4 packs of type X"). **Observers** are open-world: they discover, record and display any type through self-describing bytes or a descriptor registry, and never feed a decision. Type in the hash, instance in the name ([[instance-in-the-name-type-in-the-hash]]).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 26262-8 change and configuration management | every change gets impact analysis; configuration items are identified | why a new type is a change and a new instance need not be |
| S-CORE FEO | topics "runtime static", messages statically typed; only matching types can be sent/received | a closed-world decider by construction |
| DDS XTypes / ROS 2 type hashes | type identity carried in discovery; non-assignable types do not match | refusal at match time, before data |
| AUTOSAR E2E Data ID | sender/receiver agree on an id bound to the message; wrong id = error | masquerade and wrong-type detection at runtime |
| iceoryx2 service attributes | type name and size must match to open a port; attributes can carry a schema hash | the local mechanism for this vault's stack |

**On the Eclipse SDV stack.** Guardian (decider): iceoryx2 or FEO ports opened against a compiled list of type hashes, refusing mismatches ([[iceoryx2-reference]]); a generated `#[repr(C)]` layout from VSS would give the hash (gap B10). Instance set and placement come from a validated placement manifest (gap C8). Evidence tap and SOVD (observers): subscribe-all on Zenoh/uProtocol (gap A5) and `include-schema` in SOVD for unknown entities ([[opensovd-overview]]). The heartbeat/fault/mitigation schema (A10) should carry a schema version in its own hash so an old Guardian refuses a new event layout.

**The trap.** Letting the evidence tap's "decode anything" convenience leak into the decider, so an unvalidated layout reaches a safety decision.

**For a hackathon team.** Start a second pack instance at runtime: the dashboard shows it, the Guardian accepts it (known type, within the bounded instance rule), and a third publisher with a changed struct is refused with a logged `unknown type` fault. Pitch: "new packs plug in; new formats need a release, and our Guardian can tell the difference".

**Evidence.** FEO typing from repos/s-core-score/docs/features/frameworks/feo/index.rst ("Communication"). iceoryx2 type matching from [[iceoryx2-reference]]. ISO 26262-8 clauses from public summaries (unverified numbering). The "bounded instance rule" is this card's proposal; no Eclipse component implements it.
