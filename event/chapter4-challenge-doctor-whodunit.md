---
title: Chapter 4 challenge - Doctor Whodunit!!
type: event
component: none
tags: [event, chapter4, challenge, fault-injection, safety-evidence, battery, opendut, opensovd]
status: draft
sources:
  - https://www.eclipse-foundation.events/event/sdv-hackathon-chapter-four/summary
  - https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four
  - https://eclipsesdv.org/blogs/sdv-hackathon-2026-interview-with-two-hack-coaches/
  - https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf
  - https://blogs.eclipse.org/post/christian-heissenberger/unveiling-2025-sdv-hackathon-challenges-ideas-impact-%E2%80%93-faster
last-verified: 2026-10-03
related:
  - "[[chapter4-overview]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[chapter3-retrospective]]"
  - "[[opendut-overview]]"
  - "[[uprotocol-overview]]"
  - "[[ankaios-overview]]"
  - "[[opensovd-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[autosd-overview]]"
  - "[[s-core-overview]]"
  - "[[sdv-blueprints-overview]]"
---

# Chapter 4 challenge - Doctor Whodunit!!

Track 1 (Innovation) challenge. Part of [[chapter4-overview]]; sibling: [[chapter4-challenge-hack-to-the-future]].

## Challenge text, verbatim
Identical on the event page, Eventbrite and the GitHub org README (sources above).

> **Doctor Whodunit!!**
>
> Something in the vehicle just failed — whodunit? Travel your system's timeline: inject faults you've seen before or expect in the future, and let the evidence tell the story.
>
> Build a safety evidence factory around the Battery Thermal Guardian — an EV thermal-runaway early-warning service. Regulations require occupants be warned minutes before a battery thermal event turns dangerous, so a stale or stuck cell-temperature signal silently disarms the entire warning chain. Run the Guardian on an AutoSD-based runtime, supervised by Ankaios, exchanging heartbeat, fault, and mitigation events over uProtocol, with diagnostic truth exposed through OpenSOVD. openDuT replays repeatable fault campaigns at three levels — delayed or duplicated messages, stuck or implausible VSS signals, even device-level sensor dropout — while your evidence collector links hazard → safety goal → injected fault → detection → mitigation → verdict for every test, packaged as a reusable SDV Blueprint.
>
> _Every fault leaves evidence. Solve the case._
>
> **Prerequisites:** Basic Rust or Python, Linux/containers, pub/sub messaging
>
> **Projects:** openDuT, uProtocol, Ankaios, OpenSOVD, KUKSA, AutoSD, S-CORE, SDV Blueprints

Who can help: ask the coaches for openDuT, uProtocol, Ankaios, OpenSOVD, KUKSA, AutoSD, S-CORE or Blueprints questions; see the official coach list (https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/).

## Scenario decoded
| Piece in the text | Meaning for your team | Component note |
|---|---|---|
| Battery Thermal Guardian | The system under test: a service that reads cell temperatures and raises a thermal-runaway early warning. The text only names the service; **no source code, repo or spec for it is published** (on 2026-10-03 the org's public page showed only its `.github` profile repo; starter repos may appear during the event - check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four). You may get a skeleton on Day 1 ("pre-integrated" per event page) - unverified | - |
| "stale or stuck cell-temperature signal silently disarms the warning chain" | The core failure mode: the Guardian must detect freshness/plausibility loss of its input and not stay silent. This is the hazard your evidence should centre on | [[vss-kuksa-overview]] |
| AutoSD-based runtime | Guardian runs on a CentOS/Red Hat Automotive SIG style image | [[autosd-overview]] |
| Supervised by Ankaios | Ankaios workloads/restart policy supervise the Guardian; heartbeat loss is a supervised failure | [[ankaios-overview]] |
| Heartbeat, fault, mitigation events over uProtocol | The event vocabulary: three message classes on uProtocol topics. You may need to define the uProtocol UUris/payloads | [[uprotocol-overview]] |
| Diagnostic truth via OpenSOVD | Faults must be exposed as SOVD resources (faults/DTC-like) so a tester can query "what actually failed" - the "diagnostic truth" is the oracle your verdict compares against | [[opensovd-overview]] |
| openDuT replays fault campaigns at three levels | L1 message level (delay, duplicate), L2 signal level (stuck/implausible VSS values), L3 device level (sensor dropout on a real/virtual device in the testbench) | [[opendut-overview]] |
| Evidence collector: hazard -> safety goal -> injected fault -> detection -> mitigation -> verdict | A traceability record per test case; the "factory" is automation that runs a campaign and emits these records (report/JSON/HTML) | [[s-core-overview]] (listed; role undefined) |
| Packaged as a reusable SDV Blueprint | Output should be a repo structured like an Eclipse SDV Blueprint (README, setup, demo) - this is also what scores 5/5 on the ecosystem criterion | [[sdv-blueprints-overview]] |

S-CORE is listed in the project list but is not mentioned anywhere in the scenario text; its intended role is **unknown** (plausible: S-CORE's safety/FuSa process artefacts or its runtime as a Guardian host; also what the Esslingen HackFest integrated with OpenSOVD, see [[hackfest-esslingen-2026]]). Ask the coaches for S-CORE's role: https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/

Published intent (coach interview with Ramachandran Chakravadhanula, 9 Sep, https://eclipsesdv.org/blogs/sdv-hackathon-2026-interview-with-two-hack-coaches/): "protecting an EV battery thermal-runaway warning chain from faults that could silently disable it"; creative potential in "connect[ing] fault injection, runtime supervision, vehicle data, diagnostics, and safety evidence into one clear and understandable story ... intelligent event correlation, automated root-cause analysis, innovative visualisations, or entirely new ways of linking an injected fault to its detection, mitigation, and final verdict."

## What the rubric rewards
From the public Evaluation Forms (https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf); weights in [[chapter4-overview]]. "Only demonstrated or repository-verifiable work counts."
1. **End-to-end live demo that runs a fault campaign** (Working Demo 10 %, Code Does What It Claims 10 %): inject one fault at each of the three levels, show detection, mitigation event, and an auto-generated verdict. A stable, repeatable run with variants/failure handling is what a 5 on "Working Demo" asks for.
2. **Many projects working in one coherent flow** (Ecosystem Integrability 27 %, the heaviest item): the rubric rewards "multiple projects work together in a coherent flow" (4) and a "reusable PR, issue, Blueprint extension or integration" (5). Using AutoSD + Ankaios + uProtocol + OpenSOVD + openDuT + KUKSA together covers the challenge project list; a PR/issue upstream or a Blueprint proposal tops it.
3. **Real traceability chain**: machine-readable link hazard -> safety goal -> fault -> detection -> mitigation -> verdict, with the OpenSOVD fault state as independent ground truth (not only the Guardian's own log).
4. **Detection of the named failure**: stale/stuck cell temperature must be caught by timeout/freshness and plausibility checks and trigger a mitigation (e.g. degraded-mode warning, safe state). Show that without mitigation the chain "silently disarms".
5. **Process evidence** (Development Methods 20 %): GitHub task split, tests, reviews, documented interfaces; the Day 1 18:00 Solution Plan.
6. **Extra Technology bonus** (+0.10 each, max +0.40, final capped at 5.00, only if meaningfully used): openDuT and AutoSD are already in the challenge (+0.20); Java and ThreadX are not in the challenge text but are also eligible.
7. **Jury (20 %)**: Pitch and Handover Clarity 8 %, Community Benefit and Continuation Story 7 %, Contribution Focus and Initiative 5 %. Business story (who needs safety evidence and why; the regulatory framing comes from the challenge text only - "Regulations require occupants be warned minutes before..." - and the exact regulation is **not named**, so do not cite a specific one without checking).
Likely pitfalls (unverified, from general experience of the stack and the Esslingen HackFest report which cited setup pain with Raspberry Pis, container environments, network sessions, CAN, kernel modules): openDuT edge/CAN setup, AutoSD image availability, Ankaios-uProtocol glue, and time lost on the toolchain. Budget the first half day for getting a green baseline.

## Prerequisites
Basic Rust or Python, Linux/containers, pub/sub messaging. Ask the coaches for OpenSOVD/diagnostics, openDuT, uProtocol, AutoSD or Blueprints topics: https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/

## Compared with 2025 (Chapter 3)
Was this challenge also used in 2025? **The evidence says no**:
- The official 2025 challenge announcement (Christian Heissenberger, 19 Aug 2025) lists exactly two challenges: **"Virtual SDV Lab"** (ADAS/automated-driving feature in a virtual environment: Zenoh, uProtocol, Kuksa, ThreadX, Ankaios, CARLA, Android Auto) and **"Mission: Update Possible"** (secure, auditable OTA from cloud to simulated vehicles: Symphony, uProtocol, ThreadX, openBSW, Ankaios, Muto; UN R155/R156). The Berlin and Porto sites ran those. "Doctor Whodunit" does not appear in that post, and the Chapter 3 GitHub org page (https://github.com/Eclipse-SDV-Hackathon-Chapter-Three) has no mention of it. A web search for the title returns only Chapter 4 pages.
- So "Doctor Whodunit!!" appears to be **new in 2026**; no 2025 source was found.

What is actually different between 2025 and 2026 (see [[chapter3-retrospective]]):
| | Chapter 3 (2025) | Chapter 4 (2026) |
|---|---|---|
| Sites | Berlin and Porto | Friedrichshafen only |
| Format | Two challenges, "accessible vs advanced path" | Two tracks (Innovation + Freestyle), 2 challenges in Innovation |
| Focus | ADAS prototyping, OTA | Safety evidence / diagnostics (this challenge), portability across virtual/embedded/real (other) |
| Technologies | Zenoh, uProtocol, Kuksa, ThreadX, Ankaios, CARLA, Symphony, openBSW, Muto | openDuT, uProtocol, Ankaios, OpenSOVD, KUKSA, AutoSD, S-CORE, Blueprints; Zenoh/ThreadX/Symphony/Muto/CARLA are no longer in the challenge lists (ThreadX survives as a bonus-point technology) |
| Evaluation | Different (see retrospective) | Published 80/20 coach/jury scorecards with extra-technology bonus |

## Questions to ask the organisers
- Is there a provided Guardian codebase/reference (language, repo) and a pre-built AutoSD image? Where does it live (check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four for starter repos)?
- How is the openDuT testbench provisioned (central cluster? per-team? hardware for the L3 device-level dropout)?
- Which OpenSOVD components are expected (CDA, gateway, SOVD server) and what is the fault model/ODX equivalent for the Guardian?
- What is S-CORE's role in this challenge?
- Is the "evidence format" or Blueprint template prescribed? What does "reusable SDV Blueprint" require (see [[sdv-blueprints-overview]])?
