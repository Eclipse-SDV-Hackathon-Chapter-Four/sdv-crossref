---
title: AutoSD — Quickstart
type: quickstart
component: autosd
tags: [autosd, centos-automotive-sig, rhivos, aib, bootc, quadlet, qm]
status: verified
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

# AutoSD — Quickstart (boot a QEMU image in under 15 minutes)

**Status: NOT executed on 2026-10-03** (building requires root/privileged podman and ~10+ min; conventions forbid sudo). Recipes below come from the official quickstart and repo READMEs; verifier should run them.

## Prerequisites
- Linux x86_64 host with `podman` (or docker), `git`, `qemu-system-x86` (+ `/dev/kvm` for speed; present on this machine), ~15 GB free, internet to CentOS/COPR registries. Aarch64 image needs an aarch64 host (no cross build).
- Fedora/RHEL: `sudo dnf install -y git podman qemu-system-x86-core`; Ubuntu: `sudo apt install -y git podman qemu-system-x86` ([quickstart](https://sigs.centos.org/automotive/autosd-10/getting-started/quick-start-guide.html)).

## Path A (fastest, no build): prebuilt bootc image from Eclipse AutoSD
1. Pre-built qcow2 disks are attached to releases of https://github.com/eclipse-autosd/eclipse-autosd (README: "pre-built image qcow2 ... under releases"; release tag `dev`; assets verified 2026-10-03 via the GitHub releases API: `eclipse-autosd-bootc-qemu-x86_64.qcow2.xz` 424103948 B, `eclipse-autosd-bootc-qemu-aarch64.qcow2.xz` 389869392 B, `eclipse-autosd-bootc-ebbr-aarch64.img.xz` 389790064 B, `eclipse-autosd-bootc-rpi4-aarch64.img.xz` 395078744 B; URL pattern `https://github.com/eclipse-autosd/eclipse-autosd/releases/download/dev/<asset>`; corrected 2026-10-03).
2. Get the runner and boot:
```
curl -o air 'https://gitlab.com/CentOS/automotive/src/automotive-image-builder/-/raw/main/bin/air'
chmod +x air
./air --nographics disk.qcow2        # login root / password; Ctrl-a x exits QEMU
```
(The eclipse-autosd README links `bin/aib?ref_type=heads` for `air`; that looks like a typo, `bin/air` is the file in the repo.)
3. Optional: `bootc switch ghcr.io/eclipse-autosd/eclipse-autosd-bootc-qemu:latest --apply`.
Also nightly sample images: https://autosd.sig.centos.org/AutoSD-10/nightly/sample-images/ (rpi4 images there; qcow2 naming not checked, use the `dev` release assets above for x86_64).

## Path B: build the developer image (~10 min per the guide)
```
mkdir -p ~/autosd-quickstart && cd ~/autosd-quickstart
git clone https://gitlab.com/CentOS/automotive/sample-images.git
curl -o auto-image-builder.sh https://gitlab.com/CentOS/automotive/src/automotive-image-builder/-/raw/main/auto-image-builder.sh
chmod +x auto-image-builder.sh
./auto-image-builder.sh -d build --target qemu sample-images/images/developer.aib.yml my-first-autosd.qcow2
./air --nographics my-first-autosd.qcow2
```
Notes: the wrapper pulls `quay.io/centos-sig-automotive/automotive-image-builder:latest` and runs it privileged in podman; with rootless podman it may fail, then use `sudo ./auto-image-builder.sh ...` then `sudo chown $USER *.qcow2` (as in the S-CORE LoLa demo README). Add `--build-dir some/dir` to cache RPMs between runs. Native alternative: `dnf copr enable @centos-automotive-sig/automotive-image-builder @centos-automotive-sig/osbuild-auto; dnf install automotive-image-builder osbuild-auto; aib build --target qemu manifest.aib.yml localhost/x:latest x.qcow2` (Fedora/CentOS hosts).

## Expected output
Serial console boots to `login:`; `root`/`password`; `cat /etc/os-release` shows an AutoSD/CentOS Stream 10 identity; `podman images`, `systemctl status`. (Expected, not observed.)

## Try the sample workloads
`sample-images/images/container.aib.yml` (containers radio/engine as quadlets with vsomeip) and `qm-container.aib.yml` (same inside QM). See [[autosd-howto]].

## Observed on 2026-10-03
Only static checks: `/dev/kvm` exists; docker is running (not used); repos cloned (`repos/automotive-image-builder` e6f42f9c, `repos/sample-images` d6c1efef, `repos/eclipse-autosd` dd8e007c). No build run.

## Observed on 2026-10-03 (verifier)
Asset: https://github.com/eclipse-autosd/eclipse-autosd/releases/download/dev/eclipse-autosd-bootc-qemu-x86_64.qcow2.xz, 424103948 B (matches the API size), xz sha256 `ebf8c0316a573d3aaba6730043aeb800d4bf550aa06f5ce2dd8220277b933cfa`; decompressed qcow2 3.5 GB on disk, 8 GiB virtual, sha256 `bd0e3b9118926e3fe259c1a2b271f9c8d4889e947805e12ee4877c7ce9deafc8`. `air` from the gitlab `bin/air` URL above (needs `--ovmf-dir <dir>` with OVMF_CODE.fd/OVMF_VARS.fd on hosts where it cannot find EFI firmware: first run failed with "Unable to find EFI firmware").
Command (air starts one vCPU per host core, here 32; a copy with `num_cpus = 4` was used to cap it): `./air4 --nographics --snapshot --memory 4G --ovmf-dir ovmf autosd.qcow2` (QEMU `-smp 4 -enable-kvm -m 4G -machine q35`). Driven with pexpect (system python3 has it; the .venv does not).
- Login prompt `esdv-main-compute login:` reached about 6 s after launch (KVM, idle host); kernel `6.12.0-270.el10iv.x86_64`; boot chain UEFI, ukiboot 0.2.1, UKI slot ukiboot_a. Login `root` / `password` worked (documented above). Console starts with the `BdsDxe: loading Boot0002` lines, then `Starting ukiboot version 0.2.1`, the `Error: Driver 'pcspkr' is already registered` and `kvm: RT requires X86_FEATURE_CONSTANT_TSC` kernel lines (harmless), then the "Automotive Stream Distribution 10" banner.
- `/etc/os-release`: NAME="Automotive Stream Distribution" VERSION="10" ID=autosd, CPE `cpe:/o:centos:autosd:10`. `podman version 6.1.0`.
- QM present: `/etc/qm /usr/lib/qm /var/qm` exist; `qm.service` active (running), generated from `/usr/share/containers/systemd/qm.container`.
- `lsblk`: vda 8G; vda1 100M ESP, vda2/vda3 128M (UKI slots), vda4 1M, vda5 7.7G for `/`, `/var`, `/boot`; root is composefs (read-only, 100% full is normal).
- `bootc status` works: image `localhost/aib-11389c15a61494b2be650f8b`, transport registry (so `bootc switch` in step 3 needs network; not run).
- Guest `free -m`: 3910 MB total, 226 MB used, 3683 MB available after boot. QEMU RSS 904276 kB (about 0.9 GB) at the login prompt.
- `poweroff` in the guest shut it down cleanly ("reboot: Power down", about 46 s guest uptime incl. my commands); `pgrep -a qemu` afterwards: none.
- Resources: the image needs about 2 GB of guest RAM (air default; 4 GB used here, 0.9 GB host RSS at idle) and about 3.5 GB of disk for the qcow2 (plus 0.4 GB for the .xz, 8 GiB virtual). Do not put the image in `/tmp` when `/tmp` is a tmpfs (RAM-backed here): 3.5 GB would sit in memory, a trap for the image file; use a disk path. Use `--snapshot` to keep the image pristine.
