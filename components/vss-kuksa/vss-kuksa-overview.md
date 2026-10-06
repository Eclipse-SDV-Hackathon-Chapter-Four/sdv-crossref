---
title: COVESA VSS + Eclipse KUKSA overview
type: overview
component: vss-kuksa
tags: [vss, kuksa, databroker, grpc, vehicle-data, signals]
status: verified
sources:
  - repos/vehicle_signal_specification/CHANGELOG.md
  - repos/vss-tools/CHANGELOG.md
  - repos/kuksa-databroker/README.md
  - repos/kuksa-databroker/doc/protocol.md
  - repos/kuksa-databroker/doc/user_guide.md
  - https://github.com/eclipse-kuksa/kuksa-databroker/releases
  - https://github.com/eclipse-kuksa
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-quickstart]]"
  - "[[vss-kuksa-howto]]"
  - "[[vss-kuksa-reference]]"
  - "[[vss-kuksa-integration-notes]]"
  - "[[chapter4-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# COVESA VSS + Eclipse KUKSA

Repos looked at (shallow clones, 2026-10-03):

| repo | commit | date |
|---|---|---|
| repos/vehicle_signal_specification | 9236923 | 2026-09-29 (master, after v6.1) |
| repos/vss-tools | 5e21856 | 2026-09-29 (master, 7.0.0-dev0) |
| repos/kuksa-databroker | 7a210d0 | 2026-09-18 (master, 0.7.2-dev.0) |
| repos/kuksa-python-sdk | 08a6ec5 | 2026-08-26 |
| repos/kuksa-proto | 28bf76a | 2026-08-25 (the databroker's `proto/` submodule) |

## What it is
- **VSS (COVESA Vehicle Signal Specification)**: a *data model*, not software. It is a tree of named vehicle signals (`Vehicle.Speed`, `Vehicle.Cabin.Seat.Row1.DriverSide.IsBelted`), written as YAML `.vspec` files. Each leaf has a `type` (`sensor`, `actuator`, `attribute`), a `datatype`, and optionally `unit`, `min`/`max`, `allowed`, `default`. Since 6.1 it also has `enum`. Branches can be *instantiated* (`Row[1,2]` × `["DriverSide","Middle","PassengerSide"]`). Sources: repos/vehicle_signal_specification/spec/, repos/vehicle_signal_specification/docs-gen/content/rule_set/.
- **vss-tools** (`vspec` CLI, Python ≥3.11): validates the `.vspec` tree, applies **overlays** (`-l`), and exports it to json, csv, yaml, protobuf, ddsidl, jsonschema, go, samm, plantuml, ros2interface, avro, vhal, apigear, binary, franca, id and s2dm. The standalone `graphql` exporter was **removed in 6.0** and GraphQL output now comes from `s2dm`. Sources: repos/vss-tools/src/vss_tools/cli.py, repos/vss-tools/CHANGELOG.md, and `vspec export --help` on vss-tools 6.1.0.
- **Eclipse KUKSA Databroker**: a Rust gRPC server that holds the live values of a VSS tree in memory. Applications read values and subscribe to changes. *Providers* (feeders) publish sensor values and execute actuation requests. The statically built binary is under 4 MB, Apache-2.0 (repos/kuksa-databroker/README.md). It loads a VSS **JSON** file at start-up. The image ships `vss_release_6.0.json` as its default (`KUKSA_DATABROKER_METADATA_FILE`; observed in the image config).
- **Clients**: `databroker-cli` (Rust, in the databroker repo), `kuksa-client` (Python SDK + interactive CLI, PyPI `kuksa-client` 0.6.0), plus Rust, Java and Android SDKs of varying maturity (see [[vss-kuksa-reference]]).
- **Providers**: kuksa-can-provider (DBC↔VSS), kuksa-csv-provider (replays a CSV), kuksa-someip-provider, kuksa-dds-provider, kuksa-gps-provider, kuksa-mock-provider, and a Zenoh provider in kuksa-incubation.

## What it is NOT
- VSS is not a protocol or transport. It defines names and semantics only. KUKSA, VISS, uProtocol, DDS and others carry the values.
- The databroker does **not persist** values (memory only; repos/kuksa-databroker/doc/protocol.md) and has no history or time series.
- The databroker does **not** talk CAN or SOME/IP. A provider does that.
- KUKSA does **not** guarantee that an actuation happened. It "only forwards actuator values from the Signal Consumer to the vehicle network" (doc/user_guide.md).
- It is not safety-certified. It is fine for a demo, but it is not an ASIL path for a thermal-runaway warning. Say this explicitly in a Doctor Whodunit evidence chain.
- The old `kuksa.val` C++ server and `kuksa.val.feeders` are archived and should not be used (per the integration research and the eclipse-kuksa org page).

## Maturity and versions (as of 2026-10-03)
- **VSS 6.1**, released 2026-09-17 (tag v6.1, GitHub releases API). 6.1 adds: QUDT unit references, an `enum` keyword (integer base type), a changed GraphQL output, and signals for torque, oil pressure, road-surface conditions, vehicle orientation and air quality. **VSS 6.0** (2026-01-16) removed the `Vehicle.OBD` branch (now an overlay), added the `pattern` keyword, renamed `celsius`→`Celsius`, refactored the seat signals (breaking), and added Vehicle Health Management (`Vehicle.ControlUnit.*.Health`). Source: repos/vehicle_signal_specification/CHANGELOG.md.
- **vss-tools 6.1**: adds `vspec compose` / `vspec diff`, the avro and vhal exporters, and QUDT. Python ≥3.11 (repos/vss-tools/CHANGELOG.md).
- **KUKSA Databroker 0.7.1** (2026-08-26). 0.7.0 (2026-07-03) **removed `sdv.databroker.v1`**. 0.6.1 fixed a JWT scope bypass on the v2 provider stream. 0.5.0 (2024-11-26) introduced `kuksa.val.v2`. Source: https://github.com/eclipse-kuksa/kuksa-databroker/releases.
- Self-declared maturity on the eclipse-kuksa org README (integration research, unverified wording): databroker, python-sdk and can-provider are "Production". csv/dds/gps providers are Beta. android-sdk, someip-provider and mock-provider are Alpha. java-sdk and rust-sdk are Pre-alpha.

## Languages, APIs, transports
- gRPC over HTTP/2 on TCP **55555** by default (`--port`, `KUKSA_DATABROKER_PORT`), or a Unix socket (`--enable-unix-socket`, `/run/kuksa/databroker.sock`).
- Services: **`kuksa.val.v2.VAL`** (recommended, the only one still developed) and **`kuksa.val.v1.VAL`** (deprecated, still enabled). **`sdv.databroker.v1`** was removed in 0.7.0. The `databroker-cli` 0.7.1 still lists `sdv.databroker.v1` as a protocol option, which is a trap.
- **VISS v2** over WebSocket on port 8090. It needs a build with the `viss` feature and the `--enable-viss` flag, and has no TLS (doc/protocol.md).
- Value semantics: v1 has *current* and *target* values. v2 has a single *data value* plus an *actuation* channel that goes to a registered provider. The two "wanted value" channels are separate (verified, see [[vss-kuksa-howto]]).

## Relevance to Chapter 4
- **Doctor Whodunit (Battery Thermal Guardian)**: VSS 6.0/6.1 already has `Vehicle.Powertrain.TractionBattery.Temperature.{Average,Min,Max,CellTemperature}`, `BatteryConditioning.*`, `Charging.Temperature`, `DCDC.Temperature`, `StateOfHealth`, `ErrorCodes`, `Vehicle.Diagnostics.DTCList`, and `Vehicle.ControlUnit.*.Health.*` (watchdog/deadline flags), which fit a "stuck signal" detector. There is **no standard thermal-runaway / thermal-event signal**, so add one with an overlay. The challenge text says openDuT injects "stuck or implausible VSS signals" (https://opendut.eclipse.dev/, unverified against the primary page).
- **Hack to the Future (child presence "Guardian Loop")**: VSS has `Vehicle.Cabin.Seat.RowX.Pos.OccupancyStatus` (`UNKNOWN|OCCUPIED|EMPTY`, since the 6.0 seat refactor; the old boolean `IsOccupied` is gone), `IsBelted`, `Vehicle.Occupant.*` (identifier, head position, gaze), `Vehicle.Cabin.HVAC.AmbientAirTemperature`, door/window/lock actuators, `Vehicle.Body.Horn.IsActive`, `Vehicle.Body.Lights.Hazard.IsSignaling`, and the parked-state proxies `Vehicle.IsMoving`, `Vehicle.Speed`, `Vehicle.Chassis.ParkingBrake.IsEngaged` and `Vehicle.LowVoltageSystemState` (`LOCK|OFF|ACC|ON|START`). There is **no `ChildPresence` / CPD branch and no `IsParked`**, so add them with an overlay (recipe in [[vss-kuksa-howto]]). Full table in [[vss-kuksa-reference]].
- Both challenges name uProtocol as the transport for events. KUKSA is listed among the Chapter 4 projects (repos/hackathon-ch4-dotgithub/profile/README.md:49) but is not mandated. A common pattern is "KUKSA = vehicle-signal state store, uProtocol = service/event bus".

## Pros
- Fastest way to get a realistic, standardized vehicle data plane: one container, about 1,260 standard signals preloaded, and set/get within minutes (verified).
- A shared vocabulary between teams and projects. VSS names show up in openDuT fault campaigns, SDV Blueprints, Android VHAL and ROS 2 exports.
- Built-in type, min/max and `allowed` validation and fine-grained JWT scopes. The verifier guards against algorithm confusion, but `aud` is hard-coded to `kuksa.val` (a TODO in the code), so there is no per-vehicle audience ([[verify-offline-against-a-pinned-root]]).
- Small, Rust, runs as a container, so it drops straight into Ankaios (proven in Chapter 3 by ArBytesMoral).

## Cons / when not to use
- API churn: three gRPC APIs, CLI and SDK lag (databroker-cli cannot speak v2, the Python SDK has no v2 `Actuate`), and many blog posts and blueprints are pinned to 0.4.x/0.6.0.
- Not a pub/sub bus for arbitrary events or services. Use uProtocol or Zenoh for fault/heartbeat/mitigation events and keep KUKSA for the *state* of signals.
- No persistence, no history, no QoS guarantees, not safety-certified.
- On a microcontroller (OpenBSW/ThreadX), gRPC/HTTP2 is heavy. Bridge via Zenoh (kuksa-incubation zenoh provider) or CAN (can-provider).

## Hackathon ideas (gaps and small contributions)
1. **Signal-freshness watchdog** for the Battery Thermal Guardian: subscribe to `TractionBattery.Temperature.*` over v2, detect stuck, stale or implausible values, and raise a uProtocol fault event and a DTC visible through OpenSOVD. This directly matches the challenge's "stale or stuck cell-temperature signal" hazard.
2. **VSS overlays for CPD and thermal runaway**, contributed upstream to COVESA as a proposal (`Vehicle.Cabin.ChildPresence.*`, `TractionBattery.Temperature.IsThermalRunawayWarning`).
3. **VSS→SOVD data mapping**: no evidence of an existing mapping was found (repos/opensovd-* contain no VSS/KUKSA references). A small adapter exposing selected VSS signals as SOVD `data` resources is a real gap.
4. **KUKSA↔uProtocol bridge** (up-kuksa): only the service-to-signal blueprint's horn service exists. A generic VSS-signal-to-uProtocol-topic streamer is missing.
5. **Same service code on virtual and hardware**: on a laptop, the CSV or mock provider feeds the databroker. On hardware, the CAN provider feeds it with the same VSS names. This is the core of "Hack to the Future".
6. Small upstream fixes: v2 support in databroker-cli, `Actuate` in the Python SDK, and a refreshed Ankaios tutorial image (it still uses `ghcr.io/eclipse/kuksa.val/databroker:0.4.1`).
