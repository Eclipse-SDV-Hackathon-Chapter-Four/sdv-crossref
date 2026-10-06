---
title: Refuse loudly — a mismatch on arrival is evidence, not silence
type: pattern
cluster: identity-discovery
component: none
tags: [discovery, capability-negotiation, refusal, evidence, dds, qos, someip, iceoryx2, sovd, doctor-whodunit]
status: draft
sources:
  - https://www.omg.org/spec/DDS/1.4/ (REQUESTED_INCOMPATIBLE_QOS / OFFERED_INCOMPATIBLE_QOS: total_count, last_policy_id, policies; INCONSISTENT_TOPIC)
  - https://www.omg.org/spec/DDS-XTypes/1.3/PDF (§7.6.3.4.2: inconsistent types → INCONSISTENT_TOPIC on both sides)
  - https://www.autosar.org/fileadmin/standards/R23-11/FO/AUTOSAR_FO_PRS_SOMEIPServiceDiscoveryProtocol.pdf (SubscribeEventgroupNack, PRS_SOMEIPSD_00393)
  - https://www.autosar.org/fileadmin/standards/R23-11/FO/AUTOSAR_FO_PRS_SOMEIPProtocol.pdf (E_WRONG_INTERFACE_VERSION 0x08)
  - repos/iceoryx2/iceoryx2/src/service/builder/publish_subscribe.rs (IncompatibleTypes, IncompatibleAttributes, IncompatibleMessagingPattern, DoesNotSupportRequested*)
  - https://github.com/ros2/rmw_zenoh/blob/rolling/docs/design.md (type hash in key: non-matching, no event)
last-verified: 2026-10-03
related:
  - "[[match-on-the-type-descriptor-never-fall-back-to-the-name]]"
  - "[[a-type-name-is-a-claim-a-layout-hash-is-a-proof]]"
  - "[[pin-the-major-wildcard-the-instance]]"
  - "[[open-on-arrival-age-by-your-own-deadline]]"
  - "[[evidence-is-a-linked-record-not-a-log]]"
  - "[[a-fault-is-a-state-machine-with-evidence-attached]]"
  - "[[opensovd-reference]]"
applies-to: [iceoryx2, opensovd, zenoh, uprotocol, vss-kuksa]
gap-rows: [A1, A5, A12, H2]
---

# Refuse loudly — a mismatch on arrival is evidence, not silence

**Problem.** A new producer arrives with the wrong schema version, a smaller buffer, or a different QoS. The consumer correctly declines to connect — and nobody ever learns why the value on the dashboard is stale. In an incident review ("Doctor Whodunit") the most useful fact, *who refused whom and why*, was never written down.

**Forces.**
- Refusal must be fail-safe: no partial or coerced connection for deciding consumers.
- The reason must be specific (which policy, expected vs offered), or nobody can fix it.
- Mismatches can repeat every discovery cycle; the record must not flood.
- Some designs refuse by construction (keys never match) and so cannot report at all.

**The rule.** Every compatibility check on arrival produces **one of two outcomes, both recorded**: *accepted* (with the negotiated parameters) or *refused* (with consumer, producer identity, the failed check, expected and offered values). Refusals are counted and deduplicated per (consumer, producer, reason), surfaced as a diagnostic fault or data resource, and never turned into a fallback. DDS shows the shape: an incompatible QoS raises `REQUESTED_INCOMPATIBLE_QOS` on the reader and `OFFERED_INCOMPATIBLE_QOS` on the writer with `total_count`, `last_policy_id` and per-policy counts; a type mismatch raises `INCONSISTENT_TOPIC` on both. SOME/IP answers `SubscribeEventgroupNack` and `E_WRONG_INTERFACE_VERSION`. iceoryx2 returns typed errors (`IncompatibleTypes`, `IncompatibleAttributes` with the failing key in the log, `DoesNotSupportRequestedAmountOfSubscribers`, `VersionMismatch`). Designs where a mismatch merely fails to match — rmw_zenoh's type hash in the key — need a separate observer that lists announced-but-unmatched peers.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| DDS 1.4 status conditions | `*_INCOMPATIBLE_QOS` with `last_policy_id`; `INCONSISTENT_TOPIC` | refusal is a listener event on both sides |
| SOME/IP-SD / SOME/IP | `SubscribeEventgroupNack`; return code `E_WRONG_INTERFACE_VERSION` | the provider tells the client no, and why |
| iceoryx2 open errors | typed refusal per check (types, attributes, pattern, limits, version) | a reason code before the first sample |
| Sparkplug B | unknown metric/alias → rebirth request | refusal triggers re-sync, visibly |
| rmw_zenoh | type hash in key; mismatch = no match | safe, but silent — the counter-example |

**On the Eclipse SDV stack.**
- iceoryx2 consumers that open on arrival ([[open-on-arrival-age-by-your-own-deadline]]) publish each refusal on an `evidence/refusals` service and log it; the error enum *is* the reason code.
- OpenSOVD: expose refusals as a `faults` entry on the consumer's entity (gap A1) with environment data = expected/offered, and as a `triggers` source (gap H2); the MCP tools (gap A12) then answer "why is this stale?" directly ([[opensovd-reference]]).
- Zenoh / rmw_zenoh: an evidence recorder (gap A5) subscribes to liveliness (`@ros2_lv/**`) and flags topics announced with two different type hashes.
- KUKSA: `ALREADY_EXISTS` on a second provider claim is a refusal worth recording, not a retry loop ([[vss-kuksa-reference]]).

**The trap.** `if let Ok(port) = open(...)` with the `Err` arm dropped, so the system is safe and undiagnosable.

**For a hackathon team.** Start a producer with `schema.major=3` next to a consumer requiring 2; show the refusal appearing as a SOVD fault with expected/offered values within one discovery cycle, deduplicated on repeat. Pitch: "our system says no — and tells you why".

**Evidence.** DDS 1.4 §2.2.4.1 communication status table (IncompatibleQosStatus fields), unverified against the PDF page in this session but standard API in all DDS vendors. XTypes 1.3 §7.6.3.4.2 ("shall trigger an INCONSISTENT_TOPIC status change for both"). SOME/IP-SD PRS_SOMEIPSD_00393; SOME/IP PRS return code table (0x08). iceoryx2 `publish_subscribe.rs` L50–70, L640–700. rmw_zenoh key format: design.md. Observed `IncompatibleTypes` and `VersionMismatch`: [[iceoryx2-quickstart]].
