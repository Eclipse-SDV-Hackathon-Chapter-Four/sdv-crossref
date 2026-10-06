---
title: Overlays extend the model, but instances stay static
type: pattern
cluster: data-modelling
component: none
tags: [vss, overlays, instances, trailer, body-builder, extension]
status: draft
sources:
  - https://covesa.github.io/vehicle_signal_specification/extensions/overlay/ (repos/vehicle_signal_specification/docs-gen/content/extensions/overlay.md)
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/instances.md
  - repos/vehicle_signal_specification/overlays/README.md and overlays/profiles/motorbike.vspec
  - repos/vehicle_signal_specification/spec/Vehicle/Vehicle.vspec (Trailer branch, lines 472-481)
  - repos/vss-tools/docs/compose.md
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-overview]]"
  - "[[vss-kuksa-howto]]"
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[let-the-instance-declare-its-own-template]]"
applies-to: [vss-kuksa, sdv-blueprints]
gap-rows: [A11, B10, C8]
---

# Overlays extend the model, but instances stay static

**Problem.** A team needs `Row[1,3]` seats, a thermal-runaway flag or a motorbike tree. Forking VSS gives merge pain; assuming overlays can also describe "whatever coupled at runtime" gives a model that is silently wrong the first time a trailer arrives.

**Forces.**
- The catalog is a typical passenger car (two rows, two axles); real vehicles differ.
- Deployment data (source ECU, interval, CAN signal) must live somewhere that does not touch the catalog.
- `instances` expand at tool run time into plain nodes; the broker sees a flat static tree.
- Vehicles change shape at runtime (trailers, body modules) and VSS has no event for it.

**The rule.** Extend by overlay (add, delete, change metadata, add keys, glob keys, ordered layers), never by fork; and treat every overlay as a compile-time statement about one vehicle configuration. Overlays can change *how many* instances exist (`Vehicle.Cabin.Door: instances: [Row[1,3], ...]`, last definition wins; 6.1 adds `instances_relation: sibling`, which the 6.x catalog deliberately does not use until 7.0) but not *whether one appears while driving*. Anything whose existence is a runtime fact needs a template that is instantiated by announcement, see [[let-the-instance-declare-its-own-template]].

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| VSS overlays (`-l`, wildcard keys, `delete: true`) | ordered layers merged before export | add or prune per vehicle; `Vehicle.Speed: {unit: m/s}` patches one field |
| `overlays/profiles/motorbike.vspec` | profile = large overlay reshaping instances | shows the mechanism; README says "examples only, not part of the official specification" |
| `network_serialization` and `cybersecurity` profiles | schema'd extension keys under a node | standard place for deployment data (see mapping card) |
| `vspec compose` (6.1) | snapshot of vspec + overlays + units into one folder | the "this exact configuration" artefact to hash and archive |
| OPC UA ModellingRule (Optional, Placeholder) | the type itself says an instance may be absent or repeat | what VSS `instances` lacks: runtime multiplicity |
| DTDL Component / Relationship | by-value composition vs by-reference link | a trailer is a Relationship, not a baked-in branch |

**On the Eclipse SDV stack.** [[vss-kuksa-overview]]: the databroker loads one expanded JSON tree, so overlays are applied before `vspec export json -l overlay.vspec` and the instance set is frozen at start; a trailer needs a restart or a second tree. `Vehicle.Trailer` in VSS 6.1 holds a single signal, `Trailer.IsConnected` (verified in the spec file): nothing about axles, brakes or ISO 11992. Overlay recipe: [[vss-kuksa-howto]] section 6. Gap A11 (thermal runaway, child presence) is the overlay case that works today.

**The trap.** Reading "overlay" as "dynamic": an overlay changes the compiled tree, it cannot make an instance appear.

**For a hackathon team.** Ship one overlay file (new branch plus a `delete: true` trim) and show the same app running unmodified against two overlay sets. Pitch: "we never forked VSS; the vehicle is the catalog plus three layers".

**Evidence.** Overlay features, wildcard and delete: overlay.md. Instances, redefinition and 6.1 sibling relation: instances.md. Trailer branch content: Vehicle.vspec. No "deployment file" concept exists in VSS 6.1; the docs say deployment data goes in overlays and profiles (extensions/_index.md). Whether VSS 7 adds one: unverified.
