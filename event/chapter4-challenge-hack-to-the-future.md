---
title: Chapter 4 challenge - Hack to the Future
type: event
component: none
tags: [event, chapter4, challenge, portability, child-presence-detection, openbsw, opendut, uprotocol]
status: draft
sources:
  - https://www.eclipse-foundation.events/event/sdv-hackathon-chapter-four/summary
  - https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four
  - https://eclipsesdv.org/blogs/sdv-hackathon-2026-interview-with-two-hack-coaches/
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf
  - https://blogs.eclipse.org/post/christian-heissenberger/unveiling-2025-sdv-hackathon-challenges-ideas-impact-%E2%80%93-faster
last-verified: 2026-10-03
related:
  - "[[chapter4-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter3-retrospective]]"
  - "[[uprotocol-overview]]"
  - "[[opendut-overview]]"
  - "[[openbsw-overview]]"
  - "[[autosd-overview]]"
---

# Chapter 4 challenge - Hack to the Future

Track 1 (Innovation) challenge. Part of [[chapter4-overview]]; sibling: [[chapter4-challenge-doctor-whodunit]].

## Challenge text, verbatim
Identical on the event page, Eventbrite and the GitHub org README.

> **Hack to the Future**
>
> Your DeLorean is waiting. Build an SDV feature that jumps between hardware and virtual setups: develop it against simulated endpoints, then move it onto embedded controllers and real cars without changing your service code. uProtocol keeps services portable across platforms and transports, and openDuT rewires the testbench on the fly, so switching setups means no replugging of cables.
>
> The reference scenario is the Guardian Loop, a child presence detection feature of the kind Euro NCAP now rewards in its safety ratings: a child left in a parked car is at risk as the cabin heats up, so a sensor detects occupancy and rising temperature, a decision service on an AutoSD-built HPC image evaluates the risk, and an OpenBSW-based zonal controller responds by opening a window, running the fan, or sounding the alarm. As a stretch goal, drive the on-site Flux Capacitor and Time Circuits displays from your services.
>
> _Where we're going, we don't need cables!_
>
> **Prerequisites:** Basic knowledge of Rust and C++, Linux/containers, pub/sub messaging
>
> **Projects:** uProtocol, openDuT, OpenBSW, AutoSD

Who can help: ask the coaches for uProtocol, openDuT, OpenBSW, AutoSD or Rust/embedded questions; see the official coach list (https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/).

## Scenario decoded: the Guardian Loop
Not to be confused with Doctor Whodunit's "Battery Thermal Guardian" - same "Guardian" naming, different feature.
| Stage | Component | Note |
|---|---|---|
| Sensor: occupancy + cabin temperature rising | Simulated endpoint at first, real sensor later; the sensor side can be the zonal controller or a separate node (not specified) | - |
| Decision service evaluating risk | A service (Rust per the prerequisites) on an **AutoSD-built HPC image** | [[autosd-overview]] |
| Zonal controller reacts: open window, run fan, sound alarm | **OpenBSW**-based firmware (C++) on an embedded target; a published coach interview (https://eclipsesdv.org/blogs/sdv-hackathon-2026-interview-with-two-hack-coaches/) says OpenBSW gets teams to "target smaller embedded platforms than most are probably used to" | [[openbsw-overview]] |
| Glue between all stages | **uProtocol** - the portability claim: service code unchanged, only the transport/endpoint changes | [[uprotocol-overview]] |
| Rewiring testbench "on the fly" | **openDuT** (virtual <-> physical, no recabling) | [[opendut-overview]] |
| Stretch | Drive on-site "Flux Capacitor" and "Time Circuits" displays (Back to the Future props) from your services - interface not published | - |

The core claim your team must demonstrate: **the same service binary/config runs unchanged in three setups** (all-virtual, embedded controller in the loop, real car), and switching is done via openDuT, not by hand. Which "real car" is available on site is not published (the call for coaches asked community members to bring vehicles; see [[chapter4-overview]]).

Published framing (Christian Schilling, interview 9 Sep, https://eclipsesdv.org/blogs/sdv-hackathon-2026-interview-with-two-hack-coaches/): "close to a full real world end-to-end safety feature ... a peek at many different levels of the automotive stack." The interview also says they expect surprising solutions.

KUKSA is not in this challenge's project list; it is optional (for example as a VSS signal store next to the core path), not part of it.

## What the rubric rewards
From the public Evaluation Forms (https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf); weights in [[chapter4-overview]]. "Only demonstrated or repository-verifiable work counts."
1. **Problem Solving (13 %) and Working Demo (10 %)**: show the jump between setups live with zero change to service code - a scripted demo that flips from simulated sensor to the embedded/real one is the clearest proof.
2. **A genuine OpenBSW target** (POSIX/virtual build is the low-risk start; a real MCU is the stretch) running the actuator logic with uProtocol-compatible messaging. The embedded-to-uProtocol link is the hard part; three ways, none built yet:
   - CAN frames from OpenBSW into a small up-rust adapter on the HPC that publishes UMessages. Lowest risk; the CAN half is reproduced, see [[openbsw-howto]].
   - SOME/IP: OpenBSW ships `libs/bsw/cpp2someip` (repos/openbsw/libs/bsw/cpp2someip/doc/index.rst), uProtocol has a SOME/IP mapping (repos/up-spec/up-l1/someip.adoc), plus `up-transport-vsomeip` and a uStreamer `zenoh_someip` example (repos/up-streamer-rust). Interop with vsomeip is untested.
   - zenoh-pico on an MCU (not OpenBSW).
3. **Ecosystem Integrability (27 %)**: 4 = "multiple projects work together in a coherent flow" (uProtocol + openDuT + OpenBSW + AutoSD in one flow); 5 = a "reusable PR, issue, Blueprint extension or integration or possible blueprint proposal" (e.g. an issue/PR for the missing transport, docs).
4. **Code Does What It Claims (10 %)**: realistic safety logic you can show in code - thresholds for temperature rise, occupancy confidence, response order (fan -> window -> alarm), failure handling. The Euro NCAP framing is from the challenge text; the exact protocol is not named.
5. **Development Methods (20 %)**: GitHub task split, tests, review, docs, clear interfaces; the Day 1 18:00 Solution Plan.
6. **Extra Technology bonus** (+0.10 each, max +0.40, final capped at 5.00, only if meaningfully used): openDuT and AutoSD are in this challenge (+0.20). ThreadX would give +0.10 if the embedded side used it (OpenBSW supports its own RTOS layer; unverified); Java is also eligible.
7. **Jury (20 %)**: Pitch and Handover Clarity 8 %, Community Benefit and Continuation Story 7 %, Contribution Focus and Initiative 5 %. The Flux Capacitor / Time Circuits stretch goal is a cheap way to address the "creativity and surprise" item on the jury scorecard (how its 8 % combines is unverified, see [[chapter4-overview]]).

## Prerequisites
Basic Rust and C++, Linux/containers, pub/sub. Ask the coaches for embedded/OpenBSW, uProtocol, AutoSD, Rust or openDuT topics: https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/

## Compared with 2025
New challenge in 2026 (2025 had "Virtual SDV Lab" and "Mission: Update Possible", see [[chapter4-challenge-doctor-whodunit]] for the comparison table and [[chapter3-retrospective]]). Thematic echoes: the 2025 Virtual SDV Lab was also about virtual-first development of a feature that integrates into a real SDV system, and both years use uProtocol and OpenBSW/embedded targets in some challenge; the 2026 version adds the explicit virtual->embedded->real portability requirement, openDuT and AutoSD, and drops Zenoh/Kuksa/CARLA/ThreadX from the project list.

## Questions to ask the organisers
- What hardware is on the table (MCU boards: S32K1xx? STM32? Raspberry Pi/HPC node?) and who provisions the AutoSD image?
- Is a reference Guardian Loop codebase provided? (On 2026-10-03 the org's public page showed only its `.github` profile repo; starter repos may appear during the event - check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four.)
- Which uProtocol transport between HPC and OpenBSW controller is expected (Zenoh? SOME/IP? CAN-based?)
- How is the "real car" accessed, and is there a safety briefing?
- Where are the Flux Capacitor / Time Circuits displays, and what is their interface?
