---
title: Let the instance declare its own template
type: pattern
cluster: data-modelling
component: none
tags: [template, instance, trailer, body-builder, iso-11992, j1939, opcua, aas]
status: draft
sources:
  - https://reference.opcfoundation.org/Core/Part3/v105/docs/6.2 (ObjectTypes, ModellingRules)
  - https://sparkplug.eclipse.org/specification/ (DBIRTH)
  - https://www.iso.org/standard/ (ISO 11992 series, paywalled, unverified)
  - https://www.fms-standard.com/ (FMS standard, unverified)
  - https://industrialdigitaltwin.org/ (AAS submodel templates, unverified)
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/instances.md
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[overlays-extend-the-model-instances-stay-static]]"
  - "[[opensovd-overview]]"
applies-to: [vss-kuksa, iceoryx2, opensovd, uprotocol, zenoh]
gap-rows: [B2, C8, H2]
---

# Let the instance declare its own template

**Problem.** A trailer (ISO 11992 CAN with its own brake and axle data), a body-builder module (J1939 PGNs), or a tool the vehicle never saw before appears. The vehicle model has no branch for it, and nobody can rebuild the vehicle's VSS tree at the roadside.

**Forces.**
- The vehicle cannot know every module at build time.
- A safety consumer must not guess at a layout.
- The module's maker knows the layout best and should own the description.
- Offline and field repair mean no registry lookup can be assumed.

**The rule.** The thing that arrives carries (or points to, by hash) its own template; the host accepts it only if the template is among the layouts its consumers were built for, or routes it to generic, non-deciding consumers. Template identity is a content hash plus a name (`trailer.brake/v1#ab12`), instance identity is separate, and the arrival message pairs them. The template is the only part that is version-controlled; instances are lightweight.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| OPC UA ObjectType plus InstanceDeclaration, ModellingRule | type is the template; rules say Mandatory, Optional, Placeholder | vocabulary for "instance may add optional parts" |
| Sparkplug B DBIRTH | device publishes its metric list on arrival | template announced by the instance |
| AAS submodel templates and instances | template id referenced by the instance submodel | reference-by-id template (unverified detail) |
| J1939 address claim NAME plus PGN set | NAME identifies function; PGNs are the template | what a body builder module is on a truck |
| ISO 11992 / FMS | published fixed PGN-like message sets for tractor-trailer and fleet data | standardised templates instead of ad hoc ones (unverified) |
| DDS XTypes TypeObject | type descriptor travels in discovery | content-addressed template on the wire |

**On the Eclipse SDV stack.** There is no component for this: VSS instances are static ([[overlays-extend-the-model-instances-stay-static]]). The fitting seams: an iceoryx2 service attribute for template hash and an event-service announcement ([[iceoryx2-overview]]); a Zenoh key prefix per instance ([[zenoh-overview]]); a SOVD child component with `include-schema` ([[opensovd-reference]]). Gap C8 (placement manifest) should list which template ids a node accepts.

**The trap.** Making the vehicle's tree grow at runtime to host the new module; then every consumer needs a dynamic schema and the safety case is open-ended.

**For a hackathon team.** One template (3 signals), two instances announcing it, a consumer that refuses a third announcement with an unknown template hash and logs it. Pitch: "unknown template: refuse and record, never guess".

**Evidence.** OPC UA type and rule behaviour: fetched Part 3 6.2. Sparkplug and DDS XTypes: standard behaviour, not fetched. ISO 11992, FMS, AAS rows unverified; the "no Eclipse component exists" claim follows from the VSS Trailer branch content (a single signal) and the gap register.
