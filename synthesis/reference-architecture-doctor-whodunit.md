---
title: Reference architecture — Doctor Whodunit (fault evidence factory)
type: synthesis
component: none
tags: [reference-architecture, doctor-whodunit, chapter4, faults, evidence]
status: reviewed
sources:
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[opensovd-integration-notes]] (suggested wiring)"
  - "[[vss-kuksa-integration-notes]] (suggested wiring)"
  - "[[uprotocol-howto]] (proposed event schema)"
  - "[[hackfest-openbsw-playground]] (OpenBSW-SOVD-Demo)"
  - "[[scoring-rubric-cheatsheet]]"
last-verified: 2026-10-03
related:
  - "[[reference-architecture-hack-to-the-future]]"
  - "[[gap-register]]"
  - "[[capability-map]]"
  - "[[first-two-hours-doctor-whodunit]]"
  - "[[debugging-checklists]]"
---

# Reference architecture — Doctor Whodunit

> One possible architecture, not the official reference. If the organisers publish starter code, follow that and use this for the gaps.

**Challenge in one line** (from [[chapter4-challenge-doctor-whodunit]]): build a *safety evidence factory* around the Battery Thermal Guardian, an EV thermal-runaway early-warning service. Inject faults you have seen or expect, and let the evidence tell the story. Named technologies: openDuT, uProtocol, Ankaios, OpenSOVD, KUKSA, AutoSD, S-CORE, SDV Blueprints.

**What is not published as of 2026-10-03**: the Guardian source, the AutoSD image, the openDuT testbench setup, the expected fault model and evidence format, and S-CORE's role. On 2026-10-03 the Chapter 4 GitHub org's public page showed only its `.github` profile repo. Re-check on Day 1; everything below is designed so that a published Guardian can be dropped in.

## 1. What the rubric rewards

The public Evaluation Forms (https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf, summarised in [[scoring-rubric-cheatsheet]]) weight Ecosystem Integrability at 27 % (4 = "Multiple projects work together in a coherent flow"), Development Methods at 20 %, and give +0.10 each for openDuT, AutoSD, ThreadX and Java / Jakarta EE, counted only when "meaningfully used" ("A logo or name on a slide does not count"). The architecture therefore has **one data spine with many Eclipse projects attached**, each attached through a *real* data path the HackCoaches can trace in the 8-minute interview.

```
                 ┌──────────────────────── evidence chain ────────────────────────┐
 hazard ──► injected fault ──► detection (Guardian) ──► mitigation ──► diagnostic record ──► timeline
   │              │                    │                     │                 │                 │
 openDuT      campaign exec        uProtocol             uProtocol         OpenSOVD          Grafana /
 (EDGAR)      tc netem/canplayer   fault event           mitigation evt    faults + data     evidence store
              ank delete/restart   heartbeat
              CSV replay (KUKSA)
```

```
 ┌─────────────────────────── AutoSD (QEMU or RPi4, prebuilt bootc image) ───────────────────────────┐
 │                                                                                                      │
 │   Ankaios server+agent  (or systemd quadlets if podman is unavailable)                               │
 │   ├── kuksa-databroker 0.7.1  ◄── csv/mock provider (temperature profiles, replayable)               │
 │   │        │ kuksa.val.v2 subscribe  TractionBattery.Temperature.{Average,Max,CellTemperature}       │
 │   │        ▼                                                                                         │
 │   ├── guardian (Rust)  ──► uProtocol/Zenoh:  heartbeat 1 Hz · fault{stuck,implausible,runaway} ·     │
 │   │                                           mitigation{limit-charge,notify}                        │
 │   ├── zenoh router (optional; needed on Wi-Fi) + uStreamer → MQTT5 (optional, for dashboards)        │
 │   ├── evidence collector  ◄── subscribes all uProtocol topics; polls SOVD; writes InfluxDB            │
 │   ├── opensovd (one of):                                                                              │
 │   │     a) opensovd-core gateway + custom FaultProvider/DataProvider  (gap A1/A4)                     │
 │   │     b) CDA + OpenBSW-SOVD-Demo virtual ECU over DoIP (5 DTCs, ready today)                       │
 │   └── grafana + influxdb (fault timeline, hazard → fault → detection → mitigation → DTC)             │
 │                                                                                                      │
 │   openDuT EDGAR (joined to organiser CARL)  ◄── fault-campaign executor (tc netem, canplayer, ...)   │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────┘
          ▲ iox2 record/replay (if an S-CORE/iceoryx2 leg is present)   ▲ ank get workloads (supervisor view)
```

### KUKSA and uProtocol do not talk to each other directly

Both are named in the challenge, but no adapter connects them: KUKSA holds signal state (gRPC kuksa.val.v2), uProtocol carries the heartbeat, fault and mitigation events. The Guardian is the join: a KUKSA client on its input and a uProtocol entity on its output. A generic KUKSA ↔ uProtocol bridge is gap B1 ([[gap-register]]); it is optional here and not needed for the flow above.

## 2. Component roles and the exact seam each one owns

| Role | Component | Why this one | Seam (what crosses the boundary) | Note |
|---|---|---|---|---|
| Vehicle state | KUKSA Databroker 0.7.1 + VSS 6.1 overlay | the shared vocabulary; every provider and app agrees on `Vehicle.Powertrain.TractionBattery.Temperature.*`; overlay adds `IsThermalRunawayWarning` | kuksa.val.v2 gRPC, port 55555 | [[vss-kuksa-howto]] (overlay recipe verified) |
| Sensor source | kuksa-csv-provider / mock provider | replayable temperature profiles = repeatable fault campaigns without hardware | CSV → databroker | [[vss-kuksa-reference]] |
| Detector | Guardian (Rust; drop-in for the official one) | subscribe v2, detect stuck/implausible/runaway, publish events | uProtocol UMessage over Zenoh | schema proposal in [[uprotocol-howto]] |
| Event bus | uProtocol 0.9 over Zenoh 1.10 | named in the challenge; one envelope from vehicle to dashboard | `up-rust = "0.9.0"`, `up-transport-zenoh = "0.9.1"` | [[uprotocol-quickstart]] (verified) |
| Supervisor | Ankaios 1.0.4 | restarts the Guardian on exit and *is itself a fault injector* (`ank delete`, `restartPolicy`); it has no liveness probe, so a hung Guardian still shows Running: supervise heartbeats via gap A9, systemd `WatchdogSec`, or a podman healthcheck (unverified with Ankaios) (corrected 2026-10-03, see [[one-watchdog-per-layer-each-blind-to-the-others]]) | control interface → evidence collector (gap A9) | [[ankaios-howto]]; podman required |
| Diagnostic truth | OpenSOVD | the challenge says "diagnostic truth exposed through OpenSOVD"; faults must be readable at a SOVD URL | REST `/components/<x>/faults`, `/data` | [[opensovd-quickstart]] (verified) |
| ECU leg | OpenBSW-SOVD-Demo (virtual ECU + CDA + Grafana) | ready-made DTCs, UDS 0x19/0x14/0x22, Grafana; fork it (TTL note) | DoIP 13400 | [[hackfest-openbsw-playground]] |
| Evidence store | InfluxDB + Grafana (from fleet-management blueprint) | the timeline *is* the deliverable | Influx line protocol; Grafana Infinity for SOVD | [[sdv-blueprints-quickstart]] |
| Fault injection (network) | openDuT EDGAR + executor | bonus tech; the executor does not exist yet (gap A6) | CAN/Ethernet via EDGAR | [[opendut-howto]] |
| Runtime | AutoSD prebuilt bootc image | bonus tech; the QM partition can host the Guardian's observer/UI, but its decider belongs on the ASIL side (S-CORE safety manual) (corrected 2026-10-03, see [[freedom-from-interference-has-three-axes]], [[freedom-from-interference-is-a-stack-of-layers]]) | podman quadlets | [[autosd-quickstart]] (prebuilt `dev` image boots to login under KVM in ~6 s with 4 GB, verified 2026-10-03) (corrected 2026-10-03, see [[autosd-quickstart]]) |
| Safety framing | S-CORE (optional) | persistency KVS for evidence; Kyron chain as mitigation sequence; *runtime link to OpenSOVD does not exist* (gap A3) | iceoryx2 events; `iox2 record` | [[s-core-quickstart]] (Cargo path verified) |

## 3. Build order (levels), so the team always has a demo

| Level | Add | Time | Evidence produced | Rubric hit |
|---|---|---|---|---|
| L0 (first 3 h) | KUKSA + CSV provider + Guardian + uProtocol pub/sub + console subscriber | 3 h | fault event printed when a replayed profile spikes | Working Demo |
| L1 | InfluxDB + Grafana timeline; evidence collector | +3 h | timeline with injected-fault marker and detection latency | Code does what it claims |
| L2 | OpenSOVD: core gateway with a FaultProvider (A1) **or** CDA + OpenBSW virtual ECU | +4 h | `curl .../faults` shows the DTC the Guardian raised | Ecosystem Integrability |
| L3 | Ankaios manifest for everything; `ank delete guardian` as a fault; workload states into evidence | +3 h | supervisor view, restart latency | Integrability, Dev Methods |
| L4 | AutoSD prebuilt image as host (QEMU); openDuT EDGAR joined to CARL; campaign executor | +4 h | same demo on AutoSD; one campaign run via openDuT | +0.20 bonus |
| L5 (stretch) | S-CORE leg: Guardian logic as Kyron chain with iceoryx2 events; `iox2 record` as second evidence tap; MCP server over SOVD | rest | "whodunit" answered by an agent | Innovation |

Your Day-1 18:00 Solution Plan should describe L0–L3 as committed and L4–L5 as stretch.

## 4. Fault catalogue (what to inject, and where the evidence shows up)

| Fault | Inject with | Expected detection | Evidence location |
|---|---|---|---|
| Stuck temperature sensor | CSV provider repeats a value; or set `onchange` and freeze | Guardian freshness watchdog (timestamps, not value change) | uProtocol fault event + SOVD fault + timeline |
| Implausible jump | CSV profile with a +40 °C step | plausibility rule | same |
| Thermal runaway ramp | CSV ramp crossing threshold | runaway warning + mitigation event | overlay signal `IsThermalRunawayWarning` flips; SOVD fault |
| Guardian crash | `ank delete guardian` or `podman kill` | missed heartbeats (publish is at-most-once, tolerate N) | Ankaios workload state + heartbeat gap in timeline |
| Network partition / delay | `tc netem` via openDuT executor or the uProtocol shim (gap A7) | delayed/dropped events; detection latency grows | timeline annotation from campaign |
| ECU DTC | OpenBSW console or demo DTC simulator | CDA reads 0x19 | SOVD `/faults` on the ECU component |
| Wrong mitigation | mitigation handler returns error | mitigation event with status | SOVD `operations` (gap) or evidence store |


### Vocabulary for the catalogue, and one rule

Name injected faults and detected faults with the vocabulary of end-to-end protection, so the evidence reads like a safety case rather than a log: **length, crc, source, unknown type, mask, payload, counter repeat, counter regression, counter gap, stale**. A per-reason counter is the smallest useful evidence store, and a Grafana panel per reason is the smallest useful dashboard.

The rule: **aliveness is checked on a timer, never only on arrival.** A sensor that stops emitting produces no counter gap and no change event, so a Guardian that reacts to arrivals cannot see silence. Every reading should carry its own validity, source and age, and the policy for a bad reading is one of three: *reject* (a value nobody can believe is not a value; fall back to the safe state), *hold last* for a time bounded by the fault-tolerant time interval (FTTI) (bridge a short gap), or a *flagged substitute* (a declared default the consumer knows is not a measurement) (corrected 2026-10-03, see [[deciding-on-a-bad-state-is-wrong-not-degraded]]). Deciding on a bad state is not degraded operation, it is a wrong decision; say which policy each signal gets and why. Readings that must be judged together should carry the same pass or sequence stamp, so a decision is made once per instant of the vehicle and a spread between them is refused rather than decided on. Fresh timestamps alone do not catch a frozen provider that keeps re-sending: it needs a producer counter plus a stuck-at check against a correlated signal (corrected 2026-10-03, see [[check-plausibility-at-the-consumer-that-decides]]).

### SOVD-native evidence hooks (none exist in OpenSOVD core yet)

The standard already has the two mechanisms an evidence factory wants: **cyclic subscriptions** stream a resource over Server-Sent Events with a server timestamp on every envelope, and **triggers** fire on EnterRange / LeaveRange / OnChange / OnChangeTo and can emit an SSE event, a log entry, or a further SOVD command. A team that implements `triggers` in opensovd-core ([[gap-register]] H2) gets detection, evidence timestamps and a freestyle contribution from one piece of work, and can describe the Guardian as "a trigger on `TractionBattery.Temperature.Max` whose action is a fault". Until then, poll `data` and timestamp client-side.

## 5. What to show in the 8-minute interview

1. `ank get workloads` (or `podman ps`): every box in the diagram is a running thing.
2. Trigger one fault from the catalogue live; watch the uProtocol event, the Grafana marker, and `curl .../faults` within 30 seconds.
3. Show the repo: manifests, the event schema crate, a README that a second team could run. Development Methods is 20 %.
4. Name the gaps you hit and the issue or PR you opened (Contribution Focus, Community Benefit).

## 6. Known traps specific to this architecture

- KUKSA v1 target sets "succeed" but never reach a v2 provider: use v2 everywhere ([[vss-kuksa-reference]]).
- Zenoh multicast scouting may fail on venue Wi-Fi (unverified; the default Docker bridge passed it on one host (corrected 2026-10-03, see [[zenoh-overview]])): run a router and use `-e tcp/<ip>:7447` so the demo does not depend on the venue network.
- Ankaios treats communication between workloads as out of scope; the tutorial uses `--net=host` ([[ankaios-howto]]) (corrected 2026-10-03, see [[a-container-is-an-ecu-zenoh-is-the-only-door]]).
- opensovd-core `/faults` is 404 until you implement it; the CDA path (`/vehicle/v15`) and core path (`/sovd/v1`) differ ([[opensovd-quickstart]]); the real-CDA-over-DoIP path is verified with `playbook/fixes/openbsw-sovd-demo-real-cda.override.yaml` and the CDA needs a Bearer token from `POST /vehicle/v15/authorize` ([[hackfest-openbsw-playground]]); CDA over CAN (vcan0, UDS 0x7E0/0x7E8) to the OpenBSW POSIX app is verified rootless, but every DTC the ECU reports must exist in the MDD or `faults` answers 400 ([[opensovd-reference]]).
- OpenBSW-SOVD-Demo needs `git submodule update --init openbsw` and its compose file is broken in five ways as written; use `playbook/fixes/openbsw-sovd-demo.override.yaml` and start `sovd-cda` with `--no-deps` ([[known-broken-recipes]]).
- fleet-management and the other blueprints need the bridge-network overrides in `playbook/fixes/` on a non-swarm Docker host, and the rFMS path is `/rfms/vehiclepositions` ([[known-broken-recipes]]).
- Do not start from the HackFest S-CORE branches; use upstream `inc_diagnostics@gateway_cda_int` ([[hackfest-esslingen-2026]]).
