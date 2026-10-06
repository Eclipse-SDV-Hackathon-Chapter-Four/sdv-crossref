---
title: Pay for the uProtocol envelope where a message crosses a boundary, not inside one
type: pattern
cluster: ipc-e2e
component: none
tags: [uprotocol, envelope, iceoryx2, zenoh, at-most-once, uattributes, addressing, gateway]
status: draft
sources:
  - repos/up-spec/up-l1/iceoryx2.adoc (pub/sub only; UAttributes in a FixedSizeVec<u8, 1000> user header; iceoryx2 0.6.1)
  - repos/up-spec/up-l3/README.adoc (publication and notification at-most-once, RPC at-least-once)
  - repos/up-spec/up-l1/zenoh.adoc (attributes in the Zenoh attachment)
  - repos/up-spec/up-core-api/uprotocol/v1/uattributes.proto
  - repos/up-transport-iceoryx2-rust/Cargo.toml (iceoryx2 0.7.0, up-rust 0.7)
  - https://github.com/eclipse-uprotocol/up-spec
last-verified: 2026-10-03
related:
  - "[[one-type-source-generated-bindings]]"
  - "[[forward-sealed-frames-byte-for-byte]]"
  - "[[authority-is-the-routing-unit]]"
  - "[[uprotocol-overview]]"
  - "[[uprotocol-howto]]"
  - "[[iceoryx2-overview]]"
applies-to: [uprotocol, iceoryx2, zenoh, vss-kuksa, opensovd]
gap-rows: [B5, B8, B1, A10, E9]
---

# Pay for the uProtocol envelope where a message crosses a boundary, not inside one

**Problem.** A team wraps every 100 Hz in-host signal in a uProtocol UMessage over iceoryx2. Each sample now carries a ~1 KB protobuf header, the transport is pinned to an iceoryx2 version nothing else uses, and they still have no delivery guarantee and no integrity check. Another team skips uProtocol entirely and can no longer route its heartbeat to the cloud, to MQTT or to a second ECU.

**Forces.**
- uProtocol gives addressing (UUri), identity (UUIDv7 id), priority, TTL, `traceparent` and cross-transport routing (uStreamer).
- It does not give a counter, a CRC, a deadline or a delivery receipt. Publish is at-most-once, and `send()` succeeding means only "handed to the transport".
- The iceoryx2 mapping is a prototype: pub/sub only ("RequestResponse API MUST NOT be used"), attributes serialized into a fixed 1000-byte user header that the spec itself calls "wasteful", and iceoryx2 pinned to 0.6.1 in the spec and 0.7 in the code.
- Raw iceoryx2 is 250 ns and fixed-layout, but it ends at the host.

**The rule.** Use **raw iceoryx2 with fixed-layout, E2E-sealed payloads inside a host** between closed-world producers and consumers. Put **one gateway per host** that maps selected services to UUris and adds the uProtocol envelope **at the boundary**: other ECUs, cloud, MQTT, diagnostics, evidence. Low-rate, cross-boundary, trace-worthy messages (heartbeat, fault, mitigation) are born as uProtocol. High-rate local signals are not. In both cases the seal and the counter travel in the payload, because the envelope protects nothing.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| uProtocol up-l1 iceoryx2 | user header = `{major_version: u8, uattributes_serialized: FixedSizeVec<u8, 1000>}` | the measured cost of the envelope on shared memory |
| uProtocol up-l1 Zenoh | key `up/<authority>/…`, attributes in the attachment, payload unaltered | an envelope that stays beside the frame |
| uProtocol up-l3 | publication and notification at-most-once; RPC at-least-once | what the envelope promises, and what it does not |
| SOME/IP header | a 16-byte fixed header with service/method/session ids | addressing at a fraction of the cost |
| CloudEvents (`cloudevents.adoc` mapping) | the envelope for the off-vehicle edge | where envelopes earn their keep |

**On the Eclipse SDV stack.**
- B5: refresh up-transport-iceoryx2 to 0.10 *and* change the spec's version pin (E9). Until then a uProtocol-on-iceoryx2 process cannot share a domain with 0.10 applications (`VersionMismatch`, see [[one-type-source-generated-bindings]]).
- B8: VSS paths as plain Zenoh keys are the "no envelope" alternative for signals that cross hosts without needing uProtocol routing.
- A10: the heartbeat/fault/mitigation schema crate is exactly the boundary class. Put `seq`, monotonic time and a CRC in the protobuf payload.
- Authorities are the routing unit off-host ([[authority-is-the-routing-unit]]). Inside a host the iceoryx2 service name already encodes the same thing.

**The trap.** Believing the envelope makes delivery reliable or data trustworthy. It addresses and traces, and nothing else.

**For a hackathon team.** Run the Guardian on raw iceoryx2 at 100 Hz, plus a 150-line gateway that republishes only its 1 Hz heartbeat and faults as uProtocol over Zenoh to the uStreamer. Show the byte cost per message on both sides. Pitch: "zero-copy inside, uProtocol at the edge, the seal everywhere".

**Evidence.** The header struct, the "wasteful" remark, the 0.6.1 pin and the "MUST NOT" on RequestResponse are quoted from `up-l1/iceoryx2.adoc`. Delivery semantics are from `up-l3/README.adoc` lines 34–42. The implementation pins are from `up-transport-iceoryx2-rust/Cargo.toml` lines 21–25. The "send is not a receipt" line is from [[uprotocol-howto]] (up-rust guide). The SOME/IP header size is from PRS SOME/IP. No byte-cost measurement was run.
