---
title: Chapter 4 Freestyle (HackFest) track
type: event
component: none
tags: [event, chapter4, freestyle, hackfest, contributions, blueprints]
status: draft
sources:
  - https://eclipsesdv.org/events/eclipse-sdv-hackathon-chapter-4/
  - https://eclipsesdv.org/blogs/announcing-the-eclipse-sdv-hackathon-chapter-4-may-the-fourth-be-with-you/
  - https://www.eclipse.org/mhonarc/lists/sdv-wg/msg00865.html
  - https://www.eclipse.org/mhonarc/lists/sdv-wg/msg00870.html
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_Hackathon_Guide_Book.pdf
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf
  - https://eclipsesdv.org/blogs/the-first-sdv-hackfest-esslingen-2026-hands-on-integration-real-vehicles-and-open-code/
last-verified: 2026-10-03
related:
  - "[[chapter4-overview]]"
  - "[[hackfest-esslingen-2026]]"
  - "[[sdv-blueprints-overview]]"
  - "[[opensovd-overview]]"
  - "[[s-core-overview]]"
  - "[[openbsw-overview]]"
  - "[[opendut-overview]]"
---

# Chapter 4 Freestyle track ("HackFest Track")

Called "Track 2: Freestyle Track" on the event page and Eventbrite, and "HackFest Track" in the announcement blog, guide book and scorecards - same thing. Part of [[chapter4-overview]].

## What it is
- Audience (guide book): professionals, core contributors and project experts. Focus: "Everything that brings the Eclipse SDV Projects forward!" - project integration and innovation, new project features, interfacing multiple projects.
- Event page: develop new features and capabilities, create integrations and interfaces, improve existing project functionality, contribute directly to Eclipse SDV open source projects, "collaborating closely with project maintainers and community experts".
- Primary deliverable: **real Eclipse project pull requests** submitted to the repositories, or filed **Eclipse SDV Blueprints issues** (per the Blueprints process). Announcement blog: success is "accepted pull requests to Eclipse SDV projects or completed issues within the Eclipse SDV Blueprints initiative."
- It is **not primarily a business-pitch competition** (scorecards). Separate ranking from the Innovation track.
- Sibling to the HackFest in Esslingen (28-29 Apr 2026: no winners, shared architecture, real cars) - see [[hackfest-esslingen-2026]]; but unlike Esslingen, Chapter 4's track is scored.

## Rules specific to this track
- Choose the track on Day 1 after challenge presentations; no switching afterwards.
- Prepared code is allowed only if **declared clearly** and presented to the HackMC at the end of Day 1.
- Same logistics, Solution Plan (Day 1, 18:00), Day 3 8-minute coach interview, code freeze 08:00 Day 3 as in [[chapter4-overview]].

## What counts (scoring)
Freestyle modes (Evaluation Forms):
| Mode | What | Scoring |
|---|---|---|
| A. Existing Project Work | existing issue, PR, bug, doc gap, test gap, integration gap or Blueprint task | preferred; highest scores possible |
| B. Existing Work + Improvement | start from existing work, add analysis, integration, docs, tests or proposed extension | highest scores if the existing work is clearly advanced |
| C. New Improvement Idea | something not previously listed | allowed; scores high only if tied to a real project need and left as a follow-up issue, proposal or reusable artefact |

Weights: Contribution Value 25 % (5 = valuable enough the community should continue it), Technical Quality and Maturity 25 % (5 = near merge-ready), SDV Ecosystem Impact 20 % (4-5 = connects/improves interaction between multiple projects; Blueprint pattern, integration path, contributor workflow), Reusability and Maintainability 10 % ("could another contributor pick this up next week?") - HackCoaches 80 %; Jury 20 %: Pitch and Handover Clarity 8 %, Community Benefit and Continuation Story 7 %, Contribution Focus and Initiative 5 % (3 = works on an existing issue/gap; 4-5 = visibly advances it and leaves next steps). What follows directly for your team: get a PR **opened** (even draft) or an issue **filed** early and link it in the Solution Plan; "slides alone do not count".

The same extra-technology bonus (openDuT, Java/Jakarta EE, ThreadX, AutoSD; +0.10 each, capped at 0.40) is stated to apply to "all challenges" - the forms do not say explicitly it applies to Freestyle; the heading says "Bonus Layer for All Challenges". Confirm with the HackMC.

## Which projects are seeking contributions
**No official list of open issues or "seeking contributions" projects is published** for Chapter 4. On 2026-10-03 the org's public page showed only its `.github` profile repo; starter repos may appear during the event - check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four. No source found names specific issues. What the sources do tell us:
- The call for coaches (6 May 2026, sdv-wg msg00865) said the event would "concentrate on, but not be limited to" challenges around **Eclipse S-CORE, Eclipse OpenBSW and Eclipse OpenSOVD** (the Esslingen trio, with openDuT as the test infrastructure there).
- The Esslingen HackFest report names concrete friction that became upstream work, which is the best proxy for open needs: OpenSOVD x S-CORE integration (building OpenSOVD as part of S-CORE; Raspberry Pi on EB corbos Linux), OpenSOVD Classic Diagnostic Adapter (CDA) diagnostic-description issues with BMW/Porsche vehicles, OpenBSW virtual ECU + CDA + Grafana demo, web UIs and AI/MCP interfaces for OpenSOVD, openDuT remote access (NetBird sessions, CAN support, kernel modules, EDGAR on S-CORE image, documentation). These feed "upstream project work, documentation improvements, interoperability discussions". See [[opensovd-overview]], [[s-core-overview]], [[openbsw-overview]], [[opendut-overview]].
- Eclipse SDV Blueprints issues are the explicitly named alternative target: [[sdv-blueprints-overview]].
- The Doctor Whodunit challenge asks for its output to be "packaged as a reusable SDV Blueprint" - cross-over opportunity: a Freestyle team can build the reusable Blueprint scaffolding, evidence format, or the openDuT fault-campaign library that Innovation teams consume (a suggestion, not an official one).
- Who can review PRs: ask the coaches for your project (OpenSOVD, OpenBSW, openDuT, uProtocol, Blueprints, AutoSD and others); see the official coach list (https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/).

## Checklist for your Freestyle team
1. Which repo and which issue/PR? If none, mode C: file the issue first.
2. Prepared code declared to HackMC on Day 1?
3. Is a maintainer or coach for your project pinged and aware? Ask early about contribution rules (CLA/ECA: the Eclipse Contributor Agreement is required for Eclipse project PRs - general Eclipse practice, not stated in these sources).
4. Plan an artefact reviewable on Day 3 morning: PR link, CI status, doc, reproducible steps.

## Questions to ask the organisers
- Is there a curated "good first issues for the hackathon" list? None published; ask the HackMC and the project coaches.
- How are PRs counted if merged after the event? Scorecards value "reviewable" and "near merge-ready", not merged.
