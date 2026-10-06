---
title: Eclipse S-CORE reference (repos, versions, links, APIs)
type: reference
component: s-core
tags: [s-core, reference, repos, versions]
status: draft
sources:
  - https://api.github.com/orgs/eclipse-score/repos
  - repos/s-core-reference_integration/known_good.json
  - repos/s-core-reference_integration/docs/s_core_v_1/releases
  - repos/s-core-reference_integration/docs/s_core_v_1/roadmap/pi4.rst
  - repos/s-core-score/docs
  - repos/s-core-orchestrator/Cargo.toml
last-verified: 2026-10-03
related:
  - "[[s-core-overview]]"
  - "[[s-core-quickstart]]"
  - "[[s-core-howto]]"
---

# Eclipse S-CORE reference

## Links
- Landing page: https://eclipse.dev/score/
- Platform docs: https://eclipse-score.github.io/score/main/
- Handbook: https://eclipse-score.github.io/score/main/handbook/index.html (linked from the v0.5-beta release note)
- Releases and roadmap: https://eclipse-score.github.io/reference_integration/main/s_core_v_1/
- Process description: https://eclipse-score.github.io/process_description/main/index.html
- v1.0 planning board: https://github.com/orgs/eclipse-score/projects/17/views/37
- Slack: https://sdvworkinggroup.slack.com/archives/C083Z4VL90B
- Mailing list: score-dev
- Project page: https://projects.eclipse.org/projects/automotive.score
- HackFest org: https://github.com/Eclipse-SDV-HackFest-Esslingen-2026

## Pinned modules in the reference integration

From known_good.json at ref-int commit ecb06e668980.

| module | repo | pinned hash |
|---|---|---|
| score_baselibs | eclipse-score/baselibs | ee40fece5a |
| score_communication | eclipse-score/communication | 313f117862 |
| score_persistency | eclipse-score/persistency | 9ae529ba9f |
| score_kyron | eclipse-score/kyron | 90fb90258f |
| score_lifecycle | eclipse-score/lifecycle | 85da216832 |
| score_logging | eclipse-score/logging | b4f272b0a0 |
| score_time | eclipse-score/time | 3723ce687e |
| score_config_management | eclipse-score/config_management | e0489b190e |
| tooling | score-crates, itf, tooling, score (platform), bazel_platforms, testing_tools, docs-as-code, process_description, bazel_cpp_toolchains | |

Versions in the v0.9 release note: baselibs 0.2.12, kyron 0.1.4, platform scope v0.7.2, docs_as_code 8.1.1, bazel_platforms 1.0.0. Release dates are in [[s-core-overview]].

## Repository map

Source: GitHub API, 2026-10-03; size is the GitHub repo size.

- **Target software:** baselibs, baselibs_rust, communication (LoLa), persistency, logging, lifecycle, kyron, time, config_management, orchestrator (deprecated from the platform), feo
- **Incubation:** inc_diagnostics, inc_someip_gateway, inc_security_crypto, inc_daal, inc_ai_platform, inc_gen_ai, inc_abi_compatible_datatypes, inc_ecu_model, inc_json, inc_mw_log, inc_mw_com, inc_feo, inc_config_management, inc_score_codegen, inc_process_*
- **Integration:** reference_integration (1.4 GB full history; the shallow clone is 6 MB), scrample (example app), itf, testing_tools, os_autosd, os_images, operating_system, qnx_sdp, qnx_unit_tests
- **Build:** bazel_registry (+ UI), bazel_cpp_toolchains, bazel_platforms, toolchains_gcc(_packages), toolchains_qnx, toolchains_rust, ferrocene_toolchain_builder, rules_rust (fork, branch `score_main`), rules_imagefs, score-crates, bazel-tools-cc (clang-tidy), bazel-tools-python, score_cpp_policies, score_rust_policies, coverage_tool, sbom-tool, dash-license-scan
- **Docs and process:** score (main docs, 1.1 GB full history), docs-as-code, process_description, eclipse-score.github.io, eclipse-score-website*
- **Dev environment:** devcontainer (`ghcr.io/eclipse-score/devcontainer:<tag>`), module_template, dev_playground, tools, tooling, mcp-servers, cicd-actions, cicd-workflows

## Feature areas in the platform docs

repos/s-core-score/docs/features/ contains: ai_platform, baselibs, code_generation, communication (ipc, some_ip_gateway), configuration, diagnostics (SOVD-based; links OpenSOVD MVP design), frameworks (feo, daal), lifecycle, log_and_trace, orchestration, persistency, security_crypto, time.

Design decisions are in docs/design_decisions/:
- DR-001-strat: S-CORE is a "continuously consistent stack".
- DR-008: integration strategy via the known_good overrides.

## Key paths for grepping

- LoLa / mw::com:
  - repos/s-core-communication/score/mw/com/{impl/bindings/lola, gateway, rust, example/com-api-example, design, doc/tutorial}
  - message passing: score/message_passing/{unix_domain,qnx_dispatch}
- Orchestrator:
  - iceoryx2 events: repos/s-core-orchestrator/src/orchestration/src/events/iceoryx/event.rs
  - deployment API: src/api/deployment.rs
  - actions: src/actions/*
  - examples: src/orchestration/examples/*
- Launch Manager config example: repos/s-core-reference_integration/showcases/simple_lifecycle/configs/launch_manager_config.json
- Image definitions: repos/s-core-reference_integration/images/{linux_x86_64,qnx_x86_64,qnx_aarch64,ebclfsa_aarch64,autosd}
- Bazel configs: repos/s-core-reference_integration/.bazelrc
  - configs: `linux-x86_64`, `qnx-x86_64`, `qnx-aarch64`, `eb-aarch64`, `autosd-x86_64`, `itf-qnx-x86_64`, `unit-tests`, `ferrocene-coverage`
- FEO feature spec: repos/s-core-score/docs/features/frameworks/feo/index.rst

## Dependency versions worth knowing

- Orchestrator uses iceoryx2 git rev d3d1c9a7 (crate version 0.7.0) and Kyron rev e51832d6 (repos/s-core-orchestrator/Cargo.toml).
- score_crates provides iceoryx2 0.5.0 and iceoryx2-qnx8 0.7.0 (from repos/s-core-communication/MODULE.bazel.lock).
- FEO depends on score_communication 0.1.2, score_baselibs 0.2.4, score_logging 0.1.2 and trlc 2.0.3 (https://github.com/eclipse-score/feo/blob/main/MODULE.bazel).
