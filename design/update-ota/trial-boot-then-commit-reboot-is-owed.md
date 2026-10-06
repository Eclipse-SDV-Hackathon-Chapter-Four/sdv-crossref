---
title: Trial boot, then commit, and the reboot is owed
type: pattern
cluster: update-ota
component: none
tags: [ab, virtual-ab, bootc, ostree, greenboot, u-boot, bootcount, watchdog, transaction, commit, rollback]
status: draft
sources:
  - https://source.android.com/docs/core/ota/ab (A/B, boot control HAL, markBootSuccessful)
  - https://source.android.com/docs/core/ota/virtual_ab (snapshot, merge after successful boot)
  - https://github.com/bootc-dev/bootc/blob/main/docs/src/man/bootc-upgrade.8.md (staged, applied at shutdown)
  - https://github.com/bootc-dev/bootc/blob/main/docs/src/man/bootc-rollback.8.md
  - https://github.com/fedora-iot/greenboot-rs (health checks, boot_counter, rollback for bootc)
  - https://docs.u-boot.org/en/latest/api/bootcount.html (bootcount, bootlimit, altbootcmd, upgrade_available)
  - https://rauc.readthedocs.io/en/latest/ (RAUC slots, mark-good)
last-verified: 2026-10-03
related:
  - "[[security-version-is-not-build-order]]"
  - "[[the-component-owns-its-verdict]]"
  - "[[never-mix-banked-and-singleshot]]"
  - "[[a-campaign-commits-all-or-rolls-back-all]]"
applies-to: [autosd, opensovd, ankaios, symphony]
gap-rows: [H3, H4, H6, C2]
---

# Trial boot, then commit, and the reboot is owed

**Problem.** An update is written, the node reboots, the new image comes up "fine" and is declared done. Then it fails on the next cold start, or power drops between staging and reboot, and the node either loses the update silently, applies it twice, or has already thrown away the image it should fall back to.

**Forces.**
- The only real test of a boot image is booting it.
- Power can fail at every step; the state machine must survive it.
- Committing too early forfeits rollback; committing never leaves the node in trial forever.
- The node is often not the one deciding when to reboot (driver, parked state, workshop).

**The rule.** A node-level update is a durable transaction with four resting states: **idle → staging → reboot-pending → trial → idle**. Staging writes the inactive bank and is invisible to the running system. Reboot-pending is persisted ("a reboot is owed") so that a power cycle completes the transaction instead of forgetting it, and so that the vehicle can choose *when*. Trial boots the new bank with an armed attempt counter or watchdog; the old bank is untouched. Commit (mark good, raise the security floor, release the old bank) happens only after an explicit verdict ([[the-component-owns-its-verdict]]); counter exhaustion or a negative verdict selects the old bank automatically.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Android A/B | slot flags bootable, successful, active; unsuccessful slots marked unbootable after retries; `markBootSuccessful()` after `update_verifier` | trial and commit in the boot control HAL |
| Android Virtual A/B | delta written to a COW snapshot, merged into base partitions "after confirming a successful boot"; no rollback after merge | the commit point is the merge |
| bootc / OSTree | `bootc upgrade` queues a *staged* deployment applied at shutdown; `bootc status` shows booted/staged/rollback; `bootc rollback` reorders entries | A/B for whole OS images, no reflash |
| greenboot-rs | required health checks; on failure reboot, then roll back to the previous deployment; manages `boot_counter` / `boot_success` | the missing automatic trial verdict for bootc |
| U-Boot bootcount | `upgrade_available` arms counting, `bootlimit` exceeded runs `altbootcmd`; userspace resets `bootcount` on success | bootloader-level attempt counter |
| RAUC | A/B slots with `mark-good` / `mark-bad` from userspace | embedded Linux reference implementation |

**On the Eclipse SDV stack.** AutoSD already ships bootc images ([[autosd-overview]]): staging and rollback exist, but automatic trial rollback needs greenboot(-rs) added to the image, and nothing maps the result upward. The SOVD `/updates` state machine proposed in [[gap-register]] H3 (preparing → awaiting reboot → verifying → committed or rolled back) is exactly this transaction exposed on the wire ([[opensovd-reference]]). Ankaios workloads have no banks; "rollback" there is a forward re-apply of the previous manifest, which is acceptable for containers only if the previous image is still addressable by digest ([[release-is-the-hash-of-its-parts]]).

**The trap.** Treating "it rebooted and answered" as success, or committing in the post-install step before the trial boot.

**For a hackathon team.** On a bootc VM: `bootc switch` to a new image, a greenboot `required.d` check that fails on purpose, show the automatic return to the old deployment, and expose the four states as an SOVD-style status JSON. Pitch: "the car always has a bank it knows boots".

**Evidence.** Android and Virtual A/B: source.android.com pages (fetched 2026-10-03). bootc staged/rollback: man pages `bootc-upgrade.8.md`, `bootc-rollback.8.md` in bootc-dev/bootc main. greenboot-rs README (rollback, `boot_counter`). U-Boot bootcount page. RAUC mark-good from RAUC docs (not re-fetched; standard RAUC CLI). The four-state naming is this card's, not a standard's.
