---
title: Pin the major, wildcard the instance, and treat every offer as a lease
type: pattern
cluster: identity-discovery
component: none
tags: [identity, discovery, someip, someip-sd, versioning, ttl, autosar, uprotocol]
status: draft
sources:
  - https://www.autosar.org/fileadmin/standards/R23-11/FO/AUTOSAR_FO_PRS_SOMEIPServiceDiscoveryProtocol.pdf (PRS_SOMEIPSD_00351..00364, 00825..00827, 00254..00256)
  - https://www.autosar.org/fileadmin/standards/R23-11/FO/AUTOSAR_FO_PRS_SOMEIPProtocol.pdf (Interface Version, PRS_SOMEIP_00937/00938, E_WRONG_INTERFACE_VERSION 0x08)
  - repos/up-spec/basics/uri.adoc (UUri ue_id = instance<<16 | type, version wildcard 0xFF)
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[refuse-loudly-a-mismatch-is-evidence]]"
  - "[[a-reboot-is-a-new-session-not-the-same-producer]]"
  - "[[sommr-overview]]"
  - "[[uprotocol-overview]]"
applies-to: [sommr, uprotocol, iceoryx2, zenoh]
gap-rows: [B9, B5, E9]
---

# Pin the major, wildcard the instance, and treat every offer as a lease

**Problem.** A consumer that names one exact instance cannot use the second seat module; a consumer that accepts any version will deserialize a payload it does not understand. And an offer that never expires keeps a dead ECU "available" forever.

**Forces.**
- Several instances of one service type are normal (per door, per seat, per trailer).
- Payload compatibility is a property of the *interface version*, not of the instance.
- Minor, backwards-compatible additions must not break old clients.
- The network is unreliable; a provider can vanish without saying goodbye.

**The rule.** The full name of a service instance is **(service id, instance id, major, minor)**. A client **finds** with the instance wildcarded and the **major pinned**; the minor may be "any". The provider **offers** with a TTL, re-offers before it expires, and stops with TTL 0. SOME/IP-SD spells it out: FindService uses `0xFFFF` for "all instances", `0xFF` for "any major", `0xFFFFFFFF` for "any minor", with the note that the client "should look for a specific interface version. Different Major Versions are not compatible to each other." OfferService carries a TTL ("after this lifetime the service instance shall be considered not been offered"), `0xFFFFFF` means "until next reboot", TTL `0` is StopOffer. Subsequent offers must match service, instance and major of the initial offer. On the data path, the SOME/IP header's Interface Version (= major) is checked again and a mismatch answers `E_WRONG_INTERFACE_VERSION`. Offers are multicast after a randomised initial delay, repeated with doubling backoff, then cyclic.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| AUTOSAR SOME/IP-SD (PRS R23-11) | Find/Offer/StopOffer/Subscribe(Ack/Nack) with service, instance, major, minor, TTL | instance and version as first-class parts of the name; offers expire |
| SOME/IP Protocol PRS §4.3 | interface version bumps only on incompatible payload or behaviour change; append-at-end is compatible | a written rule for what "major" means |
| uProtocol UUri | `ue_id` = instance (high 16) + type (low 16), `ue_version_major`, wildcards `0xFFFF`/`0xFF` | the same naming, carried over Zenoh/MQTT/iceoryx2 |
| DNS-SD (RFC 6763) | browse `_svc._tcp` returns all instances; TXT `txtvers` lets clients ignore unknown versions | wildcard-instance browse on IP networks |
| Semantic Versioning 2.0 | MAJOR = incompatible, MINOR = compatible addition | the human convention SOME/IP formalises |

**On the Eclipse SDV stack.**
- uProtocol already has the shape: subscribe to `//*/FFFF0123/2/8001` style UUris (instance wildcard, major pinned), never to version `FF` in production ([[uprotocol-overview]]).
- iceoryx2: put the major in the **service name** (`seat/v2/<instance>/occupancy`) so a v3 producer is simply a different service, and minor plus schema hash in **attributes**; the consumer's `AttributeVerifier` requires the hash and accepts any minor ([[open-on-arrival-age-by-your-own-deadline]]).
- Zenoh: key `vehicle/seat/v2/*/occupancy` subscribes all instances of one major.
- SommR is empty ([[sommr-overview]]); a read-only SOME/IP-SD listener (gap B9) should republish offers as `(service, instance, major, minor, ttl, endpoint)` records and expire them by TTL, not keep them.

**The trap.** Wildcarding the major "to be flexible" and discovering the incompatibility as a corrupted value instead of as a refused match.

**For a hackathon team.** Two producers offer instance 1 and 2 of `seat/v2`, one offers `seat/v3`; a consumer pinned to v2 picks up both v2 instances and logs a refusal for v3. Kill one v2 producer and show it drop out when its TTL lapses. Pitch: "pin the major, wildcard the instance, and offers expire".

**Evidence.** Quotes: PRS_SOMEIPSD_00351 (Find fields and note), 00356 (Offer TTL, 0xFFFFFF, 0x000000), 00364 (StopOffer TTL 0), 00825–00827 (exact match rules) in the R23-11 SD PRS; PRS_SOMEIP_00937 and return code 0x08 in the SOME/IP PRS. Offer phases (INITIAL_DELAY, REPETITIONS_BASE_DELAY, CYCLIC_OFFER_DELAY): SD PRS §5.1.4 / PRS_SOMEIPSD_00400–00409. UUri layout: [[uprotocol-overview]] from `repos/up-spec/basics/uri.adoc`.
