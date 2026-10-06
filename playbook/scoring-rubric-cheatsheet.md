---
title: Chapter 4 scoring rubric - cheat sheet
type: playbook
component: none
tags: [scoring, rubric]
status: reviewed
sources:
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_Hackathon_Guide_Book.pdf
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/SolutionPlan_Template
  - https://eclipsesdv.org/blogs/announcing-the-eclipse-sdv-hackathon-chapter-4-may-the-fourth-be-with-you/
  - https://eclipsesdv.org/events/eclipse-sdv-hackathon-chapter-4/
  - https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
  - repos/hackathon-ch4-dotgithub/profile/README.md
  - repos/hc3-SolutionPlan_Template/README.md
last-verified: 2026-10-03
related:
  - "[[chapter4-overview]]"
  - "[[chapter4-freestyle-track]]"
  - "[[hackathon-patterns]]"
  - "[[chapter3-retrospective]]"
---

# Chapter 4 scoring rubric - cheat sheet

One page: how your team is scored and what the rubric rewards. Weights and quoted wording are verbatim from `https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf` (EF) and `https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_Hackathon_Guide_Book.pdf` (GB). Anything marked *(inferred)* is this repo's reading, not an organiser rule. Event context: [[chapter4-overview]], [[chapter4-freestyle-track]].

The one rule to remember (EF): **"Only demonstrated or repository-verifiable work counts. Slides alone do not count for technical scoring. Prepared code must be declared clearly."**

## 1. Timeline and hard deadlines
| When | What | Source |
|---|---|---|
| Day 1 (Tue 6 Oct), before/at kick-off | Declare ALL prepared work to the HackMC in person; Freestyle: present prepared code at end of Day 1 | GB s.3, s.8 |
| Day 1, 11:30-12:30 | Teams and challenge/track finalised; no changes after Day 1 | GB milestones, s.3 |
| **Day 1, 18:00** | **Solution Plan delivered to coaches** | GB s.4, s.5 |
| Day 2 (Wed 7 Oct) | Interview slots for Day 3 assigned to teams | GB s.5 Step 2 |
| **Day 3 (Thu 8 Oct), 08:00** | **Code freeze**: "Deadline for final project and code repository uploads" | GB milestones |
| Day 3, 09:00-10:30 (or 09:30-11:00, see s.6) | HackCoach technical interviews, "exact 8-minute interview window", 1-2 members or full team | GB s.5 |
| Day 3, after interviews | Coaches consolidate scores and select finalists ("a total number of 7") | GB s.5 Step 2 |
| **Day 3, 11:00** | **Pitch deck upload deadline** | GB s.5 |
| Day 3, 12:00-13:30 | Finalist pitches: 10 min pitch + 5 min jury Q&A | GB milestones |
| Day 3, 13:30-14:30 / 14:30-15:30 | Lunch + jury deliberation / award ceremony | GB milestones |

## 2. How the score is computed
**Split** (EF): "HackCoaches evaluate 80% of the score based on technical substance, impact, and demonstrated/repository-verifiable evidence. Jury members evaluate 20% based on final pitch quality, value communication, delivery, and contribution story." Scale 0-5 per criterion (0 "Not available / not shown", 1 "Very weak / only claimed", 3 "Solidly fulfilled", 5 "Excellent / clearly above expectations"). Tracks are ranked separately.

**Innovation Track** (EF "Innovation Track - Combined Score Overview"):
| Criterion | Weight | Who |
|---|---|---|
| Problem Solving | 13% | HackCoaches |
| Eclipse SDV Ecosystem Integrability | 27% | HackCoaches |
| Development Methods | 20% | HackCoaches |
| Working Demo | 10% | HackCoaches |
| Code Does What It Claims | 10% | HackCoaches |
| Pitch & Handover Clarity | 8% | Jury |
| Community Benefit & Continuation Story | 7% | Jury |
| Contribution Focus & Initiative | 5% | Jury |

**Freestyle / HackFest Track** (EF "Freestyle / HackFest Track - Combined Score Overview"): Contribution Value 25%, Technical Quality & Maturity 25%, Eclipse SDV Ecosystem Impact 20%, Reusability & Maintainability 10% (HackCoaches); Pitch & Handover Clarity 8%, Community Benefit & Continuation Story 7%, Contribution Focus & Initiative 5% (Jury).

**Extra Technology bonus** (EF, verbatim): "Extra Technology Points are a bonus layer on top of the regular 100% evaluation. They do not modify the existing track weighting. Award points only when the technology is meaningfully used in code, configuration, deployment, integration, testing, demo, PR, issue, or a reproducible setup. A logo or name on a slide does not count." +0.10 each for Eclipse openDUT, Java / Jakarta EE, Eclipse ThreadX, Eclipse AutoSD. "Bonus calculation: number of selected technologies x 0.10. Maximum bonus: +0.40. Final Score = MIN(5.00, Base Weighted Score + Extra Technology Bonus)."

What the numbers mean in practice *(inferred arithmetic)*:
- One point on Integrability (0.27) is worth more than two bonus technologies (0.20). Invest in integration depth before bonus-hunting.
- One bonus technology (0.10) equals one point on Working Demo or Code Does What It Claims. Cheap if it is already in the challenge stack: openDuT and AutoSD are listed in both Innovation challenges (`repos/hackathon-ch4-dotgithub/profile/README.md`); ThreadX and Java are not.
- Coaches control 80% and pick the finalists; a team that is not a finalist gets no jury score at all, so the 8-minute interview decides most outcomes.

## 3. What the rubric rewards - evidence to show in the 8 minutes *(inferred, built on the EF level definitions)*
Each line: EF wording for 5, then what a reviewer should be able to see or click in your repo or demo.

**Innovation Track - HackCoaches (80%)**
- **Problem Solving 13%** - 5 = "Clear measurable value, realistic usage, convincing outcome." See: one sentence naming user + hazard (e.g. thermal runaway warning, child left in car), a number the demo proves (warning latency, detection time, false-positive rate), and the demo showing that number.
- **Ecosystem Integrability 27%** - 5 = "Reusable PR, issue, Blueprint extension or integration or possible blueprint proposal contribution." (4 = "Multiple projects work together in a coherent flow.") See: architecture diagram with the SDV project named on every arrow; the same flow live; a link to an opened PR/issue upstream or a Blueprint-shaped folder (README, manifests, how to reuse). No link = cap at 4.
- **Development Methods 20%** - 5 = "Mature process, architecture, QA, traceability, open-source handover." See: GitHub issues/project board used since Day 1, PRs with reviews (not all commits on main by one person), tests in CI, ADR or decision log, README matching the Solution Plan.
- **Working Demo 10%** - 5 = "Stable, reproducible demo with variants or failure handling." See: the EF reviewer question answered live ("What happens when an input changes?"): change an input, inject a fault, show recovery; a second run gives the same result.
- **Code Does What It Claims 10%** - 5 = "Reproducible, understandable, well defined CI pipelines and ready for open-source follow-up." See: you point to the core function in the repo within 30 s; an honest list of "complete / mocked / prepared" (the EF reviewer question asks exactly this); green CI badge; one-command start.

**Innovation Track - Jury (20%, finalists only)**
- **Pitch & Handover Clarity 8%** - 5 = "Jury can immediately understand what happened and why it matters." Slide with repo/PR links and known limitations.
- **Community Benefit & Continuation Story 7%** - 5 = "a compelling continuation story with clear links to PRs, issues, documentation, maintainers, and follow-up actions". A "what happens next week" slide naming a maintainer.
- **Contribution Focus & Initiative 5%** - 5 = "substantially advances existing project work and leaves it in a state that is easy for the community to review, continue, or adopt."

**Freestyle Track - HackCoaches (80%)** (see [[chapter4-freestyle-track]] for modes A/B/C)
- **Contribution Value 25%** - 5 = "valuable enough that the Eclipse SDV community should actively continue it after the event." See: PR/issue URL in the upstream repo, maintainer comment or reaction on it.
- **Technical Quality & Maturity 25%** - 5 = "Near merge-ready": "Well-structured, documented, validated, and close to adoption." See: upstream CI green on the PR, tests added, follows project contribution rules.
- **Ecosystem Impact 20%** - 5 = "Blueprint pattern, integration path, or contributor workflow." See: touches two or more SDV projects or makes one easier to adopt.
- **Reusability & Maintainability 10%** - EF reviewer question: "Could another contributor pick this up next week without your help?" See: setup steps, known limitations, next-step issues filed.

## 4. Solution Plan (Day 1, 18:00)
The Chapter 3 `SolutionPlan_Template` (`https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/SolutionPlan_Template`, `repos/hc3-SolutionPlan_Template/README.md`) is a README with two parts, matching GB s.5 Step 1 for 2026:
1. **Your Team at a Glance**: Team Name / Tagline (plus "create a sheet of paper with your team name on the desk"), Team Members table (Name, GitHub Handle, Role(s)), Challenge, Core Idea ("Sketch something that helps understand e.g. mermaid chart").
2. **How Do You Work**: Development Process (Planning & Tracking; Quality Assurance - "testing, documentation, code reviews"), Communication, Decision Making.

No 2026 template repo was published as of 2026-10-03: the org's public page showed only its `.github` profile repo; starter repos may appear during the event, so check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four. Until then, assume the same shape *(inferred)*.

Filling it fast *(inferred)* - 30 minutes, as the repo README, written so it doubles as evidence for Development Methods (20%) and Code Does What It Claims (10%, which scores against "the solution plan"):
- Core Idea: three sentences (user, problem, demo moment) + one mermaid diagram with the SDV project on each box/arrow; mark the bonus technologies you intend to use.
- Planning: "GitHub issues + one project board; one issue per box in the diagram". QA: "PR per feature, one reviewer, smoke test in CI by Day 2 noon".
- Communication / decisions: stand-up times (e.g. 09:00, 14:00, 20:00), one tie-breaker person named.
- Do not over-promise: everything in the Core Idea will be checked against the code on Day 3.

## 5. Pitch (finalists): 10 min + 5 min Q&A
Official pitching instructions: "tbd" (`https://github.com/Eclipse-SDV-Hackathon-Chapter-Four`). Chapter 3 used a provided slide template ([[chapter3-retrospective]]); expect one on site *(inferred)*.

Suggested 10-minute shape *(inferred, mapped to the jury scorecards)*: problem + user (1 min) -> architecture with SDV projects (1.5) -> live demo of the end-to-end flow incl. one failure/variant (4) -> evidence chain: repo, CI, PR/issue/Blueprint links (1.5) -> what is mocked, what next, who continues it (1.5) -> one-sentence takeaway (0.5).

Live demo vs video: the EF Working Demo question asks for a "working live demo", and the interview is "an 8-minute interview and live demo" (GB s.4). Aim for live in the interview; a recorded video in the repo is a fallback for stage failure, not a substitute *(inferred)*.

Common failures in past editions, from [[hackathon-patterns]] (s.3, s.2):
- Integration without a user story reached finals but not the podium (itself inferred in that note).
- Over-scoped plans; the jury wanted one clean end-to-end demo.
- Environment and transport bridges eating Day 1 (each bridge "is a half-day").
- Repo hygiene: lock files and 600 MB-2.4 GB repos; pitch deck as the only artefact (LastOneStanding had no verifiable code - under 2026 rules that scores near 0 on coach criteria).
- Freestyle: EF says the track "is not primarily a business-pitch competition" - pitch the contribution and handover, not a market.

## 6. Questions to ask the organisers
The published sources conflict on these points; ask the HackMC on Day 1.
1. **Capacity**: "room for just 60 hackers" (`https://eclipsesdv.org/blogs/announcing-the-eclipse-sdv-hackathon-chapter-4-may-the-fourth-be-with-you/`) vs "capped at 50 people" (GB s.1).
2. **Venue address**: Am Seemooser Horn 20, 88045 Friedrichshafen (`https://eclipsesdv.org/events/eclipse-sdv-hackathon-chapter-4/`) vs "Fallenbrunnen 3" (`https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340`).
3. **Interview window**: 09:00-10:30 (GB milestones) vs "9:30 AM-11:00 AM" (GB Key Deadlines); the latter collides with the 11:00 deck deadline for late-slot teams.
4. **Finalists**: "7 finalist teams combined across both event locations" (GB) - 2025 wording; 2026 is single-site, and GB s.4 says the Hack MC decides the number on Day 1.
5. **Innovation jury weights**: the combined overview lists jury items 8% + 7% + 5%, but the Innovation Jury scorecard page scores "Selling Points" Pitch Deck 4%, Business Perspective 4%, Pitch Delivery 4%, Creativity and Surprise 8% (EF). Which sheet the jury actually fills is unclear.
6. **Bonus for Freestyle**: heading says "Bonus Layer for All Challenges"; the Freestyle section does not repeat it (EF).
7. **Pitching instructions** still "tbd"; no 2026 Solution Plan template repo.
