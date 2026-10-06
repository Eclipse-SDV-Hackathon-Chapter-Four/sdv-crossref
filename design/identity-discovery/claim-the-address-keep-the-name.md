---
title: Claim the address, keep the name — identity is self-declared, the short handle is contested
type: pattern
cluster: identity-discovery
component: none
tags: [identity, j1939, address-claim, trailer, body-builder, open-world, iceoryx2, uprotocol]
status: draft
sources:
  - https://www.sae.org/standards/content/j1939-81/ (SAE J1939-81 Network Management; paywalled, behaviour cross-checked below)
  - https://docs.kernel.org/networking/j1939.html (Linux SocketCAN J1939: NAME-SA tracking, 250 ms rule, bind by NAME)
  - https://codebrowser.dev/linux/linux/include/uapi/linux/can/j1939.h.html (64-bit NAME, 254 = idle/null address, 255 = broadcast)
  - https://copperhilltech.com/blog/sae-j1939-address-claim-procedure-sae-j193981-network-management/ (PGN 60928 Address Claimed, PGN 59904 Request, lowest NAME wins)
  - https://content.helpme-codesys.com/en/CODESYS%20CANbus/_can_edt_j1939_ecu_general.html (NAME field layout)
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[a-reboot-is-a-new-session-not-the-same-producer]]"
  - "[[open-on-arrival-age-by-your-own-deadline]]"
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[vss-kuksa-reference]]"
applies-to: [iceoryx2, uprotocol, vss-kuksa, opensovd, openbsw]
gap-rows: [B2, B6, C8]
---

# Claim the address, keep the name

**Problem.** A trailer ECU, a tail-lift controller from a body builder or a second identical sensor powers up on a bus nobody configured for it. If its identity is a slot someone had to allocate (a CAN id, a databroker numeric id, a port), two identical modules collide or the second one is invisible until an engineer edits a table.

**Forces.**
- Identical hardware from one supplier must still be told apart (two trailers, left/right lamp module).
- The short handle on the wire must be small (one byte on J1939, a u16 elsewhere), so it cannot carry identity.
- Nobody is in charge at power-up; late joiners must find out who is there.
- Consumers must keep talking to "the brake controller of trailer 2" when its short address changes.

**The rule.** The module declares a **structured, globally unique name** that it owns; the **short address is only a lease** won by contest; consumers bind to the name and re-resolve the address. J1939-81 is the archetype: the 64-bit NAME packs *what* (industry group, vehicle system, function), *which one* (vehicle system instance, function instance, ECU instance) and *who made it* (manufacturer code, 21-bit identity number), plus an "arbitrary address capable" bit. On power-up the ECU sends Address Claimed (PGN 60928) for its preferred address; on conflict the **numerically lowest NAME keeps it**, and the loser either picks another address (if arbitrary-capable) or sends Cannot Claim from the null address 254. A late joiner sends Request for Address Claimed (PGN 59904) and everyone re-announces. Use of an address waits 250 ms for contests. Linux SocketCAN J1939 lets applications `bind()` by NAME and tracks the NAME-to-address table for them.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| SAE J1939-81 address claim | 64-bit NAME is identity; 8-bit address is contested, lowest NAME wins | the trailer / body-builder power-up case, solved since the 1990s |
| Linux SocketCAN J1939 (`can-j1939`) | kernel keeps NAME↔SA, apps bind by NAME, 250 ms rule | consumers never hard-code an address |
| IPv4 link-local + ARP probing (RFC 3927) | pick an address, probe, defend or move | the same claim/defend loop on Ethernet |
| mDNS probing (RFC 6762 §8) | probe a name before using it, rename on conflict | contest for *names*, when the name is the handle |
| uProtocol UUri `ue_id` | high 16 bits = instance id, low 16 = service type | instance is a first-class field of the address, not a separate table |

**On the Eclipse SDV stack.**
- iceoryx2: put the self-declared identity in the **service name** (`trailer/<NAME-hex>/brake`) and as a service attribute (`instance.name`, `instance.function_instance`); the iceoryx2 `ServiceHash` is derived from pattern + name, so two identical modules with different NAMEs are automatically two services ([[iceoryx2-reference]], `iceoryx2/src/service/service_hash.rs`).
- KUKSA: a v2 provider *claims* signals and a second claimant gets `ALREADY_EXISTS` (kuksa.val.v2 `OpenProviderStream`) — a contest without a tiebreak. Lowest-NAME-wins is the missing rule when two trailers publish the same VSS path ([[vss-kuksa-reference]]).
- uProtocol: derive the `ue_id` instance half from the NAME's instance fields rather than allocating it ([[uprotocol-overview]]).
- OpenBSW / vcan: a J1939 feeder (gap B6) must key its KUKSA or iceoryx2 output by NAME, never by source address.

**The trap.** Using the source address as the key in a database or topic, so the archive splits in two when the trailer re-claims a different address after a reconnect.

**For a hackathon team.** Two `vcan` processes with the same function but different NAMEs claim address 0x80 via `can-j1939`; show the loser moving, and a consumer bound by NAME that keeps receiving. Pitch: "identity is claimed by the device, the address is just a lease".

**Evidence.** Kernel doc: "If no-one else contests the address claim within 250ms after transmission, the kernel marks the NAME-SA assignment as valid" and bind-by-NAME (docs.kernel.org/networking/j1939.html). Lowest NAME wins and PGNs 59904/60928: Copperhill summary of J1939-81. NAME bit layout (identity number bits 0–20, manufacturer 21–31, ECU instance 32–34, function instance 35–39, function 40–47, vehicle system 49–55, VS instance 56–59, industry group 60–62, AAC bit 63): CODESYS J1939 docs and the kernel `j1939.h` header; not checked against the paywalled SAE text (unverified). ServiceHash = hash(pattern + name): `repos/iceoryx2/iceoryx2/src/service/service_hash.rs:45`. KUKSA `ALREADY_EXISTS`: [[vss-kuksa-reference]].
