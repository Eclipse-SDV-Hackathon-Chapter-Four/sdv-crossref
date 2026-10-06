---
title: Getting started — Hack to the Future
type: playbook
component: none
tags: [first-two-hours, hack-to-the-future, getting-started, chapter4]
status: reviewed
sources:
  - "[[reference-architecture-hack-to-the-future]]"
  - "[[scoring-rubric-cheatsheet]]"
  - "[[pitfalls-top20]]"
  - "[[hackathon-patterns]]"
last-verified: 2026-10-03
related:
  - "[[first-two-hours-doctor-whodunit]]"
  - "[[gap-register]]"
  - "[[env-setup-matrix]]"
  - "[[faq]]"
---

# Getting started — Hack to the Future

A plan for your team's first two hours. Goal: the feature logic running against a virtual provider (target A), a clear list of which *two other targets* you will hop to, and a Solution Plan that names the portability layers.

## 0:00–0:15 Questions to settle in your team

0. **Have you declared all prepared work to the organisers?** The evaluation form says only demonstrated or repository-verifiable work counts and prepared code must be declared clearly, in person, at kick-off; teams and tracks are frozen after Day 1 11:30–12:30. The pitch deck upload is a separate deadline, Day 3 11:00 ([[scoring-rubric-cheatsheet]]).

1. Who has C++ (OpenBSW) or embedded experience? Who has a board (ESP32, AZ3166, S32K148) *and* its toolchain installed? No board and no toolchain = the embedded leg is the OpenBSW POSIX virtual ECU, which builds in 20 s ([[openbsw-quickstart]]).
2. Does anyone have sudo on their laptop? (vcan and TAP for OpenBSW CAN need it; otherwise the CAN leg runs inside a Docker container with `NET_ADMIN`.)
3. Which "parked" definition will you use? VSS has no `IsParked`: `IsMoving`, parking brake, `SelectedGear`=126 ([[vss-kuksa-overview]]).
4. What are your three targets? Minimum credible set: laptop (CSV provider) → OpenBSW virtual ECU over CAN → AutoSD QEMU image running the same manifest. Real car only if the organisers offer one through openDuT.
5. Has anyone opened the Chapter 4 GitHub org today (https://github.com/Eclipse-SDV-Hackathon-Chapter-Four)? On 2026-10-03 its public page showed only its `.github` profile repo; starter repos may appear during the event.

## 0:15–0:45 Green baseline (parallel)

| Person | Task | Verified recipe | Expected result |
|---|---|---|---|
| A | KUKSA 0.7.1 + overlay with `Cabin.ChildPresence.IsDetected` | [[vss-kuksa-quickstart]] Part B | `ChildPresence.IsDetected: true` after publish |
| B | uProtocol pub/sub over Zenoh | [[uprotocol-quickstart]] Path A | delivered |
| C | OpenBSW `posix-freertos` build and console | [[openbsw-quickstart]] | ECU runs, `help` works (vcan errors are non-fatal) |
| D | service-to-signal blueprint (software horn): submodules, bridge override from `playbook/fixes/`, pin `kuksa-rust-sdk = "=0.2.0"` | [[sdv-blueprints-quickstart]] Recipe B + [[known-broken-recipes]] | `docker logs software-horn` shows activate/deactivate horn |

## 0:45–1:15 Fix the portability layers on a whiteboard

From [[reference-architecture-hack-to-the-future]] section 1: write down what is **fixed** (VSS paths, UUris, the logic crate) and what **varies** (provider, transport, deployment). Put the fixed list in the README now; it is the core of the pitch.

Then choose levels: commit to L0–L2 (virtual → OpenBSW CAN → Ankaios/AutoSD), stretch L3 (MCU with zenoh-pico) and L4 (openDuT/real car). Agree which bonus tech is realistic: AutoSD prebuilt QEMU image is the cheapest +0.10.

## 1:15–1:45 Pin sheet, repo, scenarios

- Pins from [[env-setup-matrix]]; kuksa.val.v2 only.
- One scenario CSV per row of the scenario catalogue (child left, adult present, driving, dropout, cleared). The *same CSVs* run on every target: that is the portability proof.
- The CAN leg needs a DBC and a `kuksa-can-provider` overlay; budget half a day ([[hackathon-patterns]]). Start it on Day 1 afternoon, not Day 2.
- If an MCU is in the room: zenoh-pico in client mode against a `zenohd` router on the HPC, carrying UMessage bytes; there is no official embedded uProtocol client (gap D1), so filing an upstream issue is part of the deliverable per the challenge text.

## 1:45–2:00 Solution Plan against the rubric

| Criterion (weight) | What the plan must say |
|---|---|
| Ecosystem Integrability (27 %) | KUKSA + uProtocol/Zenoh + OpenBSW + Ankaios/AutoSD, with the seam named per hop |
| Development Methods (20 %) | manifests per target, scenario CSVs, a one-command run per target |
| Problem Solving (13 %) | the parked-vehicle child-presence logic and its failure modes (sensor dropout) |
| Working Demo (10 %) + Code does what it claims (10 %) | live hop from CSV provider to the OpenBSW ECU without touching the logic |
| Jury (20 %) | the upstream issue or PR for the embedded transport; the overlay as a COVESA proposal |

## Things to remember

- `IsOccupied` is gone; it is `OccupancyStatus` since VSS 6.0. ([[vss-kuksa-reference]])
- One uProtocol authority per host, lowercase. ([[uprotocol-howto]])
- Run the OpenBSW ECU with stdin from /dev/null or it stops when backgrounded. ([[openbsw-howto]])
- AutoSD has rpi4 and qemu images, no rpi5. ([[autosd-overview]])
- The ThreadX board eats the first hour; only one person on it. ([[threadx-overview]])

## Where to get help

Ask the coaches for OpenBSW, openDuT, KUKSA or Ankaios questions; the official coach list is at https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/. HackFest openDuT results: [[hackfest-opendut-playground]]. Self-help: [[faq]], [[debugging-checklists]].
