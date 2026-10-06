---
title: Ankaios reference
type: reference
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

# Ankaios reference

## Repos (cloned 2026-10-03, depth 1)
| Path | Commit | Date | Notes |
|---|---|---|---|
| repos/ankaios | 696da8a61f1e | 2026-10-02 | main = 1.1.0-pre; docs in doc/docs; examples/ |
| repos/ankaios-dashboard | 6c2e56d31b3e | 2025-09-19 | org eclipse-ankaios-dashboard (the github.com/eclipse-ankaios/ankaios-dashboard URL does not exist) |
| repos/software-orchestration-blueprint | 0a417851000a | 2025-01-20 | SDV blueprint, Ankaios (v0.5) + BlueChi |
Also cloned by others and useful: repos/software-orchestration, repos/sdv_lab, repos/hc3-challenge-mission-update-possible, repos/e2e-vehicle-signals, repos/fleet-management. An "examples" repo does not exist; examples live in repos/ankaios/examples.

## Links
- Repo https://github.com/eclipse-ankaios/ankaios ; docs https://eclipse-ankaios.github.io/ankaios/ (versioned: /0.6/, /latest/, /main/)
- SDKs: https://github.com/eclipse-ankaios/ank-sdk-python (PyPI `ankaios-sdk`), https://github.com/eclipse-ankaios/ank-sdk-rust (crate `ankaios_sdk`)
- Dashboard https://github.com/eclipse-ankaios-dashboard/ankaios-dashboard ; meta-ankaios (Yocto, "coming soon"); Symphony Rust provider https://crates.io/crates/symphony
- Awesome list: repos/ankaios/doc/docs/usage/awesome-ankaios.md

## CLI cheat sheet
`ank get state|workloads|agents`, `ank apply [--agent A] manifest.yaml` (add `-d` to delete per manifest; unverified flag), `ank run workload`, `ank delete workload N...`, `ank logs [--follow] N`, `-s/--server-url` or `ANK_SERVER_URL`. Ports: server 25551 (gRPC). Control FIFOs: /run/ankaios/control_interface/{input,output}.

## Workload states
Pending(WaitingToStart), Starting, Running(Ok), Succeeded(Ok), Failed(ExecFailed), Stopping, Removed, Unknown (documented in repos/ankaios/doc/docs/reference/complete-state.md; exact list unverified).

## Docs map (repos/ankaios/doc/docs)
usage/{installation,quickstart,tutorial-vehicle-signals,tutorial-fleet-management,tutorial-events,mtls-setup}.md; reference/{startup-configuration,control-interface,events,restart-policy,inter-workload-dependencies,complete-state,config-files,orch-comparison,resource-usage}.md; architecture.md.
