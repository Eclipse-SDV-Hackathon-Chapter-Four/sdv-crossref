---
title: The manifest programs the device
type: pattern
cluster: update-ota
component: none
tags: [suit, cbor, cose, manifest, command-sequence, envelope, trust-domains, two-level]
status: draft
sources:
  - https://www.rfc-editor.org/rfc/rfc9019 (SUIT architecture)
  - https://www.rfc-editor.org/rfc/rfc9124 (SUIT information model)
  - https://datatracker.ietf.org/doc/html/draft-ietf-suit-manifest (manifest format, -37, RFC Editor queue)
  - https://datatracker.ietf.org/doc/html/draft-ietf-suit-trust-domains (-12)
  - https://datatracker.ietf.org/doc/html/draft-ietf-suit-firmware-encryption (-26)
  - https://datatracker.ietf.org/doc/search/?name=suit&activedrafts=on&rfcs=on (status of all SUIT drafts)
  - https://github.com/RIOT-OS/RIOT/tree/master/sys/suit (RIOT SUIT implementation)
last-verified: 2026-10-03
related:
  - "[[two-keys-who-may-run-what-may-install]]"
  - "[[encrypt-once-wrap-per-device]]"
  - "[[the-hpc-is-the-mcus-update-gateway]]"
  - "[[the-manifest-says-which-bytes-the-target-says-where]]"
applies-to: [opensovd, symphony, openbsw, threadx, autosd]
gap-rows: [H5, H3, D5]
---

# The manifest programs the device

**Problem.** Update metadata that says only "version 1.4, url, sha256" leaves the order of fetch, check, install, verify and boot hard-coded in each device. Every new flow (a delta, a second component, an encrypted payload, a supplier image under an OEM wrapper) needs a firmware change on the device that is supposed to receive the update.

**Forces.**
- Constrained devices need a tiny, auditable processor, not a scripting engine.
- Several authors (supplier, OEM, distributor) contribute to one update.
- Large payloads should be fetched only after every manifest is authenticated.
- Some parts (text, install scripts) should be droppable on the device without breaking signatures.

**The rule.** Ship a signed program, not a description. The **envelope** holds an authentication wrapper (digest of the manifest plus COSE signatures), the **manifest**, severable members (removable but digest-bound) and optional integrated payloads. The manifest names components and carries **command sequences** the device interprets: `suit-payload-fetch`, `suit-install`, `suit-validate`, `suit-load`, `suit-invoke`; the trust-domains extension adds `suit-dependency-resolution` and `suit-candidate-verification`. Commands are either *conditions* (side-effect-free tests: vendor id, class id, image digest, version) or *directives* (set component, fetch, copy, process dependency). Two levels fall out naturally: a campaign or root manifest lists per-ECU image manifests by digest, each signed by its author, and the processor runs them in lockstep; all dependencies are fetched before any payload.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| RFC 9019 / RFC 9124 | architecture and information model: sequence number, vendor/class ids, precursor digest, payload format, processing steps, encryption wrapper | the vocabulary every element is checked against |
| draft-ietf-suit-manifest-37 | "a Manifest Processor -- a form of interpreter"; conditions vs directives; sequence number as anti-rollback counter | the device runs the manifest |
| draft-ietf-suit-trust-domains-12 | dependencies by digest, `suit-directive-process-dependency`, staging vs installation procedures, uninstall | campaign manifest over supplier manifests |
| draft-ietf-suit-firmware-encryption-26 | COSE_Encrypt payloads, AES-KW or ES-DH content-key distribution | encrypted payloads inside the same program |
| RIOT OS `sys/suit` | an open manifest processor on microcontrollers | proof it fits a constrained device |

**On the Eclipse SDV stack.** None of Symphony, Ankaios, opensovd-core or the CDA parse manifests today ([[gap-register]] H5). The cleanest seam is SOVD `/updates`: `register` accepts an envelope as the update package, `prepare` runs dependency resolution and fetch, `execute` runs install and validate, and status reports which sequence is running ([[opensovd-reference]]). On an MCU behind the HPC the same envelope can travel as the payload of UDS 0x34/0x36 ([[the-hpc-is-the-mcus-update-gateway]]). Keep layout and mount decisions out of it ([[the-manifest-says-which-bytes-the-target-says-where]]).

**The trap.** Inventing a JSON "manifest" whose fields the device interprets in a fixed order, which authenticates the bytes but not the procedure.

**For a hackathon team.** One COSE_Sign1-signed CBOR (or JSON) manifest with a component id, digest, security version and an ordered list of three steps (`check-digest`, `copy`, `check-version`), executed by a 100-line interpreter on the target. Pitch: "the update tells the car how to install itself, and the signature covers the procedure".

**Evidence.** Status: the manifest format itself is still an Internet-Draft (draft-ietf-suit-manifest-37, RFC Editor queue, per datatracker on 2026-10-03); only RFC 9019 and 9124 are published, so "SUIT RFC" means architecture plus information model. Sequence names and the interpreter quote: manifest draft. Dependency resolution lives in trust-domains (§5.5, §7). Nordic's nRF Connect SDK, the most visible SUIT deployment, moved nRF54H20 from SUIT to MCUboot with IronSide SE in v3.1 (migration guide title; body not read, unverified detail).
