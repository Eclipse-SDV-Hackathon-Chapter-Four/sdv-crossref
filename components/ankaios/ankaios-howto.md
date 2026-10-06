---
title: Ankaios how-to recipes and pitfalls
type: howto
component: ankaios
tags: [ankaios, orchestrator, podman, sdv]
status: draft
sources:
  - repos/ankaios/doc/docs/usage/quickstart.md
  - repos/ankaios/doc/docs/usage/tutorial-vehicle-signals.md
  - https://github.com/eclipse-ankaios/ankaios
last-verified: 2026-10-03
related:
  - "[[ankaios-overview]]"
  - "[[ankaios-quickstart]]"
  - "[[ankaios-howto]]"
  - "[[ankaios-reference]]"
  - "[[ankaios-integration-notes]]"
---

# Ankaios how-to and pitfalls

## Recipes
**Dynamic run of a one-off workload**
```shell
ank run workload hello --runtime podman --agent agent_A --config 'image: docker.io/busybox:1.36
commandArgs: ["sh","-c","echo hi"]'
ank get workloads   # Succeeded(Ok)
```
(pattern from quickstart.md; that doc uses containerd for this example)

**Control-interface app (Python SDK)** - workload needs `controlInterfaceAccess`:
```yaml
controlInterfaceAccess:
  allowRules:
    - {type: StateRule, operation: ReadWrite, filterMasks: ["*"]}
    - {type: LogRule, workloadNames: ["*"]}
```
```python
from ankaios_sdk import Workload, Ankaios
with Ankaios() as ank:
    w = Workload.builder().workload_name("dyn").agent_name("agent_A").runtime("podman") \
        .restart_policy("NEVER").runtime_config('image: docker.io/library/nginx\ncommandOptions: ["-p","8080:80"]').build()
    ank.apply_workload(w)
```
Working examples: repos/ankaios/examples/{python_sdk_hello,rust_sdk_hello,python_sdk_logging,...}; hackathon template repos/sdv_lab/ankaios/example_workloads. Subscribe to state changes with events (`subscribeForEvents`, field mask e.g. `workloadStates.*.*.*.state`) - repos/ankaios/doc/docs/reference/events.md, tutorial-events.md.

**Fault injection by workload restart** (ideas, untested): `ank delete workload X` then `ank apply` (note: explicit delete does NOT trigger restartPolicy); `podman kill <ctr>` to test `restartPolicy: ON_FAILURE/ALWAYS`; stop `ank-agent` to see workload states go Unknown/lost; supervisor workload using SDK to flip a workload on a stuck signal.

**Dashboard**: add workload `ghcr.io/eclipse-ankaios-dashboard/ankaios-dashboard:latest`, `-p 5001:5001`, needs ReadWrite on `desiredState` and `workloadStates`, login admin/admin by default (repos/ankaios-dashboard/README.md). Its README manifest is in old v0.1 syntax; convert to `apiVersion: v1`/`controlInterfaceAccess.allowRules[].filterMasks`. Last dashboard commit seen: 2025-09-19 (tested with Ankaios v0.6.0) - compatibility with 1.x unverified.

**Templated configs / files**: define `configs:` at top level, bind with `configs: {alias: name}`, use `{{alias.key}}` in runtimeConfig; mount files with `files: [{mountPoint, data}]` (see e2e-vehicle-signals vehicle-signals.yaml).

**mTLS**: repos/ankaios/doc/docs/usage/mtls-setup.md. Config files: /etc/ankaios/ank-server.conf, ank-agent.conf, $HOME/.config/ankaios/ank.conf.

## Pitfalls
1. **Podman required** (or containerd+nerdctl). Missing podman = workloads stuck/failed. podman-kube needs >= 4.3.1.
2. **Root vs rootless**: systemd-installed agent runs as root, so podman is rootful; an agent started by a user uses rootless podman with a different image store (images pulled as one are invisible to the other) and different network behavior (slirp4netns/pasta, no privileged ports < 1024 without sysctl). Tutorial: "second agent started by non-root user therefore also uses podman in user mode".
3. **Networking between workloads**: the docs treat workload communication as out of scope (corrected 2026-10-03, see [[a-container-is-an-ecu-zenoh-is-the-only-door]]). The tutorial and blueprints use `--net=host` for everything and talk via localhost; across nodes use host IPs and published ports (`-p`). With rootful vs rootless mixed, localhost via host network still works but container-network names do not. Blueprint README: "We recommend network mode host for all your workloads".
4. **Host networking/privileges**: CAN, USB, serial need `--privileged` / `--device` in `commandOptions` (see kuksa-can-provider in e2e-vehicle-signals; ThreadX flash hint in HC3 HPC variant).
5. **Shared memory for iceoryx2**: iceoryx2 uses /dev/shm and /tmp/iceoryx2 (repos/iceoryx2/FAQ.md:458). Workloads in separate podman containers need the same paths, not the same IPC namespace (`--ipc=host` does not cover POSIX shared memory; corrected 2026-10-03, see [[share-two-directories-and-one-uid-isolate-by-prefix]]): use `commandOptions: ["-v", "/dev/shm:/dev/shm", "-v", "/tmp/iceoryx2:/tmp/iceoryx2"]` and matching UIDs/permissions (FAQ.md:683 mentions sticky bit on those dirs). Ankaios docs say nothing about this; **unverified recipe**, test it. See [[iceoryx2-overview]].
6. **Restart policies**: default NEVER. ALWAYS restarts on Succeeded or Failed; ON_FAILURE only Failed(ExecFailed); explicit delete never restarts; restart ignores dependencies (restart-policy.md).
7. **Dependencies**: `ADD_COND_RUNNING|SUCCEEDED|FAILED`; waiting workloads show `Pending(WaitingToStart)`; cycles rejected; deleting a dependency is also governed by implicit dependencies. "Running" means container up, not app ready (databroker may still be initializing) - add retry in feeders. **Warning**: `ADD_COND_RUNNING` checks container state only, and dependencies are not re-checked when a workload restarts ([[one-supervisor-per-node-readiness-is-the-apps-claim]]).
8. **Express install = no auth**; anyone reaching port 25551 can start root workloads. Bind server to 127.0.0.1 or set up mTLS.
9. **Version skew**: v0.6 vs v1.x manifests/CLI differ (apiVersion, accessRights -> controlInterfaceAccess, restart -> restartPolicy). Pin the same version for server, agent, CLI, SDK. Install script overwrote existing config in a past issue (#781, open).
10. Workload names <= 63 chars, only letters/digits/`-`/`_`. Control-interface issues: #459 (connection closed after agent disconnect, open), #720 (fails after server restart, closed).
11. Image pull on first start can take long; pre-pull on offline hackathon Wi-Fi (`podman pull`). Behind VPN, buildah DNS errors: pass `--dns=<ip>` (examples README).
12. Ubuntu 24.04 AppArmor note (see quickstart).

## Observed on 2026-10-03
**iceoryx2 two-workload recipe (gap C1): VERIFIED**, rootless podman 5.7.0, Ankaios 1.0.4 without systemd (see [[ankaios-quickstart]]). The `publish_subscribe` Rust example, built with `cargo build --release -p example --example publish_subscribe_publisher --example publish_subscribe_subscriber` in repos/iceoryx2 (32 s; the Cargo package is named `example`, binaries land in `target/release/examples/`), was put in two images (`FROM debian:bookworm-slim`, `COPY publish_subscribe_<x> /usr/local/bin/app`, `ENTRYPOINT`; host glibc symbols needed <= 2.34, bookworm has 2.36). Manifest (works as is, with `/tmp/iceoryx2` created first on the host):
```yaml
apiVersion: v1
workloads:
  iox-pub:
    runtime: podman
    agent: agent_A
    runtimeConfig: |
      image: localhost/iox-publisher:dev
      commandOptions: ["--net=host", "-v", "/dev/shm:/dev/shm", "-v", "/tmp/iceoryx2:/tmp/iceoryx2"]
  iox-sub:
    runtime: podman
    agent: agent_A
    runtimeConfig: |
      image: localhost/iox-subscriber:dev
      commandOptions: ["--net=host", "-v", "/dev/shm:/dev/shm", "-v", "/tmp/iceoryx2:/tmp/iceoryx2"]
```
`ank logs iox-sub`:
```text
Subscriber ready to receive data!
received: TransmissionData { x: 1, y: 3, funky: 812.12 }
received: TransmissionData { x: 2, y: 6, funky: 1624.24 }
received: TransmissionData { x: 3, y: 9, funky: 2436.36 }
```
Facts: (1) `--ipc=host` was not needed and not tried (no failure to fix). (2) `--user`/`--userns=keep-id` was also not needed: with rootless podman, container root maps to the host user, so both workloads share one UID automatically (a first run with `--user=1000:1000 --userns=keep-id` also worked). Under rootful podman this would differ; not tested. (3) Negative control: the same two images run with plain `podman run` and NO shared mounts printed "Subscriber ready" and never received a sample, so the two mounts are what make it work. (4) `--net=host` is not needed by iceoryx2, it was just kept for consistency. Not tested: rootful agent, mixed UIDs, `--read-only` roots.
