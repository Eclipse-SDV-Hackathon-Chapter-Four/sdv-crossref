---
title: VSS + KUKSA reference (APIs, images, signals, pitfalls, links)
type: reference
component: vss-kuksa
tags: [vss, kuksa, reference, grpc, docker, signals, pitfalls]
status: verified
sources:
  - repos/kuksa-proto/kuksa/val/v2/val.proto
  - repos/kuksa-proto/kuksa/val/v1/val.proto
  - repos/kuksa-databroker/doc/protocol.md
  - repos/kuksa-databroker/doc/user_guide.md
  - repos/kuksa-databroker/data/vss-core/vss_release_6.0.json
  - repos/vehicle_signal_specification/spec/Cabin/Seat.vspec
  - repos/vehicle_signal_specification/CHANGELOG.md
  - repos/vss-tools/src/vss_tools/cli.py
  - https://github.com/eclipse-kuksa/kuksa-databroker/releases
  - https://github.com/eclipse-kuksa
  - https://covesa.github.io/vehicle_signal_specification/
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-overview]]"
  - "[[vss-kuksa-quickstart]]"
  - "[[vss-kuksa-howto]]"
  - "[[vss-kuksa-integration-notes]]"
---

# VSS + KUKSA reference

## Versions (2026-10-03)
| Thing | Current | Date | Source |
|---|---|---|---|
| VSS | v6.1 (6.0: 2026-01-16) | 2026-09-17 | GitHub releases API; repos/vehicle_signal_specification/CHANGELOG.md |
| vss-tools (PyPI `vss-tools`) | 6.1.0 (master 7.0.0-dev0) | 2026 | `pip show vss-tools`; repos/vss-tools/pyproject.toml |
| KUKSA databroker / databroker-cli | 0.7.1 | 2026-08-26 | tag date; `databroker --version` |
| kuksa-client (Python SDK + CLI) | 0.6.0 | 2026-08 | `pip show`, image label |
| Default VSS tree in databroker image | `vss_release_6.0.json` (≈1,263 leaves) | n/a | image env `KUKSA_DATABROKER_METADATA_FILE`; repos/kuksa-databroker/data/vss-core/ |

The databroker image does **not** yet ship VSS 6.1. Generate 6.1 JSON yourself (see [[vss-kuksa-quickstart]] part B). It loaded fine on 0.7.1.

## Container images (ghcr.io, tags verified via registry API)
| Image | Tags |
|---|---|
| `ghcr.io/eclipse-kuksa/kuksa-databroker` | `0.7.1`, `0.7`, `0.7.0`, `0.6.1`, `0.6.0`, `0.5.0`, `0.4.x`, `latest`, `main` |
| `ghcr.io/eclipse-kuksa/kuksa-databroker-cli` | same tag set |
| `ghcr.io/eclipse-kuksa/kuksa-python-sdk/kuksa-client` | `0.6.0`, `0.6`, `0.5.x`, `latest` (pulled OK) |
| `ghcr.io/eclipse-kuksa/kuksa-can-provider/can-provider` | `0.5.0`, `0.5`, `0.4.x`, `latest`, `main` |
| `ghcr.io/eclipse-kuksa/kuksa-csv-provider/csv-provider` | `0.4.4`–`0.4.6`, `latest`, `main` |
| mirror `quay.io/eclipse-kuksa/kuksa-databroker`, `quay.io/eclipse-kuksa/csv-provider` | used by fleet-management (repos/fleet-management/fms-blueprint-compose.yaml:161,179); also reachable from mainland China |
| legacy `ghcr.io/eclipse/kuksa.val/databroker` | `0.4.1` still pullable; used by the Ankaios tutorial. Do not use. |

The databroker image is distroless (no `/bin/sh`), and its entrypoint is `/app/databroker`, so you cannot `docker exec ... sh` into it. Env defaults: `KUKSA_DATABROKER_ADDR=0.0.0.0`, `KUKSA_DATABROKER_PORT=55555`.

## Databroker CLI flags (0.7.1, `--help` output)
`--address` (default 127.0.0.1, 0.0.0.0 in the image), `--port` (55555), `--enable-unix-socket`, `--unix-socket PATH`, `--vss FILE[,FILE]`, `--jwt-public-key FILE`, `--disable-authorization`, `--insecure`, `--tls-cert`, `--tls-private-key`, `--enable-viss`, `--viss-address`, `--viss-port` (8090), `--worker-threads`.
**`--enable-databroker-v1` no longer exists** (removed with sdv.databroker.v1 in 0.7.0), even though the README and user guide still mention it.

## gRPC APIs
| API | Status | RPCs | Value model |
|---|---|---|---|
| `kuksa.val.v2.VAL` | **recommended**, on by default | `GetValue`, `GetValues`, `Subscribe`, `SubscribeById`, `Actuate`, `ActuateStream`, `BatchActuate`, `ListMetadata`, `PublishValue`, `OpenProviderStream`, `GetServerInfo` (repos/kuksa-proto/kuksa/val/v2/val.proto) | single data value + actuation channel to a registered provider; signals addressable by path or numeric id |
| `kuksa.val.v1.VAL` | **deprecated**, still on by default | `Get`, `Set`, `StreamedUpdate`, `Subscribe`, `GetServerInfo` (repos/kuksa-proto/kuksa/val/v1/val.proto) | current value + target value (target stored, not forwarded to v2 providers) |
| `sdv.databroker.v1` | **removed in 0.7.0** | n/a | n/a |
| VISS v2 (WebSocket) | optional (`viss` build feature + `--enable-viss`), no TLS | n/a | get/subscribe current, set target |

Matrix of "current/target/actuation × set/get/subscribe" per API: repos/kuksa-databroker/doc/protocol.md.
v2 provider-stream errors (val.proto:173-223): `ALREADY_EXISTS` if another provider has already claimed the signal, `ABORTED` if you publish before claiming, `NOT_FOUND`, `PERMISSION_DENIED`, `UNAUTHENTICATED`. `Actuate` without a provider returns `UNAVAILABLE`.

## Client tooling capability matrix
| Tool | v1 | v2 | Notes |
|---|---|---|---|
| `databroker-cli` 0.7.1 | yes (default) | **no** | `--protocol` offers `kuksa.val.v1` and `sdv.databroker.v1` (the latter is dead on 0.7.x). Needs a TTY (`-it`). |
| `kuksa-client` 0.6.0 Python | get, set target, subscribe | `PublishValue`, `Subscribe`, `ListMetadata`, `OpenProviderStream` (actuation requests) | No v2 `Actuate` wrapper, so use `kuksa.val.v2.val_pb2_grpc` directly. `set_current_values` tries v2 first. |
| kuksa-rust-sdk | yes | yes | Pre-alpha per org README. Used in Chapter 3 (ArBytesMoral) and fleet-management (`kuksa_rust_sdk::v2_proto`). |
| Velocitas vehicle-app SDKs | (unverified) | (unverified) | Python SDK release v0.15.7 2024-07-03, low activity (integration research) |

## VSS model essentials
- Node types: `branch`, `sensor`, `actuator`, `attribute`, `struct`, `property`.
- Datatypes: `boolean`, `string`, `int8/16/32/64`, `uint8/16/32/64`, `float`, `double`, arrays such as `float[]`, and struct types. The databroker accepts the scalar types and arrays but not structs (repos/kuksa-databroker/databroker/src/vss.rs reads `type, datatype, min, max, allowed, default, x-kuksa-changetype` only). Structs and the branch keyword `aggregate` are VSS's grouping primitives: a struct is read or written atomically, `aggregate` is an overlay-only deployment hint the docs call ill-defined ([[coherence-is-a-set-property-declared-in-the-model]]).
- Constraints: `min`, `max`, `allowed`, `pattern` (6.0) and `enum` (6.1). **The databroker enforces min/max/allowed but ignores `enum`**: publishing `99` to the 6.1 enum signal `Vehicle.Exterior.RoadSurfaceCondition` was accepted (observed).
- Units come from `spec/units.yaml` and quantities from `spec/quantities.yaml`. Since 6.0 the unit is `Celsius`, not `celsius`.
- Instances: `Row[1,2]` × `["DriverSide","Middle","PassengerSide"]` for seats and occupants. HVAC stations use `Row1..4` × `Driver/Passenger`. Doors use `Row1..2` × `DriverSide/PassengerSide`.
- Static IDs: `vspec export id` (replaces the removed UUIDs) is a 32-bit FNV-1 over name, unit, datatype, type, `allowed`, `min` and `max` (lower-cased): a range change re-mints the id, while the 6.1 `enum` mapping is not hashed, so rebinding an enum keeps the id ([[derive-ids-from-layout-not-from-prose]], read from source, not run). The databroker assigns its **own** numeric ids at load time (e.g. `vss_id 184`), which are not stable across trees. Clients should resolve path→id via `ListMetadata` and not hard-code ids.

## Signals for Chapter 4 (present in VSS 6.0 default tree unless noted)
### Battery thermal (Doctor Whodunit, Battery Thermal Guardian)
| Path | type / datatype / unit |
|---|---|
| `Vehicle.Powertrain.TractionBattery.Temperature.Average` / `.Min` / `.Max` | sensor float Celsius |
| `Vehicle.Powertrain.TractionBattery.Temperature.CellTemperature` | sensor float[] |
| `Vehicle.Powertrain.TractionBattery.Charging.Temperature`, `.DCDC.Temperature` | sensor float Celsius |
| `Vehicle.Powertrain.TractionBattery.BatteryConditioning.{IsActive,IsOngoing,RequestedMode,TargetTemperature,...}` | mixed; `RequestedMode` ∈ INACTIVE/FAST_CHARGING_PREPARATION/DRIVING_PREPARATION |
| `Vehicle.Powertrain.TractionBattery.{StateOfHealth, StateOfCharge.Current, CurrentCurrent, CurrentVoltage, CurrentPower}` | sensors |
| `Vehicle.Powertrain.TractionBattery.ErrorCodes` | sensor string[] |
| `Vehicle.Powertrain.TractionBattery.Charging.IsCharging` | sensor boolean |
| `Vehicle.Diagnostics.DTCCount`, `Vehicle.Diagnostics.DTCList` | sensor uint8 / string[] |
| `Vehicle.ControlUnit.<Central|FrontLeft|...>.Health.SWSupervision.{IsAliveTriggered,IsDeadlineTriggered,IsLogicalTriggered,IsWatchdogTriggered}` | sensor boolean (VHM, VSS 6.0) |
| `Vehicle.ControlUnit.*.Health.Resources.Temperature` | sensor float Celsius |
| *missing*: thermal-runaway / thermal-event flag, per-module temperatures, coolant loop of the battery | use an overlay |

### Cabin occupancy / child presence (Hack to the Future, Guardian Loop)
| Path | type / datatype |
|---|---|
| `Vehicle.Cabin.Seat.Row{1,2}.{DriverSide,Middle,PassengerSide}.OccupancyStatus` | sensor string ∈ UNKNOWN/OCCUPIED/EMPTY (VSS ≥6.0; replaces the boolean `IsOccupied`) |
| `Vehicle.Cabin.Seat.*.IsBelted` | sensor boolean |
| `Vehicle.Occupant.Row*.*.Identifier.{Subject,Issuer}`, `.HeadPosition.*`, `.MidEyeGaze.*` | sensors |
| `Vehicle.Cabin.HVAC.AmbientAirTemperature`, `Vehicle.Exterior.AirTemperature` | sensor float Celsius |
| `Vehicle.Cabin.HVAC.Station.Row*.{Driver,Passenger}.{Temperature,FanSpeed}`, `Vehicle.Cabin.HVAC.IsAirConditioningActive` | actuators (mitigation) |
| `Vehicle.Cabin.Door.Row*.*.{IsOpen,IsLocked,IsChildLockActive}`, `...Window.Position` | actuators/sensors |
| `Vehicle.Body.Horn.IsActive`, `Vehicle.Body.Lights.Hazard.IsSignaling` | actuators (alert) |
| `Vehicle.Connectivity.IsConnectivityAvailable`, `Vehicle.CurrentLocation.{Latitude,Longitude}` | sensors (remote alert) |
| *missing*: CPD detection result, confidence, alert state | use an overlay (example in [[vss-kuksa-quickstart]]) |

### Parked state (no single `IsParked` signal; derive it)
`Vehicle.Speed` (km/h), `Vehicle.IsMoving` (boolean), `Vehicle.Chassis.ParkingBrake.IsEngaged`, `Vehicle.Powertrain.Transmission.SelectedGear` (int8 actuator: 0=Neutral, 1..=Forward, -1..=Reverse, **126=Park**, 127=Drive; repos/vehicle_signal_specification/spec/Powertrain/Transmission.vspec:67-70), `Vehicle.Powertrain.Transmission.IsParkLockEngaged` (boolean), `Vehicle.LowVoltageSystemState` (UNDEFINED/LOCK/OFF/ACC/ON/START), and `Vehicle.Cabin.Door.*.IsLocked`.

## Pitfalls (observed or documented)
1. **API version confusion.** There are three gRPC APIs, the CLI defaults to v1, the CLI cannot do v2, and old docs and blueprints use `sdv.databroker.v1` (gone in 0.7.0) or `--enable-databroker-v1` (flag gone). Decide on v2 on day 1.
2. **v1 target ≠ v2 actuation** (observed). A v1 `set_target_values` / CLI `actuate` "succeeds" but a v2 provider never sees it.
3. **Authorization is off by default.** Only `--jwt-public-key` enables it. The user guide table says `--disable-authorization` defaults to `true`. Good for hacking, bad for any "security" claim.
4. **`--insecure` is the default without TLS certs.** The docs recommend passing it explicitly because the default may change.
5. **Ports.** gRPC 55555, VISS 8090. On macOS port 55555 often cannot be bound, so the docs map `-p 55556:55555`. Some blueprints run the broker on **55556** (service-to-signal sets `KUKSA_DATABROKER_PORT=55556`). Check which port your client expects.
6. **CLI needs a TTY** (`docker run -it`). In CI or scripts, wrap it in `script -qec` (as done here) or use the Python client.
7. **CLI prints `[publish] OK` before the error.** Always read the error list (observed for min/max and allowed violations).
8. **Signal names change between VSS versions.** `IsOccupied`→`OccupancyStatus` (6.0), `celsius`→`Celsius`, `Vehicle.OBD.*` gone (6.0), mirrors and seats reworked. A path that 404s (`No entries found for the provided path`) usually means a tree-version mismatch. Check which JSON the broker loaded (`Populating metadata from file ...` in its log).
9. **Names vs IDs.** v2 can address by numeric id, but ids are assigned by the broker per loaded tree. Resolve ids at runtime.
10. **`enum` (VSS 6.1) is not enforced** by the databroker 0.7.1 (observed). Use `allowed` strings if you need validation.
11. **Read-back race.** After `Actuate`, the value appears only when the provider publishes it. Subscribe; do not poll immediately.
12. **No persistence.** A broker restart loses all values, so providers must republish.
13. **onchange vs continuous.** A stuck sensor with `onchange` produces no notifications. A freshness watchdog must use timestamps.
14. **Outdated docs.** The user guide still shows `./vss-tools/vspec2json.py`. The current command is `vspec export json ...`.

## Key links
- VSS docs: https://covesa.github.io/vehicle_signal_specification/ ; repo https://github.com/COVESA/vehicle_signal_specification
- vss-tools: https://github.com/COVESA/vss-tools (docs/ for each exporter, compose, diff)
- Databroker: https://github.com/eclipse-kuksa/kuksa-databroker (doc/user_guide.md, protocol.md, authorization.md, tls.md)
- Protos: https://github.com/eclipse-kuksa/kuksa-proto
- Python SDK: https://github.com/eclipse-kuksa/kuksa-python-sdk (docs/cli.md, docs/library.md)
- Providers: https://github.com/eclipse-kuksa/kuksa-can-provider , https://github.com/eclipse-kuksa/kuksa-csv-provider , kuksa-someip-provider, kuksa-dds-provider, kuksa-mock-provider, kuksa-gps-provider
- Other SDKs: kuksa-rust-sdk, kuksa-java-sdk, kuksa-android-sdk; incubation (Zenoh provider, Go client, eCAL, ESP32): https://github.com/eclipse-kuksa/kuksa-incubation
- Perf tool: https://github.com/eclipse-kuksa/kuksa-perf
- Archived (do not use): kuksa.val, kuksa.val.feeders (archived 2024-03-22), kuksa.val.services, kuksa-viss (archived 2026-04-14), per the integration research of the eclipse-kuksa org page; not independently verified.
