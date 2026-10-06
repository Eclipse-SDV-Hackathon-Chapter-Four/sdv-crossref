---
title: The transport is a black channel; the consumer's checks carry the safety
type: pattern
cluster: ipc-e2e
component: none
tags: [e2e, autosar, black-channel, crc, counter, data-id, iec-61508, safety, iceoryx2, lola]
status: draft
sources:
  - https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_E2EProtocol.pdf (PRS E2E R22-11, Tables 2.1, 6.4, 6.7, profile tables 6.12–6.103)
  - https://61508.org/wp-content/uploads/2024/11/11A-Functional-Safety-and-Communications-V1-e092024.pdf (IEC 61508-2 7.4.11 white/black channel, IEC 61784-3)
  - https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_SOMEIPProtocol.pdf (PRS_SOMEIP_00941, E2E header after Return Code)
  - repos/s-core-communication/score/mw/com/dependability/software_architectural_design/pci_e_gateway/README.md ("Safety considerations")
  - repos/iceoryx2/README.md (platform tiers; no tier-1 platform)
last-verified: 2026-10-03
related:
  - "[[detect-silence-with-a-clock-not-with-data]]"
  - "[[forward-sealed-frames-byte-for-byte]]"
  - "[[loss-is-counted-at-the-consumer-never-hidden-by-the-buffer]]"
  - "[[reference-architecture-doctor-whodunit]]"
  - "[[iceoryx2-overview]]"
  - "[[s-core-overview]]"
applies-to: [iceoryx2, s-core, zenoh, uprotocol, openbsw, vss-kuksa]
gap-rows: [A7, A10, B2, B4]
---

# The transport is a black channel; the consumer's checks carry the safety

**Problem.** A brake-relevant or thermal-runaway signal crosses shared memory, a tunnel, a router and a CAN gateway. If any hop may repeat, drop, reorder, corrupt or impersonate, and the consumer trusts the hop, then every hop must be qualified to the same integrity level. Nobody can afford that, and no Eclipse SDV transport is certified (iceoryx2 has no tier-1 platform yet).

**Forces.**
- You want unqualified, fast transports (iceoryx2, Zenoh, DDS, SOME/IP) but a qualified decision.
- Every check costs bytes on small frames (CAN: 8 bytes total) and CPU on big ones.
- Gateways want to look at the payload. That is how a gateway becomes part of the safety chain.
- Silence is not something a check of the data can see (see [[detect-silence-with-a-clock-not-with-data]]).

**The rule.** Seal at the producer, check at the final consumer, and trust nothing in between. IEC 61508-2 §7.4.11 offers two routes: a *white channel*, where the whole network is developed to the standard, or a *black channel*, where a safety communication layer at both ends detects every fault the channel can cause. AUTOSAR E2E is that layer. It has four mechanisms, and each covers a fixed set of faults (PRS E2E Table 6.4):

| Mechanism | Detects |
|---|---|
| **Counter** | repetition, loss, delay, incorrect sequence, blocking; also loss on a subset of receivers |
| **Data ID** (implicit in the CRC, or sent explicitly) | insertion, incorrect addressing, masquerade (together with the CRC) |
| **CRC** | corruption, and asymmetric information across receivers |
| **Length** (profiles 4, 6, 7, 44) | truncation or extension of dynamic-size data |
| **Timeout on the receiver's own cycle** | loss, delay, blocking (P01 table 6.12: "transmission on a regular basis and timeout monitoring") |

The profiles trade overhead for strength:

| Profile | CRC | Counter | Data ID | Length |
|---|---|---|---|---|
| P01 / P11 | 8-bit SAE J1850 (0x1D) | 4 bit | 16 bit implicit, or 12 bit (one nibble sent) | — |
| P02 / P22 | 8-bit 0x2F (H2F) | 4 bit | a list of 16 8-bit ids, chosen by the counter value | — |
| P05 | 16-bit 0x1021 | 8 bit | 16 bit implicit | — (fixed size) |
| P06 | 16-bit 0x1021 | 8 bit | 16 bit implicit | 16 bit |
| P04 / P44 | 32-bit 0xF4ACFB13 | 16 bit | 32 bit | 16 bit |
| P07 | 64-bit ECMA | 32 bit | 32 bit | 32 bit |

The check returns a status, never a boolean: OK, OKSOMELOST (the counter jumped, but within `MaxDeltaCounter`), REPEATED, WRONGSEQUENCE, NONEWDATA or ERROR (Table 6.7). Policy is written per status.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| IEC 61508-2 §7.4.11, IEC 61784-3 (PROFIsafe, CIP Safety) | a black channel plus a safety layer in the endpoints | permission to use commodity networks |
| EN 50159 / IEC 62280 (rail) | a threat list, and at least one defence per threat | the same fault model, decades earlier |
| AUTOSAR PRS E2E R22-11 | profiles P01–P44 and a check state machine | concrete header layouts and status semantics |
| SOME/IP (PRS_SOMEIP_00941) | the E2E header sits after the Return Code, default offset 64 bit | E2E inside a service-oriented frame |
| S-CORE LoLa PCIe gateway design | the fault list (repetition, loss, insertion, masquerade, addressing) re-evaluated for a gateway | evidence that the gateway is where the black-channel argument breaks |

**On the Eclipse SDV stack.**
- [[iceoryx2-overview]]: put a P04-style `#[repr(C)] struct E2eHeader { data_id: u32, length: u16, counter: u16, crc: u32 }` in the **user header** (`publish_subscribe::<T>().user_header::<E2eHeader>()`). Compute the CRC over header and payload. The Zenoh tunnel forwards user header and payload verbatim ([[forward-sealed-frames-byte-for-byte]]).
- S-CORE `mw::com` (LoLa) has **no** E2E API. Its own design note says loss detection across a gateway has "**no** solution on `mw::com` public API level" and suggests an ara::com-style E2E extension ([[s-core-overview]]).
- uProtocol: put the E2E header in the **payload** bytes, because UAttributes is a protobuf envelope that a streamer may re-encode (unverified).
- KUKSA `Datapoint` carries a timestamp and a value, with no counter and no CRC ([[a-reading-carries-what-it-is-worth]]). A KUKSA hop cannot be part of a black channel unless the payload carries the seal.
- OpenBSW on CAN: P01/P11 sized frames are the native case ([[openbsw-overview]]).

**The trap.** Running the E2E check in the bridge and forwarding "OK". The bridge is now a white-channel component, and loss that it detected never reaches the consumer (which is exactly LoLa's PCIe gateway problem).

**For a hackathon team.** Ship a 60-line crate with `protect()` and `check()` for a P04-like header (CRC-32/AUTOSAR is polynomial 0xF4ACFB13), and wire it between the Guardian's producer and consumer. Demonstrate each status with the A7 fault-injection shim. Pitch: "the transport is untrusted; our consumer proves every reading".

**Evidence.** The fault definitions, Table 6.4, the profile control-field tables and Table 6.7 come from the AUTOSAR PDF above, read on 2026-10-03. IEC 61508 clause wording is taken from the 61508.org guide, because the standard itself was not read. The LoLa quote is from `pci_e_gateway/README.md` lines 455–470. That the CRC crate catalogue has CRC-32/AUTOSAR is unverified. Whether a uStreamer re-encodes UAttributes is unverified.
