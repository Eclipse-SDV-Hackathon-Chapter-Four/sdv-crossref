---
title: Detect silence with a clock, not with data
type: pattern
cluster: ipc-e2e
component: none
tags: [aliveness, deadline, liveliness, timeout, watchdog, dds, iceoryx2, waitset, e2e]
status: draft
sources:
  - https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_E2EProtocol.pdf (§6.2.3.2 Timeout detection; Table 6.7 NONEWDATA)
  - https://www.omg.org/spec/DDS/1.4/PDF (§2.2.3.7 DEADLINE, §2.2.3.11 LIVELINESS, REQUESTED_DEADLINE_MISSED)
  - repos/iceoryx2/iceoryx2/src/waitset.rs (attach_deadline, has_missed_deadline)
  - repos/iceoryx2/iceoryx2/src/lib.rs (event service `.deadline(...)`)
  - repos/iceoryx2/examples/rust/health_monitoring/README.md
  - repos/iceoryx2/iceoryx2-bb/posix/src/process_state.rs (file-lock process monitoring)
  - repos/iceoryx2/integrations/zenoh/link-carrier/src/lib.rs (offers as Zenoh liveliness tokens)
last-verified: 2026-10-03
related:
  - "[[the-transport-is-untrusted-the-consumer-checks-carry-safety]]"
  - "[[decide-once-per-cycle-in-a-fixed-order]]"
  - "[[reference-architecture-doctor-whodunit]]"
  - "[[iceoryx2-howto]]"
  - "[[uprotocol-howto]]"
applies-to: [iceoryx2, uprotocol, zenoh, vss-kuksa, ankaios, s-core]
gap-rows: [A8, A9, A10]
---

# Detect silence with a clock, not with data

**Problem.** A temperature sensor freezes, a producer process hangs, or a cable is pulled. Nothing arrives, so there is no counter gap, no bad CRC and no change event. A consumer that only runs when data arrives cannot notice, so the Guardian keeps deciding on the last value forever.

**Forces.**
- Event-driven code is idiomatic (callbacks, `subscribe().next()`, `onchange` sensors), but only arrivals make it run.
- A deadline that is too tight raises false alarms on jitter. One that is too loose exceeds the fault-tolerant time interval (FTTI).
- "The process is alive" and "the data is fresh" are different facts, checked by different mechanisms.
- At-most-once transports (uProtocol publish) lose single samples by design.

**The rule.** Every consumer of a periodic signal owns a **deadline on its own monotonic clock**, re-armed only by a *valid, new* sample (E2E OK or OKSOMELOST). REPEATED and NONEWDATA do not re-arm it. AUTOSAR states the precondition directly: timeouts are detectable only "when the receiver is running independently from the data transmission, i.e. … not blocked waiting", and NONEWDATA "may be considered similar to REPEATED" (§6.2.3.2, Table 6.7). Size the deadline as `period × (tolerated misses + 1) + jitter`, and keep it below the FTTI. Process liveness is checked separately, and it never stands in for data freshness.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| AUTOSAR E2E §6.2.3.2 | the receiver polls on its own cycle; no new data counts as a failed check | silence becomes a status, not an absence |
| DDS DEADLINE | the writer offers and the reader requests a period (offered ≤ requested); a miss raises REQUESTED_DEADLINE_MISSED | per-instance freshness contract checked at match time |
| DDS LIVELINESS | AUTOMATIC detects process failures only; MANUAL_BY_TOPIC needs the app to assert or write | the explicit split between process liveness and app liveness |
| iceoryx2 WaitSet / event `.deadline()` | `attach_deadline(&listener, d)`, `has_missed_deadline(&guard)` | a timed wake-up when nothing arrived, with no extra thread |
| iceoryx2 `health_monitoring` example | subscribers expect samples within a time; on a miss they check for dead nodes | deadline first, then the cause |
| EN 50159 time-out defence | the safety layer drives the safe state after silence | the rail version of the same rule |

**On the Eclipse SDV stack.**
- iceoryx2: pair each pub/sub service with an event service created with `.deadline(period)`. The consumer waits in a `WaitSet` with `attach_deadline`. On a miss it reads `NodeState` to separate "producer dead" (its file lock was released, `process_state.rs`) from "producer alive but silent". Dead-node detection is process-level, like DDS AUTOMATIC liveliness ([[iceoryx2-howto]]).
- Across hosts, iceoryx2-link offers are Zenoh **liveliness tokens**. They say the session is alive, not that the signal is fresh.
- uProtocol heartbeat: the Guardian's 1 Hz beat is at-most-once, so tolerate N misses ([[uprotocol-howto]]). The monitor runs on a timer.
- KUKSA: `onchange` sensors go silent when frozen, so the A8 watchdog must compare `Datapoint.timestamp` against now, not wait for updates ([[vss-kuksa-overview]]).
- Ankaios workload state (A9) is the process-liveness half, and it is not the data-freshness half.

**The trap.** Feeding the watchdog from inside the subscriber callback. When nothing arrives, the callback never runs and the watchdog never fires. The same happens with DDS AUTOMATIC liveliness when a thread is stuck in a live process.

**For a hackathon team.** Run a publisher at 10 Hz and a consumer with a WaitSet deadline of 250 ms. `kill -STOP` the producer (silent but alive), then `kill -9` it (dead). Show two different detections with timestamps. Pitch: "silence has a deadline; death has a lock file".

**Evidence.** The AUTOSAR quotes are from PRS E2E R22-11 lines on timeout detection, read 2026-10-03. The DDS text is from DDS 1.4 §2.2.3.7 and §2.2.3.11. The iceoryx2 API was confirmed in `waitset.rs` lines 88–98 and in the event builder docs in `lib.rs`. File-lock liveness was confirmed in `process_state.rs`. The latency of event wake-ups on RT kernels is reported in iceoryx2 issue #1240 (see [[iceoryx2-overview]]); it was not measured here.
