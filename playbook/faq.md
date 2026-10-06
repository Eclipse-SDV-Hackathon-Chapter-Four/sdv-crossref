---
title: FAQ - Eclipse SDV Hackathon Chapter 4
type: playbook
component: none
tags: [faq]
status: reviewed
sources:
  - event/chapter4-overview.md
  - event/chapter4-challenge-doctor-whodunit.md
  - event/chapter4-challenge-hack-to-the-future.md
  - event/chapter4-freestyle-track.md
  - event/hackathon-patterns.md
last-verified: 2026-10-03
related:
  - "[[chapter4-overview]]"
  - "[[pitfalls-top20]]"
  - "[[debugging-checklists]]"
  - "[[env-setup-matrix]]"
  - "[[scoring-rubric-cheatsheet]]"
  - "[[first-two-hours-doctor-whodunit]]"
  - "[[first-two-hours-hack-to-the-future]]"
---

# FAQ - Eclipse SDV Hackathon Chapter 4

Questions your team is likely to have at Friedrichshafen (6-8 Oct 2026). Every answer cites the note that backs it. Statements marked "(inference)" are this repo's judgement, not published facts. Snapshot 2026-10-03: on that date the org's public page showed only its `.github` profile repo; starter repos may appear during the event, so check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four ([[chapter4-overview]]).

## Event and scoring

**Q1. What are the hard deadlines?**
Solution Plan is due to coaches on Day 1 (Tue 6 Oct) at 18:00. Code freeze (final repo upload) is Day 3 (Thu 8 Oct) at 08:00, the 8-minute coach interviews follow on Day 3 morning, and the pitch deck upload is due at 11:00. Finalist pitches run 12:00-13:30 as 10 min pitch + 5 min Q&A. The interview window is published two ways (09:00-10:30 vs 09:30-11:00), so confirm your slot on Day 2 ([[chapter4-overview]]).

**Q2. How is scoring split between coaches and jury?**
HackCoaches score 80 % (technical substance, repo-verifiable evidence, the 8-min interview/live demo) and the jury 20 % (finalist pitch only). Scale is 0-5, and "slides alone do not count for technical scoring". Rankings are calculated separately per track ([[chapter4-overview]], [[scoring-rubric-cheatsheet]]).

**Q3. Which criterion matters most in the Innovation track?**
Eclipse SDV Ecosystem Integrability at 27 %, followed by Development Methods (20 %), Problem Solving (13 %), Working Demo (10 %) and Code Does What It Claims (10 %). The jury items (pitch 8 %, community benefit 7 %, contribution focus 5 %) are small by comparison. So the weights reward wiring several projects into one real data path and showing a clean repo far more than a great pitch on a thin demo (inference from the weights) ([[chapter4-overview]], [[scoring-rubric-cheatsheet]]).

**Q4. What counts as "Ecosystem Integrability"?**
The rubric gives a 4 for "multiple projects work together in a coherent flow" and a 5 for a "reusable PR, issue, Blueprint extension or integration". For Doctor Whodunit that means AutoSD + Ankaios + uProtocol + OpenSOVD + openDuT + KUKSA in one flow; for Hack to the Future, uProtocol + openDuT + OpenBSW + AutoSD. Filing an upstream issue or a Blueprint proposal for the gap you hit is the cheapest way from 4 to 5 (inference) ([[chapter4-challenge-doctor-whodunit]], [[chapter4-challenge-hack-to-the-future]], [[gap-register]]).

**Q5. How do we get bonus points cheaply?**
Bonus is +0.10 each for openDuT, AutoSD, ThreadX and Java/Jakarta EE (max +0.40, final capped at 5.00), but only if "meaningfully used in code/config/deployment/test/demo/PR" - a logo does not count. openDuT and AutoSD are already in both challenges, so +0.20 is nearly free if genuinely used. Cheapest paths: run only EDGAR against an organiser-hosted CARL, boot the prebuilt AutoSD bootc QEMU image, and build OpenBSW with the `posix-threadx` preset (20 s build, verified) if ThreadX use is defensible (inference; whether the HackCoaches accept that is unconfirmed, so ask them) ([[chapter4-overview]], [[opendut-overview]], [[autosd-quickstart]], [[openbsw-quickstart]]).

**Q6. Does the bonus apply to the Freestyle track?**
The forms head it "Bonus Layer for All Challenges" but do not say explicitly that it applies to Freestyle. Ask the HackMC on Day 1 ([[chapter4-freestyle-track]]).

**Q7. What goes into the Solution Plan?**
Two parts: "Team at a glance" (name/tagline, roster with GitHub handles, roles, declared challenge, core idea) and "How do you work" (light dev process, QA strategy, communication, decision making). It also feeds Development Methods (20 %), so link the repo, issue board and any upstream issue/PR in it ([[chapter4-overview]], [[chapter4-freestyle-track]]).

**Q8. Can we bring code we wrote before the event?**
All code must be created during the hackathon; anything prepared beforehand must be declared in person to the HackMC on Day 1. Freestyle teams must additionally present prepared code at the end of Day 1. Business ideas may be prepared, assets not ([[chapter4-overview]]).

**Q9. Can we switch tracks or challenges later?**
No. Track is chosen on Day 1 after the challenge presentations and there are no changes after Day 1. Team size is max 5 ([[chapter4-overview]]).

**Q10. Is there starter code, a Guardian implementation, or hardware list?**
Not as of 2026-10-03: the org's public page showed only its `.github` profile repo, and neither the Battery Thermal Guardian code, the Guardian Loop reference, the hardware list nor the openDuT testbench setup is published. Starter repos may appear during the event; check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four ([[chapter4-overview]], [[chapter4-challenge-doctor-whodunit]], [[chapter4-challenge-hack-to-the-future]]).

**Q11. What is S-CORE's role in Doctor Whodunit?**
Unknown. S-CORE is in the project list but not in the scenario text. Plausible roles are its safety/FuSa artefacts or a runtime host for the Guardian; ask the coaches for S-CORE ([[chapter4-challenge-doctor-whodunit]], the official coach list (https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/)).

## Getting a baseline running

**Q12. What can run on a plain laptop without sudo?**
Verified without root on 2026-10-03: KUKSA databroker (Docker), OpenSOVD gateway mock and CDA build (Docker/cargo; the ECU sim container needs `--privileged`), uProtocol over Zenoh (cargo), iceoryx2, S-CORE orchestrator Path A (cargo), OpenBSW POSIX build+run, Zenoh Python, and autowrx sdv-runtime (Docker + internet). Not runnable without root: Ankaios (podman + systemd), AutoSD image builds, openDuT self-hosting, OpenBSW vcan/tap ([[env-setup-matrix]], [[openbsw-quickstart]], [[ankaios-quickstart]]).

**Q13. Our setup is still broken after an hour. What now?**
Run the provided demo unchanged before writing any code, and ask a coach for help if it does not run by minute ~45. Environment setup ate hours 1-4 for many Chapter 3 teams (distros, WSL, AppArmor, submodules, ARM toolchains). Put one teammate on environment from minute 0 while the others ideate ([[hackathon-patterns]], [[chapter3-retrospective]], [[debugging-checklists]]).

**Q14. Docker or podman?**
Most verified quickstarts use Docker (KUKSA, OpenSOVD, Blueprints compose). Ankaios needs podman (>= 3.4.2, podman-kube >= 4.3.1) or containerd, and AutoSD workloads are podman quadlets. A user-started Ankaios agent uses rootless podman with a separate image store from root, so images pulled as one user are invisible to the other ([[env-setup-matrix]], [[ankaios-howto]], [[autosd-howto]]).

**Q15. Why does nothing find anything on the venue Wi-Fi?**
Zenoh multicast scouting may be blocked on Wi-Fi and VLANs (unverified) - expect hackathon Wi-Fi to block it; the default Docker bridge passed it on one host (corrected 2026-10-03, see [[zenoh-overview]]). Use explicit endpoints (`-e tcp/<ip>:7447`) or a router, and host networking in containers. Chapter 3 also lost time to shared-simulator IPs edited into manifests and SSID/broker IPs compiled into firmware ([[zenoh-overview]], [[hackathon-patterns]]).

**Q16. Our first image pull or Bazel build takes forever.**
Pre-pull images (`podman pull` / `docker pull`) before Day 1 or early on Day 1; S-CORE first Bazel builds download multi-GB toolchains and take tens of minutes; AutoSD builds pull from registries and COPR at build time. Use `--build-dir` to cache AutoSD RPMs, and prefer the prebuilt bootc images ([[s-core-howto]], [[autosd-howto]], [[ankaios-howto]]).

## KUKSA/VSS

**Q17. Which KUKSA API version should we use?**
`kuksa.val.v2`, decided on Day 1. Databroker 0.7.0 removed `sdv.databroker.v1`; v1 is deprecated and v2 is the only one developed. Watch for traps: `databroker-cli` speaks only `kuksa.val.v1`, and Python `kuksa-client` 0.6.0 publishes via v2 but gets via v1 and has no v2 Actuate ([[vss-kuksa-reference]], [[vss-kuksa-overview]]).

**Q18. Our actuator provider never sees the target value, but `set` said OK.**
A v1 `set_target_values` / CLI `actuate` returns OK but never reaches a v2 provider (observed). Send actuation via v2 `Actuate` from both sides. Also note the CLI prints `[publish] OK` even for rejected values (e.g. 400 "value out of min/max bounds") ([[vss-kuksa-reference]], [[vss-kuksa-quickstart]]).

**Q19. What is the fastest KUKSA baseline?**
About 5 minutes with Docker, verified with 0.7.1:
`docker run -it --rm --name Server --network kuksa -p 55555:55555 ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1 --insecure` (after `docker network create kuksa`), then the CLI image with `--server Server:55555`. The CLI needs `-it`, otherwise `Not a tty` ([[vss-kuksa-quickstart]]).

**Q20. "No entries found for the provided path" - but the signal exists in the docs.**
The databroker loads VSS 6.0 by default and signal names change between versions (`IsOccupied` -> `OccupancyStatus` in 6.0, `Vehicle.OBD.*` gone). Check the `Populating metadata from file ...` log line to see which tree is loaded. Blueprints, Velocitas and autowrx pin databroker 0.4.4-0.6.0 with older VSS, so copying their paths is a common cause ([[vss-kuksa-reference]], [[pitfalls-top20]]).

**Q21. Which VSS signals fit the two challenges?**
Doctor Whodunit: `Vehicle.Powertrain.TractionBattery.Temperature.{Average,Min,Max,CellTemperature}`, DTC lists and ControlUnit watchdog flags; there is no thermal-runaway signal, so add an overlay. Hack to the Future: `Seat.*.OccupancyStatus`; there is no child-presence branch or IsParked, so derive parking from IsMoving / parking brake / gear, or use the verified `ChildPresence.IsDetected` overlay recipe ([[vss-kuksa-howto]], [[vss-kuksa-quickstart]]).

**Q22. How does the Guardian detect a stuck temperature if the value never changes?**
Sensors default to `continuous` since 0.4.2, but with `onchange` a frozen sensor is silent, so the watchdog must use timestamps, not change events. Detect staleness from the datapoint timestamp and plausibility from bounds/rate of change (inference on exact thresholds). This is the hazard the whole challenge centres on ([[vss-kuksa-howto]], [[chapter4-challenge-doctor-whodunit]]).

**Q22a. Do we need KUKSA at all?**
Not necessarily. KUKSA gives you a queryable current-state tree with many providers and clients, authorization, and the vocabulary every blueprint speaks, which is why it is on the Adopt ring ([[capability-map]]). But VSS is a *model*, and you can use it as the type source only: export the leaves you need, generate fixed-layout structs, and carry them on iceoryx2 or Zenoh without a broker in the loop. That is the right choice when the data path is a fixed set of signals at a fixed cadence between two processes or two ECUs, and the wrong choice when many apps need ad-hoc reads, history or actuation arbitration. Either way keep the VSS paths as the identity; the broker's numeric ids are session facts ([[vss-kuksa-reference]], [[gap-register]] B10, C8).

## uProtocol/Zenoh

**Q23. Why does my subscriber get nothing?**
In order: start the subscriber first (publish is at-most-once); check both sides are in the same multicast domain, otherwise run a router (`-m router -l tcp/0.0.0.0:7447`, clients `-m client -e tcp/<ip>:7447`); check the authority in the UUri matches the filter (lowercase, same authority on two hosts is never bridged); set `RUST_LOG=info` to see transport logs. For iceoryx2 the equivalents are publisher exiting too fast, different domain/prefix, or different user ([[uprotocol-quickstart]], [[uprotocol-howto]], [[iceoryx2-howto]], [[debugging-checklists]]).

**Q24. Which crate versions go together?**
crates.io `up-rust` 0.9.0 + `up-transport-zenoh` 0.9.1 (needs zenoh ^1.9), verified 2026-10-03. Chapter 3 apps pin 0.5-0.8, so copying their Cargo.toml breaks the build with duplicate `UMessage` types; git main is 0.10.0-SNAPSHOT with a different API (`UPayloadFormat::Text`). Pin exactly and commit Cargo.lock - the Chapter 3 `up-rust` 0.7.0 vs 0.7.1 silent upgrade broke up-transport-zenoh ([[uprotocol-howto]], [[chapter3-retrospective]]).

**Q25. What is the quickest uProtocol demo?**
Clone `up-transport-zenoh-rust`, `cargo build --examples` (~1.5 min), then run `./target/debug/examples/subscriber` and `./target/debug/examples/publisher` in two terminals. A ready heartbeat pub/sub on `//guardian/1001/1/8001` is in the vault (`components/uprotocol/examples-hb/main.rs`). No broker, Docker or sudo needed ([[uprotocol-quickstart]]).

**Q26. What topics should heartbeat/fault/mitigation use?**
There is no official schema; the uProtocol howto has a proposed topic layout for Doctor Whodunit. Since `send()` is not a delivery receipt, the supervisor should tolerate N missed heartbeats rather than alarm on one ([[uprotocol-howto]], [[reference-architecture-doctor-whodunit]]).

**Q27. Can uProtocol bridge Zenoh to MQTT or SOME/IP?**
uStreamer bridges Zenoh and MQTT5 by authority but forwards pub/sub only for topics in a static `subscription_data.json`; SOME/IP needs a separate binary. uStreamer, MQTT5 and SOME/IP were not run in verification. Each bridge between transports cost about half a day in past editions ([[uprotocol-howto]], [[hackathon-patterns]]).

**Q28. Can a microcontroller speak uProtocol?**
No official embedded SDK exists; Chapter 3 hand-rolled a send-only client over MQTT (threadx-rust on AZ3166, sdv_lab over minimq). zenoh-pico runs on ThreadX, Zephyr and FreeRTOS, so a Zenoh path is plausible but unverified for uProtocol framing (inference) ([[uprotocol-overview]], [[threadx-overview]], [[zenoh-overview]]).

## OpenSOVD and faults

**Q29. Why is `/faults` 404?**
You are on `opensovd-core`/gateway, which v0.1.1 implements only discovery, data, bulk-data and version-info; faults is issue #156 (no PR as of snapshot). Faults (read/clear), operations, modes and locks live in the Classic Diagnostic Adapter (CDA) at base path `/vehicle/v15`, not `/sovd/v1`. Workaround for your own app: expose the fault as a `data` item, per the 81-line Rust "Guardian SOVD server" recipe ([[opensovd-quickstart]], [[opensovd-howto]]).

**Q30. Fastest OpenSOVD baseline?**
Recipe A, about 2 minutes: `docker run -d --rm --name opensovd-qs -p 7690:7690 ghcr.io/eclipse-opensovd/opensovd-gateway --mock`, then `curl -s http://127.0.0.1:7690/sovd/v1/components | jq`. Recipe B (~10 min) builds the CDA with cargo and runs the ECU simulator for real faults, locks and operations ([[opensovd-quickstart]]).

**Q31. The CDA returns 503 "Variant detection has not concluded".**
No ECU was found: the `--tester-address` must be an IP on the ECU-facing interface (e.g. `172.42.0.1` on the sim bridge), or a firewall is blocking UDP 13400 broadcast. Also expect the default protocol name to skip 3 of 6 MDDs; that is a known mismatch, not your bug ([[opensovd-quickstart]]).

**Q32. Clearing faults returns 409.**
Clearing needs a lock first: `POST .../components/<id>/locks` with `{"lock_expiration":60}`, then `DELETE .../faults`. Also, the status filter `?status[confirmedDtc]=true` still returns all DTCs, so filter on `.status.mask` client-side ([[opensovd-quickstart]]).

**Q33. Is there a ready Doctor Whodunit-shaped diagnostics demo?**
The HackFest OpenBSW-SOVD-Demo: OpenBSW virtual ECU with 5 simulated DTCs, 3 sensor DIDs, a stub or real CDA, and Grafana. `docker compose --profile stub-cda up --build`, then `curl http://localhost:8080/sovd/v1/components/openbsw-ecu/faults`. Keep the OpenBSW submodule at `07b7551` (main broke the overlay), and fork early because the README states a TTL of end of April 2026 ([[hackfest-openbsw-playground]], [[hackfest-esslingen-2026]]).

**Q33a. Can we use the Flux Capacitor ECU (FLXC1000) branch?**
Not as a ready demo. `features/jkk_FLUX1000` needs openbsw commit 9950d75, which is not fetchable; with the pinned 07b7551 the overlay fails to compile (`etl::span` vs `estd::slice`) and on current openbsw main the overlay CMake breaks. Treat it as a porting task (gap D3), not a baseline. From its sources it exposes ECU FLXC1000 at 0x1000, DIDs F100/F186/F190/F200 and DTCs 0x01E240..45 ([[hackfest-openbsw-playground]], verified failure 2026-10-03).

**Q33b. Can the CDA talk UDS over CAN to the OpenBSW POSIX app?**
Yes, rootless on vcan0. Build with `cargo build --release -p opensovd-cda --features can-isotp-userspace`, set `[can] interface="rawcan:vcan0"` (userspace ISO-TP, no kernel `can_isotp` module) with ECU mapping 0x7E0/0x7E8, and keep `[ecu.OpenBSW] protocol="UDS_Ethernet_DoIP"` because the demo MDD only has that protocol. `data/StaticData` works over multi-frame ISO-TP; `faults` returns 400 because the ECU reports DTC 0x123456, which the demo MDD lacks. Config in `components/opensovd/examples-can-vcan0/` ([[opensovd-reference]], verified 2026-10-03).

**Q34. Can OpenSOVD read faults from the S-CORE/fault-lib DFM?**
Not today. fault-lib + DFM run over iceoryx2 and S-CORE persistency, but nothing exposes them over HTTP; a DFM -> SOVD faults bridge is a listed gap. Run `cargo run -p dfm_bin -- --catalog-dir ... --storage-dir ...`; the README's `dfm` example exits immediately ([[opensovd-howto]], [[gap-register]]).

**Q35. Is the CDA's auth safe for the demo?**
It is demo-only: any client_id/secret works and the JWT is signed with key `"secret"`. Fine for a hackathon, but say so in the pitch rather than claim security ([[opensovd-quickstart]]).

**Q26a. What does a complete SOVD server need that OpenSOVD core does not have yet?**
Most of the standard. Core serves discovery, `data`, `bulk-data` and `version-info`; the CDA adds `faults`, `operations`, `configurations`, `modes` and `locks` for UDS ECUs. Missing everywhere: `cyclic-subscriptions` and `triggers` (the SSE evidence hooks), `updates` (#195), `logs`, `scripts`, `clear-data`, the `/docs` capability description (#92), and mDNS/DNS-SD discovery (#31), which the standard makes mandatory. The coverage table in [[opensovd-reference]] lists them; [[gap-register]] section H sizes them. For Doctor Whodunit the two that matter are `faults` and `triggers`.

## Ankaios/AutoSD/orchestration

**Q36. Our Ankaios manifest from an old repo is rejected.**
The schema changed from v0.6 to v1.x: `apiVersion: v0.1` -> `v1`, `accessRights` -> `controlInterfaceAccess`, `restart: true` -> `restartPolicy`. The Dashboard README and older tutorials use old syntax and stale images (databroker 0.4.1). Keep server, agent, CLI and SDK on the same version (v1.0.4) ([[ankaios-howto]], [[ankaios-overview]]).

**Q37. Workloads cannot reach each other under Ankaios.**
Ankaios has no inter-workload networking: use `commandOptions: ["--net=host"]` and localhost, or host IP + `-p` across nodes. `ADD_COND_RUNNING` means the container is up, not that the app is ready, so feeders need retries. Images must exist locally before `ank apply`; debug with `ank get workloads` and `ank logs --follow <name>` ([[ankaios-howto]], [[ankaios-quickstart]]).

**Q38. How does Ankaios "supervise" the Guardian?**
Via `restartPolicy` (default NEVER; ALWAYS restarts on Succeeded or Failed; ON_FAILURE only on Failed(ExecFailed)) and the control interface for dynamic changes; restarts ignore dependencies. Ankaios can also act as a fault injector by deleting or restarting workloads (inference from the fact card) ([[ankaios-howto]], [[ankaios-overview]]).

**Q39. Do we have to build an AutoSD image?**
Not to start: boot the prebuilt `ghcr.io/eclipse-autosd/eclipse-autosd-bootc-qemu` image or use it as `FROM` + `bootc switch`. Building with aib needs root or privileged podman, about 10+ minutes and ~15 GB, and there is no cross-build. There is no rpi5 target (rpi4 yes), which matters for Hack to the Future hardware ([[autosd-quickstart]], [[autosd-howto]], [[autosd-overview]]).

**Q39a. How do we boot the AutoSD image on a laptop?**
Download https://github.com/eclipse-autosd/eclipse-autosd/releases/download/dev/eclipse-autosd-bootc-qemu-x86_64.qcow2.xz (0.4 GB; 3.5 GB qcow2 after `xz -d`, 8 GiB virtual), fetch `air` from `https://gitlab.com/CentOS/automotive/src/automotive-image-builder/-/raw/main/bin/air`, then `./air --nographics --snapshot --memory 4G --ovmf-dir <dir with OVMF_CODE.fd/OVMF_VARS.fd> autosd.qcow2`. `--ovmf-dir` is needed where `air` reports "Unable to find EFI firmware"; `air` starts one vCPU per host core (no flag to cap it). With KVM the login prompt appears in about 6 s (`root` / `password`); QEMU uses about 0.9 GB RSS at idle. Do not keep the image in `/tmp` if `/tmp` is a tmpfs: 3.5 GB would sit in RAM ([[autosd-quickstart]], verified 2026-10-03).

**Q40. Our config changes on AutoSD vanish after reboot.**
`/etc` is transient in bootc images; put config into the manifest or a quadlet. Also expect SELinux denials (`ausearch -m avc -ts recent`, volumes need `:z`/`:Z`), and resize the small prebuilt disk with `qemu-img resize x.qcow2 30G` before in-VM builds ([[autosd-howto]]).

**Q41. Does Ankaios run on AutoSD?**
Only at idea level: there is an Ankaios COPR RPM spec but no end-to-end demo, and no evidence Ankaios ships in AutoSD images. Both challenges imply the combination, so budget time for it and record it as an integration result if it works (inference) ([[autosd-overview]], [[ankaios-overview]], [[integration-matrix]]).

## openDuT

**Q42. Do we need openDuT at all?**
It is named in both challenges and earns +0.10 bonus, so yes if you want the full integrability score - but keep it thin. Self-hosting means ~12 containers, Keycloak, a CA, `*.opendut.local` DNS and sudo; the advice is to use an organiser-hosted CARL and run only EDGAR. Whether organisers provide a CARL/testbench is unpublished, so ask on Day 1 ([[opendut-overview]], [[opendut-quickstart]], [[pros-cons-when-not]]).

**Q43. Can openDuT inject faults for Doctor Whodunit?**
No fault-injection or replay feature exists. The howto proposes container executors on the cluster interface using `tc qdisc add dev <if> root netem delay 200ms loss 5% duplicate 3%` (message level), `canplayer`/`cangen` (signal level) and `ip link set can0 down` (device level). This is a design, not a documented feature, and a strong gap to build ([[opendut-howto]], [[gap-register]]).

**Q44. EDGAR lost its connection / CAN does not come up.**
NetBird session loss is known: re-run EDGAR setup. Check `ip link` for `wt0`, `br-opendut`, `gre-*`, `br-vcan-opendut`, then `netbird status --detail` and `journalctl -u opendut-edgar`. CAN needs cannelloni, vcan and can_gw modules and `OPENDUT_EDGAR_SERVICE_USER=root`; use `--skip-can` if you only need Ethernet ([[opendut-howto]], [[opendut-quickstart]]).

**Q44a. Can we self-host openDuT at the venue?**
CARL yes: the localenv compose came up as written on 2026-10-03 with no Rust compile (prebuilt CARL 0.10.2), 15 healthy containers in about 10.5 min, about 8 GB of images and 1.55 GB RAM (Keycloak 862 MB of it); LEA answered at https://opendut.local. The `*.opendut.local` hosts lines need sudo (`./test_setup.sh --apply`). EDGAR in Docker does not join yet: even with the 0.10.2 image and `OPENDUT_BACKEND_IP=127.0.0.1` its netbird-client dials `api.netbird.io` and the peer stays Disconnected. Use native EDGAR (unverified) or the organiser-hosted CARL ([[opendut-quickstart]], [[opendut-edgar-docker-notes]]).

## OpenBSW/ThreadX/embedded

**Q45. How do we run OpenBSW without hardware?**
`cmake --preset posix-freertos && cmake --build --preset posix-freertos --parallel` (11 s on 32 cores), then run `app.referenceApp.elf`. It runs without vcan/tap and logs two non-fatal errors; vcan0/tap0 need sudo. Launch with stdin from `/dev/null` if backgrounded, otherwise SIGTTOU stops it ([[openbsw-quickstart]], [[openbsw-howto]]).

**Q46. How does an OpenBSW zonal controller talk to the HPC?**
OpenBSW ships CAN/UDS, DoIP (server only, logical address 0x002A) and lwIP, but no KUKSA, Zenoh or uProtocol integration. Upstream DoIP answers ACK payloads with a Generic NACK, fixed only in the HackFest overlay (CDA workaround `send_diagnostic_message_ack=false`). The embedded-to-uProtocol transport is the hardest part of Hack to the Future; a CAN -> HPC bridge is the low-risk path (inference) ([[openbsw-overview]], [[opensovd-integration-notes]], [[reference-architecture-hack-to-the-future]]).

**Q46a. How do we get OpenBSW CAN frames into KUKSA?**
Run the OpenBSW POSIX app on vcan0 (it sends 0x558 once a second; UDS is on 0x7E0/0x7E8) and the KUKSA can-provider with the DBC and mapping from `components/openbsw/examples-can-feeder/`. No `NET_ADMIN` or `--privileged` needed, only `--network host`; the broker address must be the positional `grpc://` URL:
```bash
docker run -d --name vf-databroker --network host ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1 --insecure --port 55587
docker run -d --name vf-can --network host -v $PWD:/config:ro ghcr.io/eclipse-kuksa/kuksa-can-provider/can-provider:0.5.0 --config /config/can-provider.ini grpc://127.0.0.1:55587
.venv/bin/python -c "from kuksa_client.grpc import VSSClient; c=VSSClient('127.0.0.1',55587); c.connect(); print(c.get_current_values(['Vehicle.Speed']))"
```
Run from `components/openbsw/examples-can-feeder/`; creating vcan0 needs sudo ([[openbsw-howto]], verified 2026-10-03).

**Q47. Is real MCU hardware realistic in two days?**
OpenBSW notes say real hardware is not feasible in 2 days; boards like S32K148 need the Docker toolchain image. ThreadX demos need a board, and toolchain/flash setup (Arm GNU, probe-rs, udev) eats the first hour. Start on the POSIX build and treat hardware as a stretch ([[openbsw-howto]], [[threadx-overview]], [[chapter4-challenge-hack-to-the-future]]).

## S-CORE and iceoryx2

**Q48. Is S-CORE realistic in two days?**
Only the light path. Path A (`cargo +stable build` of the orchestrator examples, ~22 s, two-process iceoryx2 event demo) is verified; Path B (reference integration via Bazel/Docker) means multi-GB toolchains, sudo apt and 30+ minutes, and QNX needs a licence. Do not start from the HackFest S-CORE branches (toolchain URL 404, broken configs); use upstream `inc_diagnostics@gateway_cda_int` instead ([[s-core-quickstart]], [[s-core-howto]], [[hackfest-score-reference-integration]]).

**Q49. Why does the S-CORE orchestrator not build?**
`rust-toolchain.toml` pins rustc 1.85.0 but the lockfile needs 1.88 (`time@0.3.47`). Use `cargo +stable build --locked ...`. Note the orchestrator was removed from the platform in v0.9 (repo still exists) ([[s-core-quickstart]]).

**Q50. Is S-CORE's IPC iceoryx2?**
No. S-CORE's main IPC is LoLa (mw::com); iceoryx2 is used only in orchestrator cross-process events and as one FEO comm backend. OpenSOVD fault-lib also uses iceoryx2 ([[s-core-overview]], [[iceoryx2-integration-notes]]).

**Q51. iceoryx2 says `VersionMismatch` or `IncompatibleTypes`.**
All processes must use the same iceoryx2 version (e.g. PyPI 0.10.0 vs main 0.10.999 fails; use tag `v0.10.0` with the wheel). `IncompatibleTypes` means different type name/size/alignment; share a type crate or set `#[type_name]`. In containers share both `/dev/shm` and `/tmp/iceoryx2` and run as the same UID ([[iceoryx2-howto]], [[iceoryx2-quickstart]]).

**Q53a. How do we make an S-CORE or OpenSOVD contribution that maintainers can actually depend on?**
A target is dependable when it is green, pinned and published: it builds and tests in CI, every input is pinned to a commit or an immutable tag (never a floating `main`, which is exactly what broke the HackFest S-CORE branches), and the artefact is published where a consumer can fetch it. For S-CORE that means a `known_good.json` entry and a Bazel registry module; for OpenSOVD it means a tagged crate and a container image. Say which of the three words your PR delivers (inference, from the HackFest post-mortem in [[hackfest-esslingen-2026]] and [[hackfest-score-inc-diagnostics]]).

## Freestyle contributions

**Q52. What does a Freestyle team have to deliver?**
Real Eclipse project PRs or filed Eclipse SDV Blueprints issues. Mode A (existing issue/PR) scores highest; mode C (new idea) scores high only if tied to a real project need and left as a follow-up artefact. Technical Quality 25 % rewards "near merge-ready", so open a draft PR early and link it in the Solution Plan ([[chapter4-freestyle-track]]).

**Q53. Which contributions are ready to pick up?**
No official list is published. Concrete candidates from the notes: implement `/faults` in opensovd-core (issue #156), openDuT CLEO issue #495 (good-first-issue), upstream the OpenBSW DoIP ACK fix, a DFM -> SOVD faults bridge, a KUKSA + uProtocol quadlet set for AutoSD, and an openDuT fault-campaign executor. Ask the coaches or maintainers of that project before starting (official coach list: https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/; [[gap-register]], [[chapter4-freestyle-track]], [[hackfest-esslingen-2026]]).

**Q54. What do we need for an Eclipse PR?**
An Eclipse Contributor Agreement (ECA) is required for Eclipse project PRs (general Eclipse practice); S-CORE additionally needs DCO sign-off and its docs-as-code CI. Do this on Day 1, not at code freeze (inference) ([[chapter4-freestyle-track]], [[s-core-howto]]).

## Pitch and evidence

**Q55. What do we show the jury?**
The jury scores only finalists (20 %): pitch and handover clarity, community benefit and continuation story, contribution focus, plus "creativity and surprise". Show one story (who benefits, what the user sees), a live or recorded demo moment, and what you left behind (repo, PR, Blueprint issue). The exact regulation behind Doctor Whodunit is not named in the challenge text, so do not cite one without checking ([[chapter4-overview]], [[chapter4-challenge-doctor-whodunit]], [[scoring-rubric-cheatsheet]]).

**Q56. What do the HackCoaches need to see in the 8-minute interview?**
Working code that does what it claims, shown live or verifiable in the repo: one command to start, a README, tests, a task split on GitHub. "Only demonstrated or repository-verifiable work counts." Keep a short demo video/GIF in the repo as fallback and avoid committing large binaries (inference from past editions) ([[chapter4-overview]], [[hackathon-patterns]]).

**Q57. What makes a strong Doctor Whodunit evidence chain?**
A machine-readable record per test linking hazard -> safety goal -> injected fault -> detection -> mitigation -> verdict, with OpenSOVD fault state as independent ground truth rather than the Guardian's own log. Inject one fault per level (message, signal, device), and show that without mitigation the chain silently disarms (inference) ([[chapter4-challenge-doctor-whodunit]], [[reference-architecture-doctor-whodunit]]).

**Q58. What is the Hack to the Future demo moment?**
The same service binary/config running unchanged across all-virtual, embedded-in-the-loop and real-car setups, with the switch done via openDuT, not by hand. The Flux Capacitor / Time Circuits displays could address the "creativity and surprise" item on the jury scorecard, but their interface is unpublished (inference) ([[chapter4-challenge-hack-to-the-future]], [[first-two-hours-hack-to-the-future]]).

**Q59. What did past winners have in common?**
A story-driven feature on a data hub (KUKSA/VSS) with small bridges, Ankaios as the start layer, and a tangible MCU or visible physical output, often with an AI/UX layer. Pure component integration without a user story reached finals but not the podium (inference in the source) ([[hackathon-patterns]], [[chapter3-retrospective]]).
