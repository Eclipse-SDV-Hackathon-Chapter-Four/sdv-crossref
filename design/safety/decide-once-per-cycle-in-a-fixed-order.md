---
title: Decide once per cycle, in a fixed order
type: pattern
cluster: safety
component: none
tags: [feo, determinism, time-triggered, scheduling, s-core, iceoryx2, let]
status: draft
sources:
  - repos/s-core-score/docs/features/frameworks/feo/index.rst (FEO feature request, ASIL_B)
  - repos/feo/examples/rust/mini-adas/README.md (com_iox2 / com_linux_shm / com_mw backends)
  - https://github.com/eclipse-score/feo
  - https://doi.org/10.1109/JPROC.2002.805821 (Kopetz & Bauer, The Time-Triggered Architecture, Proc. IEEE 2003)
  - https://doi.org/10.1007/3-540-45449-7_12 (Henzinger et al., Giotto, EMSOFT 2001; logical execution time) (DOI unverified)
  - https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_OS.pdf (schedule tables)
last-verified: 2026-10-03
related:
  - "[[s-core-overview]]"
  - "[[iceoryx2-overview]]"
  - "[[record-at-the-seam-replay-with-the-original-clock]]"
  - "[[deciding-on-a-bad-state-is-wrong-not-degraded]]"
applies-to: [s-core, iceoryx2, vss-kuksa]
gap-rows: [A8, A5]
---

# Decide once per cycle, in a fixed order

**Problem.** An event-driven safety function wakes on every arrival. Cell temperature 3 arrives, the decider runs on a mix of this cycle's T3 and last cycle's T1/T2, a second arrival re-runs it, and the output depends on scheduler luck. Two runs of the same input give different warnings, so the test is not evidence and the silence of a dead sensor never wakes anything.

**Forces.**
- Safety decisions need a consistent snapshot; event-driven code sees a moving one.
- Latency pressure argues for reacting on arrival.
- Replay and regression need the same inputs to produce the same outputs, bit for bit.
- Silence must be observable; a cycle observes it for free, an event loop never does.

**The rule.** Run the deciding logic on a clock, not on arrivals: once per cycle, input service activities first (sample, timestamp and validate every input), then application activities in a dependency order fixed at build time, then output activities. Every input is read once per cycle from a "runtime static" topic, so the decision is a pure function of (snapshot, state). Missing input becomes an explicit "no data this cycle" value, not a missing wake-up. Event-driven code stays where it belongs: observers, loggers, the evidence tap.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| S-CORE FEO | activities with `init/step/shutdown`, one task chain per app, cyclic (e.g. 30 ms), static activity→thread mapping, input/output service activities at chain ends, topics fixed after startup | the S-CORE-native shape; "execution order and timing … independent of any communication" |
| Time-Triggered Architecture (Kopetz) | all actions triggered by a global time base; temporal firewalls | composability and replica determinism |
| Giotto / logical execution time | inputs read at period start, outputs released at period end | output timing independent of actual execution time |
| AUTOSAR OS schedule tables | statically configured expiry points activating tasks | the Classic-platform version of fixed activation |
| iceoryx2 as FEO `com_iox2` backend | zero-copy topics under FEO's static wiring | same model on the IPC this vault already uses |

**On the Eclipse SDV stack.** FEO lives in eclipse-score/feo, Bazel-only, feature flag `experimental_feo`, target ASIL_B, and is **not in known_good.json** today ([[s-core-overview]]). Its mini-adas example switches backends: `com_iox2`, `com_linux_shm`, `com_mw` (LoLa). Error handling is fail-silent: any `step()` failure or timeout makes the primary call `shutdown()` on all activities and terminate; budget overruns "shall be detected and handled outside of FEO" (FEO index.rst). So FEO needs an external supervisor ([[one-watchdog-per-layer-each-blind-to-the-others]]). For a Guardian without Bazel: a Rust loop on `tokio::time::interval` that snapshots the latest KUKSA values (with their timestamps) into one struct, then decides, is the same pattern ([[vss-kuksa-overview]]).

**The trap.** "Cyclic" code that still blocks on `subscribe().next()` inside the cycle: one silent sensor stalls the whole cycle and the heartbeat with it.

**For a hackathon team.** A 100 ms Guardian loop with three phases (sample → decide → publish), each cycle stamped with a cycle counter that goes into every fault and mitigation event. Show that replaying the same CSV twice yields identical event sequences. Pitch: "the Guardian decides once per instant of the vehicle, never on a half-updated picture".

**Evidence.** FEO semantics and error handling quoted from repos/s-core-score/docs/features/frameworks/feo/index.rst ("Scheduling", "Error Handling"); backends from repos/feo/examples/rust/mini-adas/README.md. FEO's own requirements still carry `:valid_from: v2.0.0` (feature_req.rst), i.e. it is not a v1.0 deliverable. TTA/Giotto from the cited papers (not re-read here).
