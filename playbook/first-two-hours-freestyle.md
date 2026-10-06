---
title: Getting started — Freestyle (HackFest) track
type: playbook
component: none
tags: [first-two-hours, freestyle, hackfest, getting-started, chapter4]
status: reviewed
sources:
  - "[[scoring-rubric-cheatsheet]] (Freestyle weights: Contribution Value 25 %, Technical Quality & Maturity 25 %, Ecosystem Impact 20 %, Reusability 10 %; jury 20 %)"
  - "[[chapter4-freestyle-track]]"
  - "[[gap-register]]"
  - "[[known-broken-recipes]]"
  - "[[hackfest-esslingen-2026]]"
last-verified: 2026-10-03
related:
  - "[[first-two-hours-doctor-whodunit]]"
  - "[[first-two-hours-hack-to-the-future]]"
  - "[[env-setup-matrix]]"
  - "[[debugging-checklists]]"
---

# Getting started — Freestyle track

The Freestyle rubric rewards one thing: **a contribution the project would keep after the event.** 5/5 on Contribution Value reads "valuable enough that the Eclipse SDV community should actively continue it", and 5/5 on Technical Quality reads "near merge-ready". Reusability asks "could another contributor pick this up next week without your help?". It is explicitly not a pitch competition. So your goal for the first two hours is a **named upstream issue, a reproduced failure, and a fork with a branch**, not an idea.

## 0:00–0:15 Questions and rules

0. **Declare prepared work now.** Freestyle teams present prepared code at the end of Day 1; undeclared prior work is scored as if it were done at the event, which can disqualify your team ([[scoring-rubric-cheatsheet]]). Teams and tracks freeze at Day 1 11:30–12:30.
1. Which project does someone on your team already *build* on their laptop? Rust and Docker are the common denominator; Bazel (S-CORE), C++ (OpenBSW) and podman (Ankaios) each cost half a day to set up for a newcomer ([[env-setup-matrix]]).
2. Which project has a coach in the room? Check the official coach list (https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/). A PR with a maintainer comment on it before the interview is the single strongest piece of evidence.
3. Do you want a *merged* small fix or a *reviewed* real feature? The honest answer for most two-day teams is one of each.

## 0:15–0:45 Pick from three tiers (one from tier 1, one from tier 2)

The full ready-to-file list, grouped by project with draft issue titles, is [[upstream-proposals]]. The tiers below are the short form.

**Tier 1: reproduced and fixable today** (each has a verified reproduction in this repo; see [[known-broken-recipes]] and [[gap-register]] section E)

| Pick | Project | What is broken | Size |
|---|---|---|---|
| E1 | openDuT | CLEO accepts a cluster leader outside the cluster, issue #495, labelled good-first-issue | S |
| E2 | OpenBSW | DoIP server NACKs the CDA's diagnostic-message ACK types 0x8002/0x8003; fix exists only in the HackFest overlay; overlay also needs porting past the `etl::span` change | S |
| E15 | SDV Blueprints | three compose files use swarm-only overlay networks; wrong rFMS path in README; start script not executable and a quoting bug; service-to-signal has no Cargo.lock and a drifting `kuksa-rust-sdk` pin | S each |
| E16 | HackFest playground | OpenBSW-SOVD-Demo compose broken in five ways; override file exists in `playbook/fixes/` | S |
| E4 | KUKSA | `databroker-cli` lists the removed v1 API; Python SDK lacks v2 `Actuate`; Ankaios tutorial pins a 2023 image | S each |
| E5 | iceoryx2 | README names a non-existent PyPI version; C++ example missing `IOX2_TYPE_NAME`; `iox2 node` cleanup not implemented | S |
| E6 | S-CORE | orchestrator pins rustc 1.85.0 but its lockfile needs 1.88; stale README paths; no Bazel-free "try it" page | S |

**Tier 2: a real feature with a maintainer waiting for it** (open upstream issue, no PR)

| Pick | Project | Feature | Why it lands | Size |
|---|---|---|---|---|
| A1 | OpenSOVD core | `faults` resource (issue #156): list, read, delete; mirror the CDA JSON shape | Doctor Whodunit teams need it the same week; OpenSOVD coaches are listed for the event | M |
| H2 / H1 | OpenSOVD core | `triggers` (EnterRange / LeaveRange / OnChange → SSE event or further command) on top of `cyclic-subscriptions` over SSE | the standard's own evidence mechanism; missing everywhere | M |
| C1 | Ankaios | example manifest for two workloads sharing iceoryx2 (`/dev/shm`, `/tmp/iceoryx2`, same UID) with a README | no upstream example; unverified recipe in [[ankaios-howto]] | S |
| B11 | KUKSA / vss-tools | DBC → VSS overlay drafter for `kuksa-can-provider` | saves every CAN team half a day | S–M |
| A10 | uProtocol | heartbeat / fault / mitigation schema crate (.proto + Rust + Python) | every Doctor Whodunit team would reuse it | S |
| H10 / H9 | OpenSOVD core | `{path}/docs` capability description (#92) or mDNS/DNS-SD discovery (#31) | open issues, mandatory in the standard | M |
| E14 | OpenSOVD | MDD validator / diff tool (diagnostic descriptions were the real-car blocker at HackFest) | maintainers named it as the blocker | M |

**Tier 3: ambitious, only with a maintainer at the table** — S-CORE app → OpenSOVD runtime fault path (A3), iceoryx2 → native Zenoh key gateway (B2), `updates` lifecycle in OpenSOVD core (H3), embedded uProtocol client via zenoh-pico (D1). Any of these is a full two days and scores on Ecosystem Impact, but only if you agree a design sketch with the maintainer on Day 1.

Steer away from: anything in the Hold ring of [[capability-map]] (Velocitas, Kanto, Chariott, SommR), AutoSD image building, self-hosting openDuT, S-CORE Bazel from a cold cache.

## 0:45–1:30 Reproduce, then announce

1. **Reproduce the failure or the gap locally** with the verified recipe for that project (quickstart notes, `playbook/fixes/`). A reproduction log in the repo is evidence for "Code does what it claims".
2. **Comment on the upstream issue** (or open one, mode C in [[chapter4-freestyle-track]]) saying what your team will do and how, *before* writing code. Contribution Focus & Initiative is scored by the jury; a timestamped comment is the proof. Ask the project's coach or maintainer to acknowledge it.
3. **Fork, branch, CI.** Read the project's `CONTRIBUTING`: S-CORE needs the Eclipse Contributor Agreement and `Signed-off-by`, plus `bazel test //:format.check` ([[s-core-howto]]); OpenSOVD and KUKSA need the ECA. Get the ECA signed in hour one, not on Day 3.
4. **Write the README section first**: what, why, how to run, known limitations, next-step issues. That is the Reusability score.

## 1:30–2:00 Plan the two days against the rubric

| Criterion (weight) | Day 1 evidence | Day 3 evidence |
|---|---|---|
| Contribution Value (25 %) | issue comment with intent; tier-1 PR opened | maintainer comment or review on the PR |
| Technical Quality & Maturity (25 %) | reproduction log; branch builds | upstream CI green; tests added; follows the project's conventions |
| Ecosystem Impact (20 %) | the pick touches two projects or makes one easier to adopt (state which) | demo of the integration or the easier adoption path |
| Reusability (10 %) | README section written | setup steps, limitations, next-step issues filed |
| Jury (20 %) | — | 10-minute handover story: what was broken, what is merged, what is next |

Day 1 18:00: the Solution Plan names the issue URLs, the two picks, and the maintainer contacted. Day 3 08:00 code freeze: PR links at the top of the team README.

## Things to remember

- A merged one-line fix beats an unmerged feature; do both, in that order.
- Pin to a commit or a tag, never to `main`; the HackFest S-CORE branches died of floating pins. ([[hackfest-esslingen-2026]])
- Green, pinned, published: say which of the three your PR delivers. ([[faq]] Q53a)
- Open the issue comment now; the jury scores initiative.
- Sign the ECA before lunch.

## Where to get help

Ask the coaches for project-specific questions (OpenSOVD, S-CORE, OpenBSW, openDuT and others); the official coach list is at https://eclipsesdv.org/blogs/meet-the-people-who-will-help-you-get-unstuck-at-eclipse-sdv-hackathon-2026/. For KUKSA, Ankaios, iceoryx2, uProtocol and Zenoh, also use the quickstart and how-to notes and the projects' GitHub discussions. Whether the bonus-tech layer applies to Freestyle is unresolved in the evaluation forms; ask the organisers on Day 1 ([[scoring-rubric-cheatsheet]]).
