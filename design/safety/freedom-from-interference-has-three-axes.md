---
title: Freedom from interference has three axes; a container covers one and a half
type: pattern
cluster: safety
component: none
tags: [ffi, mixed-criticality, qm, asil, partition, cgroups, hypervisor, e2e, black-channel]
status: draft
sources:
  - https://www.iso.org/standard/68388.html (ISO 26262-6:2018; Annex D freedom from interference: timing/execution, memory, exchange of information) (catalogue id unverified)
  - https://webstore.iec.ch/publication/62095 (IEC 61784-3:2021, black channel per IEC 61508)
  - https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_E2EProtocol.pdf
  - https://docs.kernel.org/admin-guide/cgroup-v2.html (cpu.max, memory.max)
  - https://sig.centos.org/automotive/latest/features-and-concepts/con_mixed-criticality.html (AutoSD QM partition)
  - https://elisa.tech/ (ELISA, Linux in safety applications)
  - repos/s-core-score/docs/safety/platform_safety_manual.rst; repos/s-core-score/docs/requirements/stakeholder/index.rst
last-verified: 2026-10-03
related:
  - "[[autosd-overview]]"
  - "[[ankaios-overview]]"
  - "[[s-core-overview]]"
  - "[[iceoryx2-overview]]"
  - "[[one-watchdog-per-layer-each-blind-to-the-others]]"
applies-to: [autosd, ankaios, s-core, iceoryx2, uprotocol]
gap-rows: [C4, A8, A10]
---

# Freedom from interference has three axes; a container covers one and a half

**Problem.** A QM dashboard and the safety Guardian share a Linux box. The dashboard leaks memory, saturates a core, or writes garbage into a shared-memory segment, and the Guardian misses its deadline or reads a corrupted temperature. "It's in a container" is not an argument.

**Forces.**
- Integration wants one SoC, one OS, shared memory for speed.
- ISO 26262 wants the lower-integrity element unable to cause a violation of the higher one's safety requirements.
- Linux is not developed to an ASIL; its isolation is good but not argued.
- A hypervisor or an MCU costs integration effort a hackathon does not have.

**The rule.** Argue FFI on three separate axes, each with its own mechanism and its own detection:
- **Spatial (memory):** separate address spaces (POSIX processes); shared memory read-only for the consumer; nothing QM linked into the ASIL process (S-CORE: "POSIX processes … provide isolation from memory and timing errors of other processes but not within").
- **Temporal (time):** budgets (cgroup `cpu.max`, RT priorities) *prevent*; supervision (deadline/alive watchdogs) *detects* what prevention missed.
- **Communication:** treat every channel, including shared memory and the kernel, as a **black channel**; end-to-end protection (CRC, counter, data id, timeout) at sender and receiver detects corruption, loss, repetition, delay, masquerade.
Containers give spatial isolation and resource *limits*; they give no timing guarantee and no message integrity. Where the argument needs a kernel you can qualify, the safety function goes below or beside Linux: hypervisor partition, safety island MCU, or certified RTOS.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 26262-6 Annex D | interference classes: timing and execution, memory, exchange of information | the three axes, from the standard |
| IEC 61508 / IEC 61784-3 black channel | safety layer above an untrusted transport | E2E without qualifying the network or the IPC |
| AUTOSAR E2E profiles | CRC + counter + data id + timeout state machine | the concrete communication-axis mechanism |
| S-CORE platform safety manual | no mixed ASIL in one process; QM may stay QM only if the DFA justifies FFI; `mw::log` frontend inside an ASIL app inherits ASIL duties, the `datarouter` daemon may stay QM | where the process boundary must fall |
| AutoSD QM partition | nested rootfs with own systemd/podman, extra SELinux labels, root side can stop it | spatial + some temporal FFI for the *QM* side |
| ELISA | method for arguing Linux in safety applications | the honest status: Linux qualification is ongoing work |

**On the Eclipse SDV stack.** AutoSD's QM partition is for the non-safety workloads; the safety Guardian belongs in the root (ASIL-intended) side, supervising and able to stop QM ([[autosd-overview]]). Gap C4 phrases it as "Guardian in the QM partition with a root-side watchdog": defensible only if the Guardian is framed as QM and the *watchdog* carries the safety claim. iceoryx2 gives process isolation and preallocated memory but no E2E; add a CRC + counter in the payload header ([[iceoryx2-overview]]). Ankaios/podman can set cgroup limits via `runtimeConfig` but has no deadline supervision ([[ankaios-overview]]). uProtocol over Zenoh is a black channel; E2E goes into the event payload (gap A10).

**The trap.** Claiming FFI from containers alone: spatial yes, temporal "limited", communication not at all.

**For a hackathon team.** A three-row FFI table in the README (axis, mechanism, detection, demo fault), then demonstrate one row per axis: `stress-ng` in QM with a `cpu.max` cap, a corrupted payload caught by CRC, a killed process caught by a missed deadline. Pitch: "we can say which interference we prevent, which we detect, and which needs a hypervisor".

**Evidence.** S-CORE quotes from platform_safety_manual.rst and stkh_req__dependability__no_mixed_asil. ISO 26262-6 Annex D classes from public summaries (unverified wording). IEC 61784-3 black channel from the IEC abstract. Contradiction noted with gap C4's placement of the Guardian; not edited.
