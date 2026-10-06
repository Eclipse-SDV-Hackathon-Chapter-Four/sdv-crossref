---
title: Environment setup matrix and pre-flight list
type: playbook
component: none
tags: [setup, environment, preflight]
status: reviewed
sources:
  - repos/fleet-management/fms-blueprint-compose.yaml
last-verified: 2026-10-03
related:
  - "[[hackathon-patterns]]"
  - "[[chapter4-overview]]"
  - "[[iceoryx2-quickstart]]"
  - "[[vss-kuksa-quickstart]]"
  - "[[uprotocol-quickstart]]"
  - "[[opensovd-quickstart]]"
  - "[[openbsw-quickstart]]"
  - "[[ankaios-quickstart]]"
  - "[[autosd-quickstart]]"
  - "[[opendut-quickstart]]"
  - "[[s-core-quickstart]]"
  - "[[sdv-blueprints-quickstart]]"
---

# Environment setup matrix and pre-flight list

Setting up the environment ate hours 1-4 in Chapter 3. The causes were Ubuntu 22.04 vs 24.04, WSL, AppArmor, submodules and ARM toolchains ([[chapter3-retrospective]], [[hackathon-patterns]]). This page lists what each component needs and what to download while you still have good Wi-Fi.

Reference host for "verified": x86_64 Linux 7.0 with 32 cores, Docker, rustc/cargo stable 1.98.1, Python 3.14, **no sudo and no podman**. Build times on a normal laptop will be several times longer (inference).

Organisers: you bring your own laptop ("standard configuration"). Nothing has been published about boards, ECUs, openDuT testbench hardware, cloud credentials, Wi-Fi or challenge repos. On 2026-10-03 the Chapter 4 GitHub org's public page showed only its `.github` profile repo; starter repos may appear during the event, so check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four. Expect details on Day 1, and ask the organisers if they are missing ([[chapter4-overview]]).

## 1. Matrix

Legend: Y = yes, N = no, opt = only for an optional part. "Verified" = run on the reference host on 2026-10-03.

| Component | OS | Docker | podman | sudo/root | Hardware | Internet at runtime | Disk/RAM | Time to first run | Verified 2026-10-03 |
|---|---|---|---|---|---|---|---|---|---|
| iceoryx2 ([[iceoryx2-quickstart]]) | Linux x86_64/aarch64; macOS/Windows/FreeBSD tier 2 | N | N | opt (C++ deps script; containers sharing `/dev/shm` need the same UID) | N | N | ~3 GB `target/` | Rust 19.4 s, C++ 54.7 s (warm) | Y |
| uProtocol, Rust + Zenoh ([[uprotocol-quickstart]]) | Linux | N | N | N | N | crates.io on first build only | not stated | `cargo build --examples` 1m32s | Y (Zenoh paths; MQTT5/SOME-IP/uStreamer not run) |
| Zenoh, Python ([[zenoh-overview]]) | Linux | N | N | N | N | N (multicast scouting on the LAN) | not stated | seconds | Y (inline; `zenohd` not run) |
| VSS/KUKSA ([[vss-kuksa-quickstart]]) | Linux (Docker or Podman); macOS port caveat | Y | alt | N | N | ghcr.io pull only | not stated | A ~5 min, B ~10 min | Y (databroker 0.7.1) |
| OpenSOVD ([[opensovd-quickstart]]) | Linux | Y | N | N (ECU sim container is `--privileged --cap-add NET_ADMIN`) | N | N after build | CDA binary ~37 MB; RAM not stated | A ~2 min, B ~10 min (CDA build 1m41s) | Y |
| OpenBSW POSIX ([[openbsw-quickstart]]) | Linux (gcc >= 11, cmake >= 3.28) | opt | N | opt (vcan0/tap0) | opt (S32K148EVB) | N | not stated | 11-20 s build on 32 cores | Y (build + run; vcan/tap not run) |
| S-CORE Path A, Cargo ([[s-core-quickstart]]) | Linux x86_64 | N | N | N | N | crates on first build | `target/` ~670 MB | ~2 min (build 22.4 s) | partly (A only) |
| S-CORE Path B/C, Bazel ([[s-core-quickstart]]) | Linux x86_64; C needs `/dev/kvm` | Y (C: docker-in-docker) | N | Y (apt packages) | opt (RPi + EB corbos; QNX needs a licence) | Y on first build (toolchain downloads) | several GB | tens of minutes cold (estimate); ~6 min warm on a 4-core Codespace; measured 2026-10-03 Path B: 130 s with a partly warm cache (12 jobs, 8 GB cap), +1 GB in `~/.cache/bazel`, +2.5 GB in `build/`, peak ~1 GB RAM used | N |
| autowrx sdv-runtime ([[autowrx-overview]]) | Docker amd64/arm64 | Y | N | N | N | **Y** (kit.digitalauto.tech) | not stated | one `docker run` | Y (inline) |
| SDV Blueprints fleet-management ([[sdv-blueprints-quickstart]]) | Linux, Docker + compose v2 | Y | N | N | N | pull only | ~4 GB free RAM | ~5 min (per doc) | N (static checks only) |
| SDV Blueprints software-orchestration | Linux | Y (`--privileged`, Podman inside) | inside | N | N | pull only | not stated | ~10 min (per doc) | N |
| Ankaios ([[ankaios-quickstart]]) | Linux x86_64/arm64, Ubuntu 22.04/24.04/26.04 | N | **Y** (>= 3.4.2; >= 4.3.1 for podman-kube) | **Y** (install, systemd) | N | image pulls | 256 MB RAM minimum | ~15 min (per doc) | N |
| AutoSD ([[autosd-quickstart]]) | Linux; host arch only, no cross-build | alt | **Y** (privileged) | **Y** (osbuild) | N (KVM helps) | Y during build (CentOS/COPR/quay) | ~15 GB | boot prebuilt < 15 min; build ~10 min (per doc) | N |
| openDuT ([[opendut-quickstart]]) | Linux with kernel modules; macOS/Windows only via a VM | Y (~12 containers) | N | **Y** (`/etc/hosts`, `modprobe vcan`/`can_gw`) | opt (Pi for EDGAR) | pull/build only | ~8 GB RAM | ~1 h setup budget | N |
| openDuT localenv measured 2026-10-03 ([[opendut-quickstart]]) | same host | 17 containers, no Rust build | N | N (prereqs pre-applied) | N | ~8 GB images, 1.3 TB disk free untouched | ~1.6 GB running (13 GB headroom was ample) | ~10.5 min to all healthy (first pull); EDGAR-in-Docker did not join | N |
| Velocitas ([[velocitas-overview]]) | Linux devcontainer | Y (docker-in-docker, `--privileged`) | N | N (needs privileged Docker) | N | Y (GitHub downloads) | ~10 GB | minutes for the first devcontainer build | N |

## 2. Laptop-only, no-root path

These run on a plain Ubuntu laptop with Docker, rustup (stable >= 1.89) and Python >= 3.11. You need no sudo, no podman and no hardware. They are ordered by value to a Chapter 4 team. The ranking is a judgement call (inference).

1. **VSS/KUKSA databroker 0.7.1.** It is the signal spine for both challenges and only needs Docker ([[vss-kuksa-quickstart]]).
2. **OpenSOVD.** Recipe A (gateway mock) runs on Docker alone. Recipe B (CDA + ECU sim) shows real faults, locks and operations. This is the diagnostics core for Doctor Whodunit ([[opensovd-quickstart]], [[chapter4-challenge-doctor-whodunit]]).
3. **uProtocol over Zenoh (Rust).** Pub/sub with no broker. Needs crates.io once ([[uprotocol-quickstart]]).
4. **Zenoh Python.** `pip install eclipse-zenoh` and you are running in seconds ([[zenoh-overview]]).
5. **iceoryx2 (Rust).** Zero-copy IPC. Python needs the matching wheel 0.10.0 ([[iceoryx2-quickstart]]).
6. **OpenBSW POSIX ECU.** Build and run work without root. CAN and DoIP need vcan/tap and therefore root ([[openbsw-quickstart]]).
7. **S-CORE Path A.** Orchestrator + iceoryx2 via `cargo +stable` ([[s-core-quickstart]]).
8. **autowrx sdv-runtime.** Docker, but needs live internet ([[autowrx-overview]]).
9. **SDV Blueprints fleet-management.** Docker compose. Not run here ([[sdv-blueprints-quickstart]]).

Not on this path: Ankaios, AutoSD builds, openDuT, S-CORE Bazel images, Velocitas devcontainer and anything that touches CAN or TAP. If your team needs these, pick one laptop with root (or a Linux VM where they have root) on Day 1 (inference from [[hackathon-patterns]] "hardware sharing"). On that root laptop, `./test_setup.sh --check` lists the missing host prerequisites (vcan0 with mtu 16, the `can_gw` module and the eight openDuT `/etc/hosts` names) and `./test_setup.sh --apply` adds them after a sudo prompt.

## 3. Pre-flight pull list (run the night before)

Every tag below is copied from a note. Where the note's own tag is stale, the replacement is marked.

```bash
# --- VSS / KUKSA (verified tags) ---
docker pull ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1
docker pull ghcr.io/eclipse-kuksa/kuksa-databroker-cli:0.7.1
docker pull ghcr.io/eclipse-kuksa/kuksa-python-sdk/kuksa-client:0.6.0
python3 -m venv ~/sdv-venv && . ~/sdv-venv/bin/activate
pip install kuksa-client==0.6.0 vss-tools==6.1 eclipse-zenoh iceoryx2==0.10.0
git clone --depth 1 --branch v6.1 https://github.com/COVESA/vehicle_signal_specification vss61

# --- OpenSOVD ---
docker pull ghcr.io/eclipse-opensovd/opensovd-gateway:latest
git clone --depth 1 https://github.com/eclipse-opensovd/opensovd-cda
(cd opensovd-cda && cargo fetch --locked)          # CDA has no published image/binary
# ECU sim image builds with Gradle inside Docker (~2-3 min): build it tonight too
(cd opensovd-cda && docker build -f testcontainer/ecu-sim/docker/Dockerfile -t opensovd-ecu-sim:local testcontainer/ecu-sim)

# --- uProtocol / Zenoh / iceoryx2 / S-CORE (Rust) ---
rustup toolchain install stable                      # 1.98.1 used for every verified build
git clone --depth 1 https://github.com/eclipse-uprotocol/up-transport-zenoh-rust
(cd up-transport-zenoh-rust && cargo build --examples)
git clone --depth 1 --branch v0.10.0 https://github.com/eclipse-iceoryx/iceoryx2
(cd iceoryx2 && cargo fetch)
git clone --depth 1 https://github.com/eclipse-score/orchestrator.git
(cd orchestrator && cargo +stable fetch --locked)

# --- Fleet-management blueprint (images from repos/fleet-management compose files) ---
docker pull quay.io/eclipse-kuksa/kuksa-databroker:0.6.0
docker pull quay.io/eclipse-kuksa/csv-provider:0.4.5
docker pull eclipse/zenoh:1.1.0
docker pull docker.io/library/influxdb:2.7
docker pull docker.io/grafana/grafana:9.5.14
git clone --depth 1 https://github.com/eclipse-sdv-blueprints/fleet-management
(cd fleet-management && docker compose -f fms-blueprint-compose.yaml -f fms-blueprint-compose-zenoh.yaml pull)   # fms-{forwarder,consumer,server}:main
git clone --recurse-submodules --depth 1 https://github.com/eclipse-sdv-blueprints/service-to-signal

# --- OpenBSW (toolchain image: arm-none-eabi gcc 14.3, LLVM-ET 19.1.1, bazelisk) ---
git clone --depth 1 https://github.com/eclipse-openbsw/openbsw
(cd openbsw && DOCKER_UID=$(id -u) DOCKER_GID=$(id -g) docker compose build development)

# --- Ankaios v1.0.4 (needs sudo + podman) ---
sudo apt-get install -y podman
curl -sfL https://github.com/eclipse-ankaios/ankaios/releases/download/v1.0.4/install.sh | bash -s -- -v v1.0.4
sudo podman pull ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1   # replaces the stale tutorial tag ghcr.io/eclipse/kuksa.val/databroker:0.4.1
sudo podman pull ghcr.io/eclipse-ankaios/speed-provider:0.1.3
sudo podman pull ghcr.io/eclipse-ankaios/speed-consumer:0.1.2

# --- AutoSD (needs podman + qemu; ~15 GB) ---
sudo apt install -y git podman qemu-system-x86
curl -o air 'https://gitlab.com/CentOS/automotive/src/automotive-image-builder/-/raw/main/bin/air' && chmod +x air
sudo podman pull quay.io/centos-sig-automotive/automotive-image-builder:latest
podman pull ghcr.io/eclipse-autosd/eclipse-autosd-bootc-qemu:latest          # rpi4 variant: eclipse-autosd-bootc-rpi4:latest
# plus a prebuilt qcow2 from https://github.com/eclipse-autosd/eclipse-autosd/releases (asset names unverified)
git clone https://gitlab.com/CentOS/automotive/sample-images.git

# --- openDuT (only if your team commits to it; ~12 containers, builds locally) ---
git clone --depth 1 https://github.com/eclipse-opendut/opendut.git
```

Notes on the list:
- **Root vs rootless podman.** Images pulled with `sudo podman` are invisible to rootless podman, and the other way round. The systemd-installed Ankaios agent is rootful, so pull with sudo ([[ankaios-howto]]).
- **Ankaios 1.0.4 has a different config format from 0.x.** Pin server, agent, CLI and SDK to the same version. The install script overwrote an existing config in the past (#781) ([[ankaios-howto]]).
- **AutoSD.** `container_images` in a manifest are pulled at build time. Pass `--build-dir` so RPMs are cached for the next run ([[autosd-howto]]).
- **S-CORE Bazel.** A `./score_starter -r linux-x86_64` build the night before is what warms the toolchain cache. Bazel fetches Ferrocene, GCC 12.2 and the EB SDK, and that is what fails on venue Wi-Fi ([[s-core-howto]]). Install bazelisk; do not pin one Bazel version.
- **Blueprint images use `:main` tags**, so their behaviour drifts. Pull once and keep them ([[sdv-blueprints-quickstart]]).
- The `iceoryx2==0.10.0` wheel only works with Rust/C++ code from tag `v0.10.0`. `main` (0.10.999) gives `VersionMismatch` ([[iceoryx2-quickstart]]).

## 4. Version pin sheet

This is the known-good combination on 2026-10-03.

| Item | Pin | Why |
|---|---|---|
| Rust | stable 1.98.1 (`rustup toolchain install stable`; use `cargo +stable` in S-CORE orchestrator) | every verified build; orchestrator pins 1.85.0 but needs 1.88; up-rust MSRV 1.88; iceoryx2 needs 1.89 |
| up-rust | `0.9.0` | crates.io current; mixing 0.7/0.8 with 0.9 gives duplicate `UMessage` types ([[uprotocol-howto]]) |
| up-transport-zenoh | `0.9.1` | needs zenoh ^1.9.0 ([[uprotocol-reference]]) |
| zenoh (Rust, Python, zenohd) | 1.10.x (1.10.1 verified for Python) | keep router, bridges and clients on the same minor; plugins must match zenohd exactly ([[zenoh-overview]]) |
| iceoryx2 (Rust/C++/Python) | `0.10.0` everywhere | same-version rule, otherwise `VersionMismatch` ([[iceoryx2-howto]]) |
| KUKSA databroker | `ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1`, API `kuksa.val.v2` | 0.7.0 removed `sdv.databroker.v1` ([[vss-kuksa-reference]]) |
| kuksa-client (Python) | `0.6.0` | verified with 0.7.1 ([[vss-kuksa-quickstart]]) |
| VSS / vss-tools | 6.1 / 6.1 | signal names changed in 6.0 ([[vss-kuksa-reference]]) |
| Ankaios | v1.0.4 (server = agent = CLI = SDK), manifest `apiVersion: v1` | ([[ankaios-overview]]) |
| Podman | >= 4.3.1 if using podman-kube | ([[ankaios-howto]]) |
| CDA | pin a commit, not `main` | ([[hackfest-score-inc-diagnostics]]) |

Cargo.toml fragment, assembled from the pins above. The combination is inference: the crates were verified separately, not built together in one project.

```toml
[dependencies]
up-rust = "=0.9.0"
up-transport-zenoh = "=0.9.1"
zenoh = "1.10"          # must satisfy up-transport-zenoh's ^1.9
iceoryx2 = "=0.10.0"
```

Commit `Cargo.lock`. The Chapter 3 trap: Cargo silently upgraded up-rust 0.7.0 to 0.7.1 and broke the build ([[chapter3-retrospective]]). In Docker Compose, never use `latest` for the databroker; write `0.7.1`. Do not mix old blueprint images (databroker 0.6.0, `kuksa.val.v1`, Zenoh 1.1.0) with the stack above unless that blueprint is run as-is ([[sdv-blueprints-overview]]).

## 5. Venue network pitfalls

| Pitfall | Symptom | Mitigation |
|---|---|---|
| Multicast blocked on Wi-Fi and VLANs (unverified; the default Docker bridge passed it on one host (corrected 2026-10-03, see [[zenoh-overview]])) | Zenoh/uProtocol peers never find each other; "nothing received" | Run a router: `-m router -l tcp/0.0.0.0:7447`; clients use `-m client -e tcp/<ip>:7447`; containers use host network ([[zenoh-overview]], [[uprotocol-quickstart]]) |
| Shared simulator/broker IP | Manifests and firmware have an IP or SSID compiled in; it breaks when the laptop moves | Put IPs in env/config; check ping and port from the team laptop first ([[hackathon-patterns]]) |
| DoIP UDP broadcast (13400) blocked | CDA returns 503 `communication-not-ready` | `--tester-address` must be an IP on the ECU-facing interface; keep the sim on a local Docker bridge ([[opensovd-quickstart]]) |
| GitHub rate limits on shared NAT | Velocitas devcontainer and S-CORE Bazel fetches fail | Set `GITHUB_API_TOKEN` for Velocitas ([[velocitas-overview]]); pre-fetch the Bazel cache ([[s-core-howto]]) |
| Registry access (ghcr.io, quay.io, docker.io, registry.gitlab.com, COPR) | Slow first pulls; AutoSD builds stall | Use the pre-flight list above; `podman pull` ahead of time; behind a VPN pass buildah `--dns=<ip>` ([[ankaios-howto]], [[autosd-howto]]) |
| Shared hosted services | autowrx runtime names clash on kit.digitalauto.tech | Set a unique `RUNTIME_PREFIX` per team ([[autowrx-overview]]) |
| Open ports with no auth | Anyone on the Wi-Fi can reach Ankaios 25551 (root workloads), Zenoh 7447 or databroker 55555 | Bind to localhost or use the team's own network where you can (inference from [[ankaios-howto]], [[zenoh-overview]], [[vss-kuksa-reference]]) |
| Ankaios workloads cannot reach each other | No networking between workloads | `commandOptions: ["--net=host"]` and localhost ([[ankaios-howto]]) |

## 6. WSL, macOS and Apple-silicon caveats

- **WSL.** The stock kernel has no SocketCAN, so OpenBSW vcan and openDuT CAN need a custom kernel ([[openbsw-howto]]). WSL was one of the Chapter 3 time sinks ([[hackathon-patterns]]).
- **macOS.** Often cannot bind port 55555, so use `-p 55556:55555` for the databroker ([[vss-kuksa-reference]]). iceoryx2 is tier 2 on macOS/Windows ([[iceoryx2-overview]]). openDuT needs a Linux VM with root and kernel modules ([[opendut-overview]]).
- **Apple silicon.** AutoSD has no cross-build, so you get aarch64 images and VMs only, and container images must be multi-arch ([[autosd-howto]]). The Velocitas devcontainer fails under emulation ([[velocitas-overview]]). The autowrx sdv-runtime ships arm64 ([[autowrx-overview]]). Ankaios supports arm64 ([[ankaios-quickstart]]).
- **Ubuntu 24.04 and newer.** AppArmor restricts user namespaces. Expect podman/Ankaios container start failures; the exact AppArmor step is unverified ([[ankaios-quickstart]]). This also breaks the Bazel linux-sandbox inside containers ([[s-core-howto]]).
- **Rootless Docker/podman.** Breaks the Velocitas devcontainer and the AutoSD privileged builder ([[velocitas-overview]], [[autosd-quickstart]]).
- **None of the above was tested on WSL or macOS here.** Every verified run was on x86_64 Linux.
