---
title: Upstream change proposals you could file at the hackathon
type: synthesis
component: none
tags: [upstream, proposals, freestyle, contributions, chapter4]
status: reviewed
sources:
  - "[[gap-register]]"
  - "[[known-broken-recipes]] (verified reproductions, 2026-10-03)"
  - "[[pitfalls-top20]]"
  - "[[design-index]] (pattern cards cited per row)"
last-verified: 2026-10-03
related:
  - "[[first-two-hours-freestyle]]"
  - "[[scoring-rubric-cheatsheet]]"
  - "[[chapter4-freestyle-track]]"
---

# Upstream change proposals

Everything here was either **reproduced on 2026-10-03** (R), **read in the upstream code or an open issue** (C), or **derived from a pattern card** (P). Sizes: S = half a day, M = a day, L = the team for two days. "File as" says whether to open an issue first (features, design questions) or go straight to a PR (bugs, docs). The Freestyle rubric rewards a contribution the project keeps, so every row has a maintainer story: an issue to comment on, or a project to ask the coaches about on site.

**Before you file anything:**
- Search the upstream tracker first (open and closed issues, open PRs); comment on an existing issue rather than opening a duplicate.
- One issue per finding; do not bundle rows.
- Include your own reproduction: exact commands, observed output, and the versions or commit hashes you ran. The evidence here is from 2026-10-03 and may be stale.
- Do not file these texts verbatim; they are drafts to rewrite in your own words after you have checked them.
- Other teams read this list too: check whether someone already filed the same thing during the event.

Rule of thumb for your team: one row from the **bugs and docs** tier (merged by Day 2), one from the **features with an open issue** tier (reviewed by Day 3), and at most one **design proposal** (filed as an issue with a sketch, not code).

## 1. OpenSOVD

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| OS-1 | `faults` resource in opensovd-core: list, read, delete; FaultProvider trait; mirror CDA JSON | feature | C: issue #156 open, no PR; `/faults` 404 reproduced | M | PR on #156 | A1, [[a-fault-is-a-state-machine-with-evidence-attached]] |
| OS-2 | Cross-entity fault view: `functions/VehicleHealth` aggregating `faults/` across apps (FaultManager does not aggregate) | feature | C: design.md | M | issue, then PR | A1 |
| OS-3 | `cyclic-subscriptions` over Server-Sent Events (201 + Location, `Accept: text/event-stream` on the subscription) | feature | C: not implemented | M | issue | H1, [[let-the-standard-timestamp-your-evidence]] |
| OS-4 | `triggers` resource (EnterRange / LeaveRange / OnChange / OnChangeTo → SSE event, log entry, command) | feature | C: not implemented | M | issue | H2 |
| OS-5 | `operations` resource in core with async `executions` (home for mitigation status) | feature | C: not implemented | M | issue | H13, [[mitigation-is-an-event-with-a-status]] |
| OS-6 | `/updates` lifecycle state machine proposal for #195 (banked: queued → … → committed/rolled back; orchestrated verdict mode) | design | C: issue #195 | L | design issue | H3, [[trial-boot-then-commit-reboot-is-owed]] |
| OS-7 | Capability description at `{path}/docs` (#92) | feature | C: issue #92 | M | PR on #92 | H10 |
| OS-8 | mDNS/DNS-SD responder `_sovd._tcp`, `<id>.local`, https `accessurl` (#31); tie to the TLS listener | feature | C: issue #31 | M | PR on #31 | H9, [[advertise-the-https-url-or-do-not-advertise]] |
| OS-9 | Disclose vendor extensions at `/.well-known/sovd-extensions` (core and CDA `x-sovd2uds-*`) | feature | P | S | issue, then PR | H12, [[spec-pure-server-integrator-mounted-extensions]] |
| OS-10 | Proxy backend in core that fronts a CDA under one base path (`/sovd/v1` vs `/vehicle/v15` split) | feature | C: roadmap item | M | issue | H11, [[one-backend-trait-many-backends]] |
| OS-11 | Core: `JwtAuthenticator` sets `validate_aud=false` and gateway accepts bearer tokens over plain http; add `aud` = vehicle id option and refuse plaintext when auth is on | security | C: code read | S | issue + PR | H7, [[verify-offline-against-a-pinned-root]] |
| OS-12 | CDA: without the `auth` feature tokens are decoded with `insecure_decode` (no signature check); fail closed or log loudly | security | C: code read | S | issue + PR | H7 |
| OS-13 | CDA: fault status spelled three ways (`test_failed`, `confirmedDtc`, `confirmedDTC`); document `mask` as the join key or unify | bug/docs | C | S | PR | E7 |
| OS-14 | CDA: href casing `/Vehicle/v15` vs routes `/vehicle/v15`; fault status filter does not narrow | bug | R | S | PR | E7 |
| OS-15 | CDA: lock contention returns 423 with a priority plugin, 409 otherwise; document both as "stop" | docs | C | S | PR | [[lock-before-clear-and-expect-it-to-break]] |
| OS-16 | fault-lib README: `cargo run -p dfm_lib --example dfm` exits immediately; document `dfm_bin`; note aging window is RAM-only | docs | R | S | PR | [[opensovd-howto]] |
| OS-17 | CDA hermetic build: `build.rs` calls git, mbedtls downloads at build time, Bazel only on `feat/bazel*` | build | C: HackFest G2/G4 | M | issue | E8 |
| OS-18 | `opensovd-mcp`: add fault and data tools once OS-1 lands | feature | C: topology tools only | S | issue | A12 |
| OS-19 | CDA: `faults` returns 400 "No DTC with code ... found" when the ECU reports a DTC the MDD lacks; degrade to an "unknown DTC" entry instead | bug | R | S | issue + PR | E18, [[opensovd-reference]] |
| OS-20 | CDA docs: document the `can-isotp-userspace` feature and the `rawcan:<if>` interface as the rootless CAN path (no kernel `can_isotp` module needed) | docs | R | S | PR | [[opensovd-reference]] |
| OS-21 | Python client library and pytest fixtures | tooling | P | S | issue | E13 |
| OS-22 | MDD validator / diff tool (descriptions were the real-car blocker) | tooling | C: HackFest G5 | M | issue | E14 |

## 2. COVESA VSS and vss-tools (file on GitHub, discuss with the KUKSA community)

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| VS-1 | Static ids: `vspec export id` hashes `min`/`max` (range retune re-mints the id) but not the 6.1 `enum` mapping (rebinding keeps the id). Propose: exclude ranges, include enum discriminants, or document the intent | design | C: `id.py` read, not run; verify with one export first | S | issue | B10, [[a-unit-is-identity-a-range-is-policy]], [[enum-discriminants-are-the-type]] |
| VS-2 | New exporter: fixed-layout structs (`#[repr(C)]` Rust / C) for shared-memory transports, with pinned enum discriminants and fixed-size strings | feature | P | M | issue, then PR | B10, [[zero-copy-pays-only-for-fixed-layout-payloads]] |
| VS-3 | DBC → VSS overlay drafter targeting the 6.1 `network_serialization` profile | tooling | P | S–M | PR | B11 |
| VS-4 | Overlays for `Vehicle.Cabin.ChildPresence.*` and a thermal-runaway warning (there is no `IsParked`, no child-presence branch, `Vehicle.Trailer` has one signal) | model | R: overlay verified locally | S | discussion issue | A11 |
| VS-5 | Document `aggregate` and struct datatypes as the grouping primitives, or fix the "ill-defined" wording | docs | C | S | PR | [[coherence-is-a-set-property-declared-in-the-model]] |
| VS-6 | Document that VSS instances are static and point to the open-world pattern (instance in the name) | docs | P | S | PR | [[overlays-extend-the-model-instances-stay-static]] |

## 3. Eclipse KUKSA

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| KU-1 | `databroker-cli` still offers the removed `sdv.databroker.v1` API and cannot speak v2 | bug | R | S | PR | E4 |
| KU-2 | Python SDK: no v2 `Actuate`; v1 target set returns OK but never reaches a v2 provider | bug | R | S | issue + PR | E4, pitfall 1 |
| KU-3 | CLI prints `[publish] OK` on a 400 rejection | bug | R | S | PR | pitfall 16 |
| KU-4 | JWT `aud` is hard-coded to `kuksa.val` (TODO in code); allow per-vehicle audience | security | C | S | PR | H7 |
| KU-5 | `Datapoint` has `{timestamp, value}` only; propose optional validity/quality field or document age as the only quality signal | design | C | S | discussion issue | A8, [[a-reading-carries-what-it-is-worth]] |
| KU-6 | can-provider 0.5.0 ignores `ip`/`port` in the ini and falls back to 55555; honour them or document that only the positional `grpc://host:port` counts | bug/docs | R | S | PR | B6, [[openbsw-howto]] |
| KU-7 | Ankaios tutorial pins databroker 0.4.1 from 2023 | docs | R | S | PR | E4 |

## 4. iceoryx2 (very responsive upstream)

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| IX-1 | Python README names `iceoryx2==0.10.999`, which does not exist on PyPI | docs | R | S | PR | E5 |
| IX-2 | C++ `publish_subscribe` example needs `IOX2_TYPE_NAME` to talk to the Rust example | docs/bug | R | S | PR | E5 |
| IX-3 | Type compatibility is name + size + alignment only; reordered same-size fields connect silently. Propose: optional layout hash in service attributes, matched on open | design | C: `is_compatible_to` read | M | issue | [[a-type-name-is-a-claim-a-layout-hash-is-a-proof]] |
| IX-4 | `iox2 service record` stamps recorder receive time; add producer timestamp/sequence in the system header or document that payloads must carry them | design | C | S | issue | A5, [[a-replay-is-evidence-only-with-the-producers-stamps]] |
| IX-5 | `iox2 node` cleanup subcommand ("NOT YET IMPLEMENTED" in FAQ) | feature | C | M | issue | E5 |
| IX-6 | Document containers: bind-mount `/dev/shm` and `/tmp/iceoryx2` with the same UID; `--ipc=host` is not the lever | docs | C | S | PR | C1, [[share-two-directories-and-one-uid-isolate-by-prefix]] |
| IX-7 | Zenoh gateway to native key expressions (tunnel exists; gateway does not); implement the link adapter trait | feature | R: tunnel verified | L | issue with sketch | B2 |

## 5. Eclipse uProtocol

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| UP-1 | Version-compatibility table across up-rust, up-transport-zenoh, up-transport-mqtt5, zenoh | docs | R: pins verified | S | PR | E9 |
| UP-2 | up-l1 iceoryx2 spec says "MUST use iceoryx2 0.6.1"; `up-transport-iceoryx2-rust` pins 0.7; both incompatible with 0.10 | spec + code | C | M | issue on up-spec + PR | B5 |
| UP-3 | Document authority rules in the quickstart: lowercase only, one per host, never shared (sdv_lab config uses mixed case) | docs | C | S | PR | pitfall 22, [[authority-is-the-routing-unit]] |
| UP-4 | Heartbeat / fault / mitigation event schema crate (.proto + Rust + Python) as a reusable artefact | feature | P | S | issue, then repo | A10 |
| UP-5 | `UTransport` fault-injection decorator (drop, delay, duplicate, corrupt) for test suites | feature | P | S | PR | A7 |
| UP-6 | uStreamer live uSubscription (config reserves `live_usubscription`) | feature | C | M | issue | [[uprotocol-howto]] |

## 6. Eclipse Ankaios

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| AK-1 | Example manifest: two workloads sharing iceoryx2 (bind-mounted `/dev/shm` and `/tmp/iceoryx2`; `--ipc=host` not needed) | docs/example | R: verified 2026-10-03 rootless; manifest in [[ankaios-howto]] | S | PR | C1 |
| AK-2 | Document that `ADD_COND_RUNNING` means container up, not app ready, that dependencies are not re-checked on restart, and that the startup flag is `--startup-manifest` (quickstart copies say `--startup-config`) | docs | R | S | PR | [[one-supervisor-per-node-readiness-is-the-apps-claim]] |
| AK-3 | No liveness/health probe: restart happens only on exit, a hung workload stays Running; dependents with `restartPolicy: NEVER` stay `Failed(ExecFailed)` after a dependency is killed and restarted; propose a health hook or document the workaround | design | R: kill/restart observed 2026-10-03 (hung-but-alive not tested); C: restart-policy doc | M | issue | [[one-watchdog-per-layer-each-blind-to-the-others]] |
| AK-4 | Port ankaios-dashboard to 1.x manifest syntax | bug | C | S | PR | C7 |
| AK-5 | Control-interface example that publishes workload states as SOVD data/faults | example | P | S | PR | A9 |

## 7. Eclipse SDV Blueprints

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| BP-1 | All three compose files use swarm-only `overlay` networks; add a bridge variant or document `docker swarm init` | bug | R | S | PR | E15 |
| BP-2 | fleet-management README and server welcome text say `/rfms/vehicleposition`; route is `/rfms/vehiclepositions` | docs | R | S | PR | E15 |
| BP-3 | e2e-vehicle-signals `start-virtual-setup.sh` not executable; `up --detach"$@"` missing space | bug | R | S | PR | E15 |
| BP-4 | service-to-signal: commit a `Cargo.lock`; `kuksa-rust-sdk = "0.2.0 "` (trailing space) drifts to 0.2.2 and breaks the build (#14) | bug | R | S | PR | E15 |
| BP-5 | fleet-management: forwarder and consumer share one uProtocol authority across all trucks; VIN only in payload; failed publish dropped with no buffer | design | C: code read | M | issue | H14, [[one-key-scheme-from-mcu-to-cloud]] |
| BP-6 | fleet-management: docs say "uProtocol Notification", code sends Publish | docs | C | S | PR | [[sdv-blueprints-overview]] |
| BP-7 | fleet-management bugs #71, #72, #74 (time unit, heading/altitude types) | bug | C | S | PR | E3 |
| BP-8 | Add a fault/DTC leg to fleet-management (none exists) as a blueprint extension | feature | P | M | issue | [[fleet-telemetry-batched-at-the-vehicle-keyed-by-vin]] |

## 8. Eclipse OpenBSW

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| OB-1 | DoIP server answers diagnostic-message ACK types 0x8002/0x8003 with a generic NACK; fix exists only in the HackFest overlay | bug | C: overlay diff | S | PR | E2 |
| OB-2 | POSIX reference app stops when backgrounded (SIGTTOU from console); document stdin from `/dev/null` or make console optional | bug/docs | R | S | PR | pitfall 13 |
| OB-3 | Document that upstream has programming session hooks but no 0x34/0x36/0x37 services and no bootloader | docs | C | S | PR | D5 |
| OB-4 | "Child presence" example ECU (PresenceSystem, console command, CAN frame, DID, DTC) | example | P | M | issue, then PR | D2 |
| OB-5 | Docs: CAN UDS IDs are 0x7E0/0x7E8 at the current commit (9b94994), not 0x02A/0x0F0 as documented | docs | R | S | PR | [[openbsw-quickstart]] |

## 9. HackFest Esslingen playground

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| HF-1 | OpenBSW-SOVD-Demo compose broken in five ways (build context, root user, folded entrypoint, tap0↔eth0 bridge, healthcheck); override attached | bug | R | S | PR with `playbook/fixes/openbsw-sovd-demo.override.yaml` | E16 |
| HF-2 | Port the overlay past the `etl::span` DoIP change; pin or unpin submodule `07b7551` | bug | C | S | PR | E2 |
| HF-3 | Docs drift: LFS claim, HACKATHON.md paths, compose profiles | docs | C | S | PR | [[hackfest-openbsw-playground]] |
| HF-4 | S-CORE fork branches: toolchain URL 404, absolute `local_path_override`, broken AutoSD config; archive with a pointer to upstream `inc_diagnostics@gateway_cda_int` | docs | C | S | issue | [[hackfest-score-reference-integration]] |
| HF-5 | OpenBSW-SOVD-Demo: ship the CDA submodule pin or the LFS binary and bump the runtime base image so `--profile real-cda` runs | bug | R | S | PR with `playbook/fixes/openbsw-sovd-demo-real-cda.override.yaml` | E17, [[hackfest-openbsw-playground]] |
| HF-6 | OpenBSW-SOVD-Demo: make `USE_FLXC1000_ECU` a compose option and rebase the FLXC1000 overlay on current openbsw (pinned 9950d75 is not fetchable) | bug | R | M | issue + PR | D3, [[hackfest-openbsw-playground]] |

## 10. Eclipse openDuT

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| OD-1 | #495: CLEO accepts a cluster leader that is not in the cluster (good-first-issue) | bug | C | S | PR on #495 | E1 |
| OD-2 | EDGAR on non-systemd targets (S-CORE/EB images) and a CAN kernel-module checklist | docs | C | S | PR | E10 |
| OD-3 | Tolerant CAN sample-point check (HackFest loop); NetBird auto re-register | bug | C | M | issue | E10 |
| OD-4 | Fault-injection executor image (`tc netem`, `canplayer`, `cangen`) with a YAML campaign; results to WebDAV | feature | P | M | issue with sketch | A6 |
| OD-5 | `.ci/docker/edgar`: default image tag (`0.10.0-alpha`) should track the CARL release (0.10.2) | bug | R | S | PR | E19, [[opendut-edgar-docker-notes]] |
| OD-6 | EDGAR in Docker: pass the local NetBird management URL to the bundled netbird-client (it dials `api.netbird.io:443`) and document `OPENDUT_BACKEND_IP` for a same-host CARL | bug/docs | R | M | issue + docs PR | E19, [[opendut-quickstart]] |
| OD-7 | Docs: localenv needs ~8 GB of images and ~10 min to all-healthy; Keycloak is the memory hog (862 MB of 1.55 GB) | docs | R | S | PR | E19, [[opendut-quickstart]] |

## 11. Eclipse S-CORE (file on GitHub)

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| SC-1 | Orchestrator pins rustc 1.85.0 but `Cargo.lock` needs 1.88 (`cargo +stable` works) | bug | R | S | PR | E6 |
| SC-2 | A Bazel-free "try it in 2 minutes" page (orchestrator + iceoryx2 example) and stale README paths | docs | R | S | PR | E6 |
| SC-3 | Document that LoLa has no E2E API and that gateway-detected loss has no public-API home | docs/design | C: PCIe gateway note | S | issue | B4, [[the-transport-is-untrusted-the-consumer-checks-carry-safety]] |
| SC-4 | Runtime fault path S-CORE app → `score/mw/diag` → DFM → SOVD (HackFest showed a build integration only) | design | C: Ulm workshop notes | L | design issue | A3 |
| SC-5 | Ankaios manifest for the showcase image | example | P | S | PR | C5 |

## 12. AutoSD / eclipse-autosd

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| AS-1 | README links `bin/aib`; the script is `bin/air` | docs | C | S | PR | [[autosd-overview]] |
| AS-2 | Quadlet set for KUKSA + uProtocol/Zenoh as a derived bootc image (blueprints document compose only) | example | P | M | PR | C3 |
| AS-3 | S-CORE sample sets SELinux permissive, QM memory unlimited and shares `/dev/shm` into QM; label it as a sharing demo, not an isolation demo | docs | C | S | PR | C4, [[freedom-from-interference-has-three-axes]] |
| AS-4 | Document greenboot as required for automatic rollback (bootc alone does not roll back) | docs | C | S | PR | [[trial-boot-then-commit-reboot-is-owed]] |
| AS-5 | rpi5 target or an explicit statement that only rpi4 is supported | feature/docs | C | L / S | issue | D7 |
| AS-6 | automotive-image-builder `air`: add a `--cpus` flag (it starts one vCPU per host core) and document `--ovmf-dir` for hosts where it cannot find EFI firmware | feature/docs | R | S | PR | [[autosd-quickstart]] |

## 13. Eclipse Zenoh and Symphony

| # | Draft issue title | Type | Evidence | Size | File as | Backing |
|---|---|---|---|---|---|---|
| ZN-1 | Quickstart note: multicast scouting can fail on Wi-Fi with client isolation; show the router + explicit endpoint variant first | docs | R | S | PR | pitfall 3 (Docker-bridge failure dropped: not reproduced (corrected 2026-10-03, see [[zenoh-overview]])) |
| SY-1 | Ankaios provider (README lists none; Chapter 3 team built a custom one) | feature | C | M | issue | C6 |
| SY-2 | README: document the Docker no-Kubernetes run (`-e CONFIG=/symphony-api-no-k8s.json`; without it the container exits) | docs | R | S | PR | [[symphony-docker-no-k8s]] |

## How to use this list in the first two hours

1. Pick one row with **R** evidence (it is reproduced; the PR is mostly mechanical) and one with an **open issue number** (a maintainer is waiting).
2. Before any code, comment on the issue or open one (after searching, see above) with your own title and a two-line intent. That comment is the jury's evidence of initiative.
3. Ask the coaches for that project on site; the row also works without them because the evidence is reproducible and this vault holds the recipe.
4. Design rows (OS-6, VS-1, IX-3, AK-3, BP-5, SC-4) are filed as issues with a sketch and the pattern card as rationale, never as unsolicited code.
