---
title: Record at the seam, replay with the original clock
type: pattern
cluster: safety
component: none
tags: [determinism, replay, reprocessing, golden-vectors, conformance, n-version, evidence]
status: draft
sources:
  - repos/iceoryx2/iceoryx2-userland/record-and-replay/src/{record.rs,replayer.rs,record_header.rs}
  - repos/s-core-score/docs/features/frameworks/feo/index.rst (reprocessing)
  - https://github.com/ros2/rosbag2 (ROS 2 bag record/play)
  - https://github.com/C2SP/wycheproof (shared test vectors run against independent implementations)
  - https://csrc.nist.gov/projects/cryptographic-algorithm-validation-program (known-answer tests)
  - https://www.w3.org/2005/rules/wiki/CR_Exit_Criteria (W3C: two independent interoperable implementations per feature)
  - https://doi.org/10.1109/TSE.1986.6312924 (Knight & Leveson 1986, correlated failures in N-version programming)
last-verified: 2026-10-03
related:
  - "[[evidence-is-a-linked-record-not-a-log]]"
  - "[[decide-once-per-cycle-in-a-fixed-order]]"
  - "[[iceoryx2-overview]]"
  - "[[opendut-overview]]"
  - "[[uprotocol-howto]]"
applies-to: [iceoryx2, s-core, uprotocol, opendut, vss-kuksa]
gap-rows: [A5, A6, A7, A10]
---

# Record at the seam, replay with the original clock

**Problem.** A fault campaign found a missed warning. Rerunning it live gives a different interleaving and the miss is gone. The team cannot show the failure again, cannot show the fix works on the *same* input, and cannot tell whether two Guardians disagree because of the code or the timing.

**Forces.**
- Live runs are realistic but not repeatable; replays are repeatable but only as faithful as what was recorded.
- Wall-clock time at replay is meaningless; the decider must read the recorded time.
- Recording everything is easy; recording the right thing (the inputs to the decision, at the boundary) is the point.
- "Our two implementations agree" is only evidence if they were built independently from the spec.

**The rule.** Record exactly the seam the decider reads (its input topics, with producer timestamps and counters, byte for byte), plus the decider's outputs. Replay feeds those bytes through the same seam with the **recorded** time injected as the decider's clock (no `now()` inside the decider), so a replay is bit-reproducible. Freeze interesting recordings as **golden vectors**: input file + expected output file, checked in, run in CI. For conformance, have a second, independently written implementation (another language or team, from the written spec only) consume the same vectors; disagreement is a finding about the spec or one implementation, agreement is evidence, with the known caveat that independent teams still make correlated mistakes.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| iceoryx2 record-and-replay | `iox2 service record/replay`; header holds payload type info and messaging pattern; per-record capture timestamp; replay refuses timestamps that go backwards | a seam recorder already on the S-CORE/iceoryx2 path |
| S-CORE FEO reprocessing | framework support to re-run activities in a simulated environment with framework-provided time (`feo::time`) | the decider-reads-injected-time rule, built in |
| ROS 2 rosbag2 | record topics with timestamps; play with clock publication (`/clock`) | the robotics norm for replay with simulated time |
| Wycheproof, NIST CAVP | shared test vectors; known-answer tests across independent implementations | golden vectors as a conformance contract |
| W3C CR exit criteria | two independent interoperable implementations per feature | "two implementations agree" as a spec-quality gate |
| Knight & Leveson 1986 | N-version failures are correlated | why agreement is evidence, not proof |

**On the Eclipse SDV stack.** iceoryx2's recorder stores the *capture* time at the recorder in milliseconds, not the producer's time: put producer timestamp and counter in the payload (or user header) so ordering survives ([[iceoryx2-overview]]). On uProtocol/Zenoh there is no recorder (gap A5); a subscribe-all tap writing `UMessage` bytes + attributes is the seam recorder ([[uprotocol-howto]]). KUKSA CSV providers are replayable input but re-stamp time on publish ([[vss-kuksa-overview]]). openDuT has no replay (gap A6); the uProtocol fault shim (A7) is the deterministic injector. Golden vectors for the heartbeat/fault/mitigation schema (A10) let a Rust and a Python Guardian be checked against each other.

**The trap.** Calling `SystemTime::now()` inside the decider, so every replay is a new experiment.

**For a hackathon team.** Record one campaign at the Guardian's input, check in `vectors/stuck_cell.{in,out}`, and run the Rust Guardian and a 50-line Python reference checker against it in CI. Pitch: "every bug we found is a file you can replay, and two independent implementations agree on it".

**Evidence.** iceoryx2 record format read in repos/iceoryx2/iceoryx2-userland/record-and-replay/src (record.rs "The time this data was captured", `timestamp: Duration`; replayer.rs millisecond monotonicity check). FEO reprocessing from FEO index.rst (mechanism details not verified in code). rosbag2 `--clock` from prior knowledge (unverified here). W3C criterion from the W3C wiki page; strictness varies by working group.
