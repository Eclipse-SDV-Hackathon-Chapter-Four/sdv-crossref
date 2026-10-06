---
title: Freedom from interference is a stack of layers, name the one you rely on
type: pattern
cluster: orchestration-criticality
component: none
tags: [mixed-criticality, qm, bluechi, selinux, cgroups, hypervisor, qnx, asil]
status: draft
sources:
  - repos/automotive-image-builder/examples/qm.aib.yml
  - repos/automotive-image-builder/tests/tests/memory-limit-cpu-weight/memory-limit-cpu-weight.aib.yml
  - repos/hackfest-eclipse-score_reference_integration/images/autosd_x86_64/build/image.aib.yml
  - https://sigs.centos.org/automotive/ (QM partition, mixed criticality)
  - https://www.qnx.com/developers/docs/8.0/com.qnx.doc.hypervisor.user/topic/about.html
  - https://docs.kernel.org/admin-guide/cgroup-v2.html
  - repos/s-core-score/docs/modules/os/operating_systems/docs/community/ebclfsa.rst
last-verified: 2026-10-03
related:
  - "[[autosd-overview]]"
  - "[[s-core-overview]]"
  - "[[one-supervisor-per-node-readiness-is-the-apps-claim]]"
applies-to: [autosd, s-core, ankaios]
gap-rows: [C4, C2]
---

# Freedom from interference is a stack of layers; name the one you rely on

**Problem.** A team says "the Guardian is isolated because it is in a container". A container shares the kernel, so a kernel bug, a CPU hog or an fd leak in the QM side still reaches it. "Isolated" is meaningless until it names the layer and the interference class (CPU, memory, I/O, timing, faults, information).

**Forces.**
- Each layer is cheaper and weaker than the one below (process, cgroup, container, QM rootfs, VM, hypervisor, separate SoC).
- Safety cases need a named mechanism per interference class; QM code must never be trusted to behave.
- The more isolation, the more crossings to design (and each crossing is a new interface to qualify).
- A hackathon can demo detection and containment, not certification.

**The rule.** For each interference class write one line: "layer, mechanism, who enforces". Layers on a Linux node: (1) SELinux labels (QM containers get distinct labels; AutoSD defaults to enforcing); (2) cgroup v2 limits per slice (AIB `qm: memory_limit: {max, high}`, `cpu_weight`; CPU pinning is a cpuset you add, not an aib default (unverified)); (3) the QM partition: nested rootfs with its own systemd and podman, a separate `/var/qm` partition option; (4) a hypervisor guest (QNX hypervisor `qvm` VMs with vdevs, shared memory only when configured; KVM or Xen on Linux hosts); (5) separate SoC. The ASIL side may observe and stop the QM side (BlueChi agent in both partitions, controller on the root side), never the reverse.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| CentOS Automotive SIG QM partition | nested systemd+podman rootfs for QM, root side supervises | OS-level separation on one kernel |
| cgroup v2 (`cpu.weight`, `memory.max/high`, cpuset) | resource controllers per slice | temporal and memory budgets |
| SELinux | MAC labels per container domain | information/access interference |
| QNX hypervisor | guest OSes in VMs created by `qvm`, vdevs, explicit shared memory | spatial isolation incl. kernel faults |
| Xen / KVM | dom0 plus guests, para-virtualised devices | open-source hypervisor option (no cert claim here) |
| EB corbos Linux for Safety Applications | hypervisor-separated HI applications beside Linux; public build is a single-kernel fast-dev variant | HI apps in Linux user space with syscall checks |

**On the Eclipse SDV stack.** The HackFest AutoSD image sets `qm: memory_limit: infinity` (no budget!) and `selinux_mode: permissive`: it demonstrates plumbing, not freedom from interference ([[autosd-overview]]). Tighten it: `memory_limit.max`, `cpu_weight`, enforcing SELinux, and measure the QM hog's effect on the root-side Guardian. Gap C4 (Guardian in QM, BlueChi watchdog on root, AVC forwarding) is the demo; note the safety direction, a Guardian is an ASIL-flavoured role, so putting it in QM is a story about monitoring *from* root. S-CORE states its own AoU: the OS/hypervisor mechanisms are the integrator's, S-CORE supports only a reference combination ([[s-core-overview]], platform_assumptions).

**The trap.** Counting a shared directory or `/dev/shm` as "just data", forgetting it is a crossing the QM side can corrupt or fill.

**For a hackathon team.** Run a CPU/memory hog in QM, show root-side latency stays within budget with limits and degrades without them, then stop QM from root via BlueChi. Pitch: "we name the layer for every interference class".

**Evidence.** QM/limits syntax: qm.aib.yml and the memory-limit-cpu-weight test. Permissive SELinux and `infinity` limits: the HackFest image.aib.yml. QNX hypervisor concepts: QNX docs page. EBcLfSA: ebclfsa.rst. No ASIL claim for upstream AutoSD (see [[autosd-overview]]).
