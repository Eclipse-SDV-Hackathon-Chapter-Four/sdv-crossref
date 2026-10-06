---
title: The conversion rule is part of the type
type: pattern
cluster: data-modelling
component: none
tags: [dbc, scale, offset, fixed-point, raw, physical, vss]
status: draft
sources:
  - repos/vehicle_signal_specification/docs-gen/content/extensions/network_serialization_profile.md
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/data_entry/data_units.md
  - https://www.autosar.org/ (COMPU_METHOD in ARXML, unverified details)
  - https://www.sae.org/standards/content/j1939da_202309/ (SPN resolution and offset, unverified)
last-verified: 2026-10-03
related:
  - "[[mappings-are-overlays-the-source-model-stays-pristine]]"
  - "[[a-unit-is-identity-a-range-is-policy]]"
  - "[[a-reading-carries-what-it-is-worth]]"
applies-to: [vss-kuksa, openbsw, iceoryx2]
gap-rows: [B6, B10]
---

# The conversion rule is part of the type

**Problem.** The same 8 raw bits are 0..5 V on the DBC (`(0.02,0)`), -100..+100 percent in VSS (`floor(x*40-100)`), and 250 in the frame. Change the factor and every archived raw value is wrong, but the signal name did not change.

**Forces.**
- Wire formats use fixed-point to save bytes; models want physical values.
- Raw and physical must both be reconstructible for diagnostics and replay.
- Putting conversion in each consumer guarantees disagreement.

**The rule.** Convert exactly once, at the boundary where a wire layout meets the model, and make the rule (factor, offset, bit length, endianness, special codes) part of the *wire* type identity; the model sees physical values only. VSS is physical-only by design: no scale or offset, and DBC's own factor/offset is applied by the provider before the mapping's `transform` (math uses `x` as the physical DBC value). A change of factor or offset re-mints the wire type id even if the VSS signal is unchanged; a change of physical meaning re-mints the VSS signal.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| DBC `SG_ name : start|len@order sign (factor,offset) [min|max] "unit"` | linear conversion with the bit layout | the canonical raw-to-physical rule, per frame |
| AUTOSAR COMPU_METHOD | conversion as a named element (linear, text table) | the same rule reusable across signals (unverified) |
| J1939 SPN | resolution and offset per SPN, reserved top codes | conversion plus validity in one definition |
| VSS network serialization `transform` | math and representation tables in an overlay | conversion lives in the mapping, not the catalog |
| OPC UA | AnalogItemType holds physical value, range and unit as properties | physical on the wire, conversion in the server |

**On the Eclipse SDV stack.** [[vss-kuksa-howto]] section 7 (CAN provider) is where conversion happens in practice; a zero-copy layout from [[iceoryx2-overview]] should carry physical `f32`/`i16` for HPC consumers and, if raw is needed, a separate raw layout with its own type hash. Gap B6/B10.

**The trap.** Two conversions in series: the provider applies the DBC factor and the VSS mapping applies it again.

**For a hackathon team.** Replay one candump, print raw, DBC-physical and VSS-physical side by side for one signal. Pitch: "one conversion, named, versioned".

**Evidence.** Mirror example (0.02 factor, `floor((x*40)-100)`): network_serialization_profile.md. "No conversion factors": data_units.md. AUTOSAR and J1939 rows unverified.
