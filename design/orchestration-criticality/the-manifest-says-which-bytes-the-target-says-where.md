---
title: The manifest says which bytes; the target config says where to mount them
type: pattern
cluster: orchestration-criticality
component: none
tags: [layers, squashfs, apex, ostree, flatpak, opt, mount-hook, block-device, dm-verity]
status: draft
sources:
  - https://source.android.com/docs/core/ota/apex (APEX: loop device, dm-verity, /apex/name@ver)
  - https://docs.flatpak.org/en/latest/under-the-hood.html (Flatpak runtimes and apps as OSTree checkouts) (unverified, not fetched)
  - https://docs.yoctoproject.org/ (image types: squashfs, wic; read-only rootfs) (unverified, not fetched)
  - https://docs.kernel.org/admin-guide/device-mapper/verity.html
  - repos/automotive-image-builder/include/defaults.ipp.yml (composefs, verity generator)
last-verified: 2026-10-03
related:
  - "[[config-in-the-image-intent-in-the-manifest]]"
  - "[[placement-is-a-manifest-not-a-model-edit]]"
applies-to: [autosd, ankaios, symphony]
gap-rows: [C3, C5]
---

# The manifest says which bytes; the target config says where to mount them

**Problem.** Application software ships as read-only filesystem images (SquashFS or EROFS), flashed to a block device or partition, and mounted by a boot hook under `/opt/<app>`. If the release manifest hard-codes mount points, every target variant needs a different release; if the target hard-codes content, you cannot update one layer.

**Forces.**
- Layers must be independently updatable and verifiable (hash, signature, verity).
- Mount points differ by target (partition labels, device names, rootfs layout).
- The platform layer must not depend on application layers being present.
- Rollback needs the old bytes still addressable.

**The rule.** Split two documents. The **release manifest** names layers by content: id, version, size, digest (and signature), nothing about the machine. The **target configuration** (per node, part of the base image or board support) maps layer id to device or partition and to a mount point, plus mount options (`ro,nosuid,nodev`) and an ordering relative to the workloads that need it. A mount hook reads both: verify the bytes against the manifest digest (preferably dm-verity at the block level), then mount where the target says. Workloads then see a stable path (`/opt/app`) regardless of which block device carried it.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Android APEX | package verified with public key, loop device plus dm-verity device, mounted at `/apex/<name>@<ver>` with a bind mount for the active version | manifest/package verification then a fixed mount namespace (verified) |
| Flatpak / OSTree deployments | runtimes and apps are content-addressed trees checked out under a fixed layout | content id separate from where it appears (unverified, not fetched) |
| Yocto read-only rootfs images | squashfs or ext4 images assembled per image recipe; fstab per machine | image bytes vs machine-specific mount config (unverified, not fetched) |
| bootc composefs | content-addressed read-only root with fs-verity | verified tree under the same split |
| dm-verity | block hash tree, root hash passed on kernel command line | the integrity mechanism for a flashed layer |

**On the Eclipse SDV stack.** There is no upstream Eclipse artefact for flashed application layers: AutoSD embeds containers in the bootc image, and Ankaios pulls OCI images. The gap is the in-between for HPCs with an immutable base and separately flashed application partitions. Build it as a Symphony Solution component or an Ankaios workload whose `files:` or `runtimeConfig` names a layer id and digest, while a target-side file (part of the base image, [[config-in-the-image-intent-in-the-manifest]]) maps id to device and mount path. Then a software update is a manifest change, and a new board is a target-config change. Ankaios `agent` tags (see [[placement-is-a-manifest-not-a-model-edit]]) select which targets get which layers.

**The trap.** Putting `/dev/mmcblk0p7` in the release manifest; the release is then valid on exactly one board.

**For a hackathon team.** Build two tiny SquashFS images with `mksquashfs`, a 20-line mount script that reads `layers.yaml` (id, sha256) and `target.yaml` (id to loop device and path), and show that swapping the target file lets the same release mount on a second layout. Pitch: "which bytes in the release, where in the target". Public OEM-neutral framing only.

**Evidence.** APEX behaviour verified against the Android docs page. Flatpak and Yocto rows are from general knowledge, not fetched (unverified). AIB composefs and verity-generator defaults: defaults.ipp.yml. The claim that the pattern appears in several OEM stacks is the requester's; not sourced here.
