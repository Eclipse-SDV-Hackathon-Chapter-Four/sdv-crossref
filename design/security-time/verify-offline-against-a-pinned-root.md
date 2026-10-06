---
title: Verify the token offline against a pinned root, and let `aud` name the vehicle
type: pattern
cluster: security-time
component: none
tags: [jwt, x5c, es256, jwks, workshop, pki, offline, aud, replay]
status: draft
sources:
  - https://www.rfc-editor.org/rfc/rfc7515#section-4.1.6 (JWS `x5c` header)
  - https://www.rfc-editor.org/rfc/rfc7519 (JWT, `aud`, `exp`, `nbf`)
  - https://www.rfc-editor.org/rfc/rfc8725 (JWT BCP: algorithm verification, audience, explicit typing)
  - https://www.rfc-editor.org/rfc/rfc7517 (JWK Set)
  - https://openid.net/specs/openid-connect-discovery-1_0.html (`jwks_uri`)
  - https://www.rfc-editor.org/rfc/rfc5280#section-6 (path validation, pathLenConstraint)
  - https://www.rfc-editor.org/rfc/rfc6750#section-5.3 (bearer tokens require TLS)
  - repos/opensovd-core/opensovd-extra/src/auth/jwt.rs; repos/kuksa-databroker/databroker/src/authorization/jwt/decoder.rs; repos/opensovd-demo/cda-oauth/
last-verified: 2026-10-03
related:
  - "[[opensovd-quickstart]]"
  - "[[opensovd-reference]]"
  - "[[the-route-names-the-capability-the-token-carries-it]]"
  - "[[time-only-moves-forward-from-signed-evidence]]"
  - "[[one-name-in-mdns-in-the-cert-and-in-the-url]]"
applies-to: [opensovd, vss-kuksa]
gap-rows: [H7, H8, H9, E7]
---

# Verify the token offline against a pinned root, and let `aud` name the vehicle

**Problem.** A workshop bay has no reliable uplink, so a vehicle that must call an identity provider to check a token cannot be serviced. A token that is valid for "the diagnostic server" is valid on every car in the bay, and a stolen one replays across the fleet.

**Forces.**
- Offline verification needs the verifier to hold a trust anchor, not a live key endpoint.
- Workshops and tools rotate keys; vehicles cannot be updated for each rotation.
- Small verifiers (gateway ECU, HPC app) cannot afford RSA-4096 or a full X.509 zoo.
- Bearer tokens are only as safe as the transport they ride on.

**The rule.** The vehicle pins *one* OEM (or workshop-authority) CA and nothing else. The minter signs each token with a short-lived ES256 key and puts its certificate chain in the JWS `x5c` header (leaf first); the vehicle validates the chain to the pinned root with a hard cap on length (say ≤ 3) and a required EKU/policy OID for "SOVD client token signer", then verifies the signature with the leaf key. Accept exactly `alg: ES256` and an explicit `typ` (RFC 8725 §3.1, §3.11); never take `alg` from the token, never follow `jku`/`x5u`. `aud` must equal this vehicle's id (VIN or `<id>.local`), optionally plus the component, so a token minted for car A is refused by car B. Capabilities go in `scope`, one entry per component and verb. The online path is a small offboard minter that also publishes its current keys as a JWKS for tools and logs; the vehicle never needs it. When authentication is on, refuse to start on plaintext HTTP.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| RFC 7515 `x5c` | chain travels with the signature; recipient MUST validate per RFC 5280 | self-contained verification |
| RFC 8725 (JWT BCP) | pin algorithms, validate `iss` and `aud`, explicit typing, distrust `jku`/`x5u` | the checklist for the verifier |
| OIDC Discovery / JWKS (RFC 7517) | issuer publishes keys at `jwks_uri` | online key distribution for tools, not for the car |
| KUKSA databroker | algorithm-family guard against the loaded key, `aud` fixed to `kuksa.val` | algorithm-confusion defence in-stack, but no per-vehicle audience |
| OpenSOVD OCA 2026 demo (cda-oauth) | Google OAuth, JWKS fetched from googleapis, `aud` = OAuth client id, email → ODX audience roles | shows the online variant and its dependency on the uplink |
| ISO 15118-2 Plug & Charge | vehicle and charger verify contract certificates against pinned V2G roots offline | automotive precedent for offline chain validation |

**On the Eclipse SDV stack.**
- OpenSOVD core `JwtAuthenticator` accepts HS512 or RS512 with one static key and sets `validate_aud = false` with the comment "the gateway is not audience-specific" — exactly the replay hole. An `X5cJwtAuthenticator` implementing the same `Authenticator` trait is the drop-in fix ([[opensovd-reference]]).
- The CDA default security plugin signs HS256 with the literal key `secret` and, without the `auth` feature, decodes with `jsonwebtoken::dangerous::insecure_decode` (no signature check) ([[opensovd-quickstart]]).
- The gateway lets `--auth-jwt-key` run over `http://`; TLS is a separate cargo feature. Add one `ensure!(scheme == https || unix socket)` when auth is on.
- `aud` should match the identity in the TLS leaf and the mDNS name ([[one-name-in-mdns-in-the-cert-and-in-the-url]]).

**The trap.** Validating everything except `aud`, so one valid token opens every vehicle that trusts the same issuer.

**For a hackathon team.** A 150-line Python minter (`cryptography` + `PyJWT`) with a self-made root and intermediate, an `x5c` verifier in the server, and a demo where the same token works on `veh-a.local` and returns 401 on `veh-b.local`. Pitch line: "one pinned root, no uplink, tokens that only open the car they were cut for".

**Evidence.** `validate_aud = false`, HS512/RS512 only: `repos/opensovd-core/opensovd-extra/src/auth/jwt.rs`. Gateway wiring and feature-gated TLS: `opensovd-cli/gateway/src/main.rs` lines ~66-145. CDA `"secret"` key and `insecure_decode`: `repos/opensovd-cda/cda-plugin-security/src/default_security_plugin.rs`. KUKSA algorithm guard and fixed audience: `repos/kuksa-databroker/databroker/src/authorization/jwt/decoder.rs` (`TODO: Make "aud" configurable`). OCA demo: `repos/opensovd-demo/cda-oauth/cda-with-oauth-plugin/plugin-google-oauth/src/plugin.rs`. ISO 15118 offline validation behaviour from the standard's PKI description (unverified this session).
