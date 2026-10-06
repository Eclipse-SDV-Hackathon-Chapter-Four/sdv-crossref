---
title: VDA 5050 — a self-describing fleet member: factsheet, state, last will
type: pattern
cluster: robotics
component: none
tags: [vda5050, agv, mqtt, last-will, factsheet, birth-certificate, fleet]
status: draft
sources:
  - https://github.com/VDA5050/VDA5050
  - https://raw.githubusercontent.com/VDA5050/VDA5050/main/VDA5050_EN.md
  - https://sparkplug.eclipse.org/specification/
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[uprotocol-overview]]"
  - "[[zenoh-overview]]"
applies-to: [uprotocol, zenoh, symphony]
gap-rows: [C8, B1]
---

# VDA 5050 — a self-describing fleet member: factsheet, state, last will

**Problem.** A fleet controller must drive AGVs from several vendors that join and leave at will, over a flaky wireless link, without per-vendor integration.

**Forces.**
- Vendors differ in kinematics, load handling and actions.
- Links drop; orders must be replayable safely.
- The controller must know whether a silent vehicle is dead or just quiet.
- Open interface, closed vehicle internals.

**The rule.** Each vehicle owns a topic subtree `interfaceName/majorVersion/manufacturer/serialNumber/<topic>` (the **instance in the topic name**), and speaks six topics: `order`, `instantActions`, `state`, `visualization`, `connection`, `factsheet`. The **factsheet** is the type: physical properties, load specs and supported actions. The **connection** topic (retained, QoS 1) carries `ONLINE`/`OFFLINE`, with a **last-will** set at connect to `CONNECTION_BROKEN`, so absence is announced by the broker. `state` is published on events and at least every 30 s. Orders are node/edge graphs with `orderId` plus `orderUpdateId`, and a *released base* vs unreleased *horizon*; an update repeats the last base node, making delivery idempotent over a lossy link.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| VDA 5050 (VDA/VDMA) | topic-per-vehicle, factsheet, retained connection + LWT, order updates | the mature "dynamic member with self-description" in logistics |
| Sparkplug B | NBIRTH/DBIRTH template, NDEATH via last will | the same pattern in industrial IoT |
| J1939 address claim | NAME as identity | bus-level equivalent |
| MQTT 3.1.1/5 LWT, retained messages | broker-announced death | liveness without heartbeat polling |
| OPC UA Robotics | MotionDeviceSystem instances | the browse-model alternative (see sibling card) |

**On the Eclipse SDV stack.** A vehicle is the same shape as an AGV: identity in the topic or UUri authority, capabilities in a factsheet-like announcement, liveness in a retained will. [[uprotocol-overview]] has the Zenoh/MQTT5 mapping where `authority_name` is the vehicle/vendor instance; the uStreamer to MQTT5 route is how a VDA-style broker would see it. Missing is a uProtocol "factsheet" resource: a retained message listing which resources and types this entity serves (relates to C8/B1). For a trailer-coupled truck, a VDA-style `order` for the trailer's own movements is a ready command model. Note: spec version on main is 3.0.0; most deployed fleets are 2.x, and the `connection` strings differ in spelling between versions (`CONNECTIONBROKEN` in 2.x, `CONNECTION_BROKEN` in 3.0; 2.x spelling unverified).

**The trap.** Using the last will as the only liveness signal: a vehicle that is connected but frozen never triggers it, so `state` age must also be watched.

**For a hackathon team.** Publish a retained `connection=ONLINE` plus a one-page factsheet for a simulated trailer, set the will, kill the process, show the controller reacting to `CONNECTION_BROKEN` and then to a state-age timeout. Pitch: "birth certificate, will, and a release horizon".

**Evidence.** Topics, QoS, connection states, 30 s rule, order/horizon: VDA5050_EN.md main (verified). Sparkplug comparison: sparkplug spec (standard knowledge, not re-fetched).
