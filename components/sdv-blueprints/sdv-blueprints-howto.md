---
title: SDV Blueprints - How-to recipes
type: howto
component: sdv-blueprints
tags: [howto,doctor-whodunit,hack-to-the-future]
status: draft
sources:
  - https://sdv-blueprints.eclipse.dev
  - https://github.com/eclipse-sdv-blueprints
  - repos/fleet-management/README.md
  - repos/service-to-signal/README.md
  - repos/software-orchestration/README.md
  - repos/companion-application/Readme.md
  - repos/e2e-vehicle-signals/README.md
  - repos/sdv_lab/README.md
  - https://api.github.com/orgs/eclipse-sdv-blueprints/repos?per_page=100
last-verified: 2026-10-03
related:
  - "[[sdv-blueprints-overview]]"
  - "[[chapter4-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[zenoh-overview]]"
  - "[[kanto-overview]]"
  - "[[velocitas-overview]]"
  - "[[symphony-overview]]"
  - "[[chapter3-retrospective]]"
---

# SDV Blueprints - How-to

## Use Fleet Management as a Doctor Whodunit scaffold (telemetry + fault evidence + dashboard)
1. Run the stack ([[sdv-blueprints-quickstart]] recipe A). Replace `csv-provider/signalsFmsRecording.csv` (format `field,signal,value,delay`, repos/fleet-management/csv-provider/) with your own recording or a fault-injected variant (e.g. brake pressure drop, DEF level 0, speed spike).
2. Add fault signals: extend the VSS overlay `spec/overlay/fms.vspec`, regenerate `vss.json` with vss-tools, mount it into the Databroker via `--metadata` (repos/fleet-management/spec/README.md). See [[vss-kuksa-overview]].
3. Forwarder: the FMS Forwarder (components/fms-forwarder, `vehicle_abstraction.rs`) subscribes only to the signals it knows; add yours there and the matching write in `fms-consumer` + `influx-client`. Transport stays uProtocol ([[uprotocol-overview]]).
4. Dashboard: copy `grafana/dashboards/FMS-Fleet.json`, add panels/annotations (Grafana provisions dashboards from the filesystem, `grafana_dashboards_from_fs.yaml`).
5. Fault evidence source: feed DTCs/events from [[opensovd-overview]] or OpenBSW diagnostics ([[openbsw-overview]]) as VSS signals through a Kuksa provider.

## Use service-to-signal as a Hack-to-the-Future scaffold (portable feature)
Feature = uService defined by protobuf (COVESA uservices) + VSS signal. Targets differ only in the *provider*: software horn (container), zenoh-pico ESP32, or your own (Android/ThreadX/Linux) subscribing to Zenoh topic `Vehicle/Body/Horn/IsActive`. Add a target by implementing a Zenoh subscriber + actuator; no change to service or client. Run containers under [[ankaios-overview]] by writing a manifest (pattern: repos/e2e-vehicle-signals/devices/raspberry-pi5/ankaios/vehicle-signals.yaml and repos/software-orchestration/eclipse-ankaios/config/startupManifest.yaml).

## Switch Fleet Management transport (Zenoh <-> Hono)
Zenoh: use the two compose files. Hono: run `./create-config-hono.sh --tenant T --device-id D --device-pwd P --provision` (Hono sandbox hono.eclipseprojects.io) then `docker compose --env-file ./config/hono/hono.env -f fms-blueprint-compose.yaml -f fms-blueprint-compose-hono.yaml up -d`. Source: repos/fleet-management/README.md. Sandbox availability unverified.

## Ankaios workload ordering pattern
Manifest `dependencies: {service_discovery: ADD_COND_RUNNING}` orders start-up; `configs` shares network name. Source: software-orchestration startupManifest.yaml. Note that newer Ankaios (0.6/0.7) changed the manifest API version - check [[ankaios-overview]] before reusing 0.5 manifests.

## Tips: first hour with blueprints
- Pre-pull images (`docker compose pull`) on venue Wi-Fi before the event; ghcr.io/quay.io pulls are many hundred MB.
- Pin image tags (`:main` moves).
- Chapter 3 lesson: pin `up-rust =0.7.0` for `up-transport-zenoh 0.8.0` (see repos/sdv_lab/README.md; [[chapter3-retrospective]]). Current blueprints use up-rust 0.9.0 + up-transport-zenoh 0.9.x - do not mix with Chapter 3 samples.
