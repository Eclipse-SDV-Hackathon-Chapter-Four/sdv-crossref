---
title: A twin is last known state and desired state, never the bus
type: pattern
cluster: fleet-cloud
component: none
tags: [digital-twin, ditto, hono, ibeji, freyja, vss, viss, vsso, dtdl]
status: draft
sources:
  - https://eclipse.dev/ditto/protocol-twinlive.html
  - https://eclipse.dev/ditto/2020-11-11-desired-properties.html
  - https://eclipse.dev/hono/docs/concepts/device-identity/
  - https://www.w3.org/TR/viss2-core/
  - https://github.com/eclipse-ibeji/freyja
last-verified: 2026-10-03
related:
  - "[[chariott-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[desired-is-a-ledger-reported-is-evidence]]"
applies-to: [chariott, vss-kuksa, sdv-blueprints, zenoh]
gap-rows: [B1]
---

# A twin is last known state and desired state, never the bus

**Problem.** Teams put a digital twin between every producer and consumer. Latency, availability and ordering of the vehicle bus now depend on a cloud database, and a sleeping vehicle looks like a broken one.

**Forces.**
- Backends want to read a vehicle that is offline.
- Operators want to write intent before the vehicle is reachable.
- Streams (10 Hz speed) and state (door locked) have different storage and retention needs.
- One schema should serve the vehicle, the twin and the dashboards.

**The rule.** A twin answers two questions: "what did the vehicle last tell us" and "what do we want it to be". It never carries the stream and never gates a control loop. Ditto says it directly: the twin channel reads "the last known state of a device without waking it up", possibly "slightly behind"; the live channel routes commands to the device when you need now. Desired properties (Ditto 1.5+) sit beside reported properties on the same Feature, so a write today and a report tomorrow converge on one record. Use VSS as the schema, one tree per vehicle, and derive twin features from it; VISS v2 already assumes "a tree-like taxonomy, typically deployed per vehicle", and a VSSo ontology can sit on top for search.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Eclipse Ditto | Thing > Features > Properties; desiredProperties; twin versus live channel; Policies | last known and desired state, per-subject access |
| Eclipse Hono | tenant + device-id, credentials, adapters | the ingestion side that feeds a twin |
| Eclipse Ibeji (DTDL) + Freyja | in-vehicle twin, cloud canonical twin, mapping service | signal-to-twin-property mapping with interval; dormant since 2024-25 |
| COVESA VSS / VISS v2 / VSSo | tree taxonomy, per-vehicle server, ontology | schema and access API; VISS has subscribe filters |
| Asset Administration Shell | submodels per asset | a non-automotive twin vocabulary |

**On the Eclipse SDV stack.**
- Ibeji/Freyja are dormant ([[chariott-overview]]); Freyja's mapping-service idea (signal A to twin property B, with transform and interval) is worth copying; its DTDL model is not VSS. A KUKSA adapter for Freyja or a Ditto feed from the fleet consumer is unbuilt.
- Cheapest twin today: the fleet-management Influx plus the rFMS server is a last-known-state store (`latestOnly=true`) with no desired-state side ([[sdv-blueprints-overview]]).
- A VSS-shaped twin: `vspec export` (json/protobuf) generates feature definitions; one Ditto Thing per VIN, one Feature per VSS branch; the vehicle's `kuksa.val.v2` `Subscribe` feeds the reported side ([[vss-kuksa-overview]]).
- Desired-side writes belong to [[desired-is-a-ledger-reported-is-evidence]]; Zenoh queryables can serve the twin read path without a database in a demo.

**The trap.** Calling the dashboard a twin, or routing actuation through it, and then explaining why the horn is slow when the cell is weak.

**For a hackathon team.** Ditto (or just a Zenoh storage) holding the last value per `fleet/<vin>/vss/**`, a dashboard reading it while the vehicle container is stopped, and a "desired" property that the vehicle picks up on reconnect. Pitch: "a twin is memory, not wiring".

**Evidence.** Twin/live and desired-properties definitions: Ditto docs (fetched). Hono identity tuple: Hono docs (fetched). VISS per-vehicle tree: W3C VISS v2 core (fetched summary). Freyja/Ibeji dormancy and mapping idea: [[chariott-overview]]. VSSo specifics not checked (unverified).
