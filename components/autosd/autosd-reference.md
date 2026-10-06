---
title: AutoSD — Reference
type: reference
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

# AutoSD — Reference

## Repos looked at (shallow clones, 2026-10-03)
| Repo | Path | Commit | Notes |
|---|---|---|---|
| automotive-image-builder | repos/automotive-image-builder | e6f42f9cabc6bd816dc332d1b6454b1fd1357691 (2026-09-29) | aib, air, targets/, distro/, files/manifest_schema.yml |
| sample-images | repos/sample-images | d6c1efef108ec912929daf15b5e5fc86a880f64a (2026-05-06) | images/{minimal,developer,container,qm,qm-container,static-ip}.aib.yml, files/*.container |
| eclipse-autosd | repos/eclipse-autosd | dd8e007c5e9d843a57237d45e9e77cb43149ab14 (2026-10-02) | bootc base for SDV, bluechi, examples/{docker,bazel} |
| eclipse-score inc_os_autosd | repos/inc_os_autosd | 16235221ac4248c2c11bfa5141dbfa22733f7a96 (2026-09-28) | Bazel `rules_aib`, toolchain |
| (old) autosd-image-eclipse-sdv | repos/eclipse-sdv-autosd | 40b7a434 (2025-12-05) | inactive, moved to eclipse-autosd |
| S-CORE reference integration | repos/hackfest-eclipse-score_reference_integration | 5ab03a01 (2026-05-19) | images/autosd_x86_64 |

## Links
- Docs: https://sigs.centos.org/automotive/ (redirects to /latest/), https://docs.centos.org/automotive-sig-documentation/
- aib manifest docs: https://centos.gitlab.io/automotive/src/automotive-image-builder/simple_manifest.html ; schema `files/manifest_schema.yml`
- Quickstart: https://sigs.centos.org/automotive/autosd-10/getting-started/quick-start-guide.html
- RPi4: https://sig.centos.org/automotive/latest/building/autosd_pi4.html ; nightlies https://autosd.sig.centos.org/AutoSD-10/nightly/
- Eclipse project: https://projects.eclipse.org/projects/automotive.autosd ; https://github.com/eclipse-autosd/eclipse-autosd
- QM: https://github.com/containers/qm ; bootc: https://bootc.dev/ ; quadlet: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- Containers: `quay.io/centos-sig-automotive/automotive-image-builder:latest`; `ghcr.io/eclipse-autosd/eclipse-autosd-bootc-{qemu,rpi4}:latest`
- Community: Slack `#automotive-image-builder` (aib README); CentOS Connect 2026 AutoSD meetup (search result).

## aib CLI cheat sheet
`aib build [--target T] [--arch A] [--distro D] [--build-dir DIR] [--define K=V] [--define-file F] [--extend-define K=V] [--policy P] [--reproducible] [--export qcow2] MANIFEST CONTAINER_REF [DISK]`; `aib to-disk-image CONTAINER_REF OUT`; `aib list-targets`; `aib list-dist`; `air [--nographics] [--aboot] disk.qcow2`.
Useful variables: `extra_rpms`, `image_size`, `use_transient_etc`, `use_debug`.

## Manifest top-level keys (seen)
`name`, `content` {`rpms`, `repos`, `enable_repos` (e.g. `devel`, `debug`), `container_images` {source, tag, name}, `add_files` {path, source_path|text}, `make_dirs`, `systemd.enabled_services`}, `qm` {`content`, `memory_limit`}, `image` {`hostname`, `sealed`, `selinux_mode`, `selinux_booleans`, `partitions`}, `auth` {`root_password`, `sshd_config`, `users`, `groups`}, `kernel`.

## Targets (repos/automotive-image-builder/targets)
qemu, abootqemu, abootqemukvm, pc, ebbr, rpi4, am62sk, am69sk, beagleplay, j784s4evm, tda4vm_sk, ride4_sa8775p_sx(+_r3), ride4_sa8650p_sx_r3, imx8qxp_mek, ccimx93dvk, aws, azure.
