---
title: Fleet telemetry is batched at the vehicle and keyed by VIN, faults get their own leg
type: pattern
cluster: fleet-cloud
component: none
tags: [telemetry, rfms, influx, grafana, batching, downsampling, backpressure, dtc]
status: draft
sources:
  - repos/fleet-management/README.md
  - repos/fleet-management/components/fms-forwarder/src/main.rs
  - repos/fleet-management/components/fms-forwarder/src/vehicle_abstraction.rs
  - repos/fleet-management/components/influx-client/src/writer.rs
  - repos/zenoh/DEFAULT_CONFIG.json5 (downsampling, congestion_control, low_pass_filter)
last-verified: 2026-10-03
related:
  - "[[sdv-blueprints-overview]]"
  - "[[one-key-scheme-from-mcu-to-cloud]]"
applies-to: [sdv-blueprints, vss-kuksa, uprotocol, zenoh]
gap-rows: [A5, A10, B1, E3]
---

# Fleet telemetry is batched at the vehicle and keyed by VIN, faults get their own leg

**Problem.** A pipeline built for one truck replaying a CSV loses data on a flaky link, floods the cell with 10 Hz signals, and has no place for a fault code.

**Forces.**
- Cellular is metered, slow and intermittent; the vehicle must not block on it.
- rFMS-style consumers want snapshots plus trigger context, not raw streams.
- Faults are rare, high value and must not be downsampled or dropped.
- The vehicle is the only place that knows what changed.

**The rule.** Decide at the vehicle, not in the cloud: aggregate into a status message on a trigger (change, event or timer), key it by VIN, and send faults as a separate, never-dropped stream. The fleet-management forwarder shows the good half: it subscribes to databroker signals, builds a `VehicleStatus` with a `trigger` (driver login, engine on/off, telltale, parking brake, `Timer` every 5 s) and the VIN, and Influx stores `vin` and `trigger` as tags. It shows the missing half too: the channel to the publisher holds 30 messages, a failed publish is logged with `warn!` and dropped, nothing is buffered or retried, and there is no fault or DTC leg anywhere in the pipeline (FMS maps only `tellTaleInfo` to `Vehicle.Cabin.Telltale.*`).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| rFMS 4 (Volvo/Scania/etc. REST API) | vehicles, vehiclepositions, vehiclestatuses; `latestOnly` or time window | the consumer contract; no DTC resource (unverified: spec not fetched) |
| Zenoh `downsampling`, `low_pass_filter`, `congestion_control: drop/block` | per-key frequency caps and drop/block policy at the router | backpressure policy as config |
| Sparkplug B | NBIRTH metrics then NDATA on change with `seq` | report-by-exception with gap detection |
| VISS v2 | subscribe with range, history, curvelog filters | edge-side change filtering vocabulary |
| Eclipse Hono | telemetry versus event semantics, Kafka back end | durable ingestion for the must-not-lose class |

**On the Eclipse SDV stack.**
- Today's chain: CSV Provider, KUKSA Databroker 0.6.0 (FMS overlay `spec/overlay/vss.json`), FMS Forwarder, uProtocol over Zenoh or Hono, FMS Consumer, InfluxDB, Grafana plus FMS Server on :8081 ([[sdv-blueprints-overview]]).
- Backpressure over cellular: set Zenoh `congestion_control: drop` on the telemetry key and `block` on the fault key, and add a downsampling rule at the uplink router for raw `vss/**` keys (config is commented-out in DEFAULT_CONFIG.json5, verified syntax only).
- Fault leg (gap): DTC or OpenSOVD fault, then a VSS overlay branch `Vehicle.Diagnostics.DTCList`, then a `fault` trigger on the same `VehicleStatus`, then an Influx annotation and a Grafana panel. Reuse A5 (evidence tap) and the A10 event schema.
- Open bugs that corrupt the series: #71 time unit, #72/#74 heading/altitude types (E3).

**The trap.** Sending every signal at source rate and reconstructing events in Grafana; faults then arrive late, downsampled, or not at all.

**For a hackathon team.** Keep the forwarder, add a `fault` trigger fed by a button or an OpenBSW DTC, show the fault arriving with the last 5 s of snapshot while the "uplink" is throttled with `tc netem`. Pitch: "the vehicle decides what is worth the bytes".

**Evidence.** Forwarder behaviour, 30-slot channel, warn-and-drop, 5 s timer: repos/fleet-management/components/fms-forwarder/src/main.rs and vehicle_abstraction.rs. README says "uProtocol Notification" but the code uses `SimplePublisher::publish`, which is a Publish message. Influx tags: influx-client writer.rs. Downsampling and congestion options: DEFAULT_CONFIG.json5. rFMS spec text not checked; web search returned no primary source (unverified).
