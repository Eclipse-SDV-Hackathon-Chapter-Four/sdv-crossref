---
title: Reference architecture — Hack to the Future (portable child-presence feature)
type: synthesis
component: none
tags: [reference-architecture, hack-to-the-future, chapter4, portability, embedded, uprotocol, openbsw]
status: reviewed
sources:
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[vss-kuksa-overview]] (OccupancyStatus, parked-state derivation)"
  - "[[openbsw-howto]] (child-presence ECU idea)"
  - "[[sdv-blueprints-overview]] (service-to-signal, e2e-vehicle-signals)"
  - "[[uprotocol-overview]] (no official embedded client)"
  - "[[scoring-rubric-cheatsheet]]"
last-verified: 2026-10-03
related:
  - "[[reference-architecture-doctor-whodunit]]"
  - "[[gap-register]]"
  - "[[capability-map]]"
  - "[[first-two-hours-hack-to-the-future]]"
  - "[[debugging-checklists]]"
---

# Reference architecture — Hack to the Future

> One possible architecture, not the official reference. If the organisers publish starter code, follow that and use this for the gaps.

**Challenge in one line** (from [[chapter4-challenge-hack-to-the-future]]): take one SDV feature, the *Guardian Loop* scenario of child presence detection in a parked vehicle, and move it between virtual setups, embedded controllers and real vehicles. Named technologies: uProtocol, openDuT, OpenBSW, AutoSD. KUKSA and VSS are **not** named; they appear below only as an optional variant. Stretch: "Flux Capacitor / Time Circuits" displays (interface unpublished).

**Not published as of 2026-10-03**: reference Guardian Loop code, hardware list, AutoSD image provisioning, how HPC ↔ OpenBSW transport is expected to work, real-car access, display interface. The challenge note says the embedded-to-uProtocol transport is the hardest part and that an upstream issue or PR for a missing transport gets top marks.

## 1. Portability is a layering decision, not a porting effort

The trick is to fix three things and let everything else vary. The core path is **uProtocol end to end**: sensor, decision service and zonal-controller actuation all exchange UMessages. uProtocol carries opaque payloads and defines no data model, so it does not need VSS ([[uprotocol-overview]]); VSS names only enter if you bridge to KUKSA (section 2b).

| Fixed across targets | Varies per target |
|---|---|
| **uProtocol UUris** for `presence/detected`, `cabin/temperature`, `alert/raise`, `actuate/{window,fan,alarm}`, `loop/heartbeat` | the **transport**: Zenoh on HPC, CAN or SOME/IP to the OpenBSW controller via an adapter, zenoh-pico or MQTT5 on a non-OpenBSW MCU, uStreamer bridging |
| **the payload schema** (one protobuf or JSON definition for occupancy, temperature, alert, actuation; your choice, uProtocol does not prescribe one) | the **sensor/actuator end**: mock publisher on laptop, OpenBSW ECU behind an adapter, real-car CAN via openDuT |
| **the feature logic** (one Rust or Python crate, no I/O inside) | the **deployment**: docker compose → Ankaios manifest → AutoSD quadlets |

```
   target A: laptop (virtual)        target B: embedded controller           target C: real vehicle (if offered)
   ┌───────────────────────┐        ┌─────────────────────────────┐          ┌──────────────────────────┐
   │ mock sensor publisher │        │ OpenBSW ECU (POSIX now,     │          │ car CAN ──► openDuT EDGAR│
   │   ▼ UMessage/Zenoh    │        │   S32K148 / ThreadX later)  │          │   ▼                      │
   │ decision service      │        │   ▲▼ CAN (opt 1) or         │          │ CAN → uProtocol adapter  │
   │ (feature logic crate) │◄───────┤      SOME/IP (opt 2)        │          │   (same as target B)     │
   │   ▼ UMessage/Zenoh    │        │ CAN/SOME/IP ↔ uProtocol     │          │   ▼                      │
   │ actuation / alert sink│        │   adapter on the HPC        │          │ same decision service    │
   │ (console, horn svc,   │        │                             │          │                          │
   │  display)             │        │ non-OpenBSW MCU: zenoh-pico │          │                          │
   └───────────────────────┘        │   (opt 3) or MQTT5→uStreamer│          └──────────────────────────┘
          docker compose            └─────────────────────────────┘           same manifests, EDGAR added
                                        Ankaios manifest / AutoSD quadlets
```

## 2. Component roles

| Role | Component | Why | Seam | Note |
|---|---|---|---|---|
| Events and commands (core) | uProtocol 0.9 over Zenoh 1.10 | named in challenge; the portability claim lives here | UUri with authority per target | [[uprotocol-quickstart]] (verified) |
| Virtual sensor | mock publisher (small up-rust or Python process replaying scenario CSVs as UMessages) | repeatable scenarios (child left, adult present, nobody) | UMessage | (inference; uProtocol pub/sub verified in [[uprotocol-quickstart]]) |
| Embedded controller | OpenBSW virtual ECU, later S32K148 or ThreadX AZ3166 | builds in 20 s on a laptop; CAN + UDS + DoIP; `presence set 1` console idea; responds by window/fan/alarm | CAN or SOME/IP to an adapter on the HPC, see 2a | [[openbsw-howto]] [[openbsw-quickstart]] (verified) |
| MCU messaging (non-OpenBSW) | zenoh-pico (ThreadX, ESP32, Zephyr) carrying UMessage bytes; or MQTT5 → uStreamer | no official embedded uProtocol client exists (gap D1) | Zenoh router on HPC | [[zenoh-overview]] [[threadx-overview]] (Cortex-M4 ThreadX library build verified 2026-10-03 with the toolchain inside the OpenBSW image) |
| Alert sink | service-to-signal "software horn" (same service against a software horn or an ESP32 over Zenoh) | already demonstrates "same service, two targets" | Zenoh | [[sdv-blueprints-overview]] |
| Deployment | compose → Ankaios 1.0.4 → AutoSD quadlets | each step is a visible portability hop | manifests | [[ankaios-howto]] [[autosd-howto]] |
| Real vehicle | openDuT EDGAR to organiser CARL; CDA for diagnostics | bonus tech; mirror-fold on a real car worked at HackFest; self-hosted CARL verified in ~10 min but EDGAR-in-Docker does not join as documented, so plan on native EDGAR or an organiser-hosted CARL (Path C in [[opendut-quickstart]]) | CAN over GRE/NetBird | [[hackfest-opendut-playground]] |
| Fleet view (optional) | Symphony Instance describing HPC + MCU software set, or a signed two-level update manifest (campaign naming per-target image manifests) | "same software set on all targets" story; a signed manifest also gives anti-rollback and trial/commit semantics ([[gap-register]] H3–H5) | REST / COSE | [[symphony-overview]] |

### 2a. OpenBSW ↔ uProtocol: three options, none built yet

No upstream OpenBSW–uProtocol integration exists ([[openbsw-overview]], [[pros-cons-when-not]]); this is gap D1 and the "top marks" contribution the challenge points at.

| # | Path | Pieces that exist | What you build | Risk | Evidence |
|---|---|---|---|---|---|
| 1 | **CAN frames → small up-rust adapter on the HPC**, publishing UMessages (and, for actuation, subscribing to UMessages and writing CAN frames back) | OpenBSW POSIX ECU sends CAN on vcan0 (demo frame 0x558, [[openbsw-howto]]); up-rust + up-transport-zenoh pub/sub ([[uprotocol-quickstart]]) | a Linux process: socketcan read/write ↔ up-rust publish/subscribe; a presence frame and actuator frames in the ECU | **lowest**; no OpenBSW network-stack work, idea 5 in [[openbsw-howto]] | R for the CAN half and the uProtocol half separately; the adapter itself is not built |
| 2 | **SOME/IP**: OpenBSW `libs/bsw/cpp2someip` ↔ uProtocol SOME/IP mapping (`ue_id` lower 16 bits = ServiceID, `resource_id` = MethodID/EventID) via `up-transport-vsomeip` or the uStreamer `zenoh_someip` example | `repos/openbsw/libs/bsw/cpp2someip/doc/index.rst` (RpcSomeIpStack, SdSomeIpStack); `repos/up-spec/up-l1/someip.adoc`; up-transport-vsomeip 0.6.0; `repos/up-streamer-rust/example-streamer-implementations/src/bin/zenoh_someip.rs` | OpenBSW services/events whose IDs follow the mapping; a vsomeip config; TAP networking for the POSIX ECU | medium–high: heavy vsomeip C++ build; cpp2someip ↔ vsomeip interop **untested**; SomeIpSystem in the ref app not run | C |
| 3 | **zenoh-pico on an MCU** (not OpenBSW) carrying UMessage bytes to a Zenoh router on the HPC | zenoh-pico supports ThreadX, ESP32, Zephyr ([[zenoh-overview]]) | UMessage encoding on the MCU (no official embedded uProtocol client, D1) | medium; needs a board; does not exercise OpenBSW, so it does not satisfy the "OpenBSW-based zonal controller" part on its own | C |

Start with option 1; it keeps OpenBSW on its verified CAN path and puts all uProtocol code in Rust on Linux. Option 2 is the more interesting upstream contribution; file the issue even if the interop does not work in two days.

### 2b. Optional variant: KUKSA / VSS as the state layer

Not named in this challenge. Use it only if your team already knows KUKSA or wants VSS names for the cross-team story; it adds a project but does not replace uProtocol, and a KUKSA ↔ uProtocol bridge is gap B1 ([[gap-register]]).

| Role | Component | Why | Seam | Note |
|---|---|---|---|---|
| Vocabulary (optional) | VSS 6.1 + overlay | `OccupancyStatus` (UNKNOWN/OCCUPIED/EMPTY) exists; there is no child-presence branch and no `IsParked`: derive parked from `IsMoving`, parking brake, `SelectedGear`=126 or `LowVoltageSystemState`. Paths: `Vehicle.Cabin.Seat.Row2.Pos1.OccupancyStatus`, `Vehicle.IsMoving`, `Vehicle.Powertrain.Transmission.SelectedGear`, `Vehicle.Chassis.ParkingBrake.IsEngaged`, overlay `Vehicle.Cabin.ChildPresence.IsDetected` | overlay `.vspec` | [[vss-kuksa-overview]] |
| State (optional) | KUKSA Databroker 0.7.1 | same container on every Linux target; <4 MB static binary | kuksa.val.v2 | [[vss-kuksa-quickstart]] (verified) |
| Virtual sensor (optional) | kuksa-csv-provider / mock | replaces the mock UMessage publisher | CSV | [[vss-kuksa-reference]] |
| Embedded sensor (optional) | OpenBSW CAN frame on vcan0 → `kuksa-can-provider` with DBC overlay | verified rootless path from the ECU into a broker; the decision service then reads kuksa.val.v2 and publishes uProtocol | CAN → VSS | [[openbsw-howto]] (verified 2026-10-03) |

In this variant the decision service is a KUKSA client on input and a uProtocol entity on output, as in [[reference-architecture-doctor-whodunit]].

## 3. Build order (levels)

| Level | Add | Time | Demonstrates | Rubric |
|---|---|---|---|---|
| L0 (first 3 h) | payload schema + mock UMessage sensor + feature crate + uProtocol alert + console sink (optional variant: KUKSA + overlay + CSV provider instead of the mock) | 3 h | feature works on target A | Working Demo |
| L1 | OpenBSW POSIX ECU → vcan0 → CAN ↔ uProtocol adapter (option 1 in 2a; needs sudo for vcan; the CAN half was verified rootless into `kuksa-can-provider` on 2026-10-03, [[openbsw-howto]]) | +4 h | same logic, different sensor path; **first portability hop** | Integrability |
| L2 | Ankaios manifest; then AutoSD prebuilt QEMU image running the same manifest or quadlets | +4 h | deployment hop; +0.10 AutoSD | Integrability, bonus |
| L3 | MCU leg: zenoh-pico on ESP32 or ThreadX AZ3166 publishing occupancy (option 3); uStreamer if MQTT; or SOME/IP to OpenBSW (option 2) | +5 h | embedded hop; +0.10 ThreadX if used | Innovation, bonus |
| L4 | openDuT EDGAR joined to CARL; real-car CAN if offered; CDA reads seat DIDs | +3 h | real-vehicle hop; +0.10 openDuT | bonus |
| L5 (stretch) | Flux Capacitor display (FLXC1000 branch; not buildable today against any reachable openbsw commit, do not promise it, see [[hackfest-openbsw-playground]]), Symphony instance, upstream issue/PR for the embedded uProtocol transport | rest | the "top marks" item from the challenge text | Contribution |

## 3b. Simulating two ECUs on one laptop

Two patterns exist for iceoryx2 in containers, and teams confuse them:

| Goal | Pattern | Why |
|---|---|---|
| Several workloads on **one** node (Ankaios, compose) | share `/dev/shm` and `/tmp/iceoryx2`, same UID ([[ankaios-howto]], [[iceoryx2-howto]]) | iceoryx2 is shared memory; one node is one shared-memory domain |
| **Two** nodes, e.g. HPC and a second ECU, on one machine | one container per node with its **own** PID namespace, `/dev/shm` and `/tmp` (no `ipc: host`, no `network_mode: host`, `shm_size: 256m`), and **only Zenoh crosses** the compose network | each container is then an iceoryx2 instance of its own, so the only seam is the one the deployment declares, which is what a real two-ECU setup looks like |

The second pattern is the credible virtual setup for the HF portability story: the feature container is identical on both nodes, the bridge (iceoryx2 tunnel over Zenoh, or a uProtocol app on each side) is what moves, and `docker compose` already resolves the other container's name as the Zenoh endpoint. A bounded run (apps end first, bridge and sensor outlive them by a few seconds) keeps the last readings whole for the demo log.

## 4. Scenario catalogue (same CSV on every target)

Signal names below are written as VSS paths for readability; in the core path they are fields of your uProtocol payloads.

| Scenario | Signals | Expected |
|---|---|---|
| Child left in rear seat, car parked | Row2.Pos1 OCCUPIED, driver EMPTY, IsMoving=false, ParkingBrake engaged | alert within N seconds, escalate after M minutes |
| Adult present | Row1.DriverSide OCCUPIED | no alert |
| Driving | IsMoving=true | no alert even if rear occupied |
| Sensor dropout | OccupancyStatus UNKNOWN for >T | degraded warning (not an alert) |
| Ignition off, occupant leaves | OCCUPIED → EMPTY | alert cleared |

## 5. What to show in the interview

1. The *same* feature binary or container on at least two targets, with the UUris (and VSS paths, if you use the KUKSA variant) visibly identical (show the config diff: only transport endpoint and sensor end change).
2. A live hop: switch the sensor end from the mock to the OpenBSW ECU (or MCU) without touching the logic.
3. The manifests for each deployment (compose, Ankaios, quadlet) in the repo, plus the scenario CSVs. Development Methods is 20 %.
4. The upstream issue or PR you filed for whatever transport piece was missing.

## 6. Known traps specific to this architecture

- (KUKSA variant) `IsOccupied` was replaced by `OccupancyStatus` in VSS 6.0: old examples silently miss ([[vss-kuksa-reference]]).
- (KUKSA variant) `kuksa-can-provider` needs a DBC and a mapping overlay; budget half a day for the first CAN → VSS bridge ([[hackathon-patterns]]); a working DBC/mapping for the demo frame 0x558 is in `components/openbsw/examples-can-feeder/` (verified 2026-10-03, [[openbsw-howto]]). If the CDA reads the ECU, every DTC the ECU reports must exist in the MDD or `faults` answers 400 ([[opensovd-reference]]).
- Zenoh scouting on Wi-Fi: router + explicit endpoints; zenoh-pico in client mode needs a router ([[zenoh-overview]]).
- Same uProtocol authority on two hosts is never bridged by uStreamer; authorities are lowercase ([[uprotocol-howto]]).
- AutoSD has no rpi5 target; prebuilt images are qemu and rpi4 ([[autosd-overview]]).
- ThreadX on AZ3166: toolchain and udev setup eats the first hour; Wi-Fi SSID and broker IP are compiled in ([[threadx-overview]] [[chapter3-retrospective]]).
- OpenBSW console reads stdin: backgrounding the ECU stops it; launch with stdin from `/dev/null` ([[openbsw-howto]]).
