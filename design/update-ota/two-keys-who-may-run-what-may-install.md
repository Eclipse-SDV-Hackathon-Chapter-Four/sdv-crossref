---
title: Two keys - who may run it, and what may be installed
type: pattern
cluster: update-ota
component: none
tags: [uptane, tuf, trust, director, image-repository, orchestrator, signing]
status: draft
sources:
  - https://uptane.org/docs/latest/standard/uptane-standard (Uptane Standard 2.1.0)
  - https://uptane.org/docs/2.1.0/deployment/best-practices (Uptane Deployment Best Practices 2.1.0)
  - https://theupdateframework.github.io/specification/latest/ (TUF specification)
  - https://datatracker.ietf.org/doc/html/draft-ietf-suit-trust-domains (SUIT trust domains, -12)
  - "[[symphony-overview]] (Solution / Target / Instance)"
  - "[[ankaios-overview]] (state manifest, control interface)"
  - "[[opensovd-reference]] (`/updates`, #195)"
last-verified: 2026-10-03
related:
  - "[[versions-ratchet-even-when-the-clock-lies]]"
  - "[[the-manifest-programs-the-device]]"
  - "[[the-hpc-is-the-mcus-update-gateway]]"
  - "[[verify-offline-against-a-pinned-root]]"
  - "[[the-manifest-says-which-bytes-the-target-says-where]]"
applies-to: [symphony, ankaios, opensovd, autosd, uprotocol]
gap-rows: [H3, H5, C6]
---

# Two keys: who may run it, and what may be installed

**Problem.** A cloud orchestrator decides which vehicle gets which software and signs that decision. If the same key also vouches for the bytes, one compromised online server (or one stolen CI token) installs arbitrary code on the whole fleet, and nothing in the vehicle can tell.

**Forces.**
- Targeting is per vehicle, per ECU, many times a day: its key must be online and automated.
- Vouching for bytes happens once per release and should be human-gated with offline keys.
- Suppliers author images the OEM integrates; each wants its own signature to survive integration.
- The in-vehicle relay (Primary, HPC, orchestrator agent) is the most exposed component.

**The rule.** Two independent trust checks, both performed by the device that installs. *Who may run it* (this ECU, this vehicle, now) is signed by an online **director**. *What may be installed* (these bytes, this hash, this hardware id) is signed by an offline-keyed **image authority**, with delegations to suppliers. The device installs only if both agree on the same digest. The orchestrator in between is untrusted by design: it carries metadata, it never holds a key that alone suffices. Compromise of the director then lets an attacker pick only among images that were legitimately released (and release counters limit even that, see [[security-version-is-not-build-order]]).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Uptane Standard 2.1.0 | Director repository (online, per-vehicle, ECU id + hardware id + release counter) vs Image repository (offline Root/Targets keys, delegations); full verification requires Director targets to match Image repo targets | compromise resilience: Director compromise alone cannot inject new code |
| Uptane rule on delegations | "Delegations only apply to the Image repository. The Targets role on the Director repository SHALL NOT delegate" | suppliers sign their own images; the director only selects |
| Uptane Deployment Best Practices | Director compromise permits mix-and-match of released images; Image repo compromise is "a much more serious affair"; Secondaries verify regardless of transport | puts the expensive protection on the rarely-used key |
| TUF | role separation (root, targets, snapshot, timestamp), thresholds, delegations | the generic metadata model Uptane extends |
| IETF SUIT trust domains (draft -12) | a root manifest composes dependency manifests by digest, each signed by its own author; the distribution system adds encryption info | the same separation in COSE/CBOR for constrained devices |

**On the Eclipse SDV stack.** Symphony's Solution/Instance/Target is a director: it says what goes where ([[symphony-overview]]). Ankaios's state manifest is the vehicle-side copy of that intent ([[ankaios-overview]]). Neither signs bytes, and neither should be the thing that does. Put the image authority beside them: a signed image manifest (SUIT envelope or a cosign-style signature over the OCI digest) produced at release time, and make the installing agent (bootc on AutoSD, a provider workload under Ankaios, the SOVD `/updates` `prepare` step in opensovd-core once #195 lands, [[opensovd-reference]]) check the director's target digest against the image authority's signature before activation. The Chapter 3 OTA stack had only the director half ([[chapter3-retrospective]]).

**The trap.** Signing the deployment manifest with the orchestrator's key and calling the update "signed".

**For a hackathon team.** Two Ed25519 keys: an "image" key used once offline to sign `{digest, hw_id, security_version}`, and a "director" key the Symphony/Ankaios side uses to sign `{vin, ecu, digest}`. The vehicle agent refuses if either fails or the digests differ. Pitch: "steal our cloud and you can still only install what we released".

**Evidence.** Uptane quotes and roles: Uptane Standard 2.1.0 and Best Practices 2.1.0 (fetched 2026-10-03). TUF roles: TUF spec. SUIT composition: draft-ietf-suit-trust-domains-12 §5.2.2, §8.3. Symphony and Ankaios do not sign artifacts: inferred from [[symphony-overview]], [[ankaios-overview]] and the Chapter 3 repos (`repos/hc3-MegaBosses/activations/*.json` deploy by tag, no signature fields).
