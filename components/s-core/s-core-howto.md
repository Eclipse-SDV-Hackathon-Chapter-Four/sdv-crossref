---
title: Eclipse S-CORE how-to recipes and pitfalls
type: howto
component: s-core
tags: [s-core, howto, bazel, pitfalls, docs-as-code, contribution]
status: draft
sources:
  - repos/s-core-reference_integration/README.md
  - repos/s-core-reference_integration/.bazelrc
  - repos/s-core-reference_integration/showcases/cli/README.md
  - repos/s-core-orchestrator/src/orchestration/examples
  - repos/s-core-score/README.md
  - repos/s-core-score/CONTRIBUTION.md
  - repos/s-core-communication/README.md
  - https://github.com/eclipse-score/feo/blob/main/examples/rust/mini-adas/README.md
  - https://github.com/eclipse-score/devcontainer
last-verified: 2026-10-03
related:
  - "[[s-core-overview]]"
  - "[[s-core-quickstart]]"
  - "[[s-core-reference]]"
---

# Eclipse S-CORE how-to recipes and pitfalls

## Recipe 1: send an event between two processes (Orchestrator + iceoryx2)

Pattern from repos/s-core-orchestrator/src/orchestration/examples/inter_process_event/{sender,receiver}.rs. It builds with Cargo (see [[s-core-quickstart]]).

- **Design side.** In the sender:
  - `design.register_event(Tag::from_str_static("ForwardCollisionEvent"))`
  - a program `SequenceBuilder::new().with_step(Invoke::from_design(..)).with_step(TriggerBuilder::from_design("ForwardCollisionEvent", di))`
- **Deployment side.** Call `deployment.bind_events_as_global("ADASEmergencyBrakeEvent", &["BrakeEvent".into()])`. The system event name is the iceoryx2 Event service name and must match in both processes. Local alternatives are `bind_events_as_local` and `bind_events_as_timer(&[..], Duration)` (src/api/deployment.rs).
- **Receiver side.** Use `SyncBuilder` to wait on the event, then invoke the handler.
- **Threads.** Use `deployment.bind_invoke_to_worker("fn", "dedicated_worker1")` with a Kyron `ExecutionEngineBuilder().workers(2).with_dedicated_worker(..)` (examples/basic.rs).
- **Payload.** Only notifications are sent (iceoryx2 *event* messaging pattern), with no data. To move data, use iceoryx2 publish-subscribe directly ([[iceoryx2-overview]]) or LoLa.

## Recipe 2: add your binary to the reference-integration showcase CLI

1. Add a Bazel target and include it in `//showcases:showcases_pkg_tar` (showcases/BUILD).
2. Ship a `<name>.score.json` with `{"name","description","apps":[{"path","args","env","dir","delay"}]}`. The CLI autodiscovers it (showcases/cli/README.md).
3. Run with `./score_starter -r linux-x86_64`.

## Recipe 3: run tests in the reference integration

```bash
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit --test_output=streamed
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios
bazel test --config=linux-x86_64 //feature_integration_tests/itf --test_output=streamed   # Docker-based ITF
bazel test --config=unit-tests //...      # see .bazelrc test:unit-tests
```
(repos/s-core-reference_integration/README.md, .bazelrc)

## Recipe 4: hack on several modules at once

Steps (repos/s-core-reference_integration/README.md, "Multi-Module Development Workspace"):

```bash
python3 scripts/known_good/update_module_from_known_good.py --override-type local_path
python3 scripts/known_good/known_good_to_workspace_metadata.py
gita clone --preserve-path --from-file .gita-workspace.csv   # clones score_* dirs
```

Bazel then uses your local checkouts. Revert with `--override-type git`.

## Recipe 5: FEO mini-ADAS (Bazel only)

Run in three terminals (https://github.com/eclipse-score/feo/blob/main/examples/rust/mini-adas/README.md):

```bash
bazelisk run //examples/rust/mini-adas:adas_primary_com_iox2_direct_unix -- 400   # 400 ms cycle
bazelisk run //examples/rust/mini-adas:adas_secondary_com_iox2_direct_unix -- 1
bazelisk run //examples/rust/mini-adas:adas_secondary_com_iox2_direct_unix -- 2
```

- Com backends: `com_iox2`, `com_linux_shm`, `com_mw`.
- Signalling: `direct_tcp|direct_unix|relayed_tcp|relayed_unix`.
- Not run here.

## Recipe 6: build docs (docs-as-code)

- `bazel run //:docs` builds the HTML into `_build`.
- `bazel run //:live_preview` serves at 127.0.0.1:8000.
- `bazel run //:ide_support` sets up the Esbonio venv `.venv_docs`.
- Source: repos/s-core-score/README.md. In the reference integration, `bazel run //:docs` builds the combined docs.

## Pitfalls

| pitfall | detail / fix | source |
|---|---|---|
| Bazel version differs per repo | ref-int 8.6.0, communication 8.7.0 (README: "8.6 <= Bazel < 9.x"), feo 8.3.0, HackFest fork 8.4.2. Always use **bazelisk** and never a distro `bazel`. | `.bazelversion` in each repo |
| Rust toolchain pin too old for the lockfile | orchestrator pins 1.85.0, but its Cargo.lock needs 1.88 (`time@0.3.47`). Use `cargo +stable`. | Observed 2026-10-03, [[s-core-quickstart]] |
| Toolchain downloads | Ferrocene Rust, GCC 12.2, the EB SDK and AutoSD toolchains are fetched by Bazel. The S-CORE registry is `raw.githubusercontent.com/eclipse-score/bazel_registry`. Venue Wi-Fi or a GitHub rate limit can break the first build. `.bazelrc` sets 10 retries. Pre-fetch before the event. | .bazelrc |
| Separate output bases | `score_starter` uses `--output_base=build/<platform>`, so each platform is a full cold build with its own disk usage. | score_starter |
| QNX needs credentials | `SCORE_QNX_USER`/`SCORE_QNX_PASSWORD` for *.qnx.com downloads via `.github/tools/qnx_credential_helper.py`. RPi deployment also needs the QNX BSP and a startup binary swap. | .bazelrc, README |
| linux-sandbox in containers | Needs `--privileged` or user namespaces. On Ubuntu 23.10+, AppArmor restricts unprivileged userns. | https://github.com/eclipse-score/devcontainer |
| Platform churn | Orchestrator removed in v0.9. `score_lifecycle_health` became `score_lifecycle`, `score_process` became `score_process_description`. docs-as-code jumped 4.6.1 -> 8.1.1 (breaking). | release_note_score_v0_9.rst |
| Comm module external-build issues | `@//third_party` vs `//third_party` labels; `runtime_test.cpp` checks an obsolete path. Ref-int carries patches in `patches/communication/`. | ref-int README "Known Issues", known_good.json |
| Docs-as-code checks | Requirements are sphinx-needs objects (`feat_req`, `stkh_req`, ...) with mandatory `:id:`, `:status:`, `:safety:`, `:security:`, `:derived_from:` and `:version:`. Broken links or missing attributes fail the docs build in CI. Some modules moved requirements to TRLC. | repos/s-core-score/docs/features/communication/ipc/requirements/index.rst, overall_status.rst |
| Contribution overhead | Requires an Eclipse ECA **and** DCO. Use the PR templates (bug_fix / improvement), then open a matching issue to trigger review. Improvements start as stakeholder/tool requirement changes. Code owners review. Expect days to weeks, not hours. | repos/s-core-score/CONTRIBUTION.md |
| Search noise | "Eclipse Score" also names an archived Java workflow engine. | https://aeemobility.de/english-content/eclipse-s-core-v0-8-released/ |
| Stale incubation repos | `inc_mw_com` (last push 2026-01) and `inc_feo` (2025-09) are superseded by `communication` and `feo`. | GitHub API org listing 2026-10-03 |

## Contribution checklist for a hackathon PR
1. Sign the ECA with the same email you commit with, and add `Signed-off-by` (DCO).
2. Use docs-only or bugfix PRs. A new feature needs a feature request and requirements first (repos/s-core-score/CONTRIBUTION.md).
3. Run `bazel test //:format.check` and `bazel run //:copyright.check` (repos/s-core-score/README.md).
