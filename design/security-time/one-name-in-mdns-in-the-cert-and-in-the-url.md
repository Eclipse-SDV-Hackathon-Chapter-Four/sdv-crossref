---
title: One name in mDNS, in the certificate and in the URL; the key never leaves secure storage
type: pattern
cluster: security-time
component: none
tags: [identity, tls, x509, mdns, dns-sd, idevid, dice, tofu, trust-anchor]
status: draft
sources:
  - https://standards.ieee.org/ieee/802.1AR/6995/ (IEEE 802.1AR IDevID / LDevID)
  - https://trustedcomputinggroup.org/work-groups/dice-architectures/ (TCG DICE)
  - https://www.rfc-editor.org/rfc/rfc7030 (EST enrolment)
  - https://www.rfc-editor.org/rfc/rfc6762 and https://www.rfc-editor.org/rfc/rfc6763 (mDNS, DNS-SD)
  - https://www.rfc-editor.org/rfc/rfc6125 (service identity in certificates)
  - https://www.rfc-editor.org/rfc/rfc4251#section-4.1 (SSH host keys, TOFU)
  - https://csa-iot.org/all-solutions/matter/ (Matter DAC/PAI/PAA and operational certificates)
last-verified: 2026-10-03
related:
  - "[[opensovd-reference]]"
  - "[[verify-offline-against-a-pinned-root]]"
  - "[[onboard-a-vehicle-the-backend-never-saw]]"
  - "[[ankaios-overview]]"
applies-to: [opensovd, ankaios, zenoh, autosd, opendut]
gap-rows: [H9, H7]
---

# One name in mDNS, in the certificate and in the URL; the key never leaves secure storage

**Problem.** A tester discovers `sovd-gw._sovd._tcp` on the bay LAN, connects to `https://192.168.7.3:7690`, and the server presents a self-signed cert for `localhost`. The tool either disables verification (and will talk to any laptop that answers mDNS first) or fails. Every demo ends with `curl -k`.

**Forces.**
- mDNS is unauthenticated; anyone can answer for any name.
- A device certificate must be issued after manufacture, by someone the tester trusts.
- Private keys copied into a container image or a config map are no longer device keys.
- Offboard tools need the trust anchor before their first connection, not after.

**The rule.** One identifier, three places: the mDNS instance and host name (`<id>.local`), the certificate's subjectAltName (`dNSName=<id>.local`, plus a URI SAN with VIN or component id), and the advertised URL (`TXT accessurl=https://<id>.local:7690/sovd`). The private key is generated inside secure storage (TPM, HSM, secure element) and never exported; a birth certificate (IDevID-style) proves "this key is in genuine hardware", and an operational TLS leaf for `<id>.local` is issued by an identity authority (CA) (the OEM's or the workshop's issuing CA, over EST or an offline CSR). Tools trust the identity authority's root, never the device's leaf. Distribute that root by export (shipped with the tool), by fetch-and-pin (download once over an authenticated channel, then pin), or by TOFU, stated as such: TOFU is acceptable only when the first contact is physically controlled, and a changed key must be a hard failure, not a prompt.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| IEEE 802.1AR | IDevID from the manufacturer, LDevID issued locally, keys in a secure module | birth vs operational identity |
| TCG DICE | identity derived per boot layer from a unique device secret | key bound to the code that uses it |
| Matter | DAC → PAI → PAA proves genuine device; commissioner then issues an operational certificate | the exact two-step: attest, then enrol |
| EST (RFC 7030) | CSR enrolment and CA-certs distribution over HTTPS | protocol for the identity authority (CA) |
| RFC 6125 | match the reference identifier against SAN dNSName | how the tool checks the name |
| SSH host keys | trust on first use, loud failure on change | the honest version of TOFU |

**On the Eclipse SDV stack.**
- OpenSOVD core gateway takes `--tls-cert`, `--tls-key`, `--tls-client-ca` (mTLS) as PEM files and requires an `https://` `--url`; there is no mDNS responder (issue #31) and no PKCS#11 key source ([[opensovd-reference]]). H9 closes discovery and TLS together: the same `<id>` feeds the responder, the SAN and `accessurl`.
- `aud` in client tokens should be this same `<id>` ([[verify-offline-against-a-pinned-root]]).
- [[ankaios-overview]] and Zenoh mTLS use the same shape: per-node certs, a pinned CA; Zenoh ACL subjects are `cert_common_names`, so the name in the cert is also the authorisation subject ([[zenoh-overview]]).
- On [[autosd-overview]] images, keep the key out of the bootc image; generate on first boot into a TPM-backed store and enrol.

**The trap.** Advertising an IP address or `localhost` in the certificate, so the name the tool discovered and the name it verifies are never the same.

**For a hackathon team.** `step-ca` or an `openssl` script as the identity authority (CA), a leaf for `veh-a.local`, `avahi-publish-service veh-a _sovd._tcp 7690 accessurl=https://veh-a.local:7690/sovd`, and a client that verifies with `--cacert ca.pem` and no `-k`. Pitch line: "we discovered it, verified it and addressed it by the same name"; say the key is in a file and would be in the TPM in production.

**Evidence.** Gateway TLS flags and `https` check: `repos/opensovd-core/opensovd-cli/gateway/src/main.rs` (lines ~135-145), `cli.rs` (`client_ca`). mDNS requirements and `accessurl`: [[opensovd-reference]] (from ISO 17978 coverage table). Matter certificate names from the Matter core specification (not re-read this session, unverified detail).
