---
title: A container is an ECU; Zenoh is the only door
type: pattern
cluster: orchestration-criticality
component: none
tags: [containers, namespaces, iceoryx2, zenoh, shm, compose, ankaios, networking]
status: draft
sources:
  - repos/ankaios/doc/docs/architecture.md (communication between workloads out of scope)
  - repos/ankaios/doc/docs/usage/tutorial-vehicle-signals.md (--net=host for databroker and providers)
  - repos/hackfest-eclipse-score_reference_integration/images/autosd_x86_64/build/image.aib.yml (shared /dev/shm and /tmp/mw_com_lola root to QM)
  - https://docs.podman.io/en/latest/markdown/podman-run.1.html (--ipc, --pid, --shm-size, --net)
  - https://zenoh.io/docs/
  - repos/iceoryx2/FAQ.md (shared /dev/shm across containers)
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[zenoh-overview]]"
  - "[[ankaios-overview]]"
  - "[[freedom-from-interference-is-a-stack-of-layers]]"
applies-to: [ankaios, iceoryx2, zenoh, autosd, s-core]
gap-rows: [C1, C5]
---

# A container is an ECU; Zenoh is the only door

**Problem.** A virtual multi-node setup on one laptop shares `/dev/shm` and the host network, so a bug that would be a wiring fault on two ECUs passes silently, and the demo does not survive deployment on real hardware.

**Forces.**
- Same-node sharing (zero-copy) is a feature on one node and a lie when simulating two.
- Shared memory is a crossing with no network failure mode: no loss, no latency, no partition.
- Ankaios does not network workloads (communication is out of scope), so the choice is yours and `--net=host` is the lazy default in its tutorials.
- Fault-injection needs a boundary where you can cut something.

**The rule.** Decide per pair of workloads: **same node** or **two ECUs**. Same node: deliberately share `/dev/shm` and the service directory (`/tmp/iceoryx2`, `/tmp/mw_com_lola`) with the same UID, and say so in the manifest. Two ECUs: each container gets its own PID namespace, `/dev/shm` (sized with `--shm-size`) and `/tmp`, no `--ipc=host`, no `--pid=host`, and the only thing that crosses is Zenoh (or uProtocol over Zenoh) on a network you can cut. Same binaries, same model, different manifest: that is the placement change of [[placement-is-a-manifest-not-a-model-edit]].

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Linux namespaces via Podman/Docker | `--ipc`, `--pid`, `--net` each opt in to sharing | the knobs are per-namespace and default private |
| Docker Compose networks | named networks, service DNS | a cuttable "bus" per ECU pair |
| iceoryx2 | zero-copy within one `/dev/shm` domain, host-local | explicit same-node scope |
| Zenoh | peer/router across nodes | the inter-node transport, wildcard keys |
| AutoSD root-to-QM | the reference image mounts `/dev/shm` and `/tmp/mw_com_lola` into the QM container | the *same-node sharing* counter-example, deliberate and visible |

**On the Eclipse SDV stack.** Ankaios `runtimeConfig.commandOptions` carries the knobs: `["--shm-size=256m"]` for an ECU container; `["--ipc=host", "-v", "/dev/shm:/dev/shm"]` only for a same-node pair (gap C1, no upstream example, recipe unverified). The KUKSA tutorial uses `--net=host` because it is single-node; do not copy it into a two-ECU demo ([[ankaios-overview]]). The S-CORE AutoSD image shows the other mode: LoLa discovery directory and `/dev/shm` shared into QM, which also means QM can fill the directory ([[freedom-from-interference-is-a-stack-of-layers]]). Bridge iceoryx2 to Zenoh with the B2 gateway ([[iceoryx2-overview]], [[zenoh-overview]]).

**The trap.** Using host networking and shared IPC "to make it work", then claiming a two-ECU architecture.

**For a hackathon team.** Two Ankaios workloads on one machine with private namespaces and a Zenoh link; show `ls /dev/shm` differs, then drop the link to demonstrate the consumer's staleness handling. Pitch: "two containers, two ECUs, one door".

**Evidence.** Workload communication out of scope: architecture.md. `--net=host` usage: tutorial-vehicle-signals.md. Shared mounts into QM: image.aib.yml `10-lola-ipc.conf`. Podman flag semantics: podman-run(1) (standard behaviour, not re-fetched).
