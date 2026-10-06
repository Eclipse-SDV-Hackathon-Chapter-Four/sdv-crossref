---
title: Eclipse Chariott / Ibeji / Agemo / Freyja - overview
type: overview
component: chariott
tags: [chariott, ibeji, agemo, freyja, microsoft, digital-twin, dormant, adjacent]
status: draft
sources:
  - https://github.com/eclipse-chariott
  - https://github.com/eclipse-chariott
  - https://github.com/eclipse-ibeji
last-verified: 2026-10-03
related:
  - "[[chariott-integration-notes]]"
  - "[[vss-kuksa-overview]]"
  - "[[sdv-blueprints-overview]]"
  - "[[sdv-landscape-overview]]"
---

# Microsoft SDV projects: Chariott, Ibeji, Agemo, Freyja

## Are they archived in 2026? No - but they are dormant
Checked 2026-10-03: none of the repos is archived on GitHub (API `archived=false`, no archive banner) and the Eclipse project pages for Chariott and Ibeji still say **Incubating** with no termination notice (https://projects.eclipse.org/projects/automotive.chariott, .../automotive.ibeji). Agemo and Freyja are sub-repos in the Chariott and Ibeji orgs, not separate Eclipse projects. But activity stopped:

| Repo | Last push | Last tag |
|---|---|---|
| eclipse-chariott/chariott | 2025-04-13 | 0.2.1 |
| eclipse-chariott/Agemo | 2024-10-14 | 0.1.2 |
| eclipse-ibeji/ibeji | 2024-07-15 | 0.1.1 |
| eclipse-ibeji/freyja | 2024-09-09 | 0.1.0 |
| eclipse-chariott/chariott-example-applications | 2025-04-13 | - |
| eclipse-ibeji/ibeji-example-applications | 2024-09-09 | 0.1.0 |
Stars 27 / 2 / 11 / 5. READMEs still show a stale "status: maintained" badge. Classification: **dormant (15-27 months without a push), not formally archived**; a project-lead or Eclipse Foundation archival could still happen. The Eclipse SDV landscape counts all of them as active-listed projects ([[sdv-landscape-overview]]).

## What each is
- **Chariott**: Rust gRPC service with two separate parts: *Intent Brokering* (apps register capabilities/"intents"; Chariott routes requests to the provider) and *Service Discovery* (registry). MIT. https://github.com/eclipse-chariott/chariott
- **Ibeji**: In-Vehicle Digital Twin Service in Rust; providers register capabilities, consumers discover and subscribe; models described in **DTDL** (JSON-LD, Azure DTDL submodules); MQTT/gRPC; optional Chariott discovery. Needs Ubuntu 22.04 and a Rust nightly pinned via `rust-toolchain.toml`. https://github.com/eclipse-ibeji/ibeji
- **Agemo**: in-vehicle dynamic pub/sub service handler (gRPC + MQTT, "managed subscribe"). https://github.com/eclipse-chariott/Agemo
- **Freyja**: sync between the in-vehicle digital twin ("instance twin") and a cloud "canonical twin"; cartographer + adapters (Ibeji, Agemo, Chariott, MQTT, gRPC, cloud, user-authored mapping service). https://github.com/eclipse-ibeji/freyja

## What it is NOT
Not a VSS/KUKSA replacement (different data model and no databroker semantics), not an orchestrator, not production-hardened (0.x tags).

## Anything still reusable
- **Ibeji digital twin and VSS**: no VSS support in the Ibeji/Freyja READMEs; Ibeji uses DTDL. A VSS<->DTDL mapping would be new work. VSS can be exported to other formats by vss-tools (not verified for DTDL). Freyja's mapping-service concept (signal A -> cloud twin property B with transformation and interval) is the closest existing pattern for "VSS signal -> cloud twin" ([[vss-kuksa-overview]]; https://github.com/eclipse-chariott).
- **Freyja adapter architecture** (data/digital-twin/cloud/service-discovery adapters) as a template for a KUKSA data adapter.
- **Agemo managed subscribe** for dynamic MQTT topic management; compare with [[zenoh-overview]] / uProtocol topics.
- **Chariott intent-brokering design docs** (docs/design/intent_brokering_design.md) as conceptual input for uProtocol-style service discovery.
- The **software-orchestration blueprint** describes a layer with "discovery and consumption of resources", "common vehicle model", "dynamic topic management", "sync to cloud digital twin" - exactly Chariott/Ibeji/Agemo/Freyja responsibilities - but its README only shows Ankaios and BlueChi implementations (https://raw.githubusercontent.com/eclipse-sdv-blueprints/software-orchestration/main/README.md); direct reuse is unverified. See [[sdv-blueprints-overview]].

## Quickstart (inline; NOT run - Rust nightly + Ubuntu 22.04 + dotnet SDK)
Per Ibeji README: `sudo apt install gcc protobuf-compiler ... libssl-dev`; install rustup (toolchain auto-selected); `git clone --recurse-submodules https://github.com/eclipse-ibeji/ibeji`; `cargo build --workspace`; install a Mosquitto broker for MQTT samples; run a sample under `samples/`. Expect build breakage on newer distros/toolchains (SDL2 and dotnet-sdk needed for dtdl-tools). Budget 30-60 min, not 15; advice: do not use in a 2-day event unless your team already knows Rust.

## Pros / cons / when not to use
Pros: clean Rust code, good design docs, MIT, ready-made gRPC/MQTT shapes.
Cons: dormant, nightly Rust, DTDL/Azure-centric cloud adapters, no VSS, no uProtocol, no community.
Not for: new designs; prefer KUKSA + uProtocol/Zenoh ([[uprotocol-overview]]).

## Hackathon ideas
1. VSS-to-DTDL generator or an Ibeji provider backed by KUKSA databroker.
2. A Freyja `kuksa_data_adapter` that syncs VSS signals to a cloud twin (Ditto, see [[kanto-overview]]).
3. Port Agemo's managed subscribe idea onto Zenoh queryables.
4. Ask the maintainers (Microsoft) / Eclipse webmaster about the planned lifecycle: archive or hand over (gap register).
