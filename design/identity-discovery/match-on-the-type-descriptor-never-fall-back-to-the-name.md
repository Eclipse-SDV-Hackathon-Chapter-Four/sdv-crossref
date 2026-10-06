---
title: Match on the type descriptor, never fall back to the type name
type: pattern
cluster: identity-discovery
component: none
tags: [identity, discovery, dds, xtypes, rtps, type-hash, assignability, iceoryx2, vss]
status: draft
sources:
  - https://www.omg.org/spec/DDS-XTypes/1.3/PDF (§7.6.3.2 TypeInformation in discovery; §7.6.3.4 TypeConsistencyEnforcementQosPolicy; EquivalenceHash = first 14 bytes of MD5)
  - https://www.omg.org/spec/DDSI-RTPS/2.5/PDF (§8.5 SPDP/SEDP; leaseDuration default 100 s, resendPeriod 30 s, 239.255.0.1)
  - https://www.omg.org/spec/DDS/1.4/ (INCONSISTENT_TOPIC, REQUESTED/OFFERED_INCOMPATIBLE_QOS statuses)
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[a-type-name-is-a-claim-a-layout-hash-is-a-proof]]"
  - "[[refuse-loudly-a-mismatch-is-evidence]]"
  - "[[derive-ids-from-layout-not-from-prose]]"
  - "[[type-hash-is-the-contract-bridges-must-not-erase-it]]"
applies-to: [iceoryx2, vss-kuksa, zenoh, uprotocol]
gap-rows: [B10, B2, B3]
---

# Match on the type descriptor, never fall back to the type name

**Problem.** Two teams both call their struct `BatteryState`. One adds a field in the middle. Every check that compares names passes, and the subscriber reads temperature from where voltage used to be.

**Forces.**
- A descriptor hash must be cheap to carry in every announcement; the full description must be fetchable on demand.
- Some evolution (append an optional field) should not break readers; some (reorder, retype) must.
- Legacy peers announce no descriptor at all.
- A strict rule in safety consumers, a lenient one in loggers.

**The rule.** Announce a **hash of a canonical type description** with every endpoint, decide compatibility from the descriptor, and treat "no descriptor" as "no match" wherever the consumer decides anything. DDS-XTypes 1.2+ does this: SEDP publication and subscription data carry `type_information` with MINIMAL and COMPLETE `TypeIdentifier`s (an EquivalenceHash of the serialized TypeObject, first 14 bytes of MD5) plus dependent type ids; a participant that does not know a hash fetches the TypeObject with the TypeLookup service. The reader's `TypeConsistencyEnforcementQosPolicy` then chooses: `DISALLOW_TYPE_COERCION` (same type) or `ALLOW_TYPE_COERCION` (reader type *assignable from* writer type, with knobs `prevent_type_widening`, `ignore_sequence_bounds`, `ignore_string_bounds`, `ignore_member_names`). If type information is absent, the spec **falls back to exact `type_name` equality** unless `force_type_validation` is set. A failed check makes the endpoints not communicate and raises `INCONSISTENT_TOPIC` on both sides.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| DDS-XTypes 1.3 | TypeInformation (hashes) in discovery, TypeObject on demand, assignability rules | structural matching across vendors |
| DDSI-RTPS 2.5 SPDP/SEDP | participants announce periodically (30 s) with a lease (100 s); endpoints exchanged per participant | discovery is periodic and leased, not one-shot |
| ROS 2 RIHS01 (REP-2016 draft) | SHA-256 over canonical TypeDescription, sent as `typehash=` in DDS USER_DATA | the same idea one layer up |
| Protocol Buffers field numbers | identity of a field is its number, not its name or position | the "member id" rule XTypes assignability relies on |
| VSS static UID (`vspec export id`) | 32-bit hash over name, datatype, unit, enum, min/max | a per-leaf descriptor hash for vehicle signals |

**On the Eclipse SDV stack.**
- iceoryx2 compares only `type_name`, size and alignment (see [[a-type-name-is-a-claim-a-layout-hash-is-a-proof]]); add a `type.hash` attribute and make every deciding consumer `require` it. A vss-tools exporter that emits `#[repr(C)]` structs (gap B10) should emit that hash alongside.
- KUKSA → iceoryx2 provider (gap B3) and the iceoryx2 → Zenoh gateway (gap B2) must carry the descriptor hash across; Zenoh keys can end in the hash as rmw_zenoh does ([[ros-over-zenoh-needs-a-router-and-a-contract]]).
- uProtocol carries `payload_format` but no schema hash in UAttributes; put it in the topic metadata (uDiscovery `UServiceTopic` already has message name and format) ([[uprotocol-overview]]).

**The trap.** Leaving `force_type_validation` off (the default), so a peer that sends no type information is matched by name alone and the structural check you trusted never ran.

**For a hackathon team.** Two publishers with the same struct name and a reordered field; an iceoryx2 subscriber requiring `type.hash` opens one and refuses the other, logging both hashes. Pitch: "we match on what the bytes mean, not on what the type is called".

**Evidence.** XTypes 1.3 §7.6.3.2.1 (TypeInformation IDL, "can use the TypeLookup Service to retrieve the TypeObject"), §7.6.3.4.1–2 (consistency kinds; default ALLOW_TYPE_COERCION; non-conformant peers assumed DISALLOW; `force_type_validation` "requires type information to be available"; failure "shall trigger an INCONSISTENT_TOPIC status change"), EquivalenceHash IDL comment "First 14 bytes of MD5 of the serialized TypeObject". RTPS 2.5 §9.6.1 defaults `resendPeriod = {30,0}`, `PID_PARTICIPANT_LEASE_DURATION` default `{100,0}`, multicast `239.255.0.1`. iceoryx2 check: `repos/iceoryx2/iceoryx2/src/service/static_config/message_type_details.rs` `is_compatible_to`. The XTypes text for `ignore_member_names` reads inverted ("If set to TRUE, member names are considered"); treat its semantics as unverified.
