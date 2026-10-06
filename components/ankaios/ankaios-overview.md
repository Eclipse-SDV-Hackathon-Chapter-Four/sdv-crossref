---
title: Eclipse Ankaios overview
type: overview
component: ankaios
tags: [ankaios, orchestrator, podman, sdv]
status: draft
sources:
  - repos/ankaios/README.md
  - repos/ankaios/doc/docs/usage/installation.md
  - https://github.com/eclipse-ankaios/ankaios
last-verified: 2026-10-03
related:
  - "[[ankaios-overview]]"
  - "[[ankaios-quickstart]]"
  - "[[ankaios-howto]]"
  - "[[ankaios-reference]]"
  - "[[ankaios-integration-notes]]"
---

# Eclipse Ankaios overview

## What it is
Workload and container orchestrator for embedded/automotive HPC, written in Rust, Apache-2.0. Server-agent architecture: one `ank-server` holds the desired state, one `ank-agent` per node starts/monitors workloads, `ank` is the CLI. Multi-node via one API. Runtimes: `podman`, `podman-kube` (K8s pod YAML via `podman play kube`), `containerd` (via nerdctl). (repos/ankaios/README.md, repos/ankaios/doc/docs/reference/startup-configuration.md)

Key concepts:
- **State manifest** (YAML, `apiVersion: v1`, `workloads:` map; fields `runtime`, `agent`, `restartPolicy`, `dependencies`, `tags`, `configs`, `files`, `controlInterfaceAccess`, `runtimeConfig` string). Handlebars templating for `agent`, `runtimeConfig`, `files`.
- **Startup manifest** read by server (`/etc/ankaios/state.yaml` by default) or dynamic `ank apply`.
- **Control interface**: each workload gets FIFOs `/run/ankaios/control_interface/{input,output}` speaking protobuf (`ankaios.proto`); lets a workload read/write CompleteState, read logs, subscribe to events. Authorized per workload by `controlInterfaceAccess` allow/deny rules (default: deny all). SDKs: Python (`ankaios-sdk`) and Rust (`ankaios_sdk`). (repos/ankaios/doc/docs/reference/control-interface.md, events.md)
- Inter-workload dependencies (`ADD_COND_RUNNING|SUCCEEDED|FAILED`), restart policies `NEVER|ON_FAILURE|ALWAYS` (restart on exit only; no liveness or health probe, so a hung workload stays Running, see [[one-watchdog-per-layer-each-blind-to-the-others]]), configs, workload files, `ank logs`, optional mTLS.

## What it is NOT
Not Kubernetes: no service discovery/DNS, no overlay network, no scheduler that places workloads (you name the agent; the cluster does not rebalance), no ingress. Not a message bus, not a vehicle-signal layer, not a safety-certified runtime (the docs advertise requirement tracing, not certification; unverified for ASIL).

## Maturity / version
- Latest release tag found: **v1.0.4** (git ls-remote, 2026-10-03); a v1.0.0 line is the benchmarked version in the orch comparison. `main` is `1.1.0-pre` (repos/ankaios/ank/Cargo.toml). Looked at commit 696da8a (2026-10-02).
- Chapter 3 (Oct 2025) and SDV Lab used **v0.6.0**: expect old tutorials/READMEs (dashboard README, sdv_lab) to show `apiVersion: v0.1`, `accessRights`, `restart: true`; v1.x uses `apiVersion: v1`, `controlInterfaceAccess`, `restartPolicy`. See upgrade guides repos/ankaios/doc/docs/usage/upgrading/.
- Min requirements: Linux x86_64/arm64, 1 core, 256 MB RAM. Podman >= 3.4.2 (`podman`) / >= 4.3.1 (`podman-kube`).

## Pros / cons
Pros: tiny footprint (Rust; docs benchmark vs K3s v1.35 on idle memory, startup, nginx deploy time, repos/ankaios/doc/docs/reference/orch-comparison.md), dependency ordering, flash-wear prevention, dynamic API for workloads (control interface), simple YAML, Podman daemonless, works rootless, official dashboard, Symphony provider, used in several SDV blueprints.
Cons: young ecosystem; no service mesh/DNS (use `--net=host` or published ports); no automatic rescheduling across agents; docs and 3rd-party examples drift between 0.x and 1.x; express install has no auth (mTLS must be set up manually); Podman dependency; no iceoryx2/uProtocol awareness built in.

Vs alternatives:
| | Ankaios | k3s | systemd (+quadlet) | plain podman |
|---|---|---|---|---|
| Multi-node single API | yes | yes | no | no |
| Footprint | very small | small-medium | none | none |
| Dependencies | yes (state-based) | no (init containers) | yes (units) | no |
| Dynamic API for apps | control interface | K8s API | D-Bus | podman API |
| Service discovery | none | yes | none | none |
| When not to use | need K8s ecosystem/Helm, autoscaling | tiny single-ECU | need scheduling across nodes | needs only one container |

Sources for table: orch-comparison.md for k3s; systemd/podman columns are general knowledge (unverified).

## Hackathon ideas
- Control-interface "supervisor" app (SDK) that watches `workloadStates` via events and restarts/redeploys on health signals (Doctor Whodunit Guardian watchdog).
- Fault injection: `ank delete workload`/`ank apply` loops, `podman kill`, or `restartPolicy` variants, then verify detection; kill agent to see state transitions.
- Dashboard: run ankaios-dashboard (dependency graph) as a workload; extend it with fault-campaign buttons.
- Missing pieces: an iceoryx2 sample manifest (shared /dev/shm), uProtocol heartbeat workload publishing Ankaios state, OpenSOVD fault-lib bridge from workload states, OTA via Symphony provider.

## Chapter note (important correction)
"Doctor Whodunit" (Battery Thermal Guardian supervised by Ankaios on AutoSD) is a **Chapter 4** challenge (repos/hackathon-ch4-dotgithub/profile/README.md lines 41-51), not Chapter 3. In Chapter 3 Ankaios was used in the SDV Lab (CARLA ego-vehicle workloads, v0.6.0, repos/sdv_lab/README.md) and in "Mission Update Possible" (HPC variant: Symphony in cloud -> Ankaios in vehicle, repos/hc3-challenge-mission-update-possible/hpc_variant/README.md). See [[chapter3-retrospective]], [[chapter4-challenge-doctor-whodunit]].

Links: [[vss-kuksa-overview]], [[symphony-overview]], [[autosd-overview]], [[opendut-overview]], [[sdv-blueprints-overview]], [[iceoryx2-overview]], [[uprotocol-overview]].
