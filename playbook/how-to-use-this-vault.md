---
title: How to use this crossref
type: playbook
component: none
tags: [howto, crossref, navigation]
status: reviewed
sources: []
last-verified: 2026-10-03
related:
  - "[[capability-map]]"
  - "[[gap-register]]"
  - "[[upstream-proposals]]"
  - "[[first-two-hours-doctor-whodunit]]"
  - "[[first-two-hours-hack-to-the-future]]"
  - "[[first-two-hours-freestyle]]"
  - "[[debugging-checklists]]"
  - "[[faq]]"
---

# How to use this crossref

This is an unofficial, AI-assisted cross-reference of public sources. It answers four kinds of question. Each has one entry point; everything else is reachable from there by wiki-link.

| Question | Start at | Then |
|---|---|---|
| What exists and how do I run it? | [[capability-map]] (layer map and 2-day radar) | `components/<slug>/<slug>-quickstart.md` (status `verified` means it ran on the reference host) |
| What is missing, and what could your team build? | [[gap-register]] (sized, tagged rows) | [[upstream-proposals]] (ready-to-file issues per project) |
| How should you think about this design problem? | [[design-index]] (type, instance, placement lens; 107 cards in ten clusters) | the "By gap row" map at the bottom links patterns to gaps |
| What should your team do first? | the three getting-started guides (`first-two-hours-*`) | [[scoring-rubric-cheatsheet]], [[pitfalls-top20]], [[debugging-checklists]], [[faq]] |

## During the event

- **Day 1 morning**: check the Chapter 4 GitHub org (https://github.com/Eclipse-SDV-Hackathon-Chapter-Four) for starter or challenge repos; they may appear during the event. The questions worth asking the organisers are in [[scoring-rubric-cheatsheet]] section 6.
- **You are stuck on a symptom**: [[debugging-checklists]] is symptom-first; each block ends with the note that holds the fix. Four upstream recipes are broken as written; the overrides are in `playbook/fixes/` and explained in [[known-broken-recipes]].
- **You want to know "does X talk to Y?"**: [[integration-matrix]], grid first, then the detail section with evidence per claim. A `?` or `·` cell is a gap; where two claims conflict, verify the higher one with the project's coach or maintainers.
- **You want a Freestyle item**: [[upstream-proposals]], one R row and one open-issue row; comment on the issue before writing code.
- **A design question comes up**: find the cluster in [[design-index]]; every card has a hackathon-sized version and a one-sentence trap.

## Reading the evidence marks

- Note `status`: `draft` (written from sources), `reviewed` (read by the maintainer of this repo), `verified` (executed, output recorded).
- Synthesis rows: R reproduced here, C read in upstream code or an issue, P derived from a pattern card.
- "(unverified)" inside a note means exactly that; treat the claim as untested.

## If this crossref and a repo disagree

- The URLs and `repos/<name>/<path>` references cited in each note are the evidence (recreate the clones with `./install_deps.sh --clone`); if a claim and a repo disagree, the repo wins and the note gets a "(corrected <date>)".
- `python3 scripts/check_links.py` checks that every `[[link]]` resolves.
