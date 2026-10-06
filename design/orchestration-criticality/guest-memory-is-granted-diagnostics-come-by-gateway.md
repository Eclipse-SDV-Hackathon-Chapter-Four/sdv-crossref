---
title: Guest memory is granted, never assumed; diagnostics reach a guest by gateway
type: pattern
cluster: orchestration-criticality
component: none
tags: [hypervisor, virtio, ivshmem, vhsm, passthrough, sovd, gateway, dm-verity, qnx, kvm]
status: draft
sources:
  - repos/s-core-communication/score/mw/com/gateway/README.md (LoLa inter-domain gateway, VMs and SoCs)
  - repos/s-core-communication/score/mw/com/gateway/transport_layer/qemu/README.md (ivshmem BAR transport)
  - repos/s-core-communication/score/mw/com/dependability/software_architectural_design/pci_e_gateway/README.md
  - repos/opensovd-main/docs/design/design.md (SOVD Gateway routes to server, CDA, native SOVD ECUs)
  - https://www.qnx.com/developers/docs/8.0/com.qnx.doc.hypervisor.user/topic/about.html
  - https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html
  - https://www.qemu.org/docs/master/system/devices/ivshmem.html
last-verified: 2026-10-03
related:
  - "[[freedom-from-interference-is-a-stack-of-layers]]"
  - "[[opensovd-overview]]"
  - "[[s-core-overview]]"
applies-to: [s-core, opensovd, autosd, iceoryx2]
gap-rows: [A3, C2]
---

# Guest memory is granted, never assumed; diagnostics reach a guest by gateway

**Problem.** An ASIL guest (QNX) and a Linux guest share a SoC. Someone maps a shared buffer "for speed", or exposes the host's diagnostic stack to the guest directly, and the isolation story is gone. Or the guest has no diagnostic path at all.

**Forces.**
- Zero-copy across guests needs shared memory, which is an interference channel.
- Devices (virtio, passthrough, a vHSM) are shared or owned, never both.
- A guest has its own OS instance, its own supervisor, its own fault model.
- Diagnostics must reach into every guest without a bespoke tester per guest.

**The rule.** Treat each guest as its own LoLa/iceoryx2 *domain*: nothing is shared by default, and each crossing is an explicit grant with a direction and a size. Grants come in three forms: a **virtio** device (hypervisor-mediated, copy semantics), a **shared region** (ivshmem BAR, QNX shared memory vdev; fixed layout, one writer), and **passthrough** (a device owned by one guest; a vHSM is served from one guest to the others over a message interface, not by sharing keys). For diagnostics, put a gateway at the boundary: the host (or one designated guest) runs the SOVD gateway and the guest exposes its components behind a gateway-side proxy, so a tester sees one tree and the guest keeps its own fault manager.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| virtio (OASIS spec) | standard paravirtual devices between guest and host | portable, hypervisor-mediated I/O |
| QEMU `ivshmem` | PCI device exposing a shared memory BAR between VMs | the open-source shared-memory crossing |
| QNX hypervisor | guests in `qvm` VMs; vdevs; shared memory "when configured" | spatial isolation with explicit crossings |
| S-CORE LoLa gateway | one gateway process per domain, Source/Destination roles, pluggable transport (TCP side channel + ivshmem BAR in the QEMU transport; PCIe DMA copy for SoC-to-SoC) | service-level forwarding with a forwarding skeleton |
| OpenSOVD gateway | routes `/components/{ecu}` to server, CDA or native SOVD ECUs (gateway forwarding is on the roadmap, not in `opensovd-core`) | diagnostics as a federation of per-domain servers |
| dm-verity guest rootfs | guest image read-only and hash-verified | the guest cannot be silently modified by the host |

**On the Eclipse SDV stack.** S-CORE's LoLa gateway is the data path: in the QEMU transport, services are allocated in ivshmem, offsets registered in a shared directory, and the remote gateway binds a forwarding skeleton at those offsets ([[s-core-overview]]). The diagnostics path is the missing sibling: OpenSOVD's gateway concept maps one-to-one onto "a guest is a component with its own server", but no code connects the fault library inside a guest to the host gateway (gap A3 for the S-CORE app to OpenSOVD link). Ankaios sees only containers, so the guest itself is a workload only in the sense of a VM launcher container (privileged; unverified). Open a real Linux guest with dm-verity root and nothing else shared, then add one ivshmem region and treat it as the audit surface.

**The trap.** Calling a shared-memory region "a bus": it has no authentication, no loss, and one stray write corrupts the peer.

**For a hackathon team.** QEMU only: two guests with ivshmem, the LoLa QEMU transport demo from `dual_qemu`, plus a one-page table "grant, direction, size, owner". Pitch: "every guest crossing is a line in a table".

**Evidence.** ivshmem transport flow: gateway/transport_layer/qemu/README.md. PCIe copy semantics: pci_e_gateway README. SOVD gateway role and the not-yet-landed forwarding: design.md and [[opensovd-overview]]. vHSM serving over messages is a design recommendation, not sourced from a public spec (unverified). KVM/Xen specifics not researched in depth.
