---
title: Switch on what you can show, name what you cannot, and bound the blast radius of each
type: pattern
cluster: security-time
component: none
tags: [threat-model, tara, r155, iso-21434, stride, hackathon, residual-risk, pitch]
status: draft
sources:
  - https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security (UN R155, Annex 5 threats and mitigations)
  - https://www.iso.org/standard/70918.html (ISO/SAE 21434:2021, TARA, cybersecurity claims)
  - https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats (STRIDE)
  - https://www.rfc-editor.org/rfc/rfc3552 (writing honest security considerations)
  - https://www.rfc-editor.org/rfc/rfc8725 (JWT BCP)
last-verified: 2026-10-03
related:
  - "[[chapter4-overview]]"
  - "[[verify-offline-against-a-pinned-root]]"
  - "[[time-only-moves-forward-from-signed-evidence]]"
  - "[[the-diagnostic-server-holds-no-secrets]]"
  - "[[authority-only-narrows-across-hops]]"
  - "[[reference-architecture-doctor-whodunit]]"
applies-to: [opensovd, vss-kuksa, zenoh, ankaios, autosd, uprotocol]
gap-rows: [H7, H8, H9, E7]
---

# Switch on what you can show, name what you cannot, and bound the blast radius of each

**Problem.** Hackathon demos either run everything with auth off and say "security is future work", or claim "secured with HSM and secure boot" for a laptop running `curl -k`. Coaches with automotive background discount both, and R155-literate jurors ask the one question neither can answer: "what happens if this token leaks?"

**Forces.**
- Two days; TLS and token plumbing cost hours, HSM integration costs days.
- Every disabled control must still be visible, or the demo lies by omission.
- The rubric rewards repo-verifiable evidence (80 % coaches) over slideware.
- One leaked secret should cost one vehicle and one hour, not the fleet.

**The rule.** Write a one-table threat model (asset, entry point, STRIDE letter, control, status: *on* / *stub* / *pitch*) and switch on every control whose absence would make the demo meaningless and that fits in an afternoon: TLS with a real CA and matching name, token signature with a pinned algorithm, `aud` = vehicle id, per-route capabilities, short `exp`, refusal of plaintext when auth is on. Stub what needs hardware behind the same seam it will use in production (key in a file behind a `KeyStore` trait, floor in a JSON file behind `TimeSource`). Pitch only what you have a seam for (HSM, secure boot, Roughtime, revocation), and state each one's blast radius: what an attacker gets if *this* key leaks, for how long, on how many vehicles. Never ship a demo default that is also a production default (no `secret`, no `-k`, no allow-all fallback).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| UNECE R155 | CSMS and type approval; Annex 5 lists threats (back-end, update, unauthorised diagnostic access, ...) with mitigations | the jurors' checklist |
| ISO/SAE 21434 TARA | asset → damage scenario → threat scenario → attack path → risk → treatment; residual risk and claims stated explicitly | the shape of the one-table model |
| STRIDE | spoofing, tampering, repudiation, information disclosure, DoS, elevation | fast enumeration per entry point |
| RFC 3552 | security considerations must say what is not protected and why | the honesty clause |
| RFC 8725 | concrete JWT controls that are cheap to switch on | the afternoon list for tokens |

**On the Eclipse SDV stack.**
- Switch on: OpenSOVD core `--tls-cert/--tls-key` + `--auth-jwt-key` with RS512 and a Rego or scope policy ([[opensovd-reference]]); KUKSA databroker with `--jwt-public-key` and TLS ([[vss-kuksa-overview]]); Zenoh TLS + ACL by cert CN ([[zenoh-overview]]); Ankaios mTLS ([[ankaios-overview]]).
- Stub honestly: `aud` check and x5c (H7) if core's authenticator is not yet replaced; time floor (H8) as a file; mDNS (H9) via avahi.
- Pitch: HSM-held device key, secure boot on [[autosd-overview]], SecOC on the CAN leg, Roughtime.
- Known demo-only defaults to call out, not hide: CDA accepts any credentials and signs with `secret`; `GET /components` worked without a token ([[opensovd-quickstart]], E7).
- Bound the radius: one vehicle per token (`aud`), minutes per token (`exp`), read-only on the reachable node ([[authority-only-narrows-across-hops]]), no secrets in the server ([[the-diagnostic-server-holds-no-secrets]]).

**The trap.** Saying "secure" without saying against whom, or listing hardware you do not have as if it were running.

**For a hackathon team.** Put the five-row threat table in the README with a status column, run the demo with TLS and tokens on, and show one attack failing live (wrong-vehicle token → 401). Pitch line: "here is what a leaked key costs us: one car, fifteen minutes, read-only".

**Evidence.** Rubric split: [[chapter4-overview]] (coaches 80 %, jury 20 %). Gateway flags: `repos/opensovd-core/opensovd-cli/gateway/src/main.rs`. CDA defaults: [[opensovd-quickstart]]. KUKSA JWT flags: `repos/kuksa-databroker/databroker/src/main.rs` (`--jwt-public-key`, `--tls-cert`). R155 Annex 5 table structure as published by UNECE (paragraph numbers unverified).
