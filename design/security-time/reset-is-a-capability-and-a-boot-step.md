---
title: Reset is a capability and a boot step, never an in-place delete
type: pattern
cluster: security-time
component: none
tags: [factory-reset, recovery, idempotency, secure-boot, fail-closed, anti-rollback, capability]
status: draft
sources:
  - https://chromium.org/chromium-os/chromiumos-design-docs/powerwash (Powerwash: request, wipe at next boot, preserve allowlist)
  - https://source.android.com/docs/security/features/verifiedboot/verified-boot (AVB: rollback indexes, boot states)
  - https://source.android.com/docs/core/ota/ab (A/B, recovery)
  - https://trustedcomputinggroup.org/resource/tpm-library-specification/ (TPM2_Clear vs platform hierarchy)
  - https://www.iso.org/standard/72439.html (ISO 14229-1 ECUReset 0x11)
  - https://bootc.dev/ (bootc image-based updates and rollback)
last-verified: 2026-10-03
related:
  - "[[the-route-names-the-capability-the-token-carries-it]]"
  - "[[time-only-moves-forward-from-signed-evidence]]"
  - "[[one-name-in-mdns-in-the-cert-and-in-the-url]]"
  - "[[opensovd-reference]]"
  - "[[autosd-overview]]"
applies-to: [opensovd, autosd, ankaios, symphony]
gap-rows: [H3, H4, H6, H7]
---

# Reset is a capability and a boot step, never an in-place delete

**Problem.** A `POST /reset` handler starts `rm -rf /var/lib/app/*` while services still run, the connection drops halfway, the tool retries, and the device boots with half its state, or with its trust anchors and anti-rollback counters gone, so an attacker who can trigger a reset can also downgrade it.

**Forces.**
- Destructive operations must be rarer and better guarded than reads.
- A wipe that runs while the system is up races its own services.
- Networks drop; tools retry; the second request must not do something different.
- "Factory" state must remove the owner's data but not the device's identity or its security floors.

**The rule.** Model every destructive operation as its own capability (`reset:user-data`, `reset:recovery`, `clear:faults`), never implied by "admin". The server only *records* a reset request (`{request_id, kind, token jti}`) in a persistent flag and reboots; an early boot stage, before any workload starts, performs the wipe and clears the flag last, so an interrupted reset simply runs again. A repeat with the same `request_id` returns the recorded outcome. What a reset wipes: user and owner data, learned values, pairing, owner-issued credentials and caches. What it must not wipe: the birth identity key, pinned trust anchors, anti-rollback counters and security-version floors, the time floor, and the recovery image itself. Boot verification fails closed: if the main image does not verify, boot the recovery environment, never "boot anyway with a warning".

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ChromeOS Powerwash | wipe requested, performed at next boot; allowlisted files preserved through a ramdisk; `powerwash_count` incremented | boot-time wipe with an explicit keep-list |
| Android Verified Boot | rollback indexes in tamper-evident storage survive factory reset; failed verification → refuse or recovery | floors that a reset cannot lower |
| Android A/B + recovery | separate recovery path, slot marked bootable only after verification | a recovery environment that is not the main image |
| TPM 2.0 `TPM2_Clear` | clears owner/storage material; platform hierarchy and endorsement identity remain | "owner wipe" vs "device identity" split in hardware |
| ISO 14229 ECUReset (0x11) | hard/soft/key-off-on reset as a diagnostic service, gated by session and security level | reset as an access-controlled verb |

**On the Eclipse SDV stack.**
- SOVD exposes `status` (restart, force-restart, shutdown) and `clear-data` (cached, learned, client-defined) ([[opensovd-reference]]); neither exists in OpenSOVD core yet. Implement them as routes whose required capability is distinct (`reset:*`, [[the-route-names-the-capability-the-token-carries-it]]) and answer 202 with a status resource keyed by request id.
- On [[autosd-overview]], bootc already gives an immutable image and rollback; a reset is "drop `/var` state except the keep-list, keep `/etc/pki` anchors and the floor file", run from a systemd unit ordered before workloads.
- Under [[ankaios-overview]], stop workloads through the control interface before the reboot; the wipe still happens at boot.
- Keep the floor and counters outside the wiped area ([[time-only-moves-forward-from-signed-evidence]]); keep the device key ([[one-name-in-mdns-in-the-cert-and-in-the-url]]).

**The trap.** A reset that also clears anti-rollback counters, turning "factory reset" into "downgrade enabler".

**For a hackathon team.** A `reset-request.json` flag file, a oneshot systemd unit (or container entrypoint) that wipes `data/` except `keep/`, and a demo that kills the process mid-reset and shows the second boot finishing it; a token without `reset:user-data` gets 403. Pitch line: "resets are requested at runtime, executed at boot, and can be retried blind".

**Evidence.** Powerwash steps and preserve path: ChromiumOS design doc (fetched via search summary 2026-10-03). AVB rollback-index persistence across reset: AOSP verified-boot docs (behaviour as documented, not re-read in full). SOVD `status` and `clear-data` coverage: [[opensovd-reference]] table. TPM2_Clear hierarchy semantics: TPM 2.0 Library Part 3 (unverified section).
