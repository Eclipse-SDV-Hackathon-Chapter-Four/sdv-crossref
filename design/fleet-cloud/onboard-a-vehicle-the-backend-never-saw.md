---
title: Onboard a vehicle the backend never saw by templates, not by registration
type: pattern
cluster: fleet-cloud
component: none
tags: [vin, onboarding, templates, instances, vss, provisioning, hono, ditto]
status: draft
sources:
  - repos/fleet-management/components/influx-client/src/writer.rs
  - repos/fleet-management/components/fms-server/src/influx_reader.rs
  - https://eclipse.dev/hono/docs/concepts/device-identity/
  - https://sparkplug.eclipse.org/specification/ (NBIRTH metric set)
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[a-vehicle-is-gone-when-its-death-certificate-says-so]]"
  - "[[a-twin-is-last-known-state-not-a-bus]]"
applies-to: [vss-kuksa, sdv-blueprints, zenoh, uprotocol, symphony]
gap-rows: [C8, B1]
---

# Onboard a vehicle the backend never saw by templates, not by registration

**Problem.** The backend needs a dashboard, a twin and a rollout target for vehicle number 1001, which nobody pre-registered, and VSS has no vehicle id in its paths.

**Forces.**
- A VIN is known only at the vehicle (`Vehicle.VehicleIdentification.VIN`).
- Pre-registration scripts do not scale and break on swapped ECUs.
- Variants differ (axles, trailer, extra sensors); one fixed tree fits none.
- Security wants a vehicle to prove it is who it says before it creates state.

**The rule.** The vehicle announces `(vin, model-id, schema-hash)` in its birth; the backend instantiates from a template keyed by `model-id`. Types live in the backend (VSS tree plus overlay, dashboard JSON, Ditto Thing definition); instances are created on first authenticated birth and named by VIN. Unknown model-id: park the vehicle in a quarantine namespace with read-only evidence, do not guess. This is [[instance-in-the-name-type-in-the-hash]] one level up.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Sparkplug NBIRTH | birth carries the full metric list | the backend learns the type from the vehicle |
| Eclipse Hono | tenant + device, auto-provisioning of gateway-connected devices (unverified in detail) | registration without a human step |
| Eclipse Ditto | Thing created from a model/definition reference | template to instance |
| Grafana variables | a `vin` template variable over a tag | one dashboard, N vehicles |
| VSS `instances` | static arrays of a branch | the in-vehicle case only |

**On the Eclipse SDV stack.**
- fleet-management already does the cheap version: the consumer ignores a status with an empty VIN, otherwise writes tags `vin` and `trigger`; the rFMS `vehicles` list is "distinct vin tag values" ([[sdv-blueprints-overview]]). Nothing registers a vehicle; the first message creates it. Missing: any check that the sender may claim that VIN ([[per-vehicle-credentials-audience-is-the-vin]]).
- COOTA (Chapter 3) hard-coded `-e VIN=VIN25555` in a Symphony Target per vehicle and one shared `coa-request` MQTT topic; that is registration by script ([[chapter3-retrospective]]).
- Template side: ship the FMS VSS overlay as the type, a Grafana dashboard variable on `vin`, and a Symphony Solution as the software template; each vehicle is a Symphony Target created on first birth ([[symphony-overview]]).

**The trap.** Encoding the VIN in the VSS path (`Vehicle.<VIN>.Speed`), which turns every vehicle into a new type and orphans every dashboard.

**For a hackathon team.** Start a third vehicle container with a new VIN while the demo runs; the dashboard variable lists it and a Target appears with no script. Pitch: "the first heartbeat is the registration form".

**Evidence.** Tag/VIN handling: influx-client writer.rs lines 260-302 and fms-server influx_reader.rs. COOTA VIN env and shared topic: repos/hc3-COOTA/campaign/fleet-1-target.json and multi-vehicle/. Hono auto-provisioning claim unverified.
