---
title: Per-vehicle credentials, token audience is the VIN
type: pattern
cluster: fleet-cloud
component: none
tags: [security, credentials, jwt, audience, tls, acl, rotation, hono, zenoh]
status: draft
sources:
  - https://eclipse.dev/hono/docs/concepts/device-identity/
  - https://www.w3.org/TR/viss2-core/
  - repos/zenoh/DEFAULT_CONFIG.json5 (access_control, cert_common_names)
  - repos/fleet-management/fms-blueprint-compose.yaml
  - repos/hc3-COOTA/campaign/campaign.json
last-verified: 2026-10-03
related:
  - "[[onboard-a-vehicle-the-backend-never-saw]]"
  - "[[one-key-scheme-from-mcu-to-cloud]]"
applies-to: [zenoh, uprotocol, vss-kuksa, sdv-blueprints, symphony, opensovd]
gap-rows: [H7, H8]
---

# Per-vehicle credentials, token audience is the VIN

**Problem.** One shared secret on every vehicle means one stolen vehicle owns the fleet; a token without an audience replays across vehicles.

**Forces.**
- A fleet is a thousand attack surfaces with physical access.
- Vehicles are offline and have unreliable clocks ([[gap-register]] H8).
- Key rotation must work with a car that sleeps for six weeks.
- Demos keep secrets in compose files because that is faster.

**The rule.** Identity is per vehicle, the key is bound to the VIN, and access is decided by key expression. Use a client certificate per vehicle with CN = VIN (Hono supports X.509 against tenant trust anchors; Zenoh access control accepts `cert_common_names` and `usernames` as subjects); write ACL rules so subject `vin0001` may publish only `fleet/vin0001/**`. For bearer tokens, make `aud`/subject the VIN so a token minted for one vehicle is refused by every other (the cross-vehicle replay guard in H7). Rotate by short-lived certificates and an overlapping trust window; hold the last accepted `not-before` as a floor so a rolled-back clock cannot revive an expired credential (H8).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Eclipse Hono | per-device credentials, auth-id versus device-id, X.509/PSK/JWT (`tid`, `sub`, `aud`, max 24 h) | the device-registry model |
| Zenoh access control | rules by key expression, flow, message type, subject (cert CN, user, interface) | per-vehicle publish rights; liveliness is a message type too |
| W3C VISS v2 | JWT access token, `aud` fixed, long-term token with proof of possession | token plus key-binding |
| Sparkplug | MQTT auth is out of scope; ACL by topic | per-group/edge topic ACLs |
| OAuth 2.0 / RFC 8705 | certificate-bound access tokens | binding token to the TLS key |

**On the Eclipse SDV stack.**
- What the blueprints skip: fleet-management compose has InfluxDB admin token `fms-backend-admin-token`, Grafana password `sdv`, Zenoh router exposed on 7447 with no auth, Databroker "no TLS for the time being" ([[sdv-blueprints-overview]]). Hono variant at least provisions a device password or certificate via `create-config-hono.sh`.
- COOTA's `campaign.json` commits a Symphony admin Bearer JWT (HS256, `aud: ["*"]`) in the repo: a wildcard audience is the opposite of this pattern.
- Zenoh: enable `access_control` with `default_permission: deny`, TLS or QUIC to the cloud router, and set the `namespace` per vehicle so ZID spoofing is irrelevant (DEFAULT_CONFIG warns ZID is not authenticated and cannot be trusted for ACL).
- KUKSA Databroker: `--jwt-public-key` turns on token checks; scope to the vehicle by token claims ([[vss-kuksa-overview]]). OpenSOVD client tokens: see H7.

**The trap.** One fleet-wide token for ingestion because Hono or Zenoh makes it easy.

**For a hackathon team.** Two certificates (vin0001, vin0002), one Zenoh ACL file; show vin0002 failing to publish on vin0001's key. Pitch: "a stolen truck owns itself, not the fleet".

**Evidence.** Hono JWT/cert rules (fetched). Zenoh ACL schema: DEFAULT_CONFIG.json5 lines ~395-500. Compose secrets: fms-blueprint-compose.yaml lines 62-64, 110, 175. COOTA token: repos/hc3-COOTA/campaign/campaign.json (the token's own `exp` was 2025). Rotation scheme here is a design proposal, not a documented behaviour.
