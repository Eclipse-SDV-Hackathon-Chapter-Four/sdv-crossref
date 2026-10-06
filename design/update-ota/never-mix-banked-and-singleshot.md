---
title: Never mix banked and singleshot parts in one transaction
type: pattern
cluster: update-ota
component: none
tags: [transaction, ab, hsm, keys, irreversible, orchestrator, invariant, mcuboot, virtual-ab]
status: draft
sources:
  - https://source.android.com/docs/core/ota/virtual_ab (no rollback after merge)
  - https://android.googlesource.com/platform/external/avb/+/refs/heads/main/README.md (stored rollback indexes only from successful slots)
  - https://docs.mcuboot.com/design.html (swap with revert vs overwrite-only; image_ok)
  - https://uptane.org/docs/2.1.0/deployment/best-practices (ECU key compromise: manual update)
  - https://datatracker.ietf.org/doc/html/draft-ietf-suit-trust-domains (staging vs installation procedure)
last-verified: 2026-10-03
related:
  - "[[trial-boot-then-commit-reboot-is-owed]]"
  - "[[a-campaign-commits-all-or-rolls-back-all]]"
  - "[[security-version-is-not-build-order]]"
applies-to: [opensovd, symphony, ankaios, autosd, openbsw]
gap-rows: [H6, H3, H4]
---

# Never mix banked and singleshot parts in one transaction

**Problem.** An update bundles a new VM image (A/B, revertible) with new HSM key material or a bootloader (written in place, irreversible). The VM trial fails and rolls back, but the keys have already moved: the old image cannot decrypt its own storage or authenticate to the backend. The vehicle is stuck between two versions, neither of which works.

**Forces.**
- Some components have two banks (HPC rootfs, VM images, dual-bank MCU flash); some have one (HSM keys, OTP fuses, bootloaders, single-bank MCUs, a merged Virtual A/B).
- Release managers want "one update" for the user and the regulator.
- The device sees one component at a time; only the planner sees the whole set.
- Irreversible steps are often the security-critical ones.

**The rule.** Classify every component as **banked** (has a trial and a fallback) or **singleshot** (applied in place, no way back). A transaction is either all-banked (trial all, verdict all, commit all) or a single singleshot step on its own, scheduled only after every banked part it depends on is committed, and designed so that both the old and the new committed images work with the new singleshot state (forward-compatible first, then switch). The orchestrator enforces this at plan time and refuses a mixed plan; the device cannot, because it never sees the whole transaction.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Android Virtual A/B | rollback is possible until the snapshot merge; once merged the old data is gone | an A/B system becomes singleshot at one known point |
| Android Verified Boot | stored rollback indexes (a one-way fuse-like state) are updated only from slots marked successful | the irreversible write waits for the banked commit |
| MCUboot | swap-with-revert (test, then `image_ok`) vs overwrite-only (no revert) upgrade modes | the bank/singleshot classification is a build option per image |
| Uptane Best Practices | compromised ECU keys: "the OEM SHOULD manually update vehicles to replace these keys" | key material is treated as outside the revertible OTA path |
| SUIT trust domains | separate staging and installation procedures | stage everything revertibly before anything irreversible runs |

**On the Eclipse SDV stack.** No Eclipse note models this ([[gap-register]] H6). The guard belongs where the plan is built: a Symphony campaign stage, the fleet campaign of [[a-campaign-commits-all-or-rolls-back-all]], or the SOVD `/updates` `register` step that can return 409/400 for a mixed package ([[opensovd-reference]]). Mark each component's class in the signed image manifest (`"bank": "ab" | "singleshot"`), so the planner reads it rather than guessing. On the device side, bootc/AutoSD images are banked ([[autosd-overview]]); an OpenBSW or ThreadX MCU without a dual-bank bootloader is singleshot ([[the-hpc-is-the-mcus-update-gateway]]).

**The trap.** Rolling a key rotation into the same "release" as the software that uses the new keys, because it looks atomic to the user.

**For a hackathon team.** A planner function `validate(plan)` that rejects any plan mixing `ab` and `singleshot` components, plus a demo plan that splits into "release N (all banked) → commit → key step". Pitch: "rollback is a promise; we refuse plans that would break it".

**Evidence.** Virtual A/B merge semantics: source.android.com (fetched 2026-10-03). AVB: README "Updating Stored Rollback Indexes". MCUboot upgrade modes: design.html (swap and overwrite-only described there; not re-quoted). Uptane quote: Best Practices 2.1.0 §2.1.2. The invariant itself is a design rule synthesised from these; no standard states it in one sentence.
