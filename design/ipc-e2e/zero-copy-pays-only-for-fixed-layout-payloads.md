---
title: Zero-copy pays only for fixed-layout payloads
type: pattern
cluster: ipc-e2e
component: none
tags: [zero-copy, shared-memory, repr-c, zerocopysend, flatbuffers, payload-layout, iceoryx2, lola, zenoh]
status: draft
sources:
  - repos/iceoryx2/examples/rust/cross_language_communication_basics/README.md (ZeroCopySend rules)
  - repos/iceoryx2/examples/rust/flatbuffer_publish_subscribe/README.md (FlatBuffers, v0.10)
  - repos/iceoryx2/FAQ.md ("Running Out of Memory", "Losing Dynamic Data")
  - repos/iceoryx2/internal/plots/benchmark_mechanism_comparison_i7_13700h.dat
  - repos/s-core-communication/score/mw/com/doc/tutorial/chapter_13/README.rst (heap-free mw::com for ASIL-B)
  - https://flatbuffers.dev/ (offset-based buffers, read without unpacking)
  - repos/zenoh/DEFAULT_CONFIG.json5 (`shared_memory`, fallback to network mode)
last-verified: 2026-10-03
related:
  - "[[one-type-source-generated-bindings]]"
  - "[[enum-discriminants-are-the-type]]"
  - "[[iceoryx2-overview]]"
  - "[[iceoryx2-quickstart]]"
  - "[[s-core-overview]]"
  - "[[zenoh-overview]]"
applies-to: [iceoryx2, s-core, zenoh, vss-kuksa]
gap-rows: [B10, B3]
---

# Zero-copy pays only for fixed-layout payloads

**Problem.** A team picks a zero-copy transport for speed. It then ships `String`, `Vec` or a protobuf blob through it and gets undefined behaviour or a segfault in another process, or it serializes anyway and pays twice. The other way round, a team pushes 4 MB camera frames through a Unix socket and wonders where the millisecond went.

**Forces.**
- Shared memory is visible to every mapped process at a different address, so pointers and heap ownership mean nothing on the other side.
- Fixed layouts are rigid: worst-case sizing, bounded strings, no optional trees.
- Memory is preallocated per publisher for the worst case (`max_subscribers × buffer × payload`, plus history and loans).
- Dynamic data (slices, FlatBuffers) is still zero-copy in transit, but the reader parses it and the size check no longer describes the layout.

**The rule.** If you take zero-copy, make the payload **its own wire format**: `#[repr(C)]`, `#[derive(ZeroCopySend)]`, no heap, no pointers, no `Drop`, `'static`. Use fixed-capacity containers from `iceoryx2-bb-container` for strings and vectors, and pin enum discriminants. Size every bounded field from the model, not from a guess. Reach for dynamic payloads only when the data really is unbounded (maps, variable-length detections), and accept a verification step on read. Measure before you choose: zero-copy pays when payloads are large, or when the hot path must not allocate. For a 16-byte 10 Hz signal, any transport is fast enough.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| iceoryx2 `ZeroCopySend` | a derive macro asserts self-contained, `repr(C)`, no `Drop`; only fixed-size ints, f32/f64 and bb-container types cross languages | layout safety by construction |
| iceoryx2 slices + `AllocationStrategy` | `publish_subscribe::<[u8]>()` with `initial_max_slice_len`; the publisher reallocates its segment | dynamic size, but a sample can be lost if the sender exits right after reallocating (FAQ) |
| iceoryx2 0.10 FlatBuffers | FlatBuffers built straight in shared memory | zero-copy for unbounded trees, at the price of read-side verification |
| S-CORE `mw::com` ch. 13 | ASIL-B consumers call `forbid_heap()`; `GetNewSamples()` is heap-free; `SetReceiveHandler` is "not heap-free end-to-end" | no-allocation hot paths as a safety requirement, not a speed trick |
| Zenoh SHM | an SHM provider and pool; "fallback on network mode" if the peer lacks SHM | zero-copy where possible, silently copied otherwise |
| FlatBuffers / Cap'n Proto | offset-based buffers readable in place | the cross-host version of "the buffer is the format" |

**On the Eclipse SDV stack.**
- Measured on this vault's machine: iceoryx2 ipc **251 ns at 8 B and 283 ns at 4 MiB** ([[iceoryx2-quickstart]]). The repo plot shows a Unix domain socket at 1.6 µs at 64 B, rising to about 1100 µs at 4 MB. The crossover in favour of zero-copy is about payload size, not about rate.
- VSS has no exporter to shared-memory layouts (gap B10). A `vspec` backend emitting `#[repr(C)]` structs with fixed-capacity strings and pinned enums is the missing type source for a KUKSA → iceoryx2 provider (B3).
- LoLa sizes its slots in `mw_com_config.json` (`numberOfSampleSlots`, `maxSubscribers`). That is the same worst-case preallocation decision, written as deployment config ([[s-core-overview]]).
- The uProtocol iceoryx2 mapping also requires `ZeroCopySend` payloads, but adds a ~1000-byte serialized header ([[pay-for-the-envelope-at-the-boundary]]).

**The trap.** Using `String`/`Vec`/`std::string` in an iceoryx2 payload because it compiles. Equally wrong: FlatBuffers for a 12-byte fixed struct, which gives you parsing cost and loses the size check.

**For a hackathon team.** Define one `#[repr(C)]` battery-pack struct (cell temperatures as `[f32; 96]` plus a pass id), publish it at 100 Hz over iceoryx2, and show `iox2 service details` with its type name, size and alignment. Pitch: "the struct is the wire format: no serializer, no allocation, 250 ns".

**Evidence.** The ZeroCopySend rules are quoted from the example README cautions. The FAQ sections were read 2026-10-03. The latency numbers come from [[iceoryx2-quickstart]] (observed) and the repo `.dat` plot. The LoLa heap-free statements are from tutorial chapter 13, lines 288–293 and 550–553. The Zenoh fallback is from the `DEFAULT_CONFIG.json5` comments. The FlatBuffers read-side verification cost is general knowledge and was not measured here.
