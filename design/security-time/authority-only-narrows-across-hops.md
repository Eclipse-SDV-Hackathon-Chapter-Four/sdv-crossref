---
title: Authority only narrows across hops; the reachable node holds the lowest ceiling
type: pattern
cluster: security-time
component: none
tags: [delegation, attenuation, confused-deputy, gateway, macaroons, biscuit, token-exchange]
status: draft
sources:
  - https://dl.acm.org/doi/10.1145/54289.871709 (Hardy 1988, The Confused Deputy)
  - https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/ (Macaroons, NDSS 2014)
  - https://www.biscuitsec.org/docs/getting-started/introduction/ (Biscuit, offline attenuation)
  - https://github.com/ucan-wg/spec (UCAN: delegation chains may only attenuate)
  - https://www.rfc-editor.org/rfc/rfc8693 (OAuth 2.0 Token Exchange, `act` claim)
  - repos/opensovd-core/opensovd-server/src/auth.rs
last-verified: 2026-10-03
related:
  - "[[the-route-names-the-capability-the-token-carries-it]]"
  - "[[one-backend-trait-many-backends]]"
  - "[[opensovd-overview]]"
  - "[[uprotocol-overview]]"
applies-to: [opensovd, uprotocol, zenoh, vss-kuksa]
gap-rows: [H11, H7, B1]
---

# Authority only narrows across hops; the reachable node holds the lowest ceiling

**Problem.** A tester talks to the SOVD gateway on the HPC, which forwards to a CDA, which speaks UDS to an ECU. If the gateway uses its own service credential downstream, any caller who reaches the gateway inherits the gateway's full authority: the classic confused deputy, now with a flash-programming session at the end.

**Forces.**
- Gateways must forward without the downstream knowing every client.
- Downstream nodes cannot call home to ask "did the minter mean this?".
- Re-minting is convenient and is exactly how authority gets amplified.
- The node with the open port is the one that gets attacked first.

**The rule.** Every hop may forward, restrict or drop authority, never add to it. A gateway either passes the client's token through unchanged (the downstream checks it against its own `aud`), or mints a *derived* token whose capabilities are the intersection of the incoming token and the gateway's own ceiling, whose `exp` is no later than the parent's, and which records the chain (`act` claim or a hash of the parent). The downstream checks the derived token against the gateway's ceiling, not its own maximum. Ceilings are configured per node, statically, and the publicly reachable node (the one listening on the workshop LAN or a cloud tunnel) has the lowest one; flash and reset capabilities only exist on hops that are not directly reachable.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Hardy 1988, Confused Deputy | a program using its own authority on behalf of a caller | the failure mode named |
| Macaroons (NDSS 2014) | chained HMAC caveats: anyone holding a token can add restrictions, nobody can remove them | attenuation as a cryptographic property |
| Biscuit | public-key tokens with appended attenuation blocks, Datalog checks, offline verification | Macaroons without a shared secret |
| UCAN | each delegation must prove its capability is within its parent's | chain verification rule |
| OAuth 2.0 Token Exchange (RFC 8693) | delegation vs impersonation; `act` records the actor chain | standard claims for a gateway re-mint |

**On the Eclipse SDV stack.**
- OpenSOVD: the roadmap's gateway forwarding to a CDA (H11, [[one-backend-trait-many-backends]]) is the hop. Core's `Identity<Claims>` extractor makes the verified claims available to the forwarding backend; pass the bearer through, or re-mint with `scope = incoming ∩ ceiling`. A forwarding backend must never attach a static service token.
- uProtocol: `UAttributes.token` (field 10) and `permission_level` travel per message ([[uprotocol-overview]]); a uStreamer that bridges authorities must not rewrite them upward.
- Zenoh ACLs bind permissions to `cert_common_names`; a router that bridges a workshop network to the vehicle gets its own, narrower subject ([[zenoh-overview]]).
- KUKSA: a bridge provider (B1) holds a `provide:` token for its paths only, never `actuate:Vehicle`.

**The trap.** A gateway that authenticates the caller and then calls downstream "as itself".

**For a hackathon team.** Two OpenSOVD processes: a public one with ceiling `read:*` that forwards to an internal one; show that an `admin` token sent to the public node still cannot clear faults downstream. Pitch line: "every hop can say less, none can say more".

**Evidence.** Identity propagation: `repos/opensovd-core/opensovd-server/src/auth.rs` (`Identity<T>`, request extensions). uProtocol fields: `repos/up-spec/up-core-api/uprotocol/v1/uattributes.proto` lines 50, 62. Zenoh ACL subjects: `repos/zenoh/DEFAULT_CONFIG.json5` (`access_control.subjects.cert_common_names`). Gateway forwarding is a roadmap item, not code (see [[opensovd-overview]]).
