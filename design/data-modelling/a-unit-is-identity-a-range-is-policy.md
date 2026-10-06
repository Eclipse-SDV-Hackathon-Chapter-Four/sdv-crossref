---
title: A unit is part of identity, a range is policy
type: pattern
cluster: data-modelling
component: none
tags: [vss, units, quantities, qudt, ucum, identity]
status: draft
sources:
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/data_entry/data_units.md
  - repos/vehicle_signal_specification/spec/units.yaml, spec/quantities.yaml
  - repos/vss-tools/src/vss_tools/utils/idgen_utils.py
  - https://ucum.org/ucum
  - https://qudt.org
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-reference]]"
  - "[[the-conversion-rule-is-part-of-the-type]]"
  - "[[derive-ids-from-layout-not-from-prose]]"
applies-to: [vss-kuksa, iceoryx2]
gap-rows: [B10]
---

# A unit is part of identity, a range is policy

**Problem.** Two services both publish `Vehicle.Speed` as a `float`, one in km/h, one in m/s. Nothing in the bytes tells them apart and the dashboard is wrong by 3.6.

**Forces.**
- A bare number is not a value; unit and quantity decide what it means.
- A range ("0..250") is a property of a vehicle or a safety goal and changes with calibration.
- Conversion tables in the model invite divergent implementations.

**The rule.** The unit is identity: a different unit is a different signal (new id), because every consumer would misread it. The range is policy: widening or tightening it must not re-mint identity unless it changes the storage type. VSS agrees on the first half: `unit` is validated against `units.yaml`, and each unit names a `quantity` (`velocity` for km/h and m/s) so a consumer *may* convert, but VSS "does not specify conversion factors". It also says the unit "does not imply" how the value is sent, but that protocols without units "expect `Vehicle.Speed` as `km/h`" without scale or offset.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| VSS `units.yaml` / `quantities.yaml` | unit has `quantity`, `allowed-datatypes`, optional QUDT mapping (6.1) | closed vocabulary; deprecation of units |
| QUDT | units and quantity kinds as linked data with conversion multipliers | the conversion table VSS refuses to carry |
| UCUM | machine-parseable case-sensitive unit codes (`km/h`, `m/s`) | an unambiguous wire string if you must send one |
| OPC UA EngineeringUnits (UNECE codes) and EURange | unit as property, range as a separate property | same split: range is data, not type |
| DTDL semantic types and units | `Velocity` semantic type with `unit` | unit is checked at model time |
| ROS 2 REP 103 | SI units mandatory by convention | agree one unit, no conversion at all |

**On the Eclipse SDV stack.** [[vss-kuksa-reference]]: the databroker stores the number and metadata; it does not convert. A generated iceoryx2 layout ([[iceoryx2-overview]], gap B10) should carry unit as a type-hash input and enforce range at the producer. Caveat found in the code: vss-tools `vspec export id` hashes `min` and `max` (see [[derive-ids-from-layout-not-from-prose]]), so a COVESA range change does re-mint a static id; your own layout hash should not.

**The trap.** Picking the unit "later, per consumer": it works until two consumers pick different ones.

**For a hackathon team.** Pick SI in the layout, put the unit string in the iceoryx2 service attributes, and refuse a subscriber whose attribute differs. Pitch: "unit mismatch is a refused connection, not a wrong number".

**Evidence.** Quotes: data_units.md (read). `min`/`max` in hash: idgen_utils.py (read). OPC UA EngineeringUnits/EURange and DTDL semantic types: stated from the specs without a page fetch (unverified).
