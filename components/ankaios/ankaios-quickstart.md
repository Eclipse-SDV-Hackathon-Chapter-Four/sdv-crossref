---
title: Ankaios quickstart
type: quickstart
component: ankaios
tags: [ankaios, orchestrator, podman, sdv]
status: verified
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

# Ankaios quickstart (KUKSA databroker + feeder, 15 min)

**Status: executed rootless on 2026-10-03** (see the Observed section at the end); the sections above are the documented sudo/systemd path, which was not run. Corrections found: `--startup-manifest` (not `--startup-config`); `ank --insecure` is valid; `kuksa.val/databroker:0.4.1` replaced by `eclipse-kuksa/kuksa-databroker:0.7.1`.

## Prerequisites
- Linux x86_64/arm64 (Ubuntu 22.04/24.04/26.04 tested upstream), root via sudo, internet for image pulls.
- `sudo apt-get install -y podman` (>= 3.4.2; >= 4.3.1 for podman-kube).
- Ubuntu 24.04: SDV Lab README says to disable AppArmor "as described in the Ankaios installation guide" (repos/sdv_lab/README.md:125); the current install.md in the repo has no AppArmor text, so the exact step is unverified. If podman containers fail to start on 24.04, suspect AppArmor/user-namespace restrictions.

## Install (one-liner, latest = v1.0.4 at time of writing)
```shell
curl -sfL https://github.com/eclipse-ankaios/ankaios/releases/latest/download/install.sh | bash -
# pinned (preferred for hackathons):
curl -sfL https://github.com/eclipse-ankaios/ankaios/releases/download/v1.0.4/install.sh | bash -s -- -v v1.0.4
```
Installs `ank`, `ank-server`, `ank-agent` into /usr/local/bin, systemd units, configs in /etc/ankaios. Insecure (no mTLS), dev only. Uninstall: `ank-uninstall.sh`.

## Start server + agent
```shell
sudo systemctl start ank-server ank-agent
sudo journalctl -t ank-server -n 20
ank get agents
```
Expected (from docs, numbers vary):
```text
NAME        WORKLOADS   CPU USAGE   FREE MEMORY
agent_A     0           ...         ...
```
Default agent name is `agent_A`. If the default /etc/ankaios/state.yaml contains nginx it will already run.

## Manifest: KUKSA databroker + feeder + consumer
Taken from the tutorial (images/tags as in docs; tags may be stale, unverified). Save as `vehicle.yaml`:
```yaml
apiVersion: v1
workloads:
  databroker:
    runtime: podman
    agent: agent_A
    restartPolicy: ALWAYS
    runtimeConfig: |
      image: ghcr.io/eclipse/kuksa.val/databroker:0.4.1
      commandArgs: ["--insecure"]
      commandOptions: ["--net=host"]
  speed-provider:            # the "feeder": web UI on :5000, auto mode pushes speed
    runtime: podman
    agent: agent_A
    dependencies:
      databroker: ADD_COND_RUNNING
    runtimeConfig: |
      image: ghcr.io/eclipse-ankaios/speed-provider:0.1.3
      commandOptions: ["--net=host", "-e", "SPEED_PROVIDER_MODE=auto"]
  speed-consumer:
    runtime: podman
    agent: agent_A
    dependencies:
      databroker: ADD_COND_RUNNING
    runtimeConfig: |
      image: ghcr.io/eclipse-ankaios/speed-consumer:0.1.2
      commandOptions: ["--net=host", "-e", "KUKSA_DATA_BROKER_ADDR=127.0.0.1"]
```
(The tutorial uses `agent: infotainment` for the consumer, requiring a 2nd agent: `ank-agent --name infotainment --server-url http://127.0.0.1:25551`. Here all run on agent_A for simplicity.)

Apply and inspect:
```shell
ank apply vehicle.yaml
ank get workloads
ank logs --follow speed-consumer
ank get state
```
Expected `ank get workloads` (docs):
```text
 WORKLOAD NAME    AGENT     RUNTIME   EXECUTION STATE   ADDITIONAL INFO
 databroker       agent_A   podman    Running(Ok)
 speed-consumer   agent_A   podman    Running(Ok)
 speed-provider   agent_A   podman    Running(Ok)
```
Speed provider UI: http://127.0.0.1:5000. Databroker gRPC on 55555 (host network; unverified default).

Clean up: `ank delete workload databroker speed-provider speed-consumer`.

## Run without systemd (rootless/dev)
```shell
ank-server --insecure --startup-config ./vehicle.yaml --address 127.0.0.1:25551 &
ank-agent  --insecure --name agent_A --server-url http://127.0.0.1:25551 &
ank --insecure get workloads
```
Flags taken from repos/ankaios-dashboard/run_dashboard.sh and the tutorial; `--insecure` on `ank` is unverified (check `ank --help`). An agent started as a normal user calls podman rootless (tutorial-vehicle-signals.md).

## Earlier note (2026-10-03, pre-run)
`git ls-remote` showed newest tag v1.0.4; clone of main = 696da8a, `ank` crate version 1.1.0-pre.

## Observed on 2026-10-03 (verifier, rootless, no systemd)
Differs from the documented path: no sudo, no install.sh, no systemd, no /etc/ankaios; binaries run from `.local-ankaios/`, podman is rootless (images in the user store), server/agent are plain background processes with logs in `.local-ankaios/logs/`. Host: podman 5.7.0 rootless.

Binaries: `https://github.com/eclipse-ankaios/ankaios/releases/download/v1.0.4/ankaios-linux-amd64.tar.gz` (contains `ank`, `ank-server`, `ank-agent`; sha256 `fef8b0ab39ab10a1bc22a064a8d938cd8f07c9428d22ae9574acc99baeaa728a`, upstream .sha512sum.txt verified OK). `ank --version` = `ank 1.0.4`.

```shell
ank-server --insecure --address 127.0.0.1:25551 > logs/server.log 2>&1 &
ank-agent  --insecure --name agent_A --server-url http://127.0.0.1:25551 > logs/agent.log 2>&1 &
ank --insecure get agents
```
```text
NAME      WORKLOADS   CPU USAGE   FREE MEMORY
agent_A   0           2%          1457356800B
```
Pre-pull (`podman pull`, warm network): databroker 0.7.1 3 s, speed-provider 0.1.3 3 s, speed-consumer 0.1.2 5 s.

Manifest: the quickstart manifest above with only the databroker image changed to `ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1` (the rest already was 1.x syntax; `restartPolicy: ALWAYS` on databroker). `ank --insecure apply vehicle.yaml` blocks and prints state transitions. Start order observed: databroker Pending(Initial) -> Pending(Starting) -> Running(Ok) about 7 s after apply; speed-consumer/speed-provider sat in Pending(WaitingToStart) until then and were Running(Ok) about 5 s later (all three at ~17:02:25).
```text
WORKLOAD NAME    AGENT     RUNTIME   EXECUTION STATE   ADDITIONAL INFO
databroker       agent_A   podman    Running(Ok)
speed-consumer   agent_A   podman    Running(Ok)
speed-provider   agent_A   podman    Running(Ok)
```
`ank logs` (last lines):
```text
databroker:     INFO databroker::grpc::server: Listening on 0.0.0.0:55555  (also: Starting Kuksa Databroker 0.7.1, WARN Authorization is not enabled)
speed-provider: 2026-10-03 15:02:23 Feeding Vehicle.Speed to 11
speed-consumer: 2026-10-03 15:02:23 Received updated speed: 11.0
```
kuksa-client 0.6.0 (`.venv`, python `VSSClient('127.0.0.1',55555)`; the `kuksa-client` CLI is interactive):
```text
get Vehicle.Speed -> {'Vehicle.Speed': Datapoint(value=15.0, timestamp=2026-10-03 15:02:27Z)}
set Vehicle.Cabin.Door.Row1.DriverSide.IsOpen=True ; get -> Datapoint(value=True, ...)
```
Note: the speed-provider "web UI on :5000" claimed above did NOT answer (curl: connection refused) in auto mode; treat as unverified/not present in 0.1.3 auto mode.

### Fault injection
- `ank delete workload speed-provider` (17:02:32): printed `speed-provider agent_A  Removed`, gone from `get workloads`. Re-apply (17:02:42): Pending(Initial) -> Pending(Starting) "Triggered at runtime." -> Running(Ok) within ~1 s (image cached). Deleted workload was not restarted by policy, as documented.
- `podman kill <databroker ctr>` with `restartPolicy: ALWAYS` (17:02:42): databroker back to Running(Ok) within 3 s (the state was already Running at first poll, no Failed state shown). But the dependents (restartPolicy default NEVER, TCP clients) exited with code 1 and stayed `Failed(ExecFailed) Exit code: '1'` indefinitely (polled for 12 s; not restarted, and dependencies are not re-checked).
- Same with `restartPolicy: NEVER` on databroker (killed 17:03:05): `Failed(ExecFailed)  Exit code: '137'` within 3 s and it stays that way.
Confirms the claim "restart only on exit, no liveness probe": Ankaios reacts to container exit codes only; a hung but alive container would stay Running(Ok). (Not tested: a hung container; inferred from the absence of any health setting.)

Teardown: all workloads deleted, agent and server stopped, no containers left; binaries kept in `.local-ankaios/`.
