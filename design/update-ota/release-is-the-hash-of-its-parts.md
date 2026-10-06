---
title: A release is the hash of its parts; the version is a label
type: pattern
cluster: update-ota
component: none
tags: [content-addressing, release, digest, oci, ostree, channel, deduplication, reproducibility]
status: draft
sources:
  - https://github.com/opencontainers/image-spec/blob/main/image-index.md (OCI image index, per-platform manifests)
  - https://github.com/opencontainers/image-spec/blob/main/descriptor.md (digests)
  - https://ostreedev.github.io/ostree/introduction/ (content-addressed object store, commits)
  - https://nixos.org/manual/nix/stable/store/store-path.html (store paths from hashes)
  - https://theupdateframework.github.io/specification/latest/ (targets: length and hashes)
  - https://uptane.org/docs/latest/standard/uptane-standard (hardware identifier per ECU)
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[the-manifest-says-which-bytes-the-target-says-where]]"
  - "[[encrypt-once-wrap-per-device]]"
applies-to: [ankaios, symphony, autosd, opensovd]
gap-rows: [H5, H3, C6]
---

# A release is the hash of its parts; the version is a label

**Problem.** Two vehicles both report "1.4.2" and behave differently, because one got a rebuild, a re-tagged container or a hotfixed calibration under the same version. Diagnostics, homologation (RXSWIN) and rollback all assume the version names the bytes; it does not.

**Forces.**
- Humans need short, ordered names; machines need identity that cannot drift.
- One release spans several device classes and CPU architectures.
- The same component image appears in many releases and should be stored once.
- Mutable tags (`latest`, `v1`) are convenient and silently re-pointable.

**The rule.** A component artifact is identified by the digest of its bytes. A **release** is a manifest listing `(component, device class, arch) → digest`, sorted and canonicalised, and its identity is the digest of that manifest. The **version** is a label that points to one release digest and can never be re-pointed; a **channel** (stable, beta, canary) is a mutable pointer to a release, resolved on the device side by its own `(device class, arch)`. Rebuild 1.4.2 and you get a new release digest, so "same version, different bytes" becomes impossible to express. Deduplication is free: identical digests are stored and transferred once.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| OCI image spec | descriptors carry `digest`; an image index maps platforms (os, architecture, variant) to manifest digests; pull by `@sha256:` | multi-arch resolution and immutable references |
| OSTree | content-addressed objects; a commit checksums its tree; refs are mutable names | channel = ref, release = commit, dedup across deployments |
| Nix store | store path derived from a hash of inputs or content | identity by content, labels optional |
| TUF / Uptane targets | every target listed with length and hashes; Uptane adds the hardware identifier per ECU | the signed release already names bytes per device class |
| Git | commit id over tree and parents; tags are labels | the everyday version of the rule |

**On the Eclipse SDV stack.** Ankaios `runtimeConfig` accepts `image: repo@sha256:...`; use it, never a tag ([[ankaios-overview]]). Chapter 3's MegaBosses rollback redeployed `image: docker.io/library/nginx` by tag (`repos/hc3-MegaBosses/activations/campaign_activation_reverse.json`, [[chapter3-retrospective]]): the "previous version" was whatever the tag pointed to that day. A Symphony Solution should carry component digests; bootc images are already OCI-addressed ([[autosd-overview]]). Report the release digest (and per-component digests) through SOVD `data` identData or `version-info`-adjacent resources so a tester sees bytes, not labels ([[opensovd-reference]]). Keep instance identity out of it, as in [[instance-in-the-name-type-in-the-hash]]: the VIN never enters the release digest.

**The trap.** Treating the version string (or a container tag) as the identity of what is installed.

**For a hackathon team.** A script that builds `release.json` from `podman inspect --format '{{.Digest}}'` for each workload, hashes it, writes the Ankaios manifest with `@sha256:` references, and a dashboard showing release digest per vehicle; then rebuild one image under the same tag and show the digest change. Pitch: "our versions cannot lie".

**Evidence.** OCI image-index and descriptor docs, OSTree introduction, Nix store-path manual, TUF spec targets (URLs resolved 2026-10-03; contents standard). Uptane hardware identifier: Uptane Standard 2.1.0. MegaBosses tag usage: repo file above. Ankaios digest references are standard Podman behaviour (not tested here).
