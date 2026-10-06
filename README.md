# SDV Crossref

> **Unofficial and AI-assisted.** Generated with Claude for a hackathon coach; human review is ongoing. Not affiliated with or endorsed by the Eclipse Foundation or any Eclipse SDV project. This is a snapshot of 2026-10-03..06: projects move fast, so verify a command, version or claim against the upstream source before you rely on it.

A cross-reference of the Eclipse SDV ecosystem, written for participants of the **Eclipse SDV Hackathon Chapter 4** (6–8 Oct 2026, Friedrichshafen, hosted by ZF) and useful beyond it: what each project is, how to run it quickly, how the projects connect, where they do not, and which design patterns help. Opens in Obsidian or any markdown viewer; `grep` works too.

## How to read a note
- **`status`** in the frontmatter: `draft` = written from sources; `reviewed` = re-read and checked against its sources in a second (AI) pass; `verified` = the recipe was executed on 2026-10-03 and the observed output is in the note (section "Observed on 2026-10-03"). Failed runs are kept as "Verification attempt … FAILED".
- **Evidence levels** in synthesis notes: **R** = reproduced here, **C** = read in upstream code or an open issue, **P** = derived from a design pattern card.
- **Every claim has a source**: a URL, a `repos/<name>/<path>` inside a shallow clone, or a `[[wiki-link]]` to the note that holds it. Anything else is marked "(unverified)".
- **Corrections** stay visible: "(corrected <date>, …)" points to the note or card that found the error.

## Layout
| Folder | What lives there |
|---|---|
| `event/` | Chapter 4 challenges and logistics; retrospectives of Chapter 3 (2025), HackFest Esslingen 2026, earlier chapters |
| `components/<name>/` | One folder per project, Diátaxis-split: `<name>-overview.md` (what/why), `<name>-quickstart.md` (run it in 15 min), `<name>-howto.md` (recipes), `<name>-reference.md` (APIs, repos, links, versions), `<name>-integration-notes.md` (what it talks to) |
| `synthesis/` | Cross-cutting views: capability map, integration matrix, reference architectures per challenge, pros/cons, gap register, upstream proposals, dependency drift |
| `design/` | Design patterns: one card per pattern (problem, forces, rule, prior art, how it lands on the Eclipse SDV stack, trap, hackathon-sized version), grouped in ten clusters; start at `design/design-index.md` |
| `playbook/` | Getting started per challenge, pitfalls, debugging checklists, FAQ, environment setup, known-broken recipes and their `fixes/` |
| `evidence/` | Raw verification log of the 2026-10-03 run (`verify-run-1.md`) |
| `facts/` | Queryable facts layer (`facts.duckdb`, built by a script; see `facts/README.md`) |
| `repos/` | Shallow clones of key repos for grep-able evidence (not part of the notes; recreate with `--clone`) |
| `scripts/` | Index, link check, matrix, design index, facts and drift builders, staleness report; see `scripts/README.md` |
| `_templates/` | Note and pattern-card templates, and the conventions the notes were written under |

## Start here
- `index.md`: generated table of all notes.
- **Your challenge**: `event/chapter4-overview.md`, `event/chapter4-challenge-doctor-whodunit.md`, `event/chapter4-challenge-hack-to-the-future.md`, `event/chapter4-freestyle-track.md`; `event/hackathon-patterns.md` for what won before.
- **One possible architecture**: `synthesis/reference-architecture-doctor-whodunit.md`, `synthesis/reference-architecture-hack-to-the-future.md`. These are starting points, not the expected answer.
- **Open problems you could solve**: `synthesis/gap-register.md` (missing pieces, sized and tagged), `synthesis/upstream-proposals.md` (ready-to-file upstream issues and PRs).
- **What exists and what talks to what**: `synthesis/capability-map.md`, `synthesis/integration-matrix.md`, `synthesis/pros-cons-when-not.md`.
- **Getting started**: `playbook/first-two-hours-*.md` (per challenge and for Freestyle), `playbook/env-setup-matrix.md` (pre-flight pulls, pin sheet), `playbook/scoring-rubric-cheatsheet.md`.
- **Before you lose an afternoon**: `playbook/pitfalls-top20.md`, `playbook/known-broken-recipes.md`, `playbook/debugging-checklists.md`, `playbook/faq.md`.
- **Components**: `components/<slug>/<slug>-overview.md`, then `-quickstart.md` (status `verified` = ran on 2026-10-03).
- **How to think about it**: `design/design-index.md`.

## Conventions
- **Unique basenames.** Every note's filename is unique across the vault (e.g. `iceoryx2-overview.md`), so `[[iceoryx2-overview]]` resolves anywhere.
- **Frontmatter** per `_templates/note.md` (notes) or `_templates/pattern.md` (cards): `type`, `component` or `cluster`, `tags`, `status`, `sources`, `last-verified`, `related`; cards add `applies-to` and `gap-rows`.
- **Verified means run.** `status: verified` only when a recipe was executed and the output is in the note.
- **Generated files are not hand-edited**: `index.md`, `synthesis/integration-matrix.md`, the generated half of `design/design-index.md`, `synthesis/dependency-drift.md`.

## Maintenance
```
./install_deps.sh --vault --clone          # .venv, then repos/ (about 4.7 GB of shallow clones, measured 2026-10-06) from repos/manifest.tsv
python3 scripts/build_index.py             # regenerate index.md after adding notes
python3 scripts/check_links.py             # broken [[links]] and duplicate basenames; exit 1 on failure
python3 scripts/build_matrix.py            # after editing any *-integration-notes.md
python3 scripts/build_design_index.py      # after adding or editing a design card
.venv/bin/python scripts/build_facts.py    # rebuild facts/facts.duckdb
.venv/bin/python scripts/build_drift.py    # regenerate synthesis/dependency-drift.md from facts.duckdb
python3 scripts/stale.py --days 30         # notes to re-verify
./install_deps.sh --pull                   # pre-flight docker images; skips without docker
```
`./install_deps.sh` without arguments only checks which tools are present. Copying the vault elsewhere: leave out `repos/`, `.venv/`, `facts/*.duckdb` and `__pycache__/`, then run the first command and `build_facts.py` on the target; `repos/manifest.tsv` travels with the notes.

## Licence
Text and notes: CC-BY-4.0, see `LICENSE`. Scripts: Apache-2.0, see `LICENSE-scripts`. Upstream projects quoted or cloned under `repos/` keep their own licences.

## Contributing
Issues and pull requests are welcome: corrections, newer versions, recipes you ran, new gaps or patterns. Keep the conventions above (unique basenames, frontmatter, `status` only `verified` if you ran it and pasted the output), give one source per claim, and run `python3 scripts/check_links.py` before you open a PR.
