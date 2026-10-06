---
title: Encrypt once, wrap per device
type: pattern
cluster: update-ota
component: none
tags: [encryption, cose, ecdh-es, aes-kw, cek, content-addressed, cdn, zstd, streaming, suit, rauc]
status: draft
sources:
  - https://datatracker.ietf.org/doc/html/draft-ietf-suit-firmware-encryption (-26; §5.1.2, §5.2.2, §6.2.1, §8)
  - https://www.rfc-editor.org/rfc/rfc9052 (COSE structures, COSE_Encrypt with recipients)
  - https://rauc.readthedocs.io/en/latest/advanced.html (crypt bundles, `rauc encrypt --to`, HTTP streaming)
  - https://www.rfc-editor.org/rfc/rfc8878 (Zstandard)
  - https://eprint.iacr.org/2015/189 (Hoang et al., online AEAD; STREAM construction)
last-verified: 2026-10-03
related:
  - "[[release-is-the-hash-of-its-parts]]"
  - "[[the-manifest-programs-the-device]]"
  - "[[one-key-scheme-from-mcu-to-cloud]]"
applies-to: [symphony, opensovd, autosd, ankaios, zenoh]
gap-rows: [H5]
---

# Encrypt once, wrap per device

**Problem.** Firmware must be confidential (supplier IP, attack surface), but encrypting a 2 GB image separately for each of a million vehicles costs a million encryptions, defeats every CDN cache, and forces the backend to hold plaintext online. Encrypting it once under one fleet-wide key means one extracted ECU decrypts every future release.

**Forces.**
- Payloads are large and identical across a device class; keys are small and per device.
- Caches and peer distribution work only on identical bytes.
- Constrained targets cannot buffer a whole image before decrypting or verifying it.
- Ciphertext does not compress; bandwidth is paid per byte.

**The rule.** Compress (zstd), then encrypt the payload **once** under a fresh random content-encryption key (CEK) per release, and address the ciphertext by its digest. Per device, deliver only a **recipient** block: the CEK wrapped to that device's key, by ECDH-ES with an ephemeral key plus AES key wrap (or AES-KW with a pre-shared KEK). Integrity comes from the signed manifest over the ciphertext and plaintext digests, not from the encryption. Use a segmented mode (AES-CTR per sector, or a chunked AEAD) so the device decrypts and verifies while streaming into the inactive bank.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| draft-ietf-suit-firmware-encryption-26 | COSE_Encrypt payloads; AES-KW or ES-DH (ECDH-ES + AES-KW + HKDF); "multiple COSE_recipient structures are included but only a single CEK is used"; §8 sector-by-sector decryption into A/B slots, AES-CTR per block | the exact construction for constrained devices |
| RFC 9052 COSE | COSE_Encrypt with a recipients array | standard container for one ciphertext, many key wraps |
| RAUC crypt bundles | AES-256 payload key in the manifest, manifest CMS-encrypted to a set of recipient certificates (`rauc encrypt --to`); install by HTTP streaming over NBD without local storage | the same split, shipped for embedded Linux |
| RFC 8878 Zstandard | fast, streaming compression with dictionaries | compression must happen before encryption |
| Hoang, Reyhanitabar, Rogaway, Vizár (2015) | online AEAD over segments (STREAM) | authenticated streaming decrypt without whole-file buffering |

**On the Eclipse SDV stack.** No Eclipse SDV component encrypts or wraps update payloads ([[gap-register]] H5). The ciphertext is just a blob: an OCI layer for AutoSD/bootc or Ankaios workloads, a `bulk-data` file for the CDA, an object behind Symphony's artifact store ([[autosd-overview]], [[opensovd-reference]], [[symphony-overview]]). The per-device recipient block travels with the director's targeting (it is per vehicle, like the director metadata in [[two-keys-who-may-run-what-may-install]]). The device key should be the same identity anchor used for everything else ([[one-key-scheme-from-mcu-to-cloud]]); for an MCU behind the HPC, either the HPC decrypts (the HPC is then in the confidentiality boundary) or the MCU holds its own key and the HPC forwards ciphertext ([[the-hpc-is-the-mcus-update-gateway]]).

**The trap.** Per-device encryption of the whole payload (no caching, plaintext online) or one fleet-wide symmetric key (one extraction leaks everything).

**For a hackathon team.** `zstd | encrypt with random CEK` once; for three simulated vehicles with X25519 keys, emit three 100-byte recipient blocks; show one ciphertext digest served to all three and a fourth vehicle failing to decrypt. Pitch: "the fleet downloads one file; each car gets its own 100-byte key".

**Evidence.** SUIT encryption quotes from the -26 draft (fetched 2026-10-03); the draft does not discuss compression ordering, so "compress first" rests on general cryptographic practice. RAUC: advanced.html (fetched). STREAM attribution to the 2015 paper is from its full text, not verified in this fetch. The security note that one CEK per release exposes that release's plaintext if any recipient leaks is inferred from the draft's single-CEK design.
