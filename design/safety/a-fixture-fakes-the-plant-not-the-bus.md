---
title: A fixture fakes the plant, not the bus
type: pattern
cluster: safety
component: none
tags: [fixture, simulation, plant-model, hil, sil, actuator, kuksa, fault-injection, closed-loop]
status: draft
sources:
  - repos/kuksa-databroker/doc/protocol.md (current / target / actuation per API)
  - repos/kuksa-proto/kuksa/val/v2/val.proto (OpenProviderStream, ALREADY_EXISTS on a second claim)
  - repos/kuksa-databroker/doc/user_guide.md (databroker "only forwards actuator values")
  - https://www.iso.org/standard/68383.html (ISO 26262-4: HIL/SIL as verification environments, unverified section)
  - https://www.asam.net/standards/detail/xil/ (ASAM XIL: test-bench model access, unverified)
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-overview]]"
  - "[[ankaios-howto]]"
  - "[[detect-silence-with-a-clock-not-with-data]]"
  - "[[kill-restart-delete-are-test-actions]]"
applies-to: [vss-kuksa, ankaios]
gap-rows: [D9, D4, A6]
---

# A fixture fakes the plant, not the bus

**Problem.** With no hardware in the room, teams replay CSV or DBC frames into the databroker. The sensor values look real, but nothing ever answers a command, so the closed loop (command, delay, effect, measurement, decision) is never exercised. The first time a mitigation meets a real actuator is the demo.

**Forces.**
- A bus replay is cheap and already shipped (CSV and CAN providers); a plant model has to be written.
- The plant's behaviour is what the function under test reacts to: lag, overshoot, side effects, a stuck valve.
- The fixture must be swappable for the real driver without touching the consumer, or it tests a different system.
- Fault injection on the bus (drop, delay) is not the same as a failing actuator that keeps answering.

**The rule.** Fake the *plant's response to a command*, behind the same actuator interface the real plant would own. The fixture claims the actuator, reads the requested target, moves the current value toward it at a configured rate after a configured delay, applies declared cross-effects to other signals (defrost on lowers cabin humidity, seat heater raises battery load) and supports named failure modes: `stuck`, `slow`, `overshoot`, `no-ack`. Everything is declared in a YAML file, so the scenario is data and the consumer cannot tell fixture from driver. Bus-level replay stays for sensors that have no command path.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Hardware-in-the-loop benches | a real-time plant model closes the loop around a real ECU | the controller sees physics, not recordings (unverified detail) |
| Software-in-the-loop (ISO 26262-4 verification environments) | the same plant model runs against compiled code on a PC | closed-loop tests without a bench (unverified section) |
| ASAM XIL | a standard API for test benches to reach model variables | the fixture's knobs are addressable by a test script (unverified) |
| KUKSA v2 actuation | `Actuate` goes to the one provider that claimed the signal; the value is published separately | target and current are distinct channels, so a fixture can lag between them ([[vss-kuksa-overview]]) |

**On the Eclipse SDV stack.** In KUKSA databroker v2 a provider opens `OpenProviderStream`, claims the actuator paths (a second claim gets `ALREADY_EXISTS`), receives actuation requests and publishes the resulting value with `PublishValue` ([[vss-kuksa-reference]]). The fixture is that provider. KUKSA itself "only forwards actuator values" ([[vss-kuksa-overview]]), so whether the value ever arrives is exactly the behaviour the fixture controls. In [[ankaios-howto]] the fixture and the real CAN driver are two workloads with the same claimed paths; the manifest decides which one runs, which is gap D4's portability claim made testable. Failure modes are toggled at runtime, so a fault campaign (A6, [[kill-restart-delete-are-test-actions]]) can say "stick the HVAC actuator" instead of "drop frames".

**The trap.** A fixture that sets current equal to target instantly hides every timing bug: no timeout is ever reached, no retry ever fires, and [[detect-silence-with-a-clock-not-with-data]] never gets tested.

**For a hackathon team.** One Python provider, one YAML file with three actuators, a rate, a delay and a `stuck` flag; demo the Guardian commanding the fan, the fixture refusing to move, and the Guardian escalating. Pitch: "we tested against a plant that can fail, not against a recording".

**Evidence.** KUKSA claim/actuate semantics: `val.proto` and `doc/protocol.md` read for [[vss-kuksa-reference]]; "only forwards" quote from `doc/user_guide.md` via [[vss-kuksa-overview]]. HIL/SIL/XIL rows are general practice, not checked against the standards text (unverified). The fixture itself is P (unverified): nothing in the vault runs one.
