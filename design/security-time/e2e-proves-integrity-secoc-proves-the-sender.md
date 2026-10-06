---
title: E2E proves the bytes arrived intact, SecOC proves who sent them; the trust boundary decides which you need
type: pattern
cluster: security-time
component: none
tags: [secoc, e2e, mac, freshness, can, key-distribution, iceoryx2, zenoh, macsec]
status: draft
sources:
  - https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf (SecOC protocol, profiles 1–3)
  - https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_SecureOnboardCommunication.pdf (SecOC SWS, Freshness Value Manager)
  - https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_E2EProtocol.pdf (E2E profiles: CRC, counter, data id)
  - https://csrc.nist.gov/pubs/sp/800/38/b/upd1/final (CMAC)
  - https://standards.ieee.org/ieee/802.1AE/7059/ (MACsec)
  - https://github.com/eclipse-uprotocol/up-spec/blob/main/topology.drawio.svg ("Zenoh-over-TCP + secOC")
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[zenoh-overview]]"
  - "[[uprotocol-overview]]"
  - "[[openbsw-overview]]"
  - "[[freedom-from-interference-has-three-axes]]"
  - "[[time-only-moves-forward-from-signed-evidence]]"
applies-to: [iceoryx2, zenoh, uprotocol, openbsw, s-core]
gap-rows: [B2, B5, B7, D1, H8]
---

# E2E proves the bytes arrived intact, SecOC proves who sent them; the trust boundary decides which you need

**Problem.** A team adds an E2E CRC and counter to a brake request and calls it "secured". A laptop on the CAN bus computes the same CRC (the algorithm is public) and sends a perfect frame. Or the opposite: a team MACs every iceoryx2 sample between two processes of the same user, paying latency for nothing.

**Forces.**
- CAN frames carry 8 (CAN FD 64) bytes; a full 128-bit MAC does not fit.
- Freshness needs a shared counter or time that both ends agree on after resets.
- Symmetric keys must reach every ECU of a group; key distribution is not in SecOC.
- Safety (ISO 26262) and security (ISO/SAE 21434) want different evidence for the same message.

**The rule.** Two properties, two mechanisms, layered. **E2E** (CRC + sequence counter + data id) detects corruption, loss, repetition and misrouting from random faults; it is a safety mechanism and assumes no attacker. **SecOC** (truncated CMAC over data id + payload + freshness value) proves the sender held the group key and that the message is fresh; it is a security mechanism. Apply SecOC where a message crosses a boundary an attacker can reach (CAN/Ethernet between ECUs, a gateway, a tunnel), and keep E2E end-to-end through it. Inside one OS trust domain (same user, same partition, shared memory) authenticate the *channel* once (OS permissions, process identity) instead of each message. Freshness is a managed counter (trip/reset counter + message counter), synchronised by a master after resets; only its low bits travel. Keys come from a separate key manager (HSM/SHE slots, AUTOSAR KeyM), never from the application.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| AUTOSAR SecOC Profile 1 | AES-128 CMAC, 24 MSB of the MAC, 8 LSB of the freshness value in the frame | the canonical truncated-MAC budget |
| SecOC Profile 3 (JASPAR) | 28-bit MAC, 4-bit truncated counter freshness, master–slave synchronisation, CAN | freshness sync after resets |
| SecOC Profile 2 | 24-bit MAC, no freshness; "only if no synchronized freshness value is established" | a named weaker fallback (replayable) |
| AUTOSAR E2E profiles | CRC, counter, data id, timeout; no key | safety, not authenticity |
| IEEE 802.1AE MACsec | hop-by-hop authenticated encryption on Ethernet links with key agreement | link-level alternative on automotive Ethernet |

**On the Eclipse SDV stack.**
- [[iceoryx2-overview]]: same-user shared memory, `dev_permissions` for others, "Identity and Access Management" still open on the roadmap. Inside the HPC the boundary is the OS user and partition ([[freedom-from-interference-has-three-axes]]); add E2E only for safety consumers.
- [[zenoh-overview]]: TLS/QUIC links and ACLs by certificate CN authenticate the hop, not the publisher; through a router the payload is not end-to-end authenticated (per-sample signing not found in this session, unverified). The uProtocol topology diagram already draws "Zenoh-over-TCP + secOC" and "SOME/IP-over-UDP + SECoC" between zones ([[uprotocol-overview]]).
- [[openbsw-overview]] → HPC on vcan/CAN (B6, B7, D1): no SecOC module in the OpenBSW tree (grep, 2026-10-03). A gateway that bridges CAN into Zenoh terminates SecOC and must re-establish authenticity on the other side, or it becomes the forging point.
- Freshness counters need the same rule as clocks: monotonic, persisted, raised only on verified input ([[time-only-moves-forward-from-signed-evidence]]).

**The trap.** Treating a CRC as authentication, or truncating the freshness value without a resynchronisation path, so every ECU reset turns into a burst of rejected frames.

**For a hackathon team.** On vcan: one sender appends `CMAC(key, id‖payload‖counter)[:3]` and the counter's low byte, one receiver rebuilds the counter and verifies; show `cansend` of a replayed frame rejected. Pitch line: "CRC for the cosmic ray, MAC for the laptop"; say keys would sit in an HSM slot.

**Evidence.** Profile parameters quoted from `AUTOSAR_FO_PRS_SecOcProtocol.pdf` R24-11 §5.3 ([PRS_SecOc_00610/00620/00630]); the counter "shall not overflow" while the key is unchanged (configuration table). iceoryx2 roadmap: `repos/iceoryx2/ROADMAP.md` "Safety & Security". uProtocol diagram: `repos/up-spec/topology.drawio.svg`. E2E profile details from the AUTOSAR E2E PRS (not re-read this session).
