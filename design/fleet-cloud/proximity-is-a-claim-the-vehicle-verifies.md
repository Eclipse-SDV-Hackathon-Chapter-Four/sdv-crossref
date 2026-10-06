---
title: Proximity is a claim the vehicle verifies, not the phone's word
type: pattern
cluster: fleet-cloud
component: none
tags: [companion-app, android, proximity, sovd, locks, kuksa, remote, security]
status: draft
sources:
  - repos/companion-application/Readme.md
  - https://github.com/eclipse-kuksa/kuksa-android-companion (unverified)
  - components/opensovd/opensovd-reference.md (locks, operations, modes)
  - https://www.w3.org/TR/viss2-core/
last-verified: 2026-10-03
related:
  - "[[per-vehicle-credentials-audience-is-the-vin]]"
  - "[[opensovd-overview]]"
applies-to: [vss-kuksa, opensovd, sdv-blueprints, zenoh]
gap-rows: [H7, H8]
---

# Proximity is a claim the vehicle verifies, not the phone's word

**Problem.** The same companion app opens the trunk standing next to the car and "pre-conditions" it from another continent, and a workshop tool runs a routine over a service-port session. If the phone says it is nearby, anyone can say it.

**Forces.**
- Co-located use (unlock, seat adjust, workshop routine) and remote use (climate, status) share one app and one API.
- Phones report location and BLE RSSI, but both are spoofable from the phone's side.
- A parked vehicle has a weak clock and a weak uplink ([[gap-register]] H8).
- Actuation and diagnostic operations must not be callable by a replayed request.

**The rule.** Classify every operation as local-only, remote-allowed or remote-with-confirmation, and let the vehicle decide using evidence it can observe itself: a short-range link it terminated (BLE, UWB, NFC, local Wi-Fi) with a challenge-response using a key bound to the VIN, not a coordinate sent by the phone. The same token, same API; the vehicle adds a `proximity` attribute to the session and refuses local-only operations without it. Hold an exclusive lock with an expiry on the target (SOVD `locks`: acquire with expiry, 409 on break) so a remote request cannot race a local one.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 17978 (SOVD) locks, operations, modes | lock with expiry; operation executions; mode changes | the vehicle-side authorisation points |
| CCC Digital Key (BLE/UWB, unverified detail) | distance bounding with a vehicle-bound key | proximity decided by the vehicle |
| W3C VISS v2 | JWT with long-term proof-of-possession | token bound to a device key |
| Hono command and control | cloud command to device, device decides | remote path with a device-side veto |
| Eclipse KUKSA Android SDK/companion (Alpha) | phone reads and writes VSS via databroker | the phone-side client |

**On the Eclipse SDV stack.**
- Companion blueprint: a mobile or cloud trigger sends MQTT, a Velocitas Seat Adjuster writes VSS through KUKSA Databroker; it is docs only and written for Leda M2, with no authentication or proximity concept ([[sdv-blueprints-overview]]).
- Proximity gate belongs where the actuation is admitted: a KUKSA provider or Velocitas app that checks a `Vehicle.X.ProximityAuthorized`-style overlay signal set by a vehicle-side agent, never by the phone. The overlay signal name is a proposal.
- OpenSOVD core has no `locks`, `operations` or `modes` yet; the CDA does ([[opensovd-reference]]). A proximity attribute in the token plus a lock gives the missing check for SOVD operations; no SDV component implements it.
- Remote path rides the fleet plane: key `fleet/<vin>/cmd/**` with the per-vehicle ACL of [[per-vehicle-credentials-audience-is-the-vin]].

**The trap.** Sending the phone's GPS position in the request and trusting it.

**For a hackathon team.** One Android or Python client; the same "seat to position" request succeeds over local BLE/LAN (vehicle side-channel challenge) and is refused over the remote route, with the refusal shown as a VSS signal. Pitch: "the car decides who is standing next to it".

**Evidence.** Companion blueprint contents: repos/companion-application/Readme.md. SOVD locks/operations not in core: [[opensovd-reference]] (rows 56, 120-123). Digital Key and the kuksa-android-companion app details unverified. No source in this vault defines proximity proof for SOVD: this card is a design proposal.
