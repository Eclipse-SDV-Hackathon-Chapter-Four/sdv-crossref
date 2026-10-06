---
title: A recording is evidence only if it keeps the producer's stamps; a replay is a stimulus
type: pattern
cluster: ipc-e2e
component: none
tags: [record, replay, evidence, timestamps, counters, mcap, rosbag2, iceoryx2, fault-injection]
status: draft
sources:
  - repos/iceoryx2/iceoryx2-cli/iox2-service/src/command/record.rs (timestamp = recorder elapsed at receive)
  - repos/iceoryx2/iceoryx2-cli/iox2-service/src/cli.rs (cycle_time_in_ms default 1, repetitions, time_factor)
  - repos/iceoryx2/iceoryx2-cli/iox2-service/src/command/replay.rs (sleep to recorded ms × time_factor)
  - repos/iceoryx2/iceoryx2-userland/record-and-replay/src/record_header.rs (iceoryx2 version, service name, types, file format)
  - repos/iceoryx2/iceoryx2/src/service/header/publish_subscribe.rs (no time, no sequence in the system header)
  - https://mcap.dev/spec (Message: sequence, log_time, publish_time)
  - https://www.omg.org/spec/DDSI-RTPS/ (writer GUID + sequence number per sample)
last-verified: 2026-10-03
related:
  - "[[evidence-is-a-linked-record-not-a-log]]"
  - "[[let-the-standard-timestamp-your-evidence]]"
  - "[[loss-is-counted-at-the-consumer-never-hidden-by-the-buffer]]"
  - "[[the-transport-is-untrusted-the-consumer-checks-carry-safety]]"
  - "[[iceoryx2-overview]]"
applies-to: [iceoryx2, uprotocol, zenoh, opensovd, opendut]
gap-rows: [A5, A6, A7, H2]
---

# A recording is evidence only if it keeps the producer's stamps; a replay is a stimulus

**Problem.** A team records the Guardian's input with `iox2 service record`, replays it, and presents the timeline as proof of when the fault happened. The times are the recorder's receive times, rounded to its poll cycle. Samples it missed while busy left no trace. The replayed run differs from the live run in publisher identity and timing, and nobody can tell which differences matter.

**Forces.**
- Recorders are subscribers, with the same finite buffers and poll loops as any other consumer.
- iceoryx2's system header carries node id and publisher id only: no publish time, no sequence.
- A replay must look real enough to drive the system, yet stay distinguishable from reality.
- Evidence needs two independent clocks (the producer's and the observer's) to be believable.

**The rule.** A recording is evidence when it preserves, **untouched**: (1) the producer's own stamps *inside the sealed frame* (counter, monotonic producer time, pass id); (2) the recorder's receive time as a **second, independent** clock; (3) type identity and middleware version; (4) a record-time **gap count** from the producer counter, so missed samples are visible; (5) a file hash linked into the evidence record. A **replay is a stimulus, not evidence**. It keeps the frames' counters, so E2E consumers react exactly as they would to a real repetition, and it re-stamps everything outside the frame.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| `iox2 service record/replay` | records system header + user header + payload with `timestamp = start.elapsed()` at receive (poll every 1 ms by default); file header has the iceoryx2 version, service name and type details; replay sleeps to the recorded ms × `time_factor`, with `--repetitions` | the free tap for iceoryx2, with recorder time only |
| MCAP (rosbag2 storage) | each Message has `sequence` ("to detect message gaps"), `log_time` and `publish_time` | two clocks plus a gap counter, standardised |
| DDS-RTPS | every sample is identified by writer GUID + sequence number | the gap count comes from the transport itself |
| AUTOSAR E2E | REPEATED / WRONGSEQUENCE statuses | a replayed loop is detectable by design |
| SOVD cyclic subscriptions | server timestamp on every envelope | the diagnostic side's independent clock ([[let-the-standard-timestamp-your-evidence]]) |

**On the Eclipse SDV stack.**
- iceoryx2: put the producer counter and monotonic time in the user header (as in [[the-transport-is-untrusted-the-consumer-checks-carry-safety]]); `iox2 service record` then preserves them for free. Before recording a fault stream, raise the service's subscriber buffer, because the defaults (buffer 2, safe overflow) let a slow recorder lose samples silently ([[loss-is-counted-at-the-consumer-never-hidden-by-the-buffer]]).
- A5 evidence tap: record, compute gap counts from the frame counters, and correlate with SOVD fault timestamps. Store `{file sha256, iceoryx2 version, service, gap count}` in the linked evidence record ([[evidence-is-a-linked-record-not-a-log]]).
- A6/A7 fault injection: `iox2 service replay --repetitions 1` replays the same counters again, which is a ready-made **repetition** fault. `--time-factor 3` is a **delay** fault. The consumer should report REPEATED and timeout.
- Replays come from node `iox2-cli-service-replayer`. Consumers that trust the iceoryx2 system header for producer identity are fooled by design, which is the masquerade case the Data ID exists for.

**The trap.** Treating recorder timestamps as event times, or "fixing" counters during replay so a loop runs cleanly. The second one trains the system to accept repeated data as fresh.

**For a hackathon team.** Record the battery stream for 60 s, replay it with `--repetitions 1`, and show the Guardian flagging REPEATED on the second pass, next to a recorder timeline with both clocks and a gap count. Pitch: "our recorder is an independent witness, and our replayer is a fault injector".

**Evidence.** The record and replay behaviour was read in `record.rs` lines 40–70, `replay.rs` lines 106–109 and `cli.rs` (defaults: cycle 1 ms, repetitions 0, time_factor 1.0), on 2026-10-03. The record header fields are in `record_header.rs`. The system header fields are in `header/publish_subscribe.rs` line 46. The MCAP field definitions were fetched from mcap.dev. That rosbag2 defaults to MCAP is unverified for the ROS distribution in use.
