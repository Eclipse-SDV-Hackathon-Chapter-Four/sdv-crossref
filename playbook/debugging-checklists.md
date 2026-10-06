---
title: Debugging checklists (symptom-driven, per component)
type: playbook
component: none
tags: [debugging, checklist]
status: reviewed
sources:
  - components/*/<name>-howto.md and <name>-quickstart.md (see per-block citations)
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-quickstart]]"
  - "[[uprotocol-quickstart]]"
  - "[[zenoh-overview]]"
  - "[[iceoryx2-howto]]"
  - "[[opensovd-quickstart]]"
  - "[[openbsw-quickstart]]"
  - "[[ankaios-howto]]"
  - "[[opendut-quickstart]]"
  - "[[s-core-quickstart]]"
  - "[[sdv-blueprints-quickstart]]"
  - "[[autosd-howto]]"
  - "[[hackathon-patterns]]"
---

# Debugging checklists

How to use this: find your symptom, walk the steps in order, and stop at the first check that fails. Each step gives a check, what you should see, and the fix. Everything here comes from the linked notes. Steps marked (unverified) are unverified in the source note too.

## VSS / KUKSA databroker

**`get` returns `No entries found for the provided path`** ([[vss-kuksa-reference]], [[vss-kuksa-quickstart]])
1. Find out which tree the broker loaded:
   ```sh
   docker logs <broker-container> | grep Populating
   ```
   Expect `Populating metadata from file '/vss/<your>.json'`. If it shows `vss_release_6.0.json`, your overlay was never mounted. Fix: `-v $PWD/vss:/vss:ro ... --vss /vss/<your>.json`.
2. The path name may differ between VSS versions (`IsOccupied` became `OccupancyStatus` in 6.0, `celsius` became `Celsius`, `Vehicle.OBD.*` is gone). Use the name from the loaded JSON.
3. Old feeders and models (VSS 4.0 in sdv-runtime, Velocitas models) will not match a 6.x tree. Regenerate the tree with `vspec export json ...`, not the old `vspec2json.py`.

**`publish`/`actuate` prints OK, but the provider never sees the target** ([[vss-kuksa-howto]], [[vss-kuksa-quickstart]])
1. Read the whole CLI line. `[publish] OK  Error [Error { code: 400, reason: "value out of min/max bounds" ...}]` means the value was rejected.
2. Check the API version. The CLI prints `Using kuksa.val.v1`. v1 `actuate` / `set_target_values` returns OK but a v2 provider (`OpenProviderStream`) never receives it. Fix: the consumer calls v2 `Actuate` (raw stubs in the `kuksa-client` wheel). Don't mix API versions between provider and client.
3. v2 `Actuate` failing with `UNAVAILABLE` / `Provider for vss_id N does not exist` means no provider registered: start the provider first.
4. In the provider, read `entry.actuator_target`, not `entry.value`. A read straight after `Actuate` can still be empty, so subscribe instead.

**CLI: `Not a tty (os error 25)` / `Error: terminfo entry not found`** ([[vss-kuksa-quickstart]], [[vss-kuksa-reference]])
1. The CLI needs a TTY. Run it with `-it`:
   ```sh
   docker run --rm -it --network kuksa ghcr.io/eclipse-kuksa/kuksa-databroker-cli:0.7.1 --server Server:55555 get Vehicle.Speed
   ```
   Expect `[get]  OK` and then `Vehicle.Speed: ...`.
2. In scripts or CI with no TTY, wrap the command in `script -qec "..."` or use the Python `kuksa-client`.

**Client cannot connect at all** ([[vss-kuksa-reference]])
- Which port? Upstream uses 55555. macOS docs map `-p 55556:55555`, and service-to-signal runs on 55556 (`KUKSA_DATABROKER_PORT=55556`).
- TLS: with certs, use `https://` (with `http://` you get `h2 protocol error: ... frame with invalid size`). Without certs, pass `--insecure` explicitly.

## uProtocol / Zenoh

**Subscriber receives nothing** ([[uprotocol-quickstart]], [[uprotocol-howto]], [[zenoh-overview]])
1. Start the subscriber first, then the publisher. Publish is at-most-once, so nothing is replayed.
2. Turn on the transport logs:
   ```bash
   RUST_LOG=info ./target/debug/examples/subscriber
   ```
   Expect `Registering message listener [source filter: ...]`, then `Received message [topic: ...]`.
3. Check the filter against the authority. Source filter `//*/...` matches any authority. Authorities must be lowercase. Two hosts using the same authority are never bridged by a uStreamer.
4. With uStreamer: every pub/sub topic needs a static subscription entry. Topics that aren't listed are silently dropped.
5. Still nothing? Treat it as a discovery problem (next block).

**Works on cable / same host, not on Wi-Fi or in Docker** ([[zenoh-overview]], [[uprotocol-quickstart]])
- Multicast scouting may be blocked by Wi-Fi client isolation and VLANs (unverified; the default Docker bridge passed it on one host (corrected 2026-10-03, see [[zenoh-overview]])). Skip discovery with a router and explicit endpoints:
  ```bash
  ./app -m router -l tcp/0.0.0.0:7447          # one side
  ./app -m client -e tcp/<router-ip>:7447      # every other side
  ```
- For Docker, use host networking. Port 7447 must be reachable (`nc -zv <router-ip> 7447`).

**Compile error: duplicate / mismatching `UMessage` types** ([[uprotocol-quickstart]], [[uprotocol-howto]], [[chapter3-retrospective]])
1. Show what Cargo resolved:
   ```bash
   cargo tree -i up-rust
   cargo tree -p up-transport-zenoh
   ```
   Expect a single `up-rust` version. Two versions (for example 0.7/0.8 next to 0.9) is the bug.
2. Fix: put `up-rust` and `up-transport-zenoh` on the same minor (`up-rust = "0.9"` + `up-transport-zenoh = "0.9.1"`). Don't copy Cargo.toml from Chapter 3 apps (0.5-0.8).
3. If you are stuck on 0.7: pin `up-rust = "=0.7.0"`, run `cargo update -p up-rust --precise 0.7.0`, and commit Cargo.lock. 0.7.1 broke up-transport-zenoh.
4. API differences you'll see: `UUri::try_from_parts` (not `from_parts`). The Zenoh transport builder is a typestate, so `.with_config(...)` must come before `.build()`.

**Zenoh router / plugin won't load** ([[zenoh-overview]])
- Plugins must match the exact `zenohd` version. 0.11 and 1.x don't interoperate. Keep the router, bridges and clients on the same minor version.

## iceoryx2

**`IncompatibleTypes`** ([[iceoryx2-howto]], [[iceoryx2-quickstart]])
1. Compare the payload metadata on both sides:
   ```bash
   iox2 service details "My/Service"
   ```
   Check `type_name`, `size` and `alignment`. They must be identical.
2. Fix: use one shared type crate, `#[type_name("X")]` in Rust, or `IOX2_TYPE_NAME` in C++. The Rust example and the C++ example are known not to match each other; use `cross_language_communication_basics` instead.

**`VersionMismatch`** ([[iceoryx2-quickstart]], [[iceoryx2-howto]])
1. Check versions: `pip show iceoryx2`, `grep iceoryx2 Cargo.lock`. All processes and languages must use the same version.
2. The PyPI wheel 0.10.0 can't talk to Rust/C++ built from `main` (0.10.999), and `pip install iceoryx2==0.10.999` doesn't exist. Fix: build Rust/C++ from tag `v0.10.0`.

**`SIGBUS`** ([[iceoryx2-howto]])
```bash
df -h /dev/shm; du -sh /dev/shm
```
If shm is full or near the container default of 64 MB, raise it with `--shm-size=` or free stale files (next block). Overcommit when growing dynamic slices also causes it.

**`HangsInCreation` / corrupted service / stale shm** ([[iceoryx2-howto]], [[iceoryx2-quickstart]])
1. `iox2 node list`. Dead nodes are normally cleaned up by the next process (log `Dead node … detected`).
2. `ls /dev/shm | grep -c iox2_`. Thousands of files means stale resources (2858 were seen on the test box).
3. Nuclear option, with **all** iceoryx2 processes stopped:
   ```bash
   rm -rf /dev/shm/iox2_* /tmp/iceoryx2
   ```
4. Prevent it from coming back: set systemd `RemoveIPC=no`, make sure no tmp cleaner touches these dirs, don't mix versions, and make sure launchers `wait()` for children (zombies cause `ExceedsMaxSupportedPublishers`).

**Container cannot see the host's publisher (or vice versa)** ([[iceoryx2-howto]], [[ankaios-howto]])
1. Both `/dev/shm` **and** `/tmp/iceoryx2` must be shared. `--ipc=host` alone isn't enough:
   ```bash
   mkdir -p /tmp/iceoryx2
   docker run --user $(id -u):$(id -g) -v /dev/shm:/dev/shm -v /tmp/iceoryx2:/tmp/iceoryx2 ...
   ```
2. Use the same UID on both sides. Only the creating user can open resources; `dev_permissions` is a dev-only workaround.
3. Use the same domain on both sides: the same `global.prefix` / root-path in `iceoryx2.toml`. `iox2 config show` on both sides should match.
4. Ankaios: put the same flags into `commandOptions` (unverified recipe).
5. Enable debug output with `export IOX2_LOG_LEVEL=Trace`.

## OpenSOVD

**`503` `communication-not-ready` / "Variant detection has not concluded"** ([[opensovd-quickstart]])
1. Is the ECU or simulator up? `curl -sf http://127.0.0.1:8181/` (sim control API).
2. `--tester-address` (`-t`) must be an IP on the interface facing the ECUs (for example `172.42.0.1` on the Docker bridge):
   ```bash
   ip -4 addr | grep 172.42
   ```
3. A firewall must not block UDP 13400 broadcast (DoIP discovery).
4. Expect the CDA log line `ECU connected - setting connectivity to Online ecu_name="flxc1000"`, then `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:20002/health/ready` gives `204`.

**`/faults` returns 404** ([[opensovd-quickstart]], [[opensovd-overview]])
- Check which server you're hitting. The opensovd-core gateway (`:7690/sovd/v1`) doesn't implement `/faults`, `/operations`, `/modes` or `/locks`: you get a 404 with an empty body (issue #156). Faults only work through the CDA at `/vehicle/v15/...`.
- Lowercase `/vehicle/v15`. hrefs returned by `/components` say `/Vehicle/v15` and don't route on a case-sensitive client.
- The HackFest stub CDA (`/sovd/v1`) and the real CDA (`/vehicle/v15`) expose different APIs ([[hackfest-openbsw-playground]]).

**`409` `lock-required`** ([[opensovd-quickstart]], [[opensovd-howto]])
```bash
curl -s -X POST $B/components/flxc1000/locks -H "$H" -H 'Content-Type: application/json' -d '{"lock_expiration":60}'
curl -s -X DELETE $B/components/flxc1000/faults -H "$H" -w '%{http_code}\n'
```
Expect `"owned":true` from the lock, then `204` (UDS 0x14). Redo the lock once it expires.

**DELETE on faults "ignored" (faults still listed)** ([[opensovd-quickstart]], [[opensovd-howto]])
1. Print the status code (`-w '%{http_code}'`). `409` means no lock (see above). `404` means you're on the core gateway, which has no faults.
2. The list merges ODX-known DTCs with the ones the ECU reports. `?status[confirmedDtc]=true` still returns all of them, so decide by `.status.mask` on the client side.
3. Check the simulator's own memory through its control API (`:8181`, not SOVD). After a successful DELETE, the sim fault memory is `[]`. You can also clear it there with `DELETE /{ECU}/dtc/Standard`.

**MDD: `Protocol UDS_Ethernet_DoIP_DOBT not found in database`** ([[opensovd-quickstart]], [[opensovd-howto]])
- The protocol name must exist in the MDD, otherwise that ECU is skipped. Try `--protocol-name UDS_Ethernet_DoIP` (off-board) against the default `UDS_Ethernet_DoIP_DOBT`.
- With the test MDDs, JGWT5000/HOVR4000/TMCC3000 fail with both names, which is expected. flxc1000/fsnr2000/flxcng1000 load. VAM `UnknownECU` logs are harmless.
- Run the CDA from a scratch directory, because it writes storage into the CWD.

## OpenBSW

**`Failed to ioctl socket (node=vcan0, error=-1)` / `TapEthernetDriver start failed!`** ([[openbsw-quickstart]], [[openbsw-howto]])
1. `ip link show vcan0` / `ip link show tap0`. If they're missing, the app still runs, but without CAN or Ethernet.
2. Fix (needs sudo): from the repo root, `./test_setup.sh --apply` creates vcan0 and, like upstream's `tools/enet/bring-up-ethernet.sh`, tap0 (192.168.0.10/24) plus VLAN 160 `tap0a0` (192.168.2.10/24); `--remove` deletes them. By hand:
   ```bash
   sudo ip link add dev vcan0 type vcan && sudo ip link set vcan0 mtu 16 && sudo ip link set up vcan0
   ./tools/enet/bring-up-ethernet.sh     # tap0 192.168.0.10/24, tap0a0 192.168.2.10/24, ECU 192.168.0.201
   ```
3. Check: `candump vcan0` shows frame `0x558` every second (observed 2026-10-03, see [[openbsw-quickstart]]). UDS over CAN at commit 9b94994 answers on request `0x7E0` / response `0x7E8` (e.g. `cansend vcan0 7E0#0322CF0100000000`), not `02A`/`0x0F0` as older docs say (corrected 2026-10-03). With vcan0 present only the `TapEthernetDriver start failed!` line remains when tap0 is missing. WSL's stock kernel has no SocketCAN. In Docker you need `--cap-add=NET_ADMIN` plus `/dev/net/tun`, and vcan needs the host kernel module ([[openbsw-integration-notes]]).

**ECU stops when backgrounded** ([[hackfest-esslingen-2026]], [[hackfest-openbsw-playground]])
- The console calls `tcsetattr` on stdin, so a background job gets SIGTTOU and stops. Fix:
  ```bash
  ./app.referenceApp.elf < /dev/null &
  ```

**CDA gets DoIP Generic NACK after `DiagnosticMessagePositiveAck` (0x8002)** ([[hackfest-openbsw-playground]], [[opensovd-integration-notes]])
- Upstream OpenBSW answers 0x8002/0x8003 with Generic NACK 0x01. Fix: use the Playground overlay (`DoIpServerConnectionHandler.cpp`, lines 284-290) **or** set `[doip] send_diagnostic_message_ack=false` in the CDA config. Also raise `send_timeout_ms` (the HackFest used 5000; 1 s was too short for lwIP, see [[hackfest-esslingen-2026]]).
- Keep the Playground's `openbsw` submodule at `07b7551`, because newer main broke the overlay.

## Ankaios

**Workload stuck in `Pending(WaitingToStart)`** ([[ankaios-howto]], [[hackathon-patterns]])
1. `ank get workloads`. A workload shows Pending until its `dependencies` condition (`ADD_COND_RUNNING|SUCCEEDED|FAILED`) is met. Check that the dependency exists and is in that state.
2. The `agent:` name in the manifest must match a connected agent: `ank get agents`.
3. `ADD_COND_RUNNING` means the container is up, not that the app is ready. Feeders need retries.

**Workload `Failed(ExecFailed)`** ([[ankaios-howto]], [[ankaios-quickstart]])
1. `ank logs <workload>`, then `podman ps -a` / `podman logs <ctr>` as the **same user** the agent runs as.
2. Is podman installed (>= 3.4.2, >= 4.3.1 for podman-kube)? Without podman, workloads fail.
3. On Ubuntu 24.04, suspect AppArmor or user-namespace restrictions (exact fix unverified).
4. The default `restartPolicy` is `NEVER`. `ON_FAILURE` only retries `Failed(ExecFailed)`.
5. Check the manifest dialect: v1 uses `apiVersion: v1`, `controlInterfaceAccess`, `restartPolicy`. v0.6 manifests (`v0.1`, `accessRights`) don't apply. Pin server, agent, CLI and SDK to the same version.

**`image not found` for `localhost/...`** ([[hackathon-patterns]], [[ankaios-howto]])
- The image must already be in **podman's** store for the agent's user (build or `podman pull` it as that user before `ank apply`). A systemd agent is rootful, a user-started agent is rootless, and the two stores don't see each other's images:
  ```bash
  sudo podman images | grep my-app     # rootful agent
  podman images | grep my-app          # rootless agent
  ```

**Two workloads cannot talk** ([[ankaios-howto]])
- Ankaios provides no networking. Use `commandOptions: ["--net=host"]` on both and talk over `localhost`. Across nodes, use host IP + `-p`. Container-network names don't work between rootful and rootless.
- CAN/USB/serial needs `--privileged` / `--device`. For iceoryx2, see the container block above.

## openDuT

**`403` on `/api/groups`** ([[opendut-quickstart]])
- Keycloak was re-provisioned after NetBird. Fix: `cargo theo testenv destroy`, then start again.

**NetBird session lost / peers cannot reach each other** ([[opendut-howto]], [[opendut-quickstart]])
Troubleshooting order:
```sh
ip link | grep -E 'wt0|br-opendut|gre-|br-vcan-opendut'
/opt/opendut/edgar/netbird/netbird status --detail
journalctl -u opendut-edgar -n 100
```
Then redeploy the cluster, and if that doesn't help, re-run EDGAR setup. L2 test: `ip address add 192.168.123.101/24 dev br-opendut` on one peer, `.102` on the other, then ping. Check wiring and the ECU before you blame openDuT.

**`cannelloni: No such file`** ([[opendut-quickstart]])
- Install cannelloni + `can-utils`, then `sudo modprobe vcan; sudo modprobe can_gw max_hops=2`, set `OPENDUT_EDGAR_SERVICE_USER=root`, and re-run `./opendut-edgar setup managed`. No CAN needed? Use `--skip-can`.

## S-CORE

**`rustc 1.85.0 is not supported by the following packages: time@0.3.47 requires rustc 1.88.0`** ([[s-core-quickstart]], [[s-core-howto]])
```bash
rustup toolchain install stable
cargo +stable build --locked --example basic
```
Expect `Finished dev profile ...`. The repo's `rust-toolchain.toml` pins 1.85.0, but the lockfile needs 1.88.

**Bazel toolchain download 404 / first build fails on downloads** ([[hackfest-score-reference-integration]], [[s-core-howto]])
1. Use `bazelisk`, never a distro `bazel`. `.bazelversion` differs per repo (8.3.0-8.7.0).
2. The HackFest fork's toolchain URL (`opajonk/eb_corbos_toolkit/.../test-tag/fastdev-sdk-...tar.gz`) returns 404. Replace it with the one from upstream branch `hackfest-raspi-demo`, or start from upstream `gateway_cda_int` ([[hackfest-score-inc-diagnostics]]).
3. Venue Wi-Fi and GitHub rate limits break Ferrocene/GCC/SDK fetches, so pre-fetch on a good link. A different `--output_base` per platform means a cold build each time.
4. linux-sandbox in containers needs `--privileged` or userns (Ubuntu 23.10+ AppArmor).

## SDV Blueprints

**Submodule empty / zenoh-kuksa-provider build fails** ([[sdv-blueprints-quickstart]])
```sh
ls components/kuksa-incubation | head      # empty = the problem
git submodule update --init --depth 1      # service-to-signal
git submodule update --init --recursive    # e2e-vehicle-signals (external/fleet-management)
```

**Port 55555 (or 3000/8080/8081) already in use** ([[sdv-blueprints-quickstart]], [[vss-kuksa-reference]])
```sh
ss -ltnp | grep -E ':(55555|55556|3000|8080|8081|8082|8086)\b'
docker ps --format '{{.Names}}\t{{.Ports}}'
```
Stop the other databroker or stack (often a leftover from the KUKSA quickstart) or remap the host port. e2e-vehicle-signals publishes the broker on host `localhost:55555` (`databroker:55556` inside the network). On macOS 55555 often can't be bound, so use `-p 55556:55555`.

## AutoSD

**Image build fails with permissions / container won't start in the image** ([[autosd-howto]], [[autosd-quickstart]])
- osbuild needs root: `sudo ./auto-image-builder.sh ...`, then `sudo chown $USER *.qcow2`.
- SELinux is enforcing: `ausearch -m avc -ts recent`, `audit2allow`. Volumes need `:z`/`:Z`. For a demo, `image.selinux_mode: permissive`.
- Config in `/etc` vanished after reboot: `/etc` is transient. Put it in the manifest or a quadlet.

## Generic first five minutes

1. **Versions** - print them, don't trust the README ([[hackathon-patterns]]):
   ```sh
   rustc --version; cargo tree -i up-rust 2>/dev/null | head -3
   docker images | grep -E 'kuksa|zenoh|opensovd|ankaios'
   ank --version 2>/dev/null; podman --version 2>/dev/null; pip list 2>/dev/null | grep -Ei 'kuksa|iceoryx2|zenoh'
   ```
   Same-version rules: iceoryx2 everywhere, up-rust/up-transport-zenoh on the same minor, zenohd and plugins exact, Ankaios server/agent/CLI on the same version, KUKSA API v2 on both ends.
2. **Ports** - `ss -ltnp` for 55555/55556 (KUKSA), 7447 (Zenoh), 25551 (Ankaios), 7690/20002/8181 (OpenSOVD), 13400 (DoIP).
3. **Network mode** - same host or Wi-Fi? Docker bridge or `--net=host`? Multicast discovery may fail on Wi-Fi (unverified); the default Docker bridge passed it on one host (corrected 2026-10-03, see [[zenoh-overview]]). Explicit endpoints remove the doubt ([[zenoh-overview]]). Look for hard-coded IPs in manifests and firmware ([[hackathon-patterns]]).
4. **Logs** - `docker logs <ctr>`, `ank logs <wl>`, `RUST_LOG=info`, `IOX2_LOG_LEVEL=Trace`, `journalctl -u opendut-edgar`.
5. **Restart order** - provider/broker first (databroker, zenohd router, ECU sim), then consumers. Subscribers start before publishers. Ankaios restarts ignore dependencies. Clean stale state (iceoryx2 shm, old containers via `docker ps -a`) before restarting.
6. Run the provided demo unchanged first. If it isn't green by about minute 45, ask a coach ([[hackathon-patterns]]).

## Collect this before asking a coach for help

- [ ] One-line goal and which component boundary fails (A -> B).
- [ ] OS / distro / WSL / macOS, arch, whether sudo, Docker or podman (rootful or rootless) are available.
- [ ] Exact versions (output of step 1 above), plus commit hashes of cloned repos (`git rev-parse --short HEAD`, `git submodule status`).
- [ ] The exact command that was run and the **full** error text (not a screenshot of the last line).
- [ ] Relevant logs from both ends (broker/router/CDA and client), with timestamps.
- [ ] Network layout: same host / containers / Wi-Fi, IPs, ports, `--net=host` or not.
- [ ] What was already tried from this checklist, and what changed since it last worked.
- [ ] Manifests and config in use (Ankaios YAML, `iceoryx2.toml`, Zenoh `json5`, CDA toml, Cargo.toml + Cargo.lock).

Post it in Slack `#ask-a-hackcoach` ([[chapter4-overview]]).
