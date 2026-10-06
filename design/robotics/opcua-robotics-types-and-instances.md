---
title: OPC UA Robotics — ObjectTypes for the type, an address-space tree for the instances
type: pattern
cluster: robotics
component: none
tags: [opcua, robotics, companion-spec, objecttype, aas, information-model]
status: draft
sources:
  - https://reference.opcfoundation.org/Robotics
  - https://reference.opcfoundation.org/specs/OPC-40010-1/7.1
  - https://reference.opcfoundation.org/specs/OPC-40010-1/7
  - https://jp.opcfoundation.org/developer-tools/documents/view/218
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[opensovd-overview]]"
  - "[[vss-kuksa-overview]]"
applies-to: [opensovd, vss-kuksa]
gap-rows: [B10]
---

# OPC UA Robotics — ObjectTypes for the type, an address-space tree for the instances

**Problem.** Every robot vendor exposes axes, controllers and safety state in its own tree. A diagnostic or asset tool then needs a driver per vendor, and a newly attached device has no agreed shape.

**Forces.**
- Common vocabulary versus vendor extension.
- Read-mostly monitoring (asset, condition) versus real-time control, which OPC UA is not for.
- Browsability: clients discover instances at runtime.
- Relation to other models (AAS, VSS, SOVD).

**The rule.** The **ObjectType is the template, the instance is a node in the address space**, found by browsing from a well-known entry point. OPC 40010-1 (OPC Foundation + VDMA; v1.02, September 2025) defines `MotionDeviceSystemType` as the entry point, with folders `MotionDevices` (instances of `MotionDeviceType`: one manipulator, turntable or linear axis, with at least one axis and one power train), `Controllers` (`ControllerType`) and `SafetyStates` (`SafetyStateType`); `PowerTrainType` sits under a motion device. Vendors subtype and add. A client needs only the namespace URI `http://opcfoundation.org/UA/Robotics/` and the type definitions; it browses to find how many arms exist. Part 1 targets status monitoring and asset management, not real-time motion control.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| OPC 40010-1 Robotics | motion device system, devices, controllers, safety states as ObjectTypes | vendor-neutral browse model for robots |
| OPC UA Machinery / Devices | common identification base types (unverified exact relation) | shared asset identity |
| Asset Administration Shell | submodel templates plus instances; OPC UA mapping exists | digital-twin vocabulary above the device |
| VSS | tree with `instances` for arrays | the vehicle analogue, signal-centric |
| SOVD entity model | components with sub-components, discoverable | the diagnostics analogue |

**On the Eclipse SDV stack.** A robot or body-builder module has two views: a signal view (VSS in [[vss-kuksa-overview]]) and a structure/asset view (OPC UA or SOVD, [[opensovd-overview]]). `MotionDeviceSystem` maps naturally to a SOVD component with `MotionDevices` as sub-components; `SafetyStates` has no VSS home and should stay outside the decision path. A vspec-to-ObjectType generator is imaginable but does not exist (unverified); the mapping is the pattern, not a tool. AAS is the neighbour for lifecycle data (nameplate, documentation), which neither VSS nor SOVD carries.

**The trap.** Exposing control through the information model; the companion spec describes state and assets, and putting command loops through an OPC UA subscription gives you latency and no determinism.

**For a hackathon team.** Draw the one-slide mapping `MotionDeviceSystem -> SOVD component, MotionDevice -> sub-component, Axis -> VSS leaf` for your demo robot; build nothing. Pitch: "types for the template, browse for the instances".

**Evidence.** ObjectTypes and container folders: OPC reference pages (search snippets, verified). Version/date: OPC page (verified). Tool changer or gripper types in Part 1: none found; I found no gripper/tool-changer ObjectType (unverified, parts 2+ not searched). AAS-to-OPC UA mapping: standard knowledge, not re-fetched.
