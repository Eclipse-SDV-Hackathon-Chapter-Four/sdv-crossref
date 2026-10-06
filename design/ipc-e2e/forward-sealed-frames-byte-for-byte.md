---
title: Forward sealed frames byte for byte; a hop may re-stamp the envelope, never the frame
type: pattern
cluster: ipc-e2e
component: none
tags: [bridge, tunnel, gateway, zenoh, iceoryx2-link, someip-tp, dds, e2e, black-channel, verbatim]
status: draft
sources:
  - repos/iceoryx2/iceoryx2-link/tunnel/src/relay/publish_subscribe.rs (send/receive copy user header + payload)
  - repos/iceoryx2/integrations/zenoh/link-carrier/src/lib.rs (keys carry a fingerprint of the service description)
  - repos/iceoryx2/iceoryx2/src/service/header/publish_subscribe.rs (system header: node_id, publisher_port_id)
  - https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_SOMEIPProtocol.pdf (SOME/IP-TP PRS_SOMEIP_00720–00750; E2E PRS_SOMEIP_00941)
  - repos/zenoh/DEFAULT_CONFIG.json5 (`shared_memory` network fallback)
  - https://www.omg.org/spec/DDSI-RTPS/ (CDR serialization per writer)
  - repos/s-core-communication/score/mw/com/dependability/software_architectural_design/pci_e_gateway/README.md
last-verified: 2026-10-03
related:
  - "[[the-transport-is-untrusted-the-consumer-checks-carry-safety]]"
  - "[[type-hash-is-the-contract-bridges-must-not-erase-it]]"
  - "[[iceoryx2-quickstart]]"
  - "[[iceoryx2-integration-notes]]"
  - "[[zenoh-integration-notes]]"
applies-to: [iceoryx2, zenoh, uprotocol, s-core, sommr, vss-kuksa]
gap-rows: [B2, B1, B4, B7, B9]
---

# Forward sealed frames byte for byte; a hop may re-stamp the envelope, never the frame

**Problem.** A signal leaves an iceoryx2 domain, crosses Zenoh to a second host and is re-published there. Somewhere a bridge decodes it to JSON "for logging", re-encodes it and recomputes the CRC. Corruption introduced in that bridge now carries a valid seal, and the black-channel argument is gone.

**Forces.**
- Bridges are where integration happens, so they are tempted to read, convert and enrich.
- Transport metadata (publisher id, session id, timestamps) is legitimately rewritten at every hop.
- Segmentation (SOME/IP-TP), batching (Zenoh) and SHM-to-network fallback all change the *carrier* of the bytes.
- Gateways for non-native peers (B2) must translate formats, and translation is decoding.

**The rule.** Separate the **sealed frame** (the producer's payload plus the E2E header, source id, counter and pass stamp inside it) from the **envelope** (anything a transport adds). Hops may segment, batch, wrap, re-address and re-stamp the envelope. They never decode-and-re-encode, edit or re-seal the frame. Therefore everything a consumer needs to judge the frame (who produced it, which instant, which sequence) lives **inside** the frame, never only in transport headers. A hop that must translate (a gateway into a foreign type system) ends the black channel. It is the new producer and must say so: a new Data ID, its own seal, and qualification to match.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| iceoryx2-link tunnel (prototype, verified locally) | `Relay::send` takes user header + payload bytes; `receive` loans and `copy_from_slice`s them on the far side; Zenoh keys carry a fingerprint of the service description | verbatim frame, re-stamped envelope: the remote system header shows the **tunnel's** node and publisher id |
| SOME/IP-TP | segments ≤ 1392 bytes; same Session ID for all segments; reordering not supported; the E2E header sits in the original message | segmentation that never touches the frame; check after reassembly |
| Zenoh SHM | SHM when both sides announce it, otherwise "fallback on network mode" | same bytes, different carrier; zero-copy is lost across hosts |
| DDS / RTPS | every writer CDR-serializes; a DDS↔X bridge re-serializes | E2E survives only inside an opaque `sequence<octet>` |
| S-CORE LoLa PCIe gateway | it must re-offer the *same* service-id/instance-id unmodified, and gets no `setuid`, against masquerade | gateway identity rules written down |

**On the Eclipse SDV stack.**
- iceoryx2 → Zenoh tunnel ([[iceoryx2-quickstart]]): keep the E2E header in the **user header** or payload. Its default 100 ms polling (log line "Polling at 100ms") adds up to one poll interval of latency, which belongs in every deadline budget ([[detect-silence-with-a-clock-not-with-data]]).
- B2 (an iceoryx2 → native Zenoh key-expression gateway): forward the frame as the Zenoh payload unchanged, and put decoded convenience fields in an attachment, never in place of the payload.
- uProtocol/uStreamer (B1, B7): the payload is "unaltered" by spec ([[uprotocol-integration-notes]]); keep the seal in it.
- SOME/IP-SD listener (B9) and LoLa bridges (B4): translation means new producer, new seal.

**The trap.** A "smart" bridge that parses, converts units and recomputes the CRC. It launders its own faults into valid frames and quietly becomes a safety component.

**For a hackathon team.** Run two iceoryx2 domains joined by `iox2-link-tunnel-zenoh`, flip one payload byte in a deliberately broken relay, and show the consumer's CRC check catching it, while `iox2 service details` on host B lists the tunnel as publisher. Pitch: "bridges carry the frame; they never vouch for it".

**Evidence.** The relay code was read in `tunnel/src/relay/publish_subscribe.rs` lines 86–150. The system header fields were read in `header/publish_subscribe.rs` line 46. The polling log is in [[iceoryx2-quickstart]]. The SOME/IP-TP rules are quoted from PRS SOME/IP R22-11. That E2E is checked after reassembly is inferred from the header placement (unverified against SWS E2E Transformer). The Zenoh text is from `DEFAULT_CONFIG.json5`.
