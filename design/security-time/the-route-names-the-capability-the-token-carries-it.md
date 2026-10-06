---
title: The route names the capability, the token carries it, one injected authorizer decides
type: pattern
cluster: security-time
component: none
tags: [capability, authorization, jwt, scope, rego, opensovd, kuksa, uprotocol]
status: draft
sources:
  - https://dl.acm.org/doi/10.1145/365230.365252 (Dennis & Van Horn 1966, capabilities)
  - https://www.rfc-editor.org/rfc/rfc6749#section-3.3 (OAuth 2.0 access token scope)
  - https://www.rfc-editor.org/rfc/rfc9068 (JWT profile for OAuth 2.0 access tokens, `scope` claim)
  - https://github.com/eclipse-kuksa/kuksa-databroker/blob/main/doc/authorization.md (read:/actuate:/provide: scopes)
  - https://github.com/eclipse-uprotocol/up-spec/blob/main/basics/permissions.adoc (CAPs and TAPs)
  - https://www.openpolicyagent.org/docs/latest/policy-language/ (Rego)
  - repos/opensovd-core/opensovd-server/src/auth.rs, opensovd-extra/src/auth/{jwt,rego}.rs, examples/server/auth/
last-verified: 2026-10-03
related:
  - "[[opensovd-reference]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[client-token-and-ecu-unlock-are-different-locks]]"
  - "[[authority-only-narrows-across-hops]]"
  - "[[verify-offline-against-a-pinned-root]]"
applies-to: [opensovd, vss-kuksa, uprotocol]
gap-rows: [H7, H12, H11]
---

# The route names the capability, the token carries it, one injected authorizer decides

**Problem.** A diagnostic server grows "auth modes": a dev mode, a workshop mode, a factory mode, each a flag that changes which routes are open. Every new mode is a code change in the vehicle, each mode is a superset of what any one tester needs, and the server ends up linked against a TPM, an OIDC client and a policy engine it cannot run on the bench.

**Forces.**
- The vehicle software is frozen for years; who may do what changes monthly.
- Bench, simulator and vehicle must run the same server binary.
- Policy must be inspectable by an assessor (ISO/SAE 21434 wants traceable controls).
- Hardware trust (HSM, TPM) exists on the target only.

**The rule.** A token is a signed statement "the bearer may do X on Y until T"; the server never knows modes or roles. Each route declares the capability it needs (`faults:clear` on `/components/{c}/faults`, `reset:recovery` on `/components/{c}/status/...`), and the request goes to *one* injected authorizer with `(verified claims, required capability, entity)`. The authorizer is a trait object chosen at start-up: allow-all on the bench, a scope matcher in the demo, Rego or an HSM-backed verifier in production. The server crate depends on the trait only, so it stays hardware-free; key material, PKCS#11 and the policy engine live behind the seam. Roles, if any, are expanded into capabilities by the *minter*, offboard, not on the vehicle.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Dennis & Van Horn 1966 | a capability is an unforgeable reference plus rights; possession is authority | the vocabulary: no ambient authority |
| OAuth 2.0 `scope`, RFC 9068 | token carries space-separated scopes; resource server checks them | a standard claim for capabilities |
| KUKSA databroker | `read:Vehicle.Speed`, `actuate:Vehicle.ADAS`, `provide:...`, deny scopes `!read:...` | capability = verb + path, already in the SDV stack |
| uProtocol uPermissions | code-based (CAP, levels) vs token-based (TAP) permissions on URIs | resource URIs as the capability object |
| OPA / Rego | policy as data-driven code, evaluated per request | replaceable decision point outside the server |

**On the Eclipse SDV stack.**
- [[opensovd-overview]] core already has the seam: `Authenticator` (identity from request parts) and `Authorizer<I>::authorize(identity, parts)` as Tower layers; `NoAuth`/`AllowAll` are the bench defaults, `JwtAuthenticator` + `RegorusAuthorizer` the production pair, wired in `opensovd-cli/gateway/src/main.rs`.
- Today the shipped example policy (`examples/server/auth/sovd_authz.rego` + `sovd_data.json`) is role-based: roles `reader`/`technician`/`admin` × path globs × methods, held *on the device*. The Rego input already contains `identity.scope`, so a capability policy is a 10-line Rego change: map method+path glob → required capability, `allow if required in split(input.identity.scope, " ")`.
- What is missing in core: the route does not name its capability; the authorizer re-derives it from method and path strings. A `required_capability` extension on each route (or a static table) makes the policy auditable and survives path renames (H11 proxy, H12 extensions).
- KUKSA ([[vss-kuksa-overview]]) is the in-stack precedent for verb:path scopes; reuse its grammar for SOVD (`clear:faults:/components/flxc1000`).

**The trap.** Putting a role table on the vehicle: every new workshop role is then a vehicle update, and "admin" becomes the role everybody gets.

**For a hackathon team.** Keep core's `Authorizer` seam, write a `ScopeAuthorizer` (or a Rego policy over `input.identity.scope`) with a route→capability table of five rows, and show one token that can read faults but gets 403 on clear. Pitch line: "the vehicle knows verbs, not people".

**Evidence.** Trait signatures and the 401/403 split: `repos/opensovd-core/opensovd-server/src/auth.rs`. Rego input shape (`method`, `path`, `identity.{sub,roles,scope}`) and query `data.sovd.authz.allow`: `opensovd-extra/src/auth/rego.rs`. Example role policy: `examples/server/auth/sovd_authz.rego`. KUKSA scopes: `repos/kuksa-databroker/doc/authorization.md`. uPermissions: `repos/up-spec/basics/permissions.adoc` (runtime enforcement of CAPs "implementation specific").
