---
title: Eclipse S-CORE integration notes
type: reference
component: s-core
tags: [s-core, integration, iceoryx2, opensovd, autosd, opendut, openbsw]
status: draft
sources:
  - repos/s-core-orchestrator/src/orchestration/src/events/iceoryx/event.rs
  - repos/s-core-reference_integration/README.md
  - repos/s-core-reference_integration/images
  - repos/s-core-score/docs/features/diagnostics/index.rst
  - https://github.com/eclipse-score/feo/blob/main/examples/rust/mini-adas/README.md
  - https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
  - https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/
  - https://github.com/eclipse-opensovd/opensovd/discussions/103
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/hackfest-docs/blob/main/2026-04-Hackfest-Welcome.pptx.pdf
last-verified: 2026-10-03
related:
  - "[[s-core-overview]]"
  - "[[iceoryx2-overview]]"
  - "[[opensovd-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[opendut-overview]]"
  - "[[autosd-overview]]"
  - "[[openbsw-overview]]"
  - "[[zenoh-overview]]"
  - "[[hackfest-esslingen-2026]]"
---

# Eclipse S-CORE integration notes

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| iceoryx2 ([[iceoryx2-overview]]) | yes, partially | Rust library. Orchestrator cross-process events use iceoryx2 Event services; FEO has a `com_iox2` backend; patched `iceoryx2_qnx8` crate for QNX. The core IPC (LoLa/mw::com) does **not** use iceoryx2. | demo (examples run; orchestrator itself was removed from the platform in v0.9) | repos/s-core-orchestrator/src/orchestration/src/events/iceoryx/event.rs; repos/s-core-orchestrator/Cargo.toml; feo mini-adas README; observed run 2026-10-03 ([[s-core-quickstart]]) |
| OpenSOVD ([[opensovd-overview]]) | yes | S-CORE diagnostics feature is SOVD-based (SOVD server/gateway, fault manager, HTTP). OpenSOVD is pulled into `inc_diagnostics` as a Bazel proxy module; IPC is "http-ipc" for now. Open question: Tokio vs Kyron runtime. | prototype / demo (HackFest: S-CORE + OpenSOVD on EB corbos on a Raspberry Pi; 1:10 RC car made diagnosable) | repos/s-core-score/docs/features/diagnostics/index.rst; https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and; https://github.com/eclipse-opensovd/opensovd/discussions/103 |
| VSS / KUKSA ([[vss-kuksa-overview]]) | none found | Would need a LoLa/mw::com <-> kuksa.val gRPC bridge | none | no hits in score docs or ref-int; web search 2026-10-03 found nothing |
| uProtocol ([[uprotocol-overview]]) | none found | Possible uTransport over LoLa or iceoryx2 | none | no hits; web search 2026-10-03 |
| Ankaios ([[ankaios-overview]]) | none found | Could run the `score_showcases` OCI image as an Ankaios workload; overlaps with the Launch Manager | none | no hits; web search 2026-10-03 |
| openDuT ([[opendut-overview]]) | loosely | At HackFest, openDuT EDGAR was installed natively on an S-CORE image and the image was connected to the internet. Issues: NetBird sessions, CAN, kernel modules. | prototype (HackFest) | https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/ |
| AutoSD ([[autosd-overview]]) | yes | Build target `--config=autosd-x86_64`; image `//images/autosd:run` (Docker); AutoSD 10 toolchain from score_toolchains_gcc; repo eclipse-score/os_autosd | demo (CI image in ref-int) | repos/s-core-reference_integration/.bazelrc, images/autosd, release_note_score_v0_9.rst |
| OpenBSW ([[openbsw-overview]]) | indirect | In the HackFest target architecture, the S-CORE node hosts OpenSOVD CDA, which talks UDS (DoIP) to an OpenBSW UDS server. There is no S-CORE code in OpenBSW. | prototype (HackFest architecture) | https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/hackfest-docs/blob/main/2026-04-Hackfest-Welcome.pptx.pdf |
| Zenoh ([[zenoh-overview]]) | none found | Not referenced; SOME/IP is the planned inter-ECU path (inc_someip_gateway) | none | repos/s-core-communication/README.md ("Inter-ECU communication via SOME/IP ... under architectural planning") |
| QNX 8.0 | yes | qcc toolchain, IFS images x86_64 and aarch64, QEMU runner, Raspberry Pi 4/5 | demo (requires a QNX licence) | repos/s-core-reference_integration/README.md |
| EB corbos Linux for Safety Applications | yes | `--config=eb-aarch64`; pre-built fast-dev image in QEMU; high-integrity app constraints | demo | repos/s-core-reference_integration/images/ebclfsa_aarch64/README.md |
| AUTOSAR Adaptive (ara::com) | concept | design goal: ara::com-style API (LoLa); ASIL-B target; no AUTOSAR integration exists | idea | repos/s-core-communication/README.md |
| Symphony, Muto, Velocitas, Kanto, ThreadX, SDV Blueprints, Chapter4 challenges | none found | | none | no references in the cloned repos |

## Notes
- "Uses iceoryx2" is a common misconception. In S-CORE the **production IPC is LoLa**. iceoryx2 appears in the orchestrator (events only) and as one FEO backend. If you want zero-copy pub/sub with minimal setup, use iceoryx2 directly, see [[iceoryx2-overview]].
- The most mature cross-project story is **S-CORE + OpenSOVD (+ EB corbos / RPi)**, started at [[hackfest-esslingen-2026]]. It is a good basis for [[chapter4-challenge-doctor-whodunit]]-style diagnostics work.
