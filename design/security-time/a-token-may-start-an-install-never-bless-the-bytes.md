---
title: A token may start an install, it never blesses the bytes
type: pattern
cluster: security-time
component: none
tags: [trust-anchors, update, capability, uptane, suit, separation-of-duties]
status: draft
sources:
  - https://uptane.org/docs/latest/standard/uptane-standard (Director vs Image repository)
  - https://www.rfc-editor.org/rfc/rfc9019 (SUIT architecture: author vs device operator)
  - https://www.rfc-editor.org/rfc/rfc9124 (SUIT information model: authorisation of manifests)
  - https://theupdateframework.github.io/specification/latest/ (role separation, thresholds)
  - https://www.iso.org/standard/70918.html (ISO/SAE 21434, cybersecurity controls traceability)
  - https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155-cyber-security-and-cyber-security (R155 Annex 5: update-procedure threats)
last-verified: 2026-10-03
related:
  - "[[two-keys-who-may-run-what-may-install]]"
  - "[[the-route-names-the-capability-the-token-carries-it]]"
  - "[[verify-offline-against-a-pinned-root]]"
  - "[[opensovd-reference]]"
applies-to: [opensovd, symphony, ankaios, autosd]
gap-rows: [H3, H5, H6, H7]
---

# A token may start an install, it never blesses the bytes

**Problem.** SOVD `/updates` gets a JWT check, the workshop tool has `update:execute`, and the server installs whatever package the tool uploads. Now every stolen workshop token is a code-signing key, and every compromised tool laptop can flash the fleet.

**Forces.**
- Workshops need to trigger updates on demand, offline, with their own credentials.
- Software provenance is decided once, at release, by a different organisation.
- The orchestrator, gateway or SOVD server that relays both is the most exposed piece.
- Two trust stores on one small device feel like duplication and get merged.

**The rule.** The device holds two independent trust anchors and checks both itself. The **operation authority** (token issuer, [[verify-offline-against-a-pinned-root]]) answers "may this bearer start, cancel or commit an update on this vehicle now". The **software authority** (release signing, offline keys) answers "are these bytes, for this hardware, at this security version, allowed to exist here". An install proceeds only if a valid capability token *and* a valid software manifest agree on the target. Neither key can stand in for the other: the token never carries a digest that the device trusts, the manifest never grants permission to act. The SOVD server, Symphony, Ankaios and the tool are carriers; none holds a key that alone suffices, and the device must not take a "verified" flag from any of them.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Uptane | Director (online, targeting) vs Image repository (offline, provenance); device requires both | the update-side precedent, see [[two-keys-who-may-run-what-may-install]] |
| IETF SUIT (RFC 9019 / 9124) | manifest signed by the author; device operator may add its own authorisation; device verifies both | author and operator as separate signers |
| TUF | separate roles and keys, thresholds, any one key compromise is bounded | role separation as a design primitive |
| ISO/SAE 21434 / UNECE R155 Annex 5 | threats to update procedures and unauthorised use of diagnostic access listed separately | two threat entries, two controls |

**On the Eclipse SDV stack.**
- OpenSOVD core: `/updates` is issue #195 ([[opensovd-reference]]). The route requires `update:execute` via the `Authorizer` ([[the-route-names-the-capability-the-token-carries-it]]); the `prepare` step verifies the package manifest against a *different* anchor, loaded from a separate file or key slot, and the `Authorizer` has no access to it.
- The CDA flashes via `x-sovd2uds-download` with demo-only auth ([[opensovd-quickstart]]): today the token is the only gate, and its key is `secret`.
- [[symphony-overview]] and [[ankaios-overview]] carry the manifest; the installing agent (bootc on [[autosd-overview]], an Ankaios workload) verifies the software signature.
- H6 adds a third check that belongs to neither key: never mix revertible and irreversible parts in one transaction.

**The trap.** Letting the update endpoint accept an unsigned package because the caller's token was valid.

**For a hackathon team.** Two key pairs in two directories (`trust/operations/`, `trust/software/`); the demo shows a valid token with a tampered package (refused at `prepare`) and a valid package with a read-only token (refused with 403). Pitch line: "workshops start updates, only the release authority makes them installable".

**Evidence.** Uptane split and the "both must match" rule: Uptane Standard (as summarised in [[two-keys-who-may-run-what-may-install]]). SUIT roles: RFC 9019 §3 (author, device operator) as remembered, not re-read this session (unverified section). R155 Annex 5 threat list categories (update procedures; unauthorised diagnostic access) from the regulation text (unverified paragraph numbers). OpenSOVD `/updates` absence: [[opensovd-reference]].
