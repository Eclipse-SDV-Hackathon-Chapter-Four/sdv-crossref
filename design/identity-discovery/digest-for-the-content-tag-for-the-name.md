---
title: Digest for the content, tag for the name — and never one id for both
type: pattern
cluster: identity-discovery
component: none
tags: [identity, content-addressing, git, oci, nix, vss, static-id, uuid, rename, fka]
status: draft
sources:
  - https://git-scm.com/book/en/v2/Git-Internals-Git-Objects (blobs named by SHA-1 of content; filenames live in trees)
  - https://github.com/opencontainers/image-spec/blob/main/descriptor.md (digest = content identifier; tags are mutable references)
  - https://nix.dev/manual/nix/2.28/store/store-path.html (store path = digest + name)
  - https://www.rfc-editor.org/rfc/rfc9562 (UUIDv5 name-based vs v4 random / v7 time-ordered)
  - repos/vss-tools/docs/id.md (`vspec export id`: hash over qualified name, datatype, type, unit, allowed, min, max; `fka`; const UID)
  - repos/iceoryx2/iceoryx2/src/service/service_hash.rs (ServiceHash = hash(pattern + name))
last-verified: 2026-10-03
related:
  - "[[derive-ids-from-layout-not-from-prose]]"
  - "[[additive-only-then-remint-identity]]"
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[claim-the-address-keep-the-name]]"
  - "[[vss-kuksa-reference]]"
  - "[[iceoryx2-reference]]"
applies-to: [vss-kuksa, iceoryx2, uprotocol, symphony, ankaios]
gap-rows: [B10, B1, H5]
---

# Digest for the content, tag for the name — and never one id for both

**Problem.** A VSS signal is renamed from `IsOccupied` to `OccupancyStatus`, or a service path gets a clearer name. If the id is derived from the path, every archive, mapping and consumer is orphaned by a cosmetic change. If the id is allocated, two independent builds cannot agree on it without a registry.

**Forces.**
- Derived ids need no registry: any party recomputes them from the model.
- Renames are frequent and usually meaning-preserving; unit or layout changes are rare and meaning-changing.
- Archives and safety consumers key on ids for years.
- Collisions in short hashes are real (VSS uses 32 bits).

**The rule.** Keep **two identities with two derivations**: a **content id** (digest over what the bytes mean: layout, datatype, unit, enum table) and a **name** (a human path) bound to it by a mutable pointer. A rename moves the pointer; a meaning change mints a new content id. Git is the model: a blob's id is the SHA-1 of its content only, the filename lives in the tree, so `git mv` keeps every blob id and changes only the tree. OCI does the same with immutable `sha256:` digests and mutable tags. Allocated ids (UUIDv4/v7, registry numbers, broker-assigned integers) are right only for *instances* nobody can derive (a vehicle, a session), never for types. When an id must hash the name (because the name is the only shared input), give it an explicit alias list so renames stay one identity.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Git object model | content → blob id; names in trees; rename keeps content ids | rename is cheap and provable |
| OCI image spec | descriptor `digest` is the content identifier; tags are mutable names | pull by digest for trust, by tag for convenience |
| Nix store paths | `/nix/store/<digest>-<name>`; digest over inputs (or content for CA derivations) | build identity derived, name only decorative |
| VSS `vspec export id` | 32-bit hash over qualified name + datatype + type + unit + allowed + min/max; `fka` keeps the old hash on rename | derived signal ids, with an escape hatch |
| RFC 9562 UUIDs | v5 = hash(namespace, name); v4 random; v7 time-ordered | derived vs allocated, in one standard |

**On the Eclipse SDV stack.**
- VSS: its static UID mixes name and meaning in one hash, so every rename is a "BREAKING CHANGE" unless the overlay carries `fka: ['A.B.OldName']` — make `fka` mandatory in any rename PR, and feed the same hash (gap B10) into iceoryx2 attributes ([[vss-kuksa-reference]]).
- KUKSA: databroker numeric ids are *allocated per loaded tree* (e.g. `vss_id 184`) — fine as session aliases, wrong as archive keys; key archives by VSS static UID ([[vss-kuksa-reference]]).
- iceoryx2: `ServiceHash` = hash(messaging pattern + service name), so renaming a service *is* a new service. Put a stable `type.hash` attribute on it and let consumers match on the attribute, so a rename needs only a config change ([[iceoryx2-reference]]).
- Update manifests (Symphony, Ankaios, gap H5): reference images by digest, display by tag.

**The trap.** Using a path-derived hash as a type id and then "fixing" a typo in the path, which silently re-mints the id and orphans every recorded trace.

**For a hackathon team.** Rename one VSS leaf in an overlay with and without `fka`, run `vspec export id --validate-static-uid` against the previous output, and show the id preserved only with `fka`. Pitch: "names move, meanings mint".

**Evidence.** vss-tools `docs/id.md`: BREAKING vs NON-BREAKING table ("Qualified name" breaking; "Qualified name (fka)" non-breaking), collision probability 0.0197 % for ~1300 signals at 2^32, const UID override. Git book §10.2 ("Git is a content-addressable filesystem"). OCI descriptor.md §Digests ("acts as a content identifier"). Nix manual "Store Path" (20-byte digest). iceoryx2 `service_hash.rs` L45–52. KUKSA allocated ids: [[vss-kuksa-reference]] pitfalls 9.
