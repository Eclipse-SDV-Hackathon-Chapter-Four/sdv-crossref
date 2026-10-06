---
title: Getting started — Doctor Whodunit
type: playbook
component: none
tags: [first-two-hours, doctor-whodunit, getting-started, chapter4]
status: reviewed
sources:
  - "[[reference-architecture-doctor-whodunit]]"
  - "[[scoring-rubric-cheatsheet]]"
  - "[[pitfalls-top20]]"
  - "[[hackathon-patterns]]"
last-verified: 2026-10-03
related:
  - "[[first-two-hours-hack-to-the-future]]"
  - "[[gap-register]]"
  - "[[env-setup-matrix]]"
  - "[[faq]]"
---

# Getting started — Doctor Whodunit

A plan for your team's first two hours. Goal: a **green baseline** (something publishes, something subscribes, something is stored) and a **one-page plan that maps onto the rubric** before the Day 1 18:00 Solution Plan deadline.

## 0:00–0:15 Questions to settle in your team

0. **Have you declared all prepared work to the organisers?** The evaluation form says only demonstrated or repository-verifiable work counts and prepared code must be declared clearly, in person, at kick-off; teams and tracks are frozen after Day 1 11:30–12:30. The pitch deck upload is a separate deadline, Day 3 11:00 ([[scoring-rubric-cheatsheet]]).

1. Who has Rust? Who has Python? Who has done gRPC before? (Decides Guardian language and whether the Python KUKSA client is the fastest path.)
2. Which of your laptops have Docker running, and does anyone have podman? (No podman = quadlets or compose instead of Ankaios until someone installs it.)
3. Has anyone opened the Chapter 4 GitHub org today (https://github.com/Eclipse-SDV-Hackathon-Chapter-Four)? On 2026-10-03 the org's public page showed only its `.github` profile repo, and Guardian code and testbench details were unpublished; starter repos may appear during the event.
4. What is your story? "A battery sensor froze during fast charging and the Guardian caught it" is enough. Winners in Chapter 3 were story-driven ([[chapter3-retrospective]]).

## 0:15–0:45 Green baseline (parallel, one person each)

| Person | Task | Verified recipe | Expected result |
|---|---|---|---|
| A | KUKSA databroker 0.7.1 + get/publish | [[vss-kuksa-quickstart]] Part A | `Vehicle.Speed: 100.34 km/h` |
| B | uProtocol pub/sub over Zenoh | [[uprotocol-quickstart]] Path A | messages delivered between two processes |
| C | OpenSOVD gateway `--mock` + curl | [[opensovd-quickstart]] Recipe A | `/components` answers; `/faults` is 404 (expected) |
| D | fleet-management compose (Grafana + Influx) **with** `playbook/fixes/fleet-management-bridge.override.yaml` | [[sdv-blueprints-quickstart]] Recipe A + [[known-broken-recipes]] | Grafana on :3000, `curl :8081/rfms/vehiclepositions?latestOnly=true` answers (plural) |

If any of these is not green by minute 45, ask the coaches for help with that component before you work on the idea.

## 0:45–1:15 Choose the architecture level

Read [[reference-architecture-doctor-whodunit]] section 3 together, commit to L0–L3 and mark L4–L5 stretch. Decide:

- Which fault from the catalogue (section 4) will be the *live demo* fault? Pick one that needs no hardware (stuck sensor via CSV replay).
- Where does "diagnostic truth" live: CDA + OpenBSW virtual ECU (ready today, needs `git submodule update --init openbsw` and the stub-cda profile) or opensovd-core + your own FaultProvider (gap A1, a real contribution)? The first is the safe choice; the second is the bigger contribution.
- Which bonus tech is cheap for *you*: AutoSD prebuilt QEMU image (yes if KVM is available), openDuT EDGAR (only if the organisers host CARL), ThreadX (only with a board).

## 1:15–1:45 Pin sheet and repo skeleton

- Put the pin sheet from [[env-setup-matrix]] into `Cargo.toml` / compose now: up-rust 0.9.0, up-transport-zenoh 0.9.1, zenoh 1.10, databroker 0.7.1, VSS 6.1, Ankaios 1.x syntax.
- Decide kuksa.val.v2 everywhere ([[pitfalls-top20]] #1).
- Create the event schema crate (heartbeat / fault / mitigation) from the proposal in [[uprotocol-howto]]; other teams can reuse it, which speaks to Community Benefit.
- Start the README as the Solution Plan draft: problem, architecture diagram, which Eclipse projects and *how they are wired*, what gets injected, what evidence appears where. Development Methods is 20 % of the score.

## 1:45–2:00 Write the Solution Plan skeleton against the rubric

| Criterion (weight) | What the plan must say |
|---|---|
| Ecosystem Integrability (27 %) | the list of projects on the spine and the seam between each pair (gRPC, UUri, REST, manifest) |
| Development Methods (20 %) | repo layout, manifests, scenario CSVs, how a second team could run it |
| Problem Solving (13 %) | the story and the fault catalogue |
| Working Demo (10 %) + Code does what it claims (10 %) | the live fault and the three places its evidence appears |
| Jury: Pitch, Community Benefit, Contribution Focus (20 %) | the gap you will file or fix: `/faults` in opensovd-core (#156), evidence schema crate, Ankaios states → SOVD, openDuT executor |

## Things to remember

- Zenoh needs a router on this Wi-Fi. ([[zenoh-overview]])
- Ankaios workloads use `--net=host`. ([[ankaios-howto]])
- Watchdogs use timestamps, not value changes. ([[vss-kuksa-howto]])
- Do not start from the HackFest S-CORE branches. ([[hackfest-esslingen-2026]])
- Check the Chapter 4 org again at 14:00 for the Guardian code.

## Where to get help

Ask the coaches for OpenSOVD, S-CORE, openDuT, Ankaios or KUKSA questions; the official coach list is at https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/. HackFest openDuT results: [[hackfest-opendut-playground]]. Self-help: [[faq]], [[debugging-checklists]].
