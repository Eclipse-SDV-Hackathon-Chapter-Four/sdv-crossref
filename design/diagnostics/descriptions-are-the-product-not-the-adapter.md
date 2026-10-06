---
title: Descriptions are the product, not the adapter
type: pattern
cluster: diagnostics
component: none
tags: [odx, pdx, mdd, did, diagnostic-description, tooling, validator, cda]
status: draft
sources:
  - https://www.iso.org/standard/72439.html (UDS 0x22/0x2E DIDs)
  - https://www.asam.net/standards/detail/mcd-2-d/ (ASAM MCD-2 D, ODX; ISO 22901-1)
  - https://github.com/eclipse-opensovd/odx-converter (PDX to MDD)
  - https://github.com/eclipse-opensovd/classic-diagnostic-adapter (README: one .mdd per ECU)
  - https://github.com/mercedes-benz/odxtools (odxtools)
  - "[[hackfest-esslingen-2026]] (G5, B11)"
last-verified: 2026-10-03
related:
  - "[[hackfest-esslingen-2026]]"
  - "[[opensovd-overview]]"
  - "[[hackfest-openbsw-playground]]"
applies-to: [opensovd, openbsw]
gap-rows: [E14, E7, A4]
---

# Descriptions are the product, not the adapter

**Problem.** The CDA reached real Mercedes, BMW and Porsche cars in a day. Only the Mercedes worked fully. The transport was done; what failed was knowing what the bytes mean.

**Forces.**
- ODX/PDX is XML, huge (a 41 MB ODX became a 470 kB MDD in the converter README) and licensed (you supply the XSD).
- The adapter cannot decode a DID it has no description for; it can only pass raw bytes.
- Descriptions are per vehicle variant and revision, and OEM data is not public.
- Authors need fast feedback; a wrong description fails at runtime with an NRC.

**The rule.** Treat the description as the versioned artefact and give it a toolchain: author in a small readable source, generate PDX or MDD, validate before deploy, diff between revisions. A DID entry is (identifier, name, type/bit layout, scaling, session/security needs, access). If you control the ECU, generate the description from the same source as the firmware table, so the two cannot drift.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 22901 / ASAM MCD-2 D (ODX) | the exchange format: DiagLayers, services, DOPs, comparams | what OEMs ship |
| OpenSOVD odx-converter, MDD | PDX to compact FlatBuffers MDD; `.mdd` per ECU, `DiagLayerContainer` short name = ECU | the runtime form the CDA reads |
| odxtools (Python) | read/write ODX/PDX, generate PDX from Python | a generator and a checker |
| OpenBSW-SOVD-Demo `odx-gen/` | `openbsw_ecu.json` -> `generate_mdd.py` -> `OpenBSW.mdd` (or `generate_pdx.sh`) | the smallest working generator, 5 DTCs and 3 DIDs 0xCF10-0xCF12 |
| AUTOSAR Dcm DID config / CDD, A2L for XCP | description beside the code | same generate-from-one-source rule |
| ASAM/Vector CANdelaStudio (CDD) | commercial authoring | what real ECU suppliers author in (unverified) |

**On the Eclipse SDV stack.**
- Authoring source is JSON in the playground, not YAML. A YAML front-end (`did: 0xCF10, name, type, unit, scale`) would be a small generator on top (proposal, none exists in the repos).
- CDA quirk to encode in the generator: empty `variant_pattern` needs `fallback_to_base_variant=true` (G8); expected NRCs on `Identification` (DID 0xF100) and `WritableData` without an extended session (B11) are description facts, not bugs ([[hackfest-esslingen-2026]]).
- Core's `include-schema=true` self-describes native values; the CDA's `/data/{id}/docs` does the same from the MDD ([[opensovd-reference]]), so an MDD that is wrong is visible at the API.
- Tooling pattern (gap E14): `mdd-lint` (required comparams present, DIDs unique, referenced DOPs exist), `mdd-diff` (added/removed/changed services between revisions), generator from the source.

**The trap.** Debugging a "CDA bug" for hours when the MDD describes a different variant or session than the car is in.

**For a hackathon team.** Take `openbsw_ecu.json`, add one DID (a Guardian-relevant temperature) and one DTC, regenerate, run a validator that fails on duplicate DIDs, show the new value in Swagger. Pitch line: "diagnostics is a description problem; we made descriptions testable".

**Evidence.** HackFest finding and gaps G5, G8, B11 from [[hackfest-esslingen-2026]]; file layout from `repos/hackfest-OpenBSW-Playground/OpenBSW-SOVD-Demo/real-sovd-cda/odx-gen/`; size figure from odx-converter README as noted in [[opensovd-overview]]. ISO 22901 numbering follows [[opensovd-reference]] (README says 22091, treated as typo).
