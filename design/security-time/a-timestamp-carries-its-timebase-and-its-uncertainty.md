---
title: A timestamp carries its timebase and its uncertainty
type: pattern
cluster: security-time
component: none
tags: [time, timestamp, timebase, gptp, 802.1as, synchronisation, uncertainty, hlc, uprotocol, iceoryx2]
status: draft
sources:
  - https://standards.ieee.org/ieee/802.1AS/7121/ (IEEE 802.1AS gPTP, unverified clause)
  - https://www.autosar.org/ (AUTOSAR Synchronized Time-Base Manager: timeBaseStatus bits GLOBAL_TIME_BASE, TIMEOUT, SYNC_TO_GATEWAY, unverified)
  - https://www.rfc-editor.org/rfc/rfc9562 (UUIDv7: Unix-epoch milliseconds)
  - repos/up-spec/basics/uuid.adoc (UAttributes ids MUST be UUIDv7)
  - repos/zenoh/Cargo.toml (depends on uhlc, a hybrid logical clock)
last-verified: 2026-10-03
related:
  - "[[a-replay-is-evidence-only-with-the-producers-stamps]]"
  - "[[detect-silence-with-a-clock-not-with-data]]"
  - "[[time-only-moves-forward-from-signed-evidence]]"
  - "[[stamp-the-instant-once-refuse-the-spread]]"
applies-to: [iceoryx2, vss-kuksa, uprotocol, zenoh]
gap-rows: [A15, A5, A8]
---

# A timestamp carries its timebase and its uncertainty

**Problem.** A fault timeline merges stamps from an MCU, a zonal provider, a recorder and a cloud exporter. Some are boot-relative, some are gPTP, one is the recorder's receive time; all are `uint64 ns`. The timeline orders events that the clocks cannot order, and a frozen provider whose stamps keep advancing looks healthy.

**Forces.**
- Every ECU has a local monotonic clock; only some are synchronised, and sync can be lost without anyone noticing.
- Adding a timebase id and an error bound costs bytes in every sample.
- Consumers want one number; correct ordering needs two (value and how good it is).
- Scope: this is SDV event ordering at millisecond to microsecond scale, not RF or sensor-fusion precision timing.

**The rule.** Every timestamp field names *which clock produced it* (local monotonic plus boot id, gPTP/802.1AS global time, GNSS, vehicle time base) and *how good it is* (synchronised or not, last sync age, uncertainty bound). A consumer then decides: compare only stamps of the same timebase, treat an unsynchronised stamp as local, widen comparisons by the bounds, and refuse to order two events whose intervals overlap. A recorder adds its own stamp beside the producer's, never in place of it. Freshness is judged on the consumer's own clock, never on the producer's claim.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| IEEE 802.1AS (gPTP) | one grandmaster time distributed over the in-vehicle Ethernet with measured path delay | a shared timebase with a known error budget (unverified clause) |
| AUTOSAR Synchronized Time-Base Manager | a time-base id plus status bits (global time reached, timeout, synced to gateway) delivered with the time | consumers see whether the stamp is trustworthy (unverified) |
| iceoryx2 record | `iox2 record` stamps the recorder's receive time | a second clock, not the producer's ([[a-replay-is-evidence-only-with-the-producers-stamps]], R) |
| Freshness by deadline | fresh-looking producer stamps do not prove a live producer | judge liveness on the consumer's clock ([[detect-silence-with-a-clock-not-with-data]], R) |
| Linux `boot_id` + `CLOCK_MONOTONIC` | a boot-relative stamp names its boot | local time that cannot be confused across reboots ([[time-only-moves-forward-from-signed-evidence]]) |

**On the Eclipse SDV stack.** In iceoryx2 the user header is the place for `{timebase_id, sync_state, uncertainty_ns, stamp}` ([[iceoryx2-overview]]). In VSS a metadata overlay field (or a sibling struct) can name the timebase of a provider's timestamps; KUKSA `Datapoint.timestamp` alone does not say ([[vss-kuksa-reference]]). uProtocol `UAttributes.id` MUST be a UUIDv7 (`repos/up-spec/basics/uuid.adoc`), which carries Unix-epoch milliseconds, but the spec does not say which clock or how synchronised (unverified beyond the text read). Zenoh stamps samples with a hybrid logical clock (`uhlc` in `repos/zenoh/Cargo.toml`) ([[zenoh-overview]]). The A15 edge witness is an MCU whose own timebase is declared, which is what makes it an independent source.

**The trap.** Treating a transport's hybrid logical clock (or a UUIDv7 time field) as physical time: it orders messages causally and stays close to wall time, but it is not a measurement of when the event happened.

**For a hackathon team.** Add two fields, `timebase` and `uncertainty_ns`, to the event schema (A10/A14) and make the timeline draw overlapping intervals as "order unknown". Pitch: "our timeline says when it does not know".

**Evidence.** The two R pointers are the iceoryx2 record behaviour and the deadline rule in the linked cards. UUIDv7 requirement read in `repos/up-spec/basics/uuid.adoc` line 27; Zenoh's `uhlc` dependency read in `repos/zenoh/Cargo.toml`; whether Zenoh's HLC tracks a synchronised clock is unverified. gPTP and AUTOSAR StbM rows are spec names only, not checked against the text (unverified). The pattern itself is P.
