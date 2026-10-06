---
title: Advertise the https URL, or do not advertise
type: pattern
cluster: diagnostics
component: none
tags: [sovd, mdns, dns-sd, tls, discovery, secure-storage, port-7690]
status: draft
sources:
  - https://www.rfc-editor.org/rfc/rfc6762 (mDNS)
  - https://www.rfc-editor.org/rfc/rfc6763 (DNS-SD)
  - https://www.asam.net/standards/detail/sovd/ (discovery use case; _sovd._tcp)
  - https://github.com/eclipse-opensovd/opensovd-core/issues/31 (mDNS)
  - https://github.com/eclipse-opensovd/opensovd-core (opensovd-extra TLS helpers, gateway --tls-cert/--tls-key/--tls-client-ca)
  - https://www.rfc-editor.org/rfc/rfc8446 (TLS 1.3)
last-verified: 2026-10-03
related:
  - "[[opensovd-reference]]"
  - "[[client-token-and-ecu-unlock-are-different-locks]]"
  - "[[instance-in-the-name-type-in-the-hash]]"
applies-to: [opensovd, openbsw]
gap-rows: [H9, H7, H8]
---

# Advertise the https URL, or do not advertise

**Problem.** A discoverable diagnostic server that announces `http://` teaches every tester to send tokens in clear, and a server that is not discoverable needs a human with an IP address in a workshop.

**Forces.**
- Co-located testers (workshop LAN, link-local) need zero-config discovery.
- Discovery is unauthenticated broadcast; whatever it says is untrusted.
- The TLS identity (key) is the most sensitive thing on the box.
- A name that cannot be verified by the certificate is no better than an IP.

**The rule.** Discovery and transport security are one unit: the thing you advertise is the thing you can authenticate. Advertise service `_sovd._tcp` (RFC 6763 DNS-SD) over mDNS (RFC 6762), host `<id>.local`, port 7690, TXT record `accessurl` = an `https://` URL, and issue a certificate whose SAN contains that `<id>.local` name. Discovery only finds the server; trust comes from the certificate chain and the token, never from the announcement. The private key lives in secure storage (HSM, TPM, keystore), loaded by handle, never copied to a plain file.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ASAM SOVD / ISO 17978 discovery | mDNS `_sovd._tcp`, `<id>.local`, TXT `accessurl` | the mandatory use case |
| RFC 6762 / 6763 | multicast name resolution and service discovery | the wire behaviour |
| ISO 13400-2 DoIP | UDP vehicle announcement on port 13400 | the legacy discovery that is *not* reused (see [[an-old-tester-gets-a-translator-not-a-second-stack]]) |
| Apple Bonjour, Avahi | deployed mDNS responders | a daemon you can use instead of writing one |
| OpenSOVD core | `--tls-cert`, `--tls-key`, `--tls-client-ca`, `--tls-client-auth required|optional` (mTLS) | the TLS half exists |
| Matter / HomeKit commissioning | discover then authenticate via a separate credential | "discovery is not trust" |

**On the Eclipse SDV stack.**
- Core has TLS and mTLS flags but no mDNS (open issue #31); the CDA has neither as advertised service ([[opensovd-reference]]). Gap H9 closes them together: an mDNS responder publishing the URL of the TLS listener.
- Mounted shape: Rust mDNS responder (or Avahi service file for the hackathon) with TXT `accessurl=https://<id>.local:7690/sovd`; the gateway's `--tls-*` flags use cert paths today. Real secure-storage loading (TPM/PKCS#11) is not in core; a file path is the demo stand-in (say so).
- Pair with H7/H8: client tokens verified offline against a pinned CA, with `aud` = vehicle id; the `<id>` in the hostname and the token `aud` should be the same string.
- Container networks: mDNS is multicast; across container networks or Ankaios hosts it may not cross (unverified; a single default Docker bridge passed Zenoh multicast (corrected 2026-10-03, see [[zenoh-overview]])), so use host networking or an Avahi reflector.

**The trap.** Announcing `http://` "just for the demo", or announcing an `https://` URL with a self-signed cert that every client is told to ignore.

**For a hackathon team.** `avahi-publish -s guardian _sovd._tcp 7690 accessurl=https://guardian.local:7690/sovd`, a self-issued CA, the gateway with `--tls-cert/--tls-key`, and a client that browses, then verifies the name. Pitch line: "found by name, trusted by certificate".

**Evidence.** Discovery details and #31: [[opensovd-reference]] (standard paywalled; unverified at clause level). TLS flags from `repos/opensovd-core/opensovd-cli/gateway/README.md`. DoIP port 13400 from ISO 13400-2 (unverified in this session; the CDA default `--gateway-port 13400` in [[opensovd-reference]] agrees).
