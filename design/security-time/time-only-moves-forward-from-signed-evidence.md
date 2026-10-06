---
title: Time only moves forward, and only on signed evidence
type: pattern
cluster: security-time
component: none
tags: [time, freshness, clock, monotonic, boot-id, roughtime, uptane, tpm, rollback]
status: draft
sources:
  - https://uptane.org/papers/V1.2.0_uptane_deploy.html (Time Server: tokens, signed attestation, "later than the last time verified")
  - https://uptane.org/papers/V2.0.0_uptane_deploy.html (Time Server removed; NTS SHOULD, Roughtime MAY, GPS SHOULD NOT)
  - https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/ (draft-19, Ed25519, MIDP/RADI, chained nonces)
  - https://www.rfc-editor.org/rfc/rfc8915 (NTS for NTP)
  - https://trustedcomputinggroup.org/resource/tpm-library-specification/ (TPMS_CLOCK_INFO: clock, resetCount, restartCount, safe)
  - https://man7.org/linux/man-pages/man5/proc_sys_kernel.5.html (`random/boot_id`)
  - https://theupdateframework.github.io/specification/latest/ (freeze attacks, metadata expiry)
last-verified: 2026-10-03
related:
  - "[[verify-offline-against-a-pinned-root]]"
  - "[[opensovd-reference]]"
  - "[[let-the-standard-timestamp-your-evidence]]"
applies-to: [opensovd, symphony, ankaios, autosd, vss-kuksa]
gap-rows: [H8, H4, H5, H7]
---

# Time only moves forward, and only on signed evidence

**Problem.** A parked vehicle's RTC is whatever the last person set it to. Wind it back a year and every expired workshop token, revoked certificate and stale update manifest is valid again; wind it forward and the car refuses its own legitimate updates.

**Forces.**
- `exp`, `nbf`, certificate validity and metadata expiry all read the wall clock.
- GPS time is spoofable; NTP is unauthenticated without NTS; the workshop LAN may have neither.
- A secure-storage write per second wears flash; a floor that never moves is useless.
- An honest clock reset (new battery, new time authority) must not brick the vehicle.

**The rule.** Keep three clocks apart. **Boot-relative**: `(boot_id, monotonic ns)` for anything that only has to be fresh within this power cycle (sessions, nonces, locks, SSE subscriptions); never persist it. **Counters**: monotonic counters in secure storage for ordering across boots (anti-rollback, token serials). **Safe-time floor**: a persisted lower bound on real time, raised only from signed artefacts the device already verifies, each carrying a time: update manifests, token `iat`, a Roughtime response (`MIDP - RADI`), an NTS-authenticated sample. Every validity check uses `now = max(rtc, floor)`; the floor never goes down, except on a signed time-authority rotation. Writes are rate-limited (raise only when the gain exceeds, say, an hour). The residual gap is honest and must be stated: a vehicle that has seen no signed time since day *D* accepts anything valid at *D*, so token lifetimes must be short and revocation must ride on the same signed artefacts.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Uptane 1.x Time Server | ECUs send nonce tokens; server returns signed time incl. all tokens; accept only if "later than the last time verified" | nonce-bound freshness plus a ratchet |
| Uptane 2.0 deployment practices | Time Server recommendation removed; NTS SHOULD, Roughtime MAY, GPS SHOULD NOT; ECUs "will not accept an earlier time" signed with the same key; reset the floor on time-key rotation | the ratchet survives, the source becomes pluggable |
| IETF Roughtime (draft-19) | client nonce, Ed25519-signed midpoint ± radius, chained requests prove server misbehaviour | cheap signed time with an error bar |
| TPM 2.0 clock | `clock` persisted, `resetCount`/`restartCount`, `safe` flag if the last value may have been lost | hardware floor with a crash-honesty bit |
| Linux `boot_id`, systemd journal | random id per boot plus `CLOCK_MONOTONIC`; journal stamps both | boot-relative ordering without wall time |
| TUF | expiring metadata defeats freeze attacks only if the client clock is right | why the floor matters for updates |

**On the Eclipse SDV stack.**
- OpenSOVD core `JwtAuthenticator` uses `jsonwebtoken`'s `exp` check against the system clock; a `TimeSource` injected beside the `Authenticator` (`fn now() -> max(rtc, floor)`) is the seam ([[opensovd-reference]]).
- Raise the floor from whatever is signed on the target: the update manifest's `issued_at` in an H3/H5 flow, a verified token's `iat`, a Roughtime response fetched by a helper workload under [[ankaios-overview]].
- SOVD `locks` and `cyclic-subscriptions` (H1) expiries should be `(boot_id, monotonic)`; a reboot invalidates them, which is the correct semantics.
- Evidence records (A5) should carry both `boot_id + monotonic` and wall time, so a timeline survives a wrong clock ([[let-the-standard-timestamp-your-evidence]]).

**The trap.** Trusting the RTC because "the car has a clock", or persisting a monotonic timestamp across reboots as if it were wall time.

**For a hackathon team.** A 50-line `floor.json` (signed or in a TPM NV index if present), raised from each accepted token's `iat`; demo: set the system clock back two days with `date -s`, an expired token is still refused. Pitch line: "our clock can be wrong, it cannot go backwards".

**Evidence.** Uptane 1.2.0 Time Server procedure and 2.0.0 removal and time-source guidance: fetched and quoted from the two deployment-practice pages in `sources` (2.0.0 changelog: "no longer recommending the Uptane Time Server"). Roughtime fields and chaining: draft-19. TPM clock fields from TPM 2.0 Library Part 2 (unverified section number). OpenSOVD time use: `repos/opensovd-core/opensovd-extra/src/auth/jwt.rs` (`Validation` default `validate_exp`).
