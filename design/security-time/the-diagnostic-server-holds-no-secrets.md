---
title: The diagnostic server holds no secrets; it relays to whoever does
type: pattern
cluster: security-time
component: none
tags: [secrets, seed-key, uds, 0x27, 0x29, hsm, pkcs11, key-service, cda]
status: draft
sources:
  - https://www.iso.org/standard/72439.html (ISO 14229-1:2020, SecurityAccess 0x27, Authentication 0x29)
  - https://docs.oasis-open.org/pkcs11/pkcs11-spec/v3.1/pkcs11-spec-v3.1.html (PKCS#11: non-extractable keys)
  - https://developer.hashicorp.com/vault/docs/secrets/transit (encryption/signing as a service, keys never leave)
  - https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_CryptoServiceManager.pdf (CSM: jobs reference keys by id)
  - https://man.openbsd.org/ssh-agent.1 (agent signs, client never sees the key)
  - repos/opensovd-cda/cda-plugin-security/src/default_security_plugin.rs; repos/opensovd-cda/docs/03_architecture/02_sovd-api/02_sovd-api.rst
last-verified: 2026-10-03
related:
  - "[[client-token-and-ecu-unlock-are-different-locks]]"
  - "[[opensovd-quickstart]]"
  - "[[spec-pure-server-integrator-mounted-extensions]]"
  - "[[an-hpc-app-is-an-entity-not-an-ecu]]"
  - "[[the-route-names-the-capability-the-token-carries-it]]"
applies-to: [opensovd, openbsw]
gap-rows: [H7, H12, E7]
---

# The diagnostic server holds no secrets; it relays to whoever does

**Problem.** The SOVD server is the most exposed process on the vehicle: HTTP parser, JSON, plugins, a network port. If it holds the UDS seed-key algorithm, a JWT signing key or an ECU unlock secret, one parser bug leaks a secret shared by every vehicle of that model, and secrets in a server binary are secrets in every firmware dump.

**Forces.**
- UDS 0x27 needs a key computed from the ECU's seed with a secret algorithm or key.
- The server must orchestrate the exchange (sessions, TesterPresent, timeouts).
- A key held offboard needs an uplink; one held onboard needs secure storage.
- Hackathon code wants one process and one config file.

**The rule.** The server parses, routes, authorises and relays; it never computes with a long-term secret. Secret operations live in a narrow **key service**: an HSM/PKCS#11 slot, a separate app entity, or an offboard OEM service, exposing only "compute key for seed S at level L for ECU E" or "sign this", each call gated by the caller's capability and logged. Key material is non-extractable. Token *verification* needs only public keys ([[verify-offline-against-a-pinned-root]]); token *minting* happens offboard. Where the ECU supports 0x29 Authentication, prefer certificate-based unlock and the shared secret disappears.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 14229-1 0x27 vs 0x29 | seed-key with a shared algorithm vs certificate exchange (PKI) | the move from shared secrets to public keys in UDS itself |
| PKCS#11 | `CKA_EXTRACTABLE=false`, operations by handle | keys usable but not readable |
| AUTOSAR Crypto Stack (CSM) | applications submit jobs referring to key ids; the crypto driver/HSM holds keys | in-ECU precedent for the seam |
| HashiCorp Vault Transit | sign/encrypt as an API; policy per key and per caller | a key service with per-call authorisation |
| ssh-agent | client asks the agent to sign; the key never enters the client | the relay pattern in one daemon |

**On the Eclipse SDV stack.**
- The CDA does *not* compute seed-keys: `PUT /components/{ecu}/modes/security` with `Level_7_RequestSeed` returns the seed; the client must send the key with a second PUT (`Send_Key`). So today the secret sits with the SOVD client. That is acceptable for an offboard tester backed by an OEM key server, and wrong for an onboard Guardian. The fix is a key-service app entity (SOVD `apps/seedkey/operations/compute-key`, an integrator-mounted extension per [[spec-pure-server-integrator-mounted-extensions]]) gated by its own capability, not seed-key code in the CDA or in the browser.
- Counter-example: the CDA's default security plugin accepts any `client_id`/`client_secret` (without the `auth` feature), signs HS256 tokens with the hard-coded key `"secret"`, and without `auth` decodes tokens with `insecure_decode` ([[opensovd-quickstart]]). An HMAC key in the server means the verifier can mint; one leak forges tokens for every CDA with the default.
- OpenSOVD core verifies with an RS512 public key or an HS512 secret passed on the command line (`--auth-jwt-secret`, base64): choose RS512 (or ES256 per H7) so the vehicle holds no signing secret.

**The trap.** Using a symmetric (HS*) JWT key on the vehicle, which turns every verifier into a minter.

**For a hackathon team.** Move the seed-key function into a tiny separate process (or a SoftHSM slot) with a Unix socket API and one capability check, and use an asymmetric token key; show that `strings` on the server binary finds no secret. Pitch line: "our diagnostic server could be dumped tomorrow and nobody gets a key".

**Evidence.** Seed/key flow: `repos/opensovd-cda/docs/03_architecture/02_sovd-api/02_sovd-api.rst` (RequestSeed / SendKey "accompanied by a key"), `cda-sovd-interfaces/src/components/ecu/modes.rs` (`Request_Seed`, `Send_Key`). Default plugin: `cda-plugin-security/src/default_security_plugin.rs` (`check_auth_payload`, `Keys::new("secret")`, `insecure_decode`). Core key flags: `repos/opensovd-core/opensovd-cli/gateway/src/main.rs`. 0x29 semantics from ISO 14229-1:2020 (standard not re-read, unverified detail).
