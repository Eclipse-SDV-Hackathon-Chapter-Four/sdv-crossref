---
title: Eclipse SDV Hackathon Chapter 4 - overview
type: event
component: none
tags: [event, chapter4, friedrichshafen, zf, logistics, judging]
status: draft
sources:
  - https://eclipsesdv.org/events/eclipse-sdv-hackathon-chapter-4/
  - https://eclipsesdv.org/blogs/announcing-the-eclipse-sdv-hackathon-chapter-4-may-the-fourth-be-with-you/
  - https://www.eclipse-foundation.events/event/sdv-hackathon-chapter-four/summary
  - https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_Hackathon_Guide_Book.pdf
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf
  - https://www.eclipse.org/mhonarc/lists/sdv-wg/msg00865.html
  - https://www.eclipse.org/mhonarc/lists/sdv-wg/msg00870.html
  - https://www.eclipse.org/mhonarc/lists/sdv-wg/msg00897.html
  - repos/hackathon-ch4-dotgithub (commit c7af56b, 2026-08-28)
last-verified: 2026-10-03
related:
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[chapter4-freestyle-track]]"
  - "[[hackfest-esslingen-2026]]"
  - "[[chapter3-retrospective]]"
---

# Eclipse SDV Hackathon Chapter 4 - overview

Snapshot date 2026-10-03 (three days before kick-off). Everything below is from the primary sources listed in the frontmatter; conflicts between sources are called out in "Discrepancies".

## Facts
| Item | Value | Source |
|---|---|---|
| Dates | Tue 6 - Thu 8 Oct 2026. Start 06.10 at 08:00; closing 08.10 at 16:00 | eclipse-foundation.events summary page |
| Venue | Zeppelin Universitaet ("ZF Campus der ZU" / "See Campus", "Lake Campus"), Friedrichshafen, Lake Constance, Germany. Official address: Zeppelin Universitaet gemeinnuetzige GmbH, Am Seemooser Horn 20, 88045 Friedrichshafen | eclipsesdv.org event page; GitHub profile README |
| Host | ZF (facility and hospitality provider) | announcement blog |
| Organiser | Eclipse Foundation / Eclipse SDV working group; partners and sponsors Eclipse SDV and the Eclipse Foundation, "in collaboration with FEDERATE and HAL4SDV"; media partner germantechjobs.de | coaches blog; summary page |
| Hack MC | Christian Heissenberger (Technical Program Manager, Eclipse SDV WG). The guide book also mentions a "Hack MC & Assistant" (assistant unnamed) | coaches blog; guide book |
| Other organisers named | Ana Bukvic (blog author, listed as contact), Sara Gallian (Senior Manager SDV & Automotive Programs); events@eclipse-foundation.org | sdv-wg msg00870; GitHub org profile |
| Cost | Free | eclipsesdv.org event page |
| Language | English | call for coaches (msg00865) |
| Format | Two parallel, co-located tracks. Choose a track on Day 1 after the challenge presentations; no changes after Day 1 | guide book |
| Tracks | Track 1 "Hackathon Challenge" / Innovation Track (two challenges). Track 2 "Freestyle Track" / HackFest Track | all |
| Capacity | "room for just 60 hackers" (blog) vs "max 50 people" (guide book) | see Discrepancies |
| Team size | max 5; pre-formed or join on-site at the team-formation session | guide book |
| Prizes | Top teams get "tech gadgets", special awards, swag; main prizes for first places by cumulative score (per track) | announcement blog; guide book |

Registration: https://www.eclipse-foundation.events/event/sdv-hackathon-chapter-four/registration . As of 2026-10-03 the summary page says **registration is closed**; late joiners should write to events@eclipse-foundation.org. Eventbrite listing (organiser Eclipse Foundation, "8 AM-4 PM") exists but links back to the same registration page.

## Tracks in one paragraph each
- **Hackathon / Innovation track**: teams build on "pre-integrated" SDV projects; focus on application, UX, innovative use case, business value, final pitch. Two challenges: [[chapter4-challenge-doctor-whodunit]] (host ZF presented one of the two challenges) and [[chapter4-challenge-hack-to-the-future]]. Deliverables: business pitch deck plus working demo; bonus points for specific technologies.
- **Freestyle / HackFest track**: real contributions to Eclipse SDV projects - accepted/open PRs or Eclipse SDV Blueprints issues. See [[chapter4-freestyle-track]]. Inspired by the Esslingen HackFest ([[hackfest-esslingen-2026]]).

## Schedule (from the Guide Book, "Chronological Event Milestones")
Treat as the best published schedule, but the guide book still shows traces of 2025 text (see Discrepancies). No session-by-session agenda (talks, challenge presentation time, team-formation start) is published beyond this.

| Day | Time | What |
|---|---|---|
| Day 1 Tue 6 Oct | 08:00-09:00 | Registration and breakfast |
| | 11:30-12:30 | Team and challenge selection finalised |
| | 18:00 | **Solution Plan due** to coaches |
| Day 2 Wed 7 Oct | 08:30 | Breakfast |
| | all day | Intensive hacking, cross-track interaction |
| | evening | Networking dinner (BBQ) |
| | (Day 2) | Interview slots for Day 3 are assigned to teams |
| Day 3 Thu 8 Oct | 08:00 | **Code freeze** - final repo upload |
| | 08:30 | Breakfast |
| | 09:00-10:30 | HackCoach technical interviews (8 min per team) |
| | 11:00 | Pitch deck upload deadline |
| | 12:00-13:30 | Finalist pitches to jury (10 min pitch + 5 min Q&A) |
| | 13:30-14:30 | Lunch, jury deliberation |
| | 14:30-15:30 | Award ceremony, closing |
| | 15:30-16:00 | Closure |

Venue open 08:00-22:00. All meals, snacks, drinks Tue morning to Thu afternoon provided; declare dietary needs at registration. A locked room for small items is available - ask on-site staff. Support channels: Slack `#ask-a-hackcoach` (technical bugs, including 02:00 emergencies) and `#hackathon2026` (venue, general, team forming).

## Team rules (Guide Book)
- All code must be created during the hackathon. Anything prepared beforehand must be declared **in person to the HackMC on Day 1**; the Freestyle track additionally must present prepared code at the end of Day 1. Business ideas may be prepared, assets not.
- Bring your own laptop (standard configuration).
- Eclipse Community Code of Conduct applies to everyone including coaches; report to codeofconduct@eclipse.org.
- Solution Plan (Day 1, 18:00): "Team at a glance" (name/tagline, roster with GitHub handles, roles, declared challenge, core idea) and "How do you work" (light dev process, QA strategy, communication, decision making).
- Day 3 interview: 8 minutes, 1-2 team members (or whole team) in the room, the rest keep working.
- Finalists: 7 teams total (guide book says "combined across both event locations" - stale 2025 wording, see below). Number of finalists is decided by the Hack MC on Day 1.
- Rankings are calculated separately per track.

## Judging criteria (published: Evaluation Forms PDF)
Split: **HackCoaches 80 %** (technical substance, impact, repo-verifiable evidence - during the 8 min interview/live demo) and **Jury 20 %** (final pitch). Jury: 5-7 members, evaluating finalists only; they do not score teams from their own organisation. Jury members are not named in any source I found. "Only demonstrated or repository-verifiable work counts. Slides alone do not count for technical scoring." Score scale 0-5.

Innovation track weights:
| Criterion | Weight | Scored by |
|---|---|---|
| Problem Solving | 13 % | coaches |
| Eclipse SDV Ecosystem Integrability (27 % - the biggest single item; 5 = reusable PR/issue/Blueprint extension) | 27 % | coaches |
| Development Methods (GitHub, task split, tests, review, docs, interfaces) | 20 % | coaches |
| Working Demo | 10 % | coaches |
| Code Does What It Claims | 10 % | coaches |
| Pitch and Handover Clarity | 8 % | jury |
| Community Benefit and Continuation Story | 7 % | jury |
| Contribution Focus and Initiative | 5 % | jury |

The jury scorecard also lists "Selling Points" sub-items (pitch deck 4 %, business perspective 4 %, delivery 4 %, creativity and surprise 8 %); the PDF's combined table does not show these in the 100 % total, so exactly how they combine is **unverified** - ask the HackMC. The 1 Sep sdv-wg mail says the jury weighs "usability, creativity, coding complexity, completeness, originality, project fusion, and efficiency".

**Extra Technology bonus** (on top of base, +0.10 each, max +0.40, final capped at 5.00): Eclipse openDuT, Java/Jakarta EE, Eclipse ThreadX, Eclipse AutoSD - only if meaningfully used in code/config/deployment/test/demo/PR (a logo on a slide does not count). Note openDuT and AutoSD are already named in both challenges; Java and ThreadX are not.

Freestyle weights: Contribution Value 25 %, Technical Quality and Maturity 25 %, SDV Ecosystem Impact 20 %, Reusability and Maintainability 10 % (all coaches = 80 %); jury: Pitch and Handover 8 %, Community Benefit and Continuation 7 %, Contribution Focus 5 %. Details in [[chapter4-freestyle-track]].

## Hardware and infrastructure provided
Published: venue facilities and hospitality by ZF; real cars on site were solicited ("bring your vehicles", Mercedes/BMW/Porsche were at Esslingen) - whether any are confirmed for Friedrichshafen is **unverified**; "on-site Flux Capacitor and Time Circuits displays" for the Hack to the Future stretch goal; teams "build on pre-integrated Eclipse SDV technologies" in Track 1. Nothing is published about boards, ECUs, openDuT testbench hardware, cloud credentials, Wi-Fi, or repo templates for the challenges; on 2026-10-03 the org's public page showed only its `.github` profile repo (last push 2026-08-28); starter repos may appear during the event - check https://github.com/Eclipse-SDV-Hackathon-Chapter-Four. Participants bring their own laptops. Expect these to be handed out on Day 1 - **open question**.

## Discrepancies and open questions
1. Capacity: 60 (announcement blog) vs 50 (guide book).
2. Venue address: eclipsesdv.org and GitHub use Am Seemooser Horn 20 (See Campus); Eventbrite uses "Fallenbrunnen 3" (Zeppelin University main campus). Blog says See Campus; go with Am Seemooser Horn 20 but confirm.
3. Interview window: guide book milestones say 09:00-10:30; the deadlines section says 09:30-11:00. Pitch deck deadline 11:00 either way.
4. Guide book "both event locations" is a leftover from 2025 (Berlin + Porto); in 2026 everything is in Friedrichshafen. Whether 7 finalists still applies to a single-site event is unverified.
5. Coach count: blog subtitle says "Nine hack coaches" but the post introduces seven ("Seven of Nine") - see the official coach list (https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/).
6. GitHub README "Pitching Instructions: tbd".
7. Doctor Whodunit is sometimes assumed to have run in 2025 as well; no evidence of that was found, see [[chapter4-challenge-doctor-whodunit]].
8. Call for coaches (6 May) said challenges would concentrate on S-CORE, OpenBSW and OpenSOVD (the Esslingen trio). The published challenges list OpenSOVD and S-CORE only in Doctor Whodunit; OpenBSW only in Hack to the Future.

## Links
- Event page: https://eclipsesdv.org/events/eclipse-sdv-hackathon-chapter-4/
- Registration/summary: https://www.eclipse-foundation.events/event/sdv-hackathon-chapter-four/summary
- Announcement: https://eclipsesdv.org/blogs/announcing-the-eclipse-sdv-hackathon-chapter-4-may-the-fourth-be-with-you/
- Coaches post: https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/
- Coach interview: https://eclipsesdv.org/blogs/sdv-hackathon-2026-interview-with-two-hack-coaches/
- Eventbrite: https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
- GitHub org: https://github.com/Eclipse-SDV-Hackathon-Chapter-Four (guide book and evaluation-forms PDFs in `.github/profile`, local clone `repos/hackathon-ch4-dotgithub`)
- sdv-wg list archive: https://www.eclipse.org/lists/sdv-wg/ (relevant: msg00851/863/865 call for coaches, msg00870 registration open, msg00897 coaches and jury). No challenge-specific threads found in Jun-Sep 2026.
- Related notes: [[hackfest-esslingen-2026]], [[chapter3-retrospective]], and components [[opendut-overview]], [[uprotocol-overview]], [[ankaios-overview]], [[opensovd-overview]], [[vss-kuksa-overview]], [[autosd-overview]], [[s-core-overview]], [[openbsw-overview]], [[sdv-blueprints-overview]].
