---
title: Top 20 pitfalls, ranked by how much hackathon time they cost
type: playbook
component: none
tags: [pitfalls, chapter4]
status: reviewed
sources:
  - "[[hackathon-patterns]] (time sinks of Chapters 1–3)"
  - "[[chapter3-retrospective]]"
last-verified: 2026-10-03
related:
  - "[[debugging-checklists]]"
  - "[[env-setup-matrix]]"
  - "[[faq]]"
  - "[[first-two-hours-doctor-whodunit]]"
  - "[[first-two-hours-hack-to-the-future]]"
---

# Top 20 pitfalls, ranked

Ranking = (how many teams will hit it) × (hours lost if nobody warns you). Symptom-driven fixes are in [[debugging-checklists]].
Items marked **verified** were reproduced on 2026-10-03.

| # | Pitfall | Cost | What to do, in one sentence | Source |
|---|---|---|---|---|
| 1 | **KUKSA API split.** Three gRPC APIs; `databroker-cli` speaks only v1; v1 target sets return OK but never reach a v2 provider; 0.7.0 removed `sdv.databroker.v1`. **verified** | half a day of "it says OK but nothing happens" | "Decide kuksa.val.v2 everywhere on Day 1 and use the Python client, not the CLI, for actuation." | [[vss-kuksa-reference]] |
| 2 | **uProtocol version matrix.** Copying Chapter 3 or blueprint `Cargo.toml` (up-rust 0.5–0.8) against crates.io 0.9 gives duplicate `UMessage` types; 0.7.0 vs 0.7.1 silently broke the Zenoh transport in 2025. **verified** | 2–4 h of compile errors | "Pin `up-rust = "0.9.0"`, `up-transport-zenoh = "0.9.1"`, zenoh 1.10, commit Cargo.lock." | [[uprotocol-howto]] [[chapter3-retrospective]] |
| 3 | **Zenoh scouting on venue Wi-Fi.** Multicast discovery may be blocked by client isolation or VLANs; peers never find each other. The default Docker bridge passed scouting on one host (corrected 2026-10-03, see [[zenoh-overview]]). | hours of "subscriber gets nothing" | "Run one `zenohd` router and connect with `-e tcp/<ip>:7447`; use host networking in containers" - it removes the dependency on the venue network. | [[zenoh-overview]] [[uprotocol-quickstart]] |
| 4 | **Environment setup eats hours 1–4** (OS, toolchains, submodules, ARM toolchains, AppArmor on Ubuntu 24.04). Every previous chapter reports it. | up to half of Day 1 | "Run the provided demo unchanged first; if it is not green by minute 45, ask a coach." | [[hackathon-patterns]] [[env-setup-matrix]] |
| 5 | **Ankaios needs podman** (not Docker), manifests changed 0.6 → 1.x (`apiVersion v1`, `controlInterfaceAccess`, `restartPolicy`), no networking between workloads, images must exist locally before `ank apply`. | 2–3 h | "Install podman first, use 1.x syntax, `--net=host`, pull images before apply." | [[ankaios-howto]] |
| 6 | **OpenSOVD has two codebases with different paths.** core = `/sovd/v1` (no `/faults`, returns 404); CDA = `/vehicle/v15` (href says `/Vehicle/v15`); clearing faults needs a lock (409); the CDA answers 401 without a Bearer token from `POST /vehicle/v15/authorize` (any client_id/secret; R, [[hackfest-openbsw-playground]]). **verified** | 2 h of 404 confusion | "`/faults` lives only in the CDA; core needs a FaultProvider you write (gap A1)." | [[opensovd-quickstart]] |
| 7 | **iceoryx2 same-version and same-type rule.** `VersionMismatch` across languages (PyPI wheel vs git main), `IncompatibleTypes` between Rust and C++ examples; stale `/dev/shm/iox2_*` after crashes. **verified** | 1–2 h | "One iceoryx2 version everywhere, shared type crate, and `rm -rf /dev/shm/iox2_* /tmp/iceoryx2` when all processes are stopped." | [[iceoryx2-howto]] |
| 8 | **Each transport bridge costs half a day** (MQTT ↔ Zenoh ↔ uProtocol ↔ VSS). Teams plan three and finish one. | a day | "Pick one spine (KUKSA + uProtocol/Zenoh) and add bridges only where the rubric rewards them." | [[hackathon-patterns]] |
| 9 | **openDuT self-hosting** is ~12 containers, Keycloak, a CA, `/etc/hosts` edits and root. NetBird sessions drop. | a day, for +0.10 | "Use the organiser's CARL and run only EDGAR; if there is no CARL, skip openDuT." | [[opendut-quickstart]] |
| 10 | **AutoSD image building** needs root or privileged podman, ~15 GB, registry and COPR access, no cross-build; `/etc` is transient; images are sealed. | half a day, for +0.10 | "Boot the prebuilt `eclipse-autosd-bootc-qemu` image; never build on venue Wi-Fi." | [[autosd-howto]] |
| 11 | **S-CORE beyond the Cargo demo is Bazel** with multi-GB toolchains and per-repo Bazel versions; the orchestrator pins rustc 1.85 but needs 1.88 (`cargo +stable`). HackFest branches are broken (404 toolchain URL). **verified for Path A** | a day | "Run the 2-minute Cargo demo for the story; use upstream `inc_diagnostics@gateway_cda_int` if you must build with Bazel." | [[s-core-quickstart]] [[hackfest-esslingen-2026]] |
| 12 | **Signal names changed in VSS 6.0** (`IsOccupied` → `OccupancyStatus`, `celsius` → `Celsius`, `Vehicle.OBD.*` gone); the databroker image loads VSS 6.0 while 6.1 is current. | 1 h of "No entries found" | "Check the `Populating metadata from file` log line and export your own JSON from VSS 6.1." | [[vss-kuksa-reference]] |
| 13 | **OpenBSW needs sudo for vcan and TAP**; the ECU stops when backgrounded (SIGTTOU); upstream DoIP NACKs the CDA's ACK types; the demo overlay only works with submodule `07b7551`. **verified build** | 1–2 h | "Use `playbook/fixes/openbsw-sovd-demo.override.yaml`; the demo compose is broken in five ways as written (verified)." | [[known-broken-recipes]] [[openbsw-howto]] |
| 14 | **Blueprint shallow clones leave submodules empty** (service-to-signal `kuksa-incubation`, e2e `external/fleet-management`); images are `:main` tags that drift; fleet-management has open data bugs #71/#72/#74. | 1 h | "Init submodules, use the bridge-network overrides in `playbook/fixes/`, pin `kuksa-rust-sdk = \"=0.2.0\"`, and the rFMS path is `vehiclepositions`." (all three blueprints fail on stock Docker, verified) | [[known-broken-recipes]] [[sdv-blueprints-quickstart]] |
| 15 | **GitHub API rate limits and registry pulls on shared Wi-Fi** (hit repeatedly while building this repo). | unpredictable | "Pre-pull images and clone the night before; see the pre-flight list." | [[env-setup-matrix]] |
| 16 | **CLI needs a TTY**: `databroker-cli` without `-it` gives `Not a tty`; it prints `[publish] OK` even on a 400 rejection. **verified** | 30 min | "Use `-it`, read the error line under the OK." | [[vss-kuksa-quickstart]] |
| 17 | **Sensors default to `continuous`; with `onchange` a frozen sensor is silent.** A watchdog that waits for changes never fires. | breaks the Guardian story | "Watchdogs use timestamps, not value changes." | [[vss-kuksa-howto]] |
| 18 | **uProtocol publish is at-most-once and `send()` is not a receipt**; same authority on two hosts is never bridged by uStreamer; authorities are lowercase; the streamer is itself a Zenoh router on 7447, so a separate `zenohd` there fails with "Address already in use" (R, 2026-10-03). | 1 h | "Tolerate N missed heartbeats; one authority per host." | [[uprotocol-howto]] |
| 19 | **Dormant projects look alive**: Velocitas (maintenance, pinned to KUKSA 0.5.0, 10 GB devcontainer), Kanto (frozen 2024), Chariott/Ibeji (dormant), SommR (archived, empty), autowrx runtime (databroker 0.4.4, needs hosted SaaS). | a day if chosen | "Hold ring; mention as 'why not' in the pitch." | [[capability-map]] |
| 20 | **Nothing about the challenges was published as of 2026-10-03** (Guardian code, hardware, openDuT testbench, display interface, S-CORE's role). Teams wait for it instead of building the spine. | Day 1 | "Build L0 from the reference architecture; drop the official Guardian in when it appears." | [[chapter4-challenge-doctor-whodunit]] [[reference-architecture-doctor-whodunit]] |
| 21 | **CDA built without the `auth` feature decodes JWTs with `insecure_decode`** (no signature check), and opensovd-core's JwtAuthenticator sets `validate_aud=false`, so a token for one vehicle is accepted by any. | a failed security story | "Build with `auth`; check `aud` yourself until core does." | [[verify-offline-against-a-pinned-root]] [[opensovd-quickstart]] |
| 22 | **uProtocol authorities must be lowercase and one per host**; the sdv_lab config uses mixed case (`EGOVehicle`, `AAOS`) and fleet-management shares one authority across all trucks. | 1 h | "Lowercase the VIN and use it as the authority." | [[authority-is-the-routing-unit]] [[uprotocol-howto]] |
| 23 | **`--ipc=host` is the wrong lever for iceoryx2 in containers**: the IPC namespace does not cover POSIX shared memory. Bind-mount `/dev/shm` and `/tmp/iceoryx2` and run with the same UID. | 1 h | "Two directories, one UID." | [[share-two-directories-and-one-uid-isolate-by-prefix]] [[ankaios-howto]] |
| 24 | **iceoryx2's type check is name + size + alignment only**: reordered same-size fields connect silently, and a manual `IOX2_TYPE_NAME` disables the only check. | silent wrong data | "Generate payload types from one source; hash the layout." | [[a-type-name-is-a-claim-a-layout-hash-is-a-proof]] [[iceoryx2-overview]] |

Also seen on 2026-10-03 (R):
- automotive-image-builder `air` starts one vCPU per host core and needs `--ovmf-dir` where it cannot find EFI firmware ([[autosd-quickstart]]).
- `/tmp` as tmpfs is RAM: a 3.5 GB qcow2 or a build dir there eats memory; use a disk path ([[autosd-quickstart]]).
- Symphony's Docker image exits unless run with `-e CONFIG=/symphony-api-no-k8s.json` ([[symphony-docker-no-k8s]]).
- OpenBSW UDS over CAN is on 0x7E0/0x7E8, not the documented 0x02A/0x0F0 ([[openbsw-quickstart]]).
- KUKSA can-provider takes the databroker only as the positional `grpc://host:port` URL; `ip`/`port` in its ini are ignored ([[openbsw-howto]]).
- EDGAR-in-Docker ships a stale image tag (`0.10.0-alpha` vs CARL 0.10.2), needs `OPENDUT_BACKEND_IP`, and its netbird-client dials the public management URL `api.netbird.io`, so the peer never goes Online ([[opendut-quickstart]], [[opendut-edgar-docker-notes]]).

## Three habits that prevent most of the above

1. **Pin sheet on the wall.** Rust stable 1.98, up-rust 0.9.0, up-transport-zenoh 0.9.1, zenoh 1.10.x, iceoryx2 0.10.0, databroker 0.7.1, VSS 6.1, Ankaios 1.0.4. ([[env-setup-matrix]])
2. **Green baseline before any idea.** The verified quickstarts run in 2–15 minutes each; if your team has all of them green by lunch on Day 1, you are ahead of most of Chapter 3.
3. **One router, one authority per host, one API version.** Most "nothing arrives" reports are one of these three.
