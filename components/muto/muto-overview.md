---
title: Eclipse Muto - overview
type: overview
component: muto
tags: [sdv, muto]
status: draft
sources:
  - https://github.com/eclipse-muto
  - https://projects.eclipse.org/projects/automotive.muto/governance
  - https://sdv-blueprints.eclipse.dev/docs/ros-racer/
  - https://github.com/eclipse-muto
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
---

# Eclipse Muto

## What it is / is NOT
Adaptive framework and runtime for **dynamically composable, model-driven ROS (2) software stacks** on robots/vehicles (https://projects.eclipse.org/projects/automotive.muto/governance snippet). A "stack" is a declarative model of ROS nodes/launch context; Muto Agent (gateway to cloud: MQTT gateway to Ditto plus a Symphony provider, see [[muto-declares-the-stack-the-orchestrator-owns-the-process]]), Composer (resolves and launches stacks), Core (common lib), Dashboard (web/mobile mgmt). Origin: Composiv / Eteration (unverified). It is NOT a generic container orchestrator (see [[ankaios-overview]]) and NOT a middleware.

## Maturity / version
Org https://github.com/eclipse-muto: repos muto, agent, composer, core, messages; Python mostly; EPL-2.0. Container deployment is "planned" (org README). Version numbers and recent activity: **unverified** (not cloned). Treat as incubation-stage / demo-grade; the best working demo is the SDV **ROS Racer** blueprint (https://sdv-blueprints.eclipse.dev/docs/ros-racer/): OTA swap of driving algorithms, rollback, Ditto digital twin, optional Symphony layer, CycloneDDS + Mosquitto.

## Quickstart (not run)
Docs: pre-built images or build from source per the Developer Guide in the muto repo. Practical path: follow ROS Racer blueprint steps (needs ROS 2 distro, MQTT broker, optionally Ditto). To try it: `git clone https://github.com/eclipse-muto/muto`, read docs/ quickstart, run the container image, record output. Prereqs: ROS 2 (Humble/Jazzy - unverified), Docker, Mosquitto.

## Pitfalls
- ROS 2 build times; ROS-version coupling.
- Cloud side needs Ditto and/or Symphony; MQTT topic conventions must match.
- Sparse docs outside the blueprint (unverified; expect gaps).

## Pros / cons / when not to use
Pros: only SDV project that deploys ROS stacks declaratively, rollback, Symphony/Ditto hooks, a working blueprint. Cons: ROS-only, small community, docs thin, no Zenoh or Ankaios story found; the Symphony link is an Agent provider, so cloud-side desired state depends on it. Not for non-ROS workloads.

## Hackathon ideas
1. Run Muto stacks on Ankaios (container deployment is "planned") - Ankaios workload that hosts Muto Composer.
2. Muto over Zenoh (rmw_zenoh) instead of CycloneDDS/MQTT ([[zenoh-overview]]).
3. Symphony target + Muto OTA for the Hack to the Future HPC ([[symphony-overview]], [[chapter4-challenge-hack-to-the-future]]).
4. Muto agent exposing diagnostics to OpenSOVD ([[opensovd-overview]]).
