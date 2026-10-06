---
title: The HPC is the MCU's update gateway, not its trust anchor
type: pattern
cluster: update-ota
component: none
tags: [mcu, uds, flashing, 0x34, 0x36, 0x37, cda, openbsw, threadx, suit, mcuboot, gateway, uptane-secondary]
status: draft
sources:
  - https://uptane.org/docs/latest/standard/uptane-standard (full vs partial verification of Secondaries)
  - https://docs.mcuboot.com/design.html (signed images, swap/test, security counter)
  - https://github.com/RIOT-OS/RIOT/tree/master/sys/suit (SUIT on microcontrollers)
  - https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/releases_and_maturity/migration/migration_3.1_54h_suit_ironside.html (Nordic SUIT → IronSide SE)
  - "[[opensovd-reference]] (CDA `x-sovd2uds-download/{requestdownload,flashtransfer,transferexit}` → UDS 0x34/0x36/0x37)"
  - "[[openbsw-reference]] (UDS services present)"
last-verified: 2026-10-03
related:
  - "[[two-keys-who-may-run-what-may-install]]"
  - "[[never-mix-banked-and-singleshot]]"
  - "[[the-manifest-programs-the-device]]"
  - "[[versions-ratchet-even-when-the-clock-lies]]"
applies-to: [opensovd, openbsw, threadx, symphony, ankaios]
gap-rows: [D5, H5, H6, E2]
---

# The HPC is the MCU's update gateway, not its trust anchor

**Problem.** MCUs sit behind the HPC on CAN or local Ethernet and cannot reach the backend. The easy design lets the HPC check the signature and then push raw bytes over UDS; a compromised HPC then owns every MCU, and an MCU that cannot roll back is bricked by the first bad image.

**Forces.**
- MCUs have little flash, no TLS, often no clock and sometimes one bank.
- UDS flashing (session, security access, download, transfer, exit, reset) is the workshop standard and must keep working.
- The HPC has the bandwidth, storage and network; the MCU has the safety role.
- Some MCU vendors are moving between manifest formats.

**The rule.** The HPC is the **gateway**: it fetches, does full verification (both keys, all metadata), buffers, schedules, supplies signed time, and drives the transfer. The MCU is still the **verifier** of what it installs: its bootloader checks the author's signature, digest, hardware id and security version on the received image (Uptane partial verification at minimum), so the HPC's word is never enough. The transport is plain UDS: 0x10 02 programming session, 0x27 security access, 0x34 RequestDownload, 0x36 TransferData, 0x37 RequestTransferExit, routine checks via 0x31, 0x11 reset. The signed envelope (SUIT or an MCUboot image with TLVs) is the payload; the MCU's own classification (dual-bank with test/confirm, or singleshot) goes into the plan ([[never-mix-banked-and-singleshot]]).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Uptane Primary / Secondary | Primary must do full verification; Secondaries should, and at minimum do partial verification of Director targets plus time | the gateway relays; the ECU still decides |
| ISO 14229 UDS 0x34/0x36/0x37 | download request, block transfer, exit | the existing flashing transport any tester speaks |
| MCUboot | signed image with TLVs, swap-with-revert test images, `image_ok`, hardware security counter | an MCU-side verifier and A/B on dual-bank flash |
| RIOT OS SUIT | manifest processor and fetch on microcontrollers | SUIT is feasible on an MCU |
| Nordic nRF Connect SDK | nRF54H20 used SUIT envelopes in v3.0 and moved to MCUboot + IronSide SE in v3.1 | vendor formats change; keep the manifest at the gateway portable |

**On the Eclipse SDV stack.** The CDA already exposes the transport: `PUT .../x-sovd2uds-download/requestdownload`, `POST .../flashtransfer`, `PUT .../transferexit` map to 0x34/0x36/0x37 (`repos/opensovd-cda/cda-sovd/src/sovd/components/ecu/x_sovd2uds_download.rs`, [[opensovd-reference]]). OpenBSW upstream has a programming session with a bootloader-handover hook (`PLATFORM_SUPPORT_PROGRAMMING_SESSION` in the reference app's `DiagSession.cpp`) and constants for 0x34/0x36, but no download/transfer service implementations and no bootloader ([[openbsw-reference]]), so an OpenBSW MCU needs a bootloader leg before it can be flashed. ThreadX boards in Chapter 3 were flashed with OpenOCD from a privileged container, not over UDS ([[threadx-overview]], [[chapter3-retrospective]]). The HPC agent driving the CDA is the "Symphony target for an MCU" of [[gap-register]] D5.

**The trap.** Verifying on the HPC and sending the MCU unsigned bytes, which turns one HPC compromise into a fleet of compromised MCUs.

**For a hackathon team.** OpenBSW POSIX ECU plus the CDA: add a minimal 0x34/0x36/0x37 handler that writes to a file "bank", verifies an Ed25519 signature and digest on 0x37, and refuses on mismatch; drive it through `x-sovd2uds-download` from an HPC script. Pitch: "the gateway carries the update; the ECU decides".

**Evidence.** CDA routes: `cda-sovd/src/sovd.rs` lines ~1006–1041 and the module above. OpenBSW: `libs/bsw/uds/include/uds/services/` lists no download/transfer service; `UdsConstants.h` defines `REQUEST_DOWNLOAD = 0x34U`, `TRANSFER_DATA = 0x36U`; `executables/referenceApp/udsConfiguration/src/uds/session/DiagSession.cpp` has the programming-session handover. Uptane verification levels: Standard 2.1.0. Nordic migration: guide title only (body not read, unverified). UDS service ids are ISO 14229-1 (paywalled; standard knowledge).
