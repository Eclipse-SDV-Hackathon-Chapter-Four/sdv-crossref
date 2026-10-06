---
title: Eclipse S-CORE overview
type: overview
component: s-core
tags: [s-core, middleware, safety, iso26262, bazel, rust, cpp, qnx, linux]
status: draft
sources:
  - https://eclipse.dev/score/
  - https://eclipse-score.github.io/score/
  - https://github.com/eclipse-score
  - repos/s-core-score
  - repos/s-core-reference_integration
  - repos/s-core-communication
  - repos/s-core-orchestrator
  - repos/s-core-hackfest-reference_integration
  - https://eclipse.dev/score/
  - https://www.vda.de/en/press/press-releases/2025/250624_PM_Automotive_industry_signs_Memorandum_of_Understanding
  - https://directory.elisa.tech/workshops/2026-06-London/D3-11-15_Lightning-S-CORE_Philipp.pdf
  - https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
  - https://aeemobility.de/english-content/eclipse-s-core-v0-8-released/
last-verified: 2026-10-03
related:
  - "[[s-core-quickstart]]"
  - "[[s-core-howto]]"
  - "[[s-core-reference]]"
  - "[[s-core-integration-notes]]"
  - "[[iceoryx2-overview]]"
  - "[[opensovd-overview]]"
  - "[[autosd-overview]]"
  - "[[hackfest-esslingen-2026]]"
  - "[[chapter4-overview]]"
---

# Eclipse S-CORE overview

Repos inspected on 2026-10-03 (shallow clones):

| clone | commit | date |
|---|---|---|
| repos/s-core-score | 13c8313276e0 | 2026-10-02 |
| repos/s-core-reference_integration | ecb06e668980 | 2026-10-01 |
| repos/s-core-communication | 0345d84f51ae | 2026-10-02 |
| repos/s-core-orchestrator | 749c11371a9d | 2026-09-03 |
| repos/s-core-hackfest-reference_integration (HackFest fork) | 3c843821b8e0 | 2026-04-24 |
| eclipse-score/feo (read on GitHub only, not cloned) | 16c4fefaf466 | HEAD on 2026-10-03 |

## What it is

- **Eclipse S-CORE = Eclipse Safe Open Vehicle Core.** It is a "safety-critical automotive grade middleware stack on top of POSIX OS" for embedded high-performance ECUs. The ELISA 2026 talk says it targets "ADAS DOMAIN UP TO ASIL B" (https://directory.elisa.tech/workshops/2026-06-London/D3-11-15_Lightning-S-CORE_Philipp.pdf; repos/s-core-score/CONTRIBUTION.md).
- It is built for the processes needed for ASPICE, **ISO 26262** (functional safety) and ISO/SAE 21434 (security). Every requirement, architecture element and test is tracked as a sphinx-needs object, and the release gates are defined by inspection checklists and verification reports (https://eclipse.dev/score/; repos/s-core-reference_integration/docs/s_core_v_1/roadmap/pi4.rst).
- **Founders and MoU:** S-CORE was founded in 2024 by Accenture, BMW, ETAS, Mercedes-Benz and Qorix. The VDA MoU was signed on 23 June 2025 by 11 companies: Aumovio, BMW, Bosch, ETAS, Hella, Mercedes-Benz, Qorix, Valeo, Vector, VW and ZF. It had 32 companies by January 2026 (https://www.vda.de/en/press/press-releases/2025/250624_PM_Automotive_industry_signs_Memorandum_of_Understanding).
- **What it is NOT:** it is "not a ready-to-integrate series product. It is a generic foundation for commercial distributions". Compliance responsibility stays with the series project (ELISA slides). Each release note says it does "not 'release for production'" (repos/s-core-reference_integration/docs/s_core_v_1/releases/release_note_score_v0_9.rst). It is also not a vehicle-signal API (that is KUKSA/VSS), not a cloud connector, and not a container orchestrator (that is Ankaios).
- **Naming trap:** "Eclipse Score" is also an unrelated, archived Java workflow engine. Web searches for "Eclipse Score orchestrator" return it (https://aeemobility.de/english-content/eclipse-s-core-v0-8-released/).

## Release state (as of 2026-10-03)

Release dates come from repos/s-core-reference_integration/docs/s_core_v_1/releases/*.rst.

| release | date | notes |
|---|---|---|
| v0.5.0-alpha | 2025-11-17 | First public release: baselibs, communication (LoLa), orchestrator, persistency, FEO |
| v0.5.0-beta | 2025-12-19 | Adds the logging daemon, CodeQL MISRA C++ 2023 and clang-tidy. FEO stayed at v0.5-alpha. |
| v0.6.0 | 2026-02-23 | |
| v0.7.0 | 2026-05-11 | Adds Lifecycle (Launch Manager + Health Monitoring) and Kyron |
| v0.8.0 | press: 2026-08-03 (the repo note says "TBD") | Process gate: complete requirements, architecture and safety artifacts. Orchestrator is "Scheduled to be archived in v0.9". |
| v0.9.0 | 2026-09-07 | Adds Config Management, Bazel 8.6.0 and DR-008 dependency overrides. **The Orchestrator was removed from the platform.** Renames: score_lifecycle_health -> score_lifecycle, score_process -> score_process_description. |
| v1.0 | release gate 3 Nov - 15 Dec 2026 (repos/.../roadmap/pi4.rst) | "Hardening & Release": all checklists valid, verification reports approved |

- **The brief vs. the repo:** the brief said "1.0 in 2028". The repo roadmap puts the **v1.0 gate in Nov-Dec 2026**. The ELISA slides say "complete solution by 2028" and "v2.0 Ready for SOP 2030". Read 2028 as the target for "complete platform", not for the v1.0 tag. The mapping of dates to milestones in the slide graphic is ambiguous (unverified).
- The Overall Status page carries a warning: "generated with AI assistance and is not yet fully accurate" (repos/s-core-reference_integration/docs/s_core_v_1/roadmap/overall_status.rst).

## Module map

The pinned set is in repos/s-core-reference_integration/known_good.json.

| area | repo | language | state |
|---|---|---|---|
| Base libraries | eclipse-score/baselibs, baselibs_rust | C++ / Rust | integrated |
| Communication / IPC (**LoLa**, mw::com) | eclipse-score/communication | C++ with a Rust API | integrated, ASIL-B design target |
| Persistency (KVS) | eclipse-score/persistency | Rust + C++ | integrated |
| Logging (mw::log + datarouter, DLT) | eclipse-score/logging | C++ (+ Rust) | integrated since v0.5-beta |
| Lifecycle (Launch Manager, health monitoring) | eclipse-score/lifecycle | C++ / Rust | integrated since v0.7 |
| Kyron (safe async runtime for Rust) | eclipse-score/kyron | Rust | integrated |
| Time sync | eclipse-score/time | | integrated (v0.8) |
| Config management | eclipse-score/config_management | | integrated (v0.9) |
| Orchestrator | eclipse-score/orchestrator | Rust | **removed from the platform in v0.9**; the repo still exists |
| FEO (fixed execution order) | eclipse-score/feo | Rust + C++ | released v0.1.2 at v0.5; not in known_good.json today |
| Diagnostics (SOVD/OpenSOVD) | eclipse-score/inc_diagnostics | Rust | incubation |
| SOME/IP gateway | inc_someip_gateway | | incubation, module CI only |
| Security/crypto | inc_security_crypto | | incubation, module CI only |
| Other incubation repos | inc_daal, inc_ai_platform, inc_gen_ai, inc_abi_compatible_datatypes, inc_ecu_model, inc_mw_log, inc_feo, inc_mw_com (stale since 2026-01) | | |
| Tooling | docs-as-code, process_description, tooling, bazel_registry, bazel_cpp_toolchains, toolchains_gcc/qnx/rust, rules_rust fork, score-crates, itf, testing_tools, devcontainer, sbom-tool, coverage_tool, module_template, scrample (example app) | Python/Starlark | |
| OS integration | os_autosd, os_images, qnx_sdp, qnx_unit_tests, rules_imagefs | | |

The org repo list was fetched from the GitHub API on 2026-10-03 (see [[s-core-reference]]).

## OS and languages

- **OS:** Linux x86_64 (via Docker), QNX 8.0 x86_64 and aarch64 (via QEMU or Raspberry Pi 4/5), Elektrobit corbos Linux for Safety Applications aarch64 (via QEMU), and Red Hat AutoSD 10 x86_64 (repos/s-core-reference_integration/README.md, "Supported Platforms"). The Orchestrator also documents QNX 7.1 (repos/s-core-orchestrator/src/orchestration/doc/features.md).
- **Languages:** C++17 (GCC 12.2 toolchain, qcc for QNX) and Rust (Ferrocene toolchain, `.bazelrc` `--extra_toolchains=@score_toolchains_rust//toolchains/ferrocene...`). Python and Sphinx are used for docs and tests. TRLC is used for some requirements (overall_status.rst).

## Process model and IPC (how the pieces fit)

- **Apps are separate POSIX processes.** They are started and supervised by the **Launch Manager** (lifecycle module). Its JSON config declares components, run targets, `depends_on`, a sandbox (uid/gid/scheduling) and alive supervision with recovery actions (repos/s-core-reference_integration/showcases/simple_lifecycle/configs/launch_manager_config.json). It keeps readiness (`ready_condition`) separate from aliveness and recovers by switching the Run State ([[one-supervisor-per-node-readiness-is-the-apps-claim]]).
- **IPC inside S-CORE is LoLa (mw::com), not iceoryx2.**
  - It is zero-copy shared memory with a skeleton/proxy pattern from ara::com, flag-file-based service discovery, and events/fields/methods.
  - Message passing underneath uses Unix domain sockets on Linux and QNX dispatch on QNX.
  - Sources: repos/s-core-communication/README.md, score/mw/com/impl/bindings/lola, score/message_passing/unix_domain and qnx_dispatch.
  - A LoLa inter-domain gateway (SoC-SoC or VM-VM) lives in score/mw/com/gateway.
  - LoLa has no E2E API; the PCIe gateway design note says loss detected at the gateway has "no solution on mw::com public API level" ([[the-transport-is-untrusted-the-consumer-checks-carry-safety]]).
- **Logging:** apps write via shared memory to the `datarouter` daemon, which emits DLT (repos/s-core-reference_integration/images/linux_x86_64/BUILD; release_note v0.5-beta).
- **Where iceoryx2 is actually used** (see [[iceoryx2-overview]]):
  1. **Orchestrator** cross-process events. `src/orchestration/src/events/iceoryx/event.rs` creates an iceoryx2 `Node` (prefix `orch_node`) with Event services (Notifier/Listener). User events become global events via `deployment.bind_events_as_global(...)` (src/api/deployment.rs:37). The iceoryx2 git rev is pinned at d3d1c9a7, v0.7.0 (repos/s-core-orchestrator/Cargo.toml). A patched `iceoryx2_qnx8` crate is used for QNX (patches/qnx8_iceoryx2.patch).
  2. **FEO** communication backend `com_iox2`, with alternatives `com_linux_shm` and `com_mw` (= mw::com/LoLa) (https://github.com/eclipse-score/feo/blob/main/examples/rust/mini-adas/README.md).
  3. `score_crates` exposes iceoryx2 0.5.0 and iceoryx2-qnx8 0.7.0 crates (iceoryx2 appears in repos/s-core-communication/MODULE.bazel.lock), but LoLa itself does not depend on it. grep found no BUILD reference.
- **Orchestrator scheduling:**
  - A `Design` registers invocables (sync/async fns, C++ via FFI) and events, then builds programs from actions: `Sequence`, `Concurrency`, `LocalGraph` (DAG, topologically sorted), `Select`, `IfElse`, `Catch`, `Sync` (wait on event) and `Trigger` (send event).
  - The **deployment** step, separate from the design, binds events as local, timer or global (iceoryx2) and pins invocables to Kyron workers.
  - Programs run on the **Kyron** async runtime (`ExecutionEngineBuilder().workers(n).with_dedicated_worker(...)`).
  - Sources: repos/s-core-orchestrator/src/orchestration/examples/basic.rs, doc/features.md, doc/orch_design.md.
- **FEO (Fixed Execution Order framework)** is an application framework for data- and time-driven apps, mainly ADAS, targeting ASIL_B (repos/s-core-score/docs/features/frameworks/feo/index.rst).
  - Apps are made of **activities** with `init()`, `step()` and `shutdown()`. Activities are statically mapped to threads in a primary process plus secondary processes.
  - Input and output **service activities** sit at the ends of a task chain.
  - Topics are typed and "runtime static". Supports reprocessing/replay.
  - Feature flag `experimental_feo`. Bazel only, no Cargo build. FEO's .bazelversion is 8.3.0.

## Pros / cons for a 2-day hackathon

**Pros**
- Real safety-oriented middleware: zero-copy IPC, lifecycle, persistency, DLT logging.
- Rust and C++.
- QNX, EB corbos and AutoSD images already wired up.
- Very active: 80+ repos with commits daily.
- The OpenSOVD x S-CORE path was proven at HackFest Esslingen on EB corbos on a Raspberry Pi (https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and).

**Cons**
- Bazel-only for most modules. Toolchains download several GB (Ferrocene, GCC, QNX); this is unverified, see the quickstart.
- Bazel versions differ per repo: 8.6.0 ref-int, 8.7.0 communication, 8.3.0 feo, 8.4.2 HackFest fork.
- QNX needs a licensed SDP (env vars `SCORE_QNX_USER`/`SCORE_QNX_PASSWORD`, used by .github/tools/qnx_credential_helper.py).
- APIs churn fast: Orchestrator removed in v0.9, module renames.
- No native host Bazel toolchain for aarch64 Linux was found in .bazelrc (unverified).
- Contributing upstream requires ECA + DCO and requirements/safety documentation.

**When NOT to use it:**
- The team needs a vehicle-signal API (use KUKSA/VSS), a cloud link (uProtocol/Zenoh) or container orchestration (Ankaios).
- Nobody on the team knows Bazel.
- The demo must run on a Raspberry Pi with Linux (not EB corbos/QNX) within hours.
- In those cases, use S-CORE pieces that build with Cargo (orchestrator, kyron) or pure [[iceoryx2-overview]].

## Hackathon ideas (freestyle / gaps)

1. **Diagnose a S-CORE app via OpenSOVD.** Build on the HackFest result: expose LoLa/persistency state as SOVD data items (see [[opensovd-overview]]). Relevant to [[chapter4-challenge-doctor-whodunit]].
2. **KUKSA/VSS <-> mw::com bridge.** A small Rust/C++ process that subscribes to a LoLa event and pushes VSS signals to a KUKSA databroker. No evidence of this exists yet ([[vss-kuksa-overview]]).
3. **Orchestrator/Kyron program as a fault-handling chain.** For example, a thermal-runaway warning chain with `Catch` and `Select` timeouts, using iceoryx2 global events across processes. It builds with Cargo in about 25 s (see [[s-core-quickstart]]).
4. **Ankaios manifest for the Launch-Manager image.** Run the S-CORE showcase container under Ankaios ([[ankaios-overview]]). No integration found.
5. **Docs contributions:** a quickstart for Raspberry Pi with Linux, a Bazel-free "try it" page, and fixing stale paths in READMEs (for example, the HackFest fork README still references orchestrator showcases).
6. **uProtocol transport over LoLa or iceoryx2.** This is idea stage only ([[uprotocol-overview]]).

See also [[s-core-integration-notes]], [[s-core-howto]], [[hackfest-esslingen-2026]], [[chapter4-overview]], [[chapter4-challenge-hack-to-the-future]]. S-CORE is named only in the Chapter 4 challenge [[chapter4-challenge-doctor-whodunit]] (OpenBSW is the one named in Hack to the Future), per [[chapter4-overview]]. S-CORE's concrete role in that challenge is not published (see the challenge note's open questions).
