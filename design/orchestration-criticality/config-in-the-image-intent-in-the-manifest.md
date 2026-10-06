---
title: Configuration belongs in the image or in the manifest, never in a mutated /etc
type: pattern
cluster: orchestration-criticality
component: none
tags: [bootc, ostree, image-mode, quadlet, etc, dm-verity, composefs, sealed]
status: draft
sources:
  - repos/automotive-image-builder/README.md (use_transient_etc)
  - repos/automotive-image-builder/include/defaults.ipp.yml (use_composefs_signed, use_transient_etc, containers_transient_store)
  - repos/automotive-image-builder/docs/CODEBASE.md (path validation: /etc, /usr, /var)
  - repos/sample-images/images/qm-container.aib.yml (quadlets via add_files, container_images embedded)
  - https://bootc.dev/bootc/
  - https://docs.kernel.org/admin-guide/device-mapper/verity.html
  - https://ostreedev.github.io/ostree/
last-verified: 2026-10-03
related:
  - "[[autosd-overview]]"
  - "[[the-manifest-says-which-bytes-the-target-says-where]]"
applies-to: [autosd, ankaios]
gap-rows: [C3, C2]
---

# Configuration belongs in the image or in the manifest, never in a mutated /etc

**Problem.** A team SSHes into the vehicle, edits `/etc/containers/systemd/x.container`, and the demo works. After the next `bootc update`, or a reboot with transient `/etc`, the change is gone or silently merged.

**Forces.**
- Image-mode OSes make `/usr` immutable and swap the whole tree atomically; mutable state is a liability for rollback.
- Ankaios workload config changes at runtime; image config changes only with an update.
- Offline operation needs container images embedded in the image, not pulled.
- Guest rootfs under a hypervisor wants integrity (dm-verity) and so cannot be edited at all.

**The rule.** Two homes only. **In the image**: everything that must exist at boot and be identical per variant: quadlets for the supervisor layer, the Ankaios agent, embedded container images, SELinux policy. **In the manifest** (desired state, applied at runtime): workload set, versions, restart policy, per-node parameters. Anything else (hand edits) is lost by design: AIB defaults to `use_transient_etc: true` and signed composefs; flip the flag only for development. Per-vehicle secrets and identity live under `/var` or a provisioning step, not in either.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| bootc / OSTree | image-based atomic updates; `/usr` read-only; `/etc` merged on update; `/var` persistent | rollback is a bank switch |
| AIB `use_transient_etc`, `use_composefs_signed` | transient `/etc`, signed composefs | reboot returns to image truth |
| Podman quadlet | container as a systemd unit generated from a `.container` file | the unit is a deployable file, so it can live in the image |
| dm-verity | block-level hash tree verified on read | tamper-evident read-only rootfs (guests) |
| NixOS / Fedora CoreOS (Ignition) | declarative host config at first boot | same split: image plus first-boot manifest |

**On the Eclipse SDV stack.** AutoSD's `.aib.yml` `add_files` plus `container_images` is the image side: `qm-container.aib.yml` puts `radio.container` in `/etc/containers/systemd/` of the QM partition and embeds the container image ([[autosd-overview]]). Gap C3 is the derived bootc image with KUKSA and Zenoh quadlets (`FROM ghcr.io/eclipse-autosd/eclipse-autosd-bootc-qemu`). The Ankaios manifest (server `state.yaml` or `ank apply`) is the runtime side. Rule of thumb: if changing it should need a new image version and a rollback test, it is image; if it should be a fleet toggle, it is manifest.

**The trap.** Debugging with an in-place edit that happens to survive until the first update.

**For a hackathon team.** Bake one quadlet and one embedded image into a derived bootc image, change a parameter via the manifest only, and show a reboot with an edited `/etc` file reverting. Pitch: "image is the platform, manifest is the intent".

**Evidence.** Transient etc defaults and README text: AIB README and defaults.ipp.yml. `/etc`/`/var` merge semantics of bootc and OSTree: standard documented behaviour (bootc.dev, not re-fetched; unverified here). dm-verity for guests: see [[guest-memory-is-granted-diagnostics-come-by-gateway]].
