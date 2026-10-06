---
title: Pick the messaging pattern by signal class; state is last-value, events are history
type: pattern
cluster: ipc-e2e
component: none
tags: [messaging-patterns, pub-sub, request-response, event, blackboard, field, ara-com, lola, iceoryx2, history]
status: draft
sources:
  - repos/iceoryx2/README.md (messaging patterns)
  - repos/iceoryx2/examples/rust/blackboard/README.md
  - repos/iceoryx2/iceoryx2/src/port/reader.rs (`is_up_to_date`, per-entry generation counter)
  - repos/iceoryx2/doc/release-notes/ (v0.10.0 #1185 per-subscriber history)
  - repos/s-core-communication/score/mw/com/doc/tutorial/README.rst (proxy/skeleton, ara::com roots)
  - repos/s-core-communication/score/mw/com/doc/tutorial/chapter_9/README.rst (field notifier vs getter)
  - https://www.omg.org/spec/DDS/1.4/PDF (§2.2.3.18 HISTORY)
  - repos/up-spec/up-l3/README.adoc (RPC at-least-once, publish at-most-once)
last-verified: 2026-10-03
related:
  - "[[loss-is-counted-at-the-consumer-never-hidden-by-the-buffer]]"
  - "[[stamp-the-instant-once-refuse-the-spread]]"
  - "[[a-fault-is-a-state-machine-with-evidence-attached]]"
  - "[[iceoryx2-overview]]"
  - "[[s-core-overview]]"
applies-to: [iceoryx2, s-core, uprotocol, opensovd, vss-kuksa]
gap-rows: [A2, A10, B3, B4]
---

# Pick the messaging pattern by signal class; state is last-value, events are history

**Problem.** A fault is published as a "last value" field, and two faults within one consumer cycle become one. Or a temperature is queued as a deep-history event stream, and the Guardian acts on a reading that is three cycles old. Either way the pattern choice made the decision wrong, with no transport error to show for it.

**Forces.**
- For state, only the newest value matters. For events, every one matters.
- Deeper buffers hide loss but deliver stale data. Shallow buffers are fresh but lossy.
- Late joiners need the current state, and sometimes the recent past.
- Each pattern has a different memory and wake-up cost.

**The rule.** Classify each signal first, then choose the pattern:

| Signal class | iceoryx2 | LoLa / ara::com | Buffer and history |
|---|---|---|---|
| periodic **state** (temperature, speed) | publish-subscribe | event, or field with notifier | buffer 1–2, history 1 for late joiners, safe overflow on: newest wins |
| sporadic **event** (fault raised, button) | publish-subscribe | event | buffer ≥ worst burst; safe overflow off or a counted loss; never last-value |
| shared **configuration / mode** | blackboard (one writer, `Copy` values, per-entry generation counter) | field with getter (and setter) | no history; readers check `is_up_to_date` |
| **wake-up** only | event (Notifier/Listener, no payload) | receive handler | combine with pub/sub, and carry a deadline |
| **command** with an outcome | request-response (streaming responses) | method | correlation id; caller-side timeout |

Last-value-wins is correct for state and wrong for events. History is correct for events and dangerous for state.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ara::com (Adaptive AUTOSAR) | events, fields (notifier/getter/setter), methods on proxy/skeleton | the automotive vocabulary that LoLa reuses |
| S-CORE LoLa ch. 9 | notifier + `GetNewSamples()` and `Get()` have no *semantic* difference, only one of efficiency | a field is state, however you read it |
| DDS HISTORY | KEEP_LAST depth 1 is the default; KEEP_ALL is bounded by RESOURCE_LIMITS | state vs event as one QoS knob |
| iceoryx2 patterns | pub/sub, request-response, event, blackboard; per-subscriber history since 0.10 | all five rows in one library |
| uProtocol L3 | publish/notification at-most-once, RPC at-least-once | delivery semantics follow the pattern |

**On the Eclipse SDV stack.**
- OpenSOVD fault-lib → DFM already uses iceoryx2 **pub/sub** for fault records (`dfm/event`), which is the event row. A2's HTTP bridge must not collapse it into a last-value cache ([[a-fault-is-a-state-machine-with-evidence-attached]]).
- A KUKSA → iceoryx2 provider (B3) maps sensors to pub/sub with depth 1, and attributes or configuration to a blackboard.
- A LoLa ↔ other bridge (B4) maps a field to state and an event to history, keeping `numberOfSampleSlots` ≥ the burst.
- A blackboard read of two keys is not a snapshot (see [[stamp-the-instant-once-refuse-the-spread]]).

**The trap.** Choosing by convenience ("everything is a field" or "everything is a topic with history 10"). Faults then merge, or decisions run on queued, stale state.

**For a hackathon team.** Put Guardian temperature on pub/sub with depth 1, faults on pub/sub with a 16-slot buffer and a counter, and the thresholds on a blackboard. Send three faults inside one consumer cycle and show all three arrive. Pitch: "state is last-value, events are history, configuration is a blackboard".

**Evidence.** The iceoryx2 patterns are from the README and the blackboard example. `is_up_to_date` is in `reader.rs` (lines 496 and 612). Per-subscriber history is release note #1185. The LoLa field semantics are from tutorial chapter 9, lines 22–56. The DDS text is from §2.2.3.18. The fault-lib services are from [[iceoryx2-integration-notes]]. The uProtocol semantics are from [[uprotocol-overview]].
