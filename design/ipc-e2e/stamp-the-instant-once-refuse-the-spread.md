---
title: Stamp the instant once; refuse a spread instead of deciding on it
type: pattern
cluster: ipc-e2e
component: none
tags: [coherence, consistency, sequence-stamp, signal-group, dds-presentation, blackboard, snapshot, decision]
status: draft
sources:
  - https://www.omg.org/spec/DDS/1.4/PDF (§2.2.3.6 PRESENTATION: coherent_access, ordered_access, access_scope)
  - https://autosar.org/fileadmin/standards/R21-11/CP/AUTOSAR_SRS_COM.pdf (signal groups, consistent transfer)
  - repos/iceoryx2/iceoryx2/src/port/reader.rs (blackboard per-entry `is_up_to_date`)
  - https://github.com/eclipse-score/feo (fixed execution order)
last-verified: 2026-10-03
related:
  - "[[coherence-is-a-set-property-declared-in-the-model]]"
  - "[[decide-once-per-cycle-in-a-fixed-order]]"
  - "[[pick-the-pattern-by-signal-class]]"
  - "[[reference-architecture-doctor-whodunit]]"
  - "[[iceoryx2-overview]]"
applies-to: [iceoryx2, s-core, vss-kuksa, zenoh, uprotocol]
gap-rows: [C8, B3, B10]
---

# Stamp the instant once; refuse a spread instead of deciding on it

**Problem.** The Guardian needs cell temperature, pack current and coolant flow. It reads each from its own service. Temperature is from pass 41, current from pass 42, and flow is three passes old. The rule "high temperature and no coolant flow" fires on a combination that never existed in the vehicle.

**Forces.**
- Transports give atomicity per sample (one iceoryx2 sample, one blackboard entry, one DDS instance), never across services.
- Merging everything into one struct couples producers that run on different nodes and cadences.
- Waiting for alignment adds latency, and deciding on a mix adds wrong decisions.
- Wall clocks across nodes disagree, while pass counters only exist where somebody stamps them.

**The rule.** Coherence comes from the producer. A consumer cannot reconstruct it.
1. Readings from **one producer** that must agree go in **one sample** (one struct, one E2E seal). That is the cheapest coherence there is.
2. Readings from **several producers** carry the **same pass/sequence stamp**, issued once per instant by the cycle that samples them.
3. The consumer collects the newest sample of each set and **decides only if the stamps match**, or fall inside a declared window. Otherwise it holds the last decision (bounded) or rejects.

A spread is a status to count and report, never input to a decision. Decide once per stamp, never once per arrival.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| DDS PRESENTATION | `coherent_access` with `access_scope` INSTANCE / TOPIC / GROUP; `begin_coherent_changes` groups writes, and GROUP spans the DataWriters of one Publisher | middleware-level multi-topic snapshots, but only within one publisher |
| AUTOSAR COM signal groups | signals of one composite type are kept in one I-PDU through a shadow buffer | "one producer, one sample" in the CAN world |
| S-CORE FEO | a fixed execution order per cycle; inputs read once per cycle | the stamp is the cycle ([[decide-once-per-cycle-in-a-fixed-order]]) |
| VSS struct / aggregate | the model declares which leaves belong together | the set is declared in the model ([[coherence-is-a-set-property-declared-in-the-model]]) |
| iceoryx2 blackboard | per-entry generation counter, `is_up_to_date` | each entry is consistent; two entries are not a snapshot |

**On the Eclipse SDV stack.**
- iceoryx2: carry `pass_id: u64` in the user header next to the E2E header. The consumer keeps one slot per service and compares `pass_id` values. A blackboard does not give a multi-key snapshot, so a set that must agree goes in one blackboard value (a `Copy` struct), not in N keys.
- KUKSA: `Datapoint.timestamp` is per leaf. A provider that writes a set should give every leaf the same timestamp, so consumers can check the spread.
- Placement (C8): the stamp authority is whoever runs the sampling cycle, written in the placement manifest. Two nodes producing parts of one set need a shared cycle or an explicit window.
- Across Zenoh or uProtocol hops the stamp is inside the sealed payload, so routers cannot disturb it ([[forward-sealed-frames-byte-for-byte]]).

**The trap.** Reading two subscribers or two blackboard keys back to back and assuming they describe the same instant, because the reads were microseconds apart.

**For a hackathon team.** Run two producers stamped by one 10 Hz cycle counter, delay one by 150 ms with a fault-injection shim, and show the consumer refusing the spread (a "spread" counter on the dashboard) instead of tripping. Pitch: "we decide once per instant, and we can prove which instant".

**Evidence.** PRESENTATION semantics are quoted from DDS 1.4 §2.2.3.6. The AUTOSAR signal-group and shadow-buffer description is from SRS COM and secondary summaries; the SWS COM text was not read (unverified detail). Blackboard per-entry semantics are from `reader.rs`. The "spread is refused" rule restates [[reference-architecture-doctor-whodunit]] §4 and makes the transport limits explicit.
