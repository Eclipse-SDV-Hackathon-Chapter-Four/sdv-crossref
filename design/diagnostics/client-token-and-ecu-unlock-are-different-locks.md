---
title: The client token and the ECU unlock are different locks
type: pattern
cluster: diagnostics
component: none
tags: [uds, session, security-access, 0x10, 0x27, 0x29, jwt, tester-present, authz]
status: draft
sources:
  - https://www.iso.org/standard/72439.html (ISO 14229-1: 0x10, 0x27, 0x29, 0x3E)
  - https://github.com/eclipse-opensovd/classic-diagnostic-adapter (docs 02_sovd-api modes/security; cda-comm-uds/src/tester_present.rs)
  - https://www.rfc-editor.org/rfc/rfc7519 (JWT)
  - https://www.asam.net/standards/detail/sovd/
  - "[[opensovd-reference]] (modes, JWT)"
last-verified: 2026-10-03
related:
  - "[[opensovd-reference]]"
  - "[[lock-before-clear-and-expect-it-to-break]]"
  - "[[opensovd-integration-notes]]"
applies-to: [opensovd, openbsw]
gap-rows: [H7, E7, H8]
---

# The client token and the ECU unlock are different locks

**Problem.** A demo passes a JWT and gets 200 on a read, then a write returns NRC 0x33 securityAccessDenied. Someone "fixes" it by loosening the token check, or by sending the seed-key from the browser.

**Forces.**
- A client must prove *who it is* to the SOVD server (HTTP layer).
- An ECU must be unlocked for *what the session may do* (UDS layer), per ECU and per level.
- UDS sessions die without TesterPresent; HTTP clients should not need to know.
- Seed-key algorithms are secret and belong near the ECU.

**The rule.** Two layers, two owners. Layer 1 (client auth): TLS plus a token (JWT/OAuth) checked by the server; it answers "may this caller use this entity or resource". Layer 2 (ECU unlock): the adapter owns UDS state: 0x10 session (default, extended, programming), 0x27 seed/key at a level or 0x29 authentication, 0x3E TesterPresent keep-alive, and exposes it as `modes` (`session`, `security`) so the client asks for a mode. In the CDA today the SOVD *client* performs the seed/key exchange: `PUT modes/security` with `*_RequestSeed` returns the seed and the client sends the key in a second PUT, so the secret sits with the client (corrected 2026-10-03, see [[the-diagnostic-server-holds-no-secrets]]). A client token never becomes an ECU key; an ECU unlock never becomes client identity.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 14229-1 0x10 / 0x27 / 0x29 / 0x3E | sessions with S3 timeout, seed-key by level, certificate-based authentication, keep-alive | the legacy state machine |
| ASAM SOVD / ISO 17978 `modes` | `session`, `security`, `comm-ctrl`, `dtcsetting` as resources; PUT to change | UDS state as REST resources |
| OpenSOVD CDA | `modes/security` handles both RequestSeed and SendKey via `Level_7_RequestSeed` style values; background TesterPresent tasks (`tester_present.rs`) per ECU and functional group | adapter-owned keep-alive; the key itself comes from the client today ([[the-diagnostic-server-holds-no-secrets]]) |
| OAuth 2.0 / JWT (RFC 7519) | bearer token with claims and audience | layer 1 |
| OpenSOVD core `Authenticator`/`Authorizer`, Rego | pluggable identity and policy per request | the layer 1 seam |

**On the Eclipse SDV stack.**
- Layer 1: CDA default plugin accepts anything and signs with the literal key `secret`; core has JWT + Rego hooks ([[opensovd-overview]]). Offline-verifiable token design is gap H7, clock floor H8.
- Layer 2: `PUT /components/{ecu}/modes/security` with the level name; the vault notes that 0x27 and 0x29 both map onto `modes/security` (cda-interfaces), so the client cannot choose between them. `session` maps to 0x10, `dtcsetting` to 0x85, `commctrl` to 0x28.
- OpenBSW (UDS server over DoIP): expect 0x7F NRCs on writes without an extended session (B11), and 0x7F 0x3E on keep-alive handled inside the CDA ([[hackfest-esslingen-2026]]).
- A Guardian that is *not* a UDS ECU has no layer 2 at all; do not invent fake `modes` for it.

**The trap.** Making the browser or the Guardian send TesterPresent or seed-key: the session then dies with the tab, and the secret leaks to the client.

**For a hackathon team.** Show the two layers in one demo: a request with a bad token gets 401/403, a good token on a protected DID gets an NRC until `modes/security` is set, then succeeds. Pitch line: "identity at the edge, unlock at the ECU".

**Evidence.** CDA seed/key mapping and TesterPresent task: `repos/opensovd-cda/docs/03_architecture/02_sovd-api/02_sovd-api.rst` lines ~771-805 and `cda-comm-uds/src/tester_present.rs`. Mode-to-service table from [[opensovd-reference]]. 0x29 semantics are from the UDS standard (unverified this session).
