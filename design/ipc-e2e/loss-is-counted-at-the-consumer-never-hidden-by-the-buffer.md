---
title: Loss is counted at the consumer, never hidden by the buffer
type: pattern
cluster: ipc-e2e
component: none
tags: [backpressure, history, buffer, overflow, reliability, best-effort, sample-lost, iceoryx2, dds, lola, zenoh]
status: draft
sources:
  - repos/iceoryx2/iceoryx2/src/config.rs (publish_subscribe defaults)
  - repos/iceoryx2/iceoryx2/src/port/backpressure_strategy.rs (RetryUntilDelivered, DiscardData)
  - repos/iceoryx2/examples/rust/publish_subscribe_with_backpressure/README.md
  - repos/iceoryx2/FAQ.md ("Failed To Create Port Due To ExceedsMaxSupported**")
  - https://www.omg.org/spec/DDS/1.4/PDF (§2.2.3.14 RELIABILITY, §2.2.3.18 HISTORY, SAMPLE_LOST)
  - repos/s-core-communication/score/mw/com/dependability/software_architectural_design/pci_e_gateway/README.md (max_samples AoU)
  - repos/zenoh/DEFAULT_CONFIG.json5 (congestion_control drop/block)
  - https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_E2EProtocol.pdf (OKSOMELOST, MaxDeltaCounter)
last-verified: 2026-10-03
related:
  - "[[the-transport-is-untrusted-the-consumer-checks-carry-safety]]"
  - "[[pick-the-pattern-by-signal-class]]"
  - "[[freedom-from-interference-is-a-stack-of-layers]]"
  - "[[iceoryx2-howto]]"
applies-to: [iceoryx2, s-core, zenoh, uprotocol, opensovd]
gap-rows: [H1, A5, A8]
---

# Loss is counted at the consumer, never hidden by the buffer

**Problem.** A subscriber falls behind and the transport silently overwrites the oldest samples. Or someone turns on blocking "so nothing is lost", and a slow logging consumer now stalls the safety producer. Either way the safety case says nothing about loss, because nobody counted it.

**Forces.**
- Every buffer is finite: something drops, blocks or fails when it is full.
- Blocking pushes a consumer's slowness into the producer, which is interference across criticality levels.
- Middleware loss counters (where they exist) are per hop. Only an end-to-end counter sees the whole path.
- Port limits are preallocated, and dead ports use them up.

**The rule.** For each service, decide **what happens when full** and make the **consumer count** it. Safety producers never block on consumers: use overwrite (state) or discard (events), and let every consumer measure loss from the frame's own counter. OKSOMELOST (gap ≤ `MaxDeltaCounter`) and WRONGSEQUENCE (beyond) are separate counters with separate policies. Backpressure (`RetryUntilDelivered`) is allowed only between components of equal criticality, with a bounded wait. Raise port limits deliberately, and treat `ExceedsMaxSupported*` as a cleanup signal first.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| iceoryx2 defaults (`config.rs`) | buffer 2, history 0, 2 publishers, 8 subscribers, 20 nodes, **`enable_safe_overflow: true`** | the oldest sample is overwritten; no lost-sample counter was found on the Subscriber API |
| iceoryx2 backpressure | safe overflow off + `RetryUntilDelivered` or `DiscardData`, plus a publisher-side handler | an explicit full-buffer policy |
| DDS RELIABILITY / HISTORY | BEST_EFFORT never retransmits but keeps order; RELIABLE + KEEP_ALL blocks the writer up to `max_blocking_time`; SAMPLE_LOST status | the standard vocabulary for the trade |
| S-CORE LoLa AoU | if `GetNewSamples()` returns `max_samples`, "a potential overflow/data-loss might have happened" | loss is inferred by the consumer, and a gateway cannot forward it |
| Zenoh congestion control | `drop` waits 1 ms, then drops; `block` closes the session after 5 s | per-hop policy, invisible end to end |
| AUTOSAR E2E | OKSOMELOST vs WRONGSEQUENCE by `MaxDeltaCounter` | loss tolerance written as a number |

**On the Eclipse SDV stack.**
- iceoryx2: the defaults are right for state (newest wins) and wrong for events. Raise `subscriber_max_buffer_size` to the burst for fault streams, keep safe overflow on, and count gaps from the frame counter. Ports are preallocated, so `max_subscribers` is a memory decision ([[iceoryx2-howto]]).
- A QM logger or recorder subscribing to an ASIL producer must never be able to backpressure it ([[freedom-from-interference-is-a-stack-of-layers]]). This is the concrete FFI argument for `enable_safe_overflow`.
- H1 (SSE cyclic subscriptions): when a client lags, surface the loss as an error envelope rather than dropping silently. Same rule, HTTP edition.
- uProtocol publish is at-most-once, and `send()` success is not a delivery receipt ([[uprotocol-howto]]). The counter in the payload is the only loss meter.

**The trap.** Turning on blocking or retry "to never lose data", and letting the slowest, least critical consumer set the producer's timing.

**For a hackathon team.** Show a per-reason counter panel (OK, OKSOMELOST, WRONGSEQUENCE, REPEATED, timeout) fed by the consumer. Then `kill -STOP` a slow subscriber and show the producer's period unchanged while that subscriber's OKSOMELOST rises. Pitch: "we never hide loss, we count it, and no consumer can slow the producer".

**Evidence.** Defaults were read in `iceoryx2/src/config.rs` (publish_subscribe defaults block). "No lost-sample counter" comes from a grep of `port/subscriber.rs` that found only `enable_safe_overflow`; the absence is not proven. The backpressure enum is in `backpressure_strategy.rs`. The DDS text is from §2.2.3.14 and §2.2.3.18. The LoLa AoU is quoted from the PCIe gateway note. The Zenoh values are from `DEFAULT_CONFIG.json5`.
