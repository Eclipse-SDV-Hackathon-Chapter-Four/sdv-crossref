---
title: Coherence is a set property, declared in the model
type: pattern
cluster: data-modelling
component: none
tags: [coherence, atomic, struct, aggregate, dds, autosar, sovd, groups]
status: draft
sources:
  - repos/vehicle_signal_specification/docs-gen/content/rule_set/data_entry/data_types_struct.md
  - repos/vss-tools/docs/avro.md
  - https://www.omg.org/spec/DDS/1.4/ (PRESENTATION QoS coherent_access, access_scope; KEY)
  - https://www.autosar.org/ (SignalGroup, I-signal group, update bit; unverified details)
  - repos/components opensovd-reference (data-lists, data-groups)
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[opensovd-reference]]"
  - "[[a-reading-carries-what-it-is-worth]]"
applies-to: [vss-kuksa, iceoryx2, opensovd]
gap-rows: [B10, H1, A8]
---

# Coherence is a set property, declared in the model

**Problem.** Latitude, longitude and heading were read at three different instants and the vehicle appears to teleport; or three phase currents from three cycles feed one power calculation.

**Forces.**
- Independent signals are what makes VSS composable; atomicity breaks that.
- Transports differ: one frame, one shared-memory struct, many topics.
- Consumers cannot discover which signals belong together from names alone.

**The rule.** Whether signals must be read at the same instant is a property of the *set*, so declare the set once in the model and let every transport honour it, rather than rediscover it per consumer. Correction to the usual claim that VSS has no grouping primitive: it has two. A **struct** datatype (all members mandatory, "read or written in an atomic operation", not a serialisation promise) and a branch keyword **`aggregate`**, which the VSS docs themselves call ill-defined, unused in the catalog, and allowed only as a deployment-level overlay hint. Prefer a struct for a coherent measurement; use `aggregate` in an overlay only when the producer is already a single frame.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| VSS struct / `aggregate` | atomic read/write of a typed set; `aggregate` as overlay-only deployment hint | the model-level declaration |
| DDS PRESENTATION QoS | `coherent_access` with `access_scope` TOPIC or GROUP; KEYed topics for instances | a transport that guarantees the set |
| AUTOSAR SignalGroup and update bit | signals in one PDU are updated together | coherence tied to one frame (unverified) |
| SOVD `data-lists`, `data-groups` | read several data resources in one request | request-level grouping, not model-level |
| iceoryx2 | one sample is one struct, so a struct is coherent by construction | the cheapest coherent set |

**On the Eclipse SDV stack.** The databroker stores signals independently; a struct signal is not a coherent set across `Vehicle.CurrentLocation.*` leaves ([[vss-kuksa-overview]]). In iceoryx2 ([[iceoryx2-overview]]) the exporter in gap B10 should emit one `#[repr(C)]` struct per declared set, with the set name in the service name. In OpenSOVD map the set to a `data-list` ([[opensovd-reference]]); H1 cyclic subscriptions would then stream a coherent list.

**The trap.** Mixing sensors, attributes and actuators in one `aggregate` branch: the VSS docs say the semantics are then ambiguous.

**For a hackathon team.** Show a torn read: three separate publishes yield an inconsistent triple; one struct sample does not. Pitch: "coherence is declared, not hoped for".

**Evidence.** Struct and `aggregate` text read verbatim in data_types_struct.md. SOVD data-lists listed in opensovd-reference. DDS and AUTOSAR rows from standard behaviour, not fetched (the DDS PDF fetch returned binary), unverified.
