---
title: An old tester gets a translator, not a second stack
type: pattern
cluster: diagnostics
component: none
tags: [uds, doip, uds2sovd, legacy, obd, epti, coexistence, sovd]
status: draft
sources:
  - https://github.com/eclipse-opensovd/uds2sovd-proxy (README only)
  - https://github.com/eclipse-opensovd/opensovd (docs/design/design.md UDS2SOVD Proxy; discussion #103)
  - https://www.iso.org/standard/72439.html (ISO 14229-1 UDS)
  - https://www.iso.org/standard/74785.html (ISO 13400-2 DoIP; number unverified)
  - https://www.iso.org/standard/66369.html (ISO 15031-5 / SAE J1979 OBD; number unverified)
  - https://www.asam.net/standards/detail/sovd/
last-verified: 2026-10-03
related:
  - "[[opensovd-overview]]"
  - "[[advertise-the-https-url-or-do-not-advertise]]"
  - "[[descriptions-are-the-product-not-the-adapter]]"
applies-to: [opensovd, openbsw]
gap-rows: [H11, H9, E2, E7]
---

# An old tester gets a translator, not a second stack

**Problem.** Workshops own UDS testers that will outlive every SOVD migration plan. Either they get nothing (the new vehicle is "untestable"), or the team builds a second diagnostic implementation that disagrees with the first.

**Forces.**
- Legacy testers speak UDS over DoIP or CAN and expect their own session state.
- The new truth (faults, data) lives behind SOVD resources.
- Regulatory diagnostics (OBD, ePTI) have fixed formats and must not be mutated by extension.
- Vehicle announcement for DoIP is not SOVD discovery; mixing them confuses both.

**The rule.** One source of truth (the SOVD tree), two front doors. A UDS2SOVD proxy accepts UDS requests on DoIP, keeps the UDS session concept (0x10, TesterPresent) locally, and maps a *configured subset* of services onto SOVD resources (0x19 to faults, 0x22 to data, 0x31 to operations). It exposes only what its description says; everything else is NRC 0x11/0x31. Regulated formats are tagged, not extended: an OBD view (J1979/ISO 15031) and an ePTI view are *projections* of the same data, selected by a tag, never new routes.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| OpenSOVD uds2sovd-proxy (design.md) | maps "any UDS service to SOVD functionality" for backward-compatible testers; configured via ODX; per ECU or per system; shares the UDS transport with the CDA | the architecture (code: README only; DoIP "currently on hold" per #103) |
| ISO 13400-2 DoIP | UDP announcement and request, TCP diagnostic messages, logical addresses | what the legacy tester expects; its announcement stays DoIP-only |
| OpenSOVD CDA | the reverse direction: SOVD to UDS over DoIP; the transport layer is shared | the one place DoIP is already implemented in Rust |
| OpenBSW DoIP server | ISO 13400-2 server for a virtual ECU; needed the 0x8002/0x8003 ack fix | a test target for the proxy |
| SAE J1979 / ISO 15031-5 OBD, ISO 27145 WWH-OBD | fixed PIDs/DTC formats for emissions | the regulated projection |
| Periodic technical inspection (ePTI) | roadworthiness data read electronically; SOVD is being discussed as the carrier (unverified) | an extension target, tagged not branched |

**On the Eclipse SDV stack.**
- Gap: no runnable proxy. Smallest honest version: a DoIP listener (reuse the CDA's DoIP crate or OpenBSW test client) mapping 0x19 02 and 0x14 to `GET/DELETE /faults` of the *same* server, with one mask byte converted back (the CDA already carries `mask` as hex; [[a-fault-is-a-state-machine-with-evidence-attached]]).
- Keep SOVD discovery and DoIP announcement separate: `_sovd._tcp` mDNS for SOVD, UDP 13400 for the proxy ([[advertise-the-https-url-or-do-not-advertise]]).
- Tag, do not branch: mark data resources with `tags=obd` or `x-obd-` categories so a projection can be generated; the description tooling ([[descriptions-are-the-product-not-the-adapter]]) emits the proxy's exposure list too.
- Locks: the proxy takes the SOVD lock on behalf of the UDS tester ([[lock-before-clear-and-expect-it-to-break]]).

**The trap.** Letting the proxy read its own side store (a second DTC memory) so UDS and SOVD views diverge after the first clear.

**For a hackathon team.** Use a stock UDS client to send `19 02 09` and `14 FF FF FF`, translate to the SOVD calls on the Guardian and show the same fault via both. Pitch line: "new truth, old tester".

**Evidence.** Proxy design: `repos/opensovd-main/docs/design/design.md` and [[hackfest-esslingen-2026]]; workshop status in `https://github.com/eclipse-opensovd/opensovd/discussions/103`. uds2sovd-proxy repo is README only ([[opensovd-reference]]). ePTI and ISO standard numbers unverified; DoIP ack bug from [[hackfest-esslingen-2026]] E2.
