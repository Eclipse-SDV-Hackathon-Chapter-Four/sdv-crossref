---
title: AutoSD — Overview
type: overview
component: autosd
tags: [autosd, centos-automotive-sig, rhivos, aib, bootc, quadlet, qm]
status: draft
sources:
  - https://sigs.centos.org/automotive/
  - https://gitlab.com/CentOS/automotive/sample-images
  - https://gitlab.com/CentOS/automotive/src/automotive-image-builder
  - repos/automotive-image-builder/README.md
  - repos/sample-images/images/
  - repos/eclipse-autosd/README.md
  - repos/hackfest-eclipse-score_reference_integration/images/autosd_x86_64/build/README.md
  - https://sigs.centos.org/automotive/autosd-10/getting-started/quick-start-guide.html
  - https://sig.centos.org/automotive/latest/building/autosd_pi4.html
  - https://sig.centos.org/automotive/latest/features-and-concepts/con_mixed-criticality.html
  - https://projects.eclipse.org/node/33726
last-verified: 2026-10-03
related:
  - "[[autosd-overview]]"
  - "[[autosd-quickstart]]"
  - "[[autosd-howto]]"
  - "[[autosd-reference]]"
  - "[[autosd-integration-notes]]"
  - "[[ankaios-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[s-core-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# AutoSD (Automotive Stream Distribution) — Overview

## What it is
- AutoSD is the **upstream, public, in-development binary distribution of the CentOS Automotive SIG**, based on CentOS Stream with automotive divergences (automotive kernel, QM, extra repos). It is the public preview of **Red Hat In-Vehicle Operating System (RHIVOS)**. [sigs.centos.org](https://sigs.centos.org/automotive), [docs discover page](https://docs.centos.org/automotive-sig-documentation/discover/)
- Current distro definitions: `autosd` -> `autosd10` (CentOS Stream 10 based nightly-validated snapshot), `autosd10-sig` (adds the SIG repo with Raspberry Pi support and dev tooling; the default for aib), `autosd10-latest-sig`. Downstream product distros `rhivos-2`, `rhivos-core-2` need Red Hat packages. `f43` (Fedora 43) is a "less supported" test distro. [repos/automotive-image-builder/README.distros.md](../../repos/automotive-image-builder/README.distros.md), `distro/*.ipp.yml`
- **Image mode / bootc**: aib builds **bootc container images** (immutable, atomically updatable, ostree underneath) from YAML manifests (`*.aib.yml`), then optionally a disk image (qcow2/raw). A running system updates with `bootc switch` / `bootc update`, no reflash. bootc never rolls back on its own: automatic rollback after a failed boot needs greenboot (greenboot-rs; the shell greenboot is deprecated) ([[trial-boot-then-commit-reboot-is-owed]]). [README.md of aib](../../repos/automotive-image-builder/README.md)
- **Mixed criticality**: a **QM partition** is a nested rootfs (`/usr/share/qm/rootfs`) with its own systemd and podman, for non-safety workloads; root partition (ASIL side) can monitor/stop it. Extra SELinux labels for QM containers. **BlueChi** orchestrates systemd services across partitions/nodes. [mixed-criticality doc](https://sig.centos.org/automotive/latest/features-and-concepts/con_mixed-criticality.html), `examples/qm.aib.yml`
- **Workloads**: podman + **quadlet** (`/etc/containers/systemd/*.container`) so containers are systemd units. Containers can be embedded in the image (`container_images:`) so they are available offline.

## What it is NOT
- Not a general-purpose desktop distro; the sample images are explicitly "proof of concept" ([sample-images README](../../repos/sample-images/README.md)). Default `root`/`password`, sshd root login in dev manifests: dev only.
- Not an orchestrator (no Ankaios-like API); BlueChi/systemd/quadlet are the native tools. Not cross-compiling: build x86_64 images on x86_64, aarch64 on aarch64 ([getting-started-on-linux](https://sig.centos.org/automotive/latest/getting-started/getting-started-on-linux.html)).
- Not safety-certified in its upstream form (ASIL-B certification claims concern the RHIVOS product: [press](https://www.mobilityoutlook.com/news/red-hat-achieves-milestone-with-asil-b-certified-in-vehicle-operating-system/)). Treat as "unverified" for any certification claim.

## Maturity and versions
- aib repo HEAD looked at: `e6f42f9c` (2026-09-29); sample-images `d6c1efef` (2026-05-06); eclipse-autosd `dd8e007c` (2026-10-02). Active.
- Targets in aib: qemu, abootqemu(+kvm), pc, ebbr (generic EBBR boards e.g. R-Car S4, S32G), rpi4, TI (am62sk, am69sk, beagleplay, j784s4evm, tda4vm_sk), Qualcomm ride4 variants, NXP imx8qxp_mek, Digi ccimx93dvk, aws, azure. **No rpi5 target** in `repos/automotive-image-builder/targets/` (checked). [README.targets.md](../../repos/automotive-image-builder/README.targets.md)
- Policy system (`--policy`, `.aibp.yml`) can force/forbid RPMs, sysctls, SELinux booleans, targets.

## Interfaces
- CLI: `aib build|to-disk-image|list-targets|list-dist|...`, `air` (QEMU runner), `auto-image-builder.sh` (runs aib in a container `quay.io/centos-sig-automotive/automotive-image-builder:latest`).
- Manifest schema: https://centos.gitlab.io/automotive/src/automotive-image-builder/manifest_schema.yml (local: `repos/automotive-image-builder/files/manifest_schema.yml`).
- Languages: manifests YAML, osbuild MPP internals (Python); workloads any (containers or RPMs).

## Ecosystem inside Eclipse SDV
- **Eclipse Automotive Integration for AutoSD** (`eclipse-autosd/eclipse-autosd`, Apache-2.0 in repo): published bootc images `ghcr.io/eclipse-autosd/eclipse-autosd-bootc-{qemu,rpi4}:latest` (x86_64 + aarch64 tags `-amd64`/`-arm64`), designed so SDV projects can `FROM` them and `bootc switch`. [repos/eclipse-autosd/README.md](../../repos/eclipse-autosd/README.md), [creation review](https://projects.eclipse.org/node/33726)
- **S-CORE**: `eclipse-score/inc_os_autosd` (Bazel rules `rules_aib` + toolchain) and the reference integration's `images/autosd_x86_64` (LoLa communication RPMs in root + QM partition). That image sets SELinux permissive, leaves the QM `memory_limit` infinite and bind-mounts `/dev/shm` + `/tmp/mw_com_lola` into QM, so it is a same-node sharing example, not a freedom-from-interference demonstration (corrected 2026-10-03, see [[freedom-from-interference-is-a-stack-of-layers]]). See [[s-core-overview]].
- Details: [[autosd-integration-notes]].

## Relevance to Chapter 4
- **[[chapter4-challenge-doctor-whodunit]] (runtime for the Guardian)**: AutoSD gives a realistic "vehicle OS" to host a guardian/diagnostic service: run its observer/UI as a quadlet container in the **QM partition** and keep the decider on the ASIL side (S-CORE safety manual: QM stays QM only with dependent-failure analysis; corrected 2026-10-03, see [[freedom-from-interference-has-three-axes]]), with a root-side watchdog (systemd/BlueChi) that can stop it; SELinux denials and the QM boundary become demonstrable "isolation" story. Cost: image build is minutes and root/podman-heavy, so prebuild before the event. (Fit judgement is the author's; challenge specifics are in the challenge note.)
- **[[chapter4-challenge-hack-to-the-future]] (portable target)**: AutoSD is a portable target in the sense of one manifest -> qemu / rpi4 / ebbr boards / cloud, x86_64 and aarch64. Because it ships as an OCI bootc image, any team can iterate in a container (`podman run` of the bootc image) and deploy to a VM by `bootc switch`. Raspberry Pi 5 is not supported.

## Pros / cons vs alternatives
| | AutoSD | Plain Fedora/Ubuntu | EB corbos Linux |
|---|---|---|---|
| Immutable + atomic update | yes (bootc/ostree) | Fedora Atomic/bootc yes; Ubuntu no | yes (Ubuntu-based, per vendor material; unverified here) |
| QM / mixed criticality, BlueChi | yes, built in | manual | partial/unverified |
| Time to first boot | download prebuilt qcow2 ~minutes; build ~10+ min | minutes | needs vendor access (unverified) |
| Ease for hackathon | medium: aib/osbuild quirks | easiest | unverified |
| RPM ecosystem for SDV projects | few (Ankaios COPR, S-CORE COPR); mostly containers | rich (Fedora) / apt | apt/Debian packaging (unverified) |
| Safety story | upstream of RHIVOS (ASIL-B product) | none | ASIL-B Linux offering (vendor claim, unverified) |

Use plain Fedora/Ubuntu when you only need to run a container fast. Use AutoSD when the point is the OS story: isolation, image update, vehicle-like target.

## Hackathon ideas
1. Quadlet + Ankaios: ship an Ankaios server/agent RPM (COPR `pingou/ankaios`) in an aib manifest, with workloads in root and in QM; show Ankaios restart vs systemd restart.
2. A "guardian observer in QM" demo: Guardian observer/UI container in QM (decider on the ASIL side, see [[freedom-from-interference-has-three-axes]]), root-side BlueChi watchdog, SELinux AVC log forwarded to the guardian.
3. Kuksa Databroker + uProtocol/Zenoh quadlet images packaged as an `eclipse-autosd` derived bootc image (service-to-signal blueprint currently only has docker compose: gap).
4. Add an `rpi5` target or document the gap upstream (check aib issues first; unverified whether in progress).
5. Pre-baked "hackathon image" with podman cache, ssh keys, kuksa/ankaios containers embedded to avoid registry waits.
