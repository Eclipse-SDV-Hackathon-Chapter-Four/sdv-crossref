---
title: AutoSD — How-to
type: howto
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

# AutoSD — How-to recipes

All recipes unexecuted on 2026-10-03 (see [[autosd-quickstart]]); sources are repo files cited inline.

## 1. Add a containerized workload via quadlet (root partition)
Quadlet files in `/etc/containers/systemd/` become systemd services (`foo.container` -> `foo.service`). Pattern from `repos/sample-images/images/container.aib.yml` and `files/radio.container`:
```yaml
name: my-workload
content:
  rpms: [curl]
  container_images:                       # embedded in the image, offline at boot
    - source: ghcr.io/eclipse-kuksa/kuksa-databroker
      tag: latest
      name: localhost/kuksa-databroker
  add_files:
    - path: /etc/containers/systemd/kuksa.container
      text: |
        [Unit]
        Description=KUKSA databroker
        [Container]
        Image=localhost/kuksa-databroker
        PublishPort=55555:55555
        [Service]
        Restart=always
        [Install]
        WantedBy=multi-user.target
auth:
  root_password: <crypt hash; sample uses hash of "password">
```
(Image name/ports for KUKSA are illustrative, unverified; the manifest keys `container_images`, `add_files` with `text:`/`source_path:` are verified in the repo's manifests.) Build: `./auto-image-builder.sh build --target qemu my-workload.aib.yml localhost/my:latest my.qcow2`. In the VM: `systemctl status kuksa`, `podman ps`. Quadlet generation is done by `files/quadlet_preprocess.sh` at build time too.

## 2. Same workload in the QM partition
Put content under `qm:` and the quadlet in the QM tree (`sample-images/images/qm-container.aib.yml`): `qm.content.container_images`, and `qm.content.add_files` with path `/etc/containers/systemd/radio.container`. Note the QM variant files drop `Requires=routingmanagerd.socket` (root-side socket) and share `/run/vsomeip` by volume. Give the QM partition room: `image.partitions.var_qm.relative_size: 0.04` as in `examples/qm.aib.yml`. Share IPC/sockets from root into QM by a drop-in `/etc/containers/systemd/qm.container.d/NN-x.conf` with `[Container] Volume=...` (pattern used for BlueChi and S-CORE LoLa in `repos/eclipse-autosd/files/` and the S-CORE reference image).

## 3. Iterate fast without reflashing (bootc)
Build a container with any OCI tool `FROM ghcr.io/eclipse-autosd/eclipse-autosd-bootc-qemu:latest` (see `repos/eclipse-autosd/examples/docker/Dockerfile`), push to a registry reachable from the VM, then in the VM: `bootc switch <image> --apply`. Target must match (qemu vs rpi4). Or build locally with `aib build --target qemu my.aib.yml localhost/my:latest` and `bootc update`.
Pitfall: aib images are **sealed by default** (`image.sealed: true`) and "can only boot the original, or re-sealed images, not e.g. layered bootc images" (manifest_schema.yml); `eclipse-autosd/aib/image.aib.yml` sets `sealed: false` for this reason.

## 4. Raspberry Pi 4
Download `auto-osbuild-rpi4-autosd10-developer-regular-aarch64-*.raw.xz` from https://autosd.sig.centos.org/AutoSD-10/nightly/sample-images/, update Pi EEPROM first, `unxz`, `sudo dd ... bs=4M; sync`, boot with Ethernet, login `root`/`guest` password `password`. WiFi and serial reported non-functional ([doc](https://sig.centos.org/automotive/latest/building/autosd_pi4.html)). Build yourself on an aarch64 host: `--target rpi4` (target pulls COPR `@centos-automotive-sig/rpi-board-support`, package `pi4-firmware-blob`: `repos/automotive-image-builder/targets/rpi4.ipp.yml`). **Raspberry Pi 5: no target (unverified whether community images exist).** Use rpi4 or the generic `ebbr` target for other boards.

## 5. Run AutoSD "in a container"
- As the **builder**: `auto-image-builder.sh` runs aib in `quay.io/centos-sig-automotive/automotive-image-builder` (needs privileges).
- As a **runtime for apps**: `podman run -it --rm ghcr.io/eclipse-autosd/eclipse-autosd-bootc-qemu:latest bash` gives the AutoSD userland for compile/test (the README says it is for "lightweight testing or local development"); systemd-in-container behaviour is unverified.

## 6. Deploy SDV projects
- **Ankaios**: install via RPM from COPR `pingou/ankaios` (spec seen in search results; Podman runtime required per [Ankaios docs](../../repos/ankaios/doc/docs/usage/installation.md): Podman >= 3.4.2, `podman-kube` >= 4.3.1) or via containers/quadlet; enable `ank-server`, `ank-agent` systemd units. Not shown end-to-end anywhere found: **unverified**. See [[ankaios-overview]].
- **KUKSA / Zenoh / uProtocol**: ship as containers via quadlet (recipe 1). Upstream service-to-signal blueprint only documents docker compose ([docs](https://sdv-blueprints.eclipse.dev/docs/service-to-signal)); Eclipse AutoSD proposal names it as first blueprint to support. See [[vss-kuksa-overview]], [[uprotocol-overview]], [[zenoh-overview]].
- **S-CORE**: LoLa/communication RPMs in COPR `pingou/score-playground`; image in `repos/hackfest-eclipse-score_reference_integration/images/autosd_x86_64/build/` (needs `selinux_mode: permissive`, shared `/dev/shm` volume into QM). Build with `sudo ./auto-image-builder.sh build --define-file vars.yml --define-file vars-devel.yml --target qemu --export qcow2 --distro autosd10 lola-demo.aib.yml out.qcow2`. See [[s-core-overview]].

## Pitfalls checklist
- **Root/privileges**: osbuild needs root or privileged podman; run `sudo`, then `chown` output.
- **Dependencies**: native aib needs the `osbuild-auto` COPR (osbuild extensions); easiest is the container wrapper. `aib` builds only the host arch.
- **Disk size**: prebuilt AutoSD disk is small; `qemu-img resize x.qcow2 30G` before in-VM builds (doc); builds themselves cache RPMs: use `--build-dir`.
- **Registry access**: `container_images` are pulled at *build* time; corporate proxies/ghcr/quay/registry.gitlab.com blocks stall builds; COPR repos (`download.copr.fedorainfracloud.org`) must be reachable. Pre-pull on hackathon Wi-Fi is a bad idea.
- **/etc is transient** by default in bootc images (`use_transient_etc`; set false for testing only, per aib README): edits to /etc vanish on reboot. Put config in the manifest or quadlet drop-ins.
- **SELinux denials**: enforcing by default; use `ausearch -m avc -ts recent`, `audit2allow`, or temporarily `image.selinux_mode: permissive` (what the S-CORE demo does). Containers need correct volume labels (`:z`/`:Z`), QM has extra labels.
- **x86 vs aarch64**: no cross-building; Apple Silicon users get aarch64 VMs (use `--arch`/qemu aarch64); container images must be multi-arch (eclipse-autosd publishes `-amd64`/`-arm64`).
- **EFI/EEPROM** for rpi4 (see recipe 4).
- Dev manifests set `root`/`password` and sshd root login: never reuse.
