---
title: Security version is not build order
type: pattern
cluster: update-ota
component: none
tags: [anti-rollback, security-version, sequence-number, avb, mcuboot, uptane, ab-testing, commit]
status: draft
sources:
  - https://android.googlesource.com/platform/external/avb/+/refs/heads/main/README.md (Rollback Protection; Updating Stored Rollback Indexes)
  - https://docs.mcuboot.com/design.html (hardware rollback protection, security counter)
  - https://uptane.org/docs/2.1.0/deployment/best-practices (release counters, §6.1)
  - https://www.rfc-editor.org/rfc/rfc9124 (§3.2 monotonic sequence number "is not a firmware version field")
  - https://datatracker.ietf.org/doc/html/draft-ietf-suit-manifest (sequence number as anti-rollback counter)
last-verified: 2026-10-03
related:
  - "[[versions-ratchet-even-when-the-clock-lies]]"
  - "[[trial-boot-then-commit-reboot-is-owed]]"
  - "[[a-campaign-commits-all-or-rolls-back-all]]"
applies-to: [symphony, ankaios, opensovd, autosd, openbsw]
gap-rows: [H4, H5, H3]
---

# Security version is not build order

**Problem.** If the anti-rollback counter is the build number, every release becomes a one-way door: a fleet cannot A/B-test build 107 against 105, cannot step back from a bad but harmless release, and a trial that fails after the counter moved leaves the old bank unbootable.

**Forces.**
- Attackers must not reinstall images with known vulnerabilities.
- Operators must be free to move between builds that are equally safe.
- Metadata needs its own freshness counter that always increases.
- A trial must stay revertible until it is committed.

**The rule.** Keep three numbers apart. The **version** is a label for humans. The **sequence number** orders manifests from one signer and always increases (freshness, not policy). The **security version** says "everything below this has a known hole"; it rises only when a vulnerability is fixed, many builds share one value, and the device refuses anything below its stored floor. Raise the floor on **commit**, never on install or trial, and only from the committed slot. To retire a vulnerable build fleet-wide without shipping code, send a **policy-only** signed manifest that carries nothing but a new floor; it is accepted once the running image already satisfies it.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Android Verified Boot | `rollback_index[n]` is "increased for each image as security flaws are discovered and fixed"; with A/B, stored indexes are updated "only from slots that are marked as SUCCESSFUL" | security floor separate from build, raised on commit |
| MCUboot hardware rollback protection | security counter in the signed TLV area; counters "do not need to increase with each software release", so equal-counter downgrades are accepted | the same split on microcontrollers |
| Uptane release counters | Director targets carry a release counter; ECUs refuse lower; best practices warn against never incrementing it | limits what a compromised director can downgrade to |
| RFC 9124 / SUIT manifest | sequence number "is not a firmware version field. It is a manifest sequence number" | freshness counter kept apart from versioning |

**On the Eclipse SDV stack.** None of the Eclipse update paths model this ([[gap-register]] H4): Symphony campaigns and Ankaios manifests name images by tag, and the Chapter 3 "rollback" was a forward redeploy of an older container spec (`repos/hc3-MegaBosses/activations/campaign_activation_reverse.json`, [[chapter3-retrospective]]). Add `security_version` to the signed image manifest ([[the-manifest-programs-the-device]]); store the floor per component in the HPC update agent (and in MCU secure storage behind it); raise it in the commit step of SOVD `/updates` or the fleet campaign ([[a-campaign-commits-all-or-rolls-back-all]]). For AutoSD/bootc, the floor check belongs in the agent before `bootc switch`, since bootc itself checks no counter (inferred from bootc docs).

**The trap.** Using the build number (or a semver compare) as the anti-rollback check, or raising the floor at install time.

**For a hackathon team.** Three builds: v1 (sv=1), v2 (sv=2), v3 (sv=2). Show v3 → v2 rollback accepted, v2 → v1 refused after commit, and a trial of v3 that fails leaving v2 bootable because the floor did not move. Pitch: "we can A/B test freely and still never go back to a known hole".

**Evidence.** AVB quotes: README sections "Rollback Protection" and "Updating Stored Rollback Indexes" (fetched 2026-10-03). MCUboot quote: design.html "Security counter". Uptane: Best Practices 2.1.0 §6.1. Policy-only manifests are a design pattern here, not a named SUIT feature (unverified whether draft-ietf-suit-update-management covers it).
