# AGENTS.md — working in this repo

SDV Crossref is an unofficial, AI-assisted markdown cross-reference of the Eclipse SDV ecosystem, written for participants of the Eclipse SDV Hackathon (first edition: Chapter 4, 6–8 Oct 2026). Humans read it in Obsidian or any viewer; agents read it with grep and the scripts below. Readers are hackathon participants: write in second person ("you", "your team"), not coach-to-coach.

## Read first
1. `README.md` — layout, status and evidence levels, licence.
2. `index.md` — every note, grouped by type (generated).
3. `synthesis/capability-map.md`, `synthesis/gap-register.md`, `design/design-index.md` — the three entry points for "what exists", "what is missing", "how to think".
4. `playbook/how-to-use-this-vault.md` — reading order per question; `playbook/known-broken-recipes.md` — recipes that failed once.
5. `tasks/lessons.md` — mistakes already made once while building this repo (agent fan-out, scratch space, filename clashes).

## Layout
| Folder | Note type | What goes there |
|---|---|---|
| `event/` | `event` | Chapter 4 facts, rubric sources, retrospectives, HackFest findings |
| `components/<slug>/` | `overview`, `quickstart`, `howto`, `reference`, plus `<slug>-integration-notes.md` | one folder per project; integration-notes tables feed the matrix |
| `synthesis/` | `synthesis` | capability map, generated integration matrix, gap register, reference architectures, pros/cons, upstream proposals, generated dependency drift |
| `design/<cluster>/` | `pattern` | one card per design pattern; ten clusters; `design-index.md` is generated below its marker |
| `playbook/` | `playbook` | getting-started per challenge, rubric, pitfalls, debugging, FAQ, env setup, known-broken recipes, `fixes/` overrides |
| `evidence/` | — | verifier logs behind `status: verified` claims |
| `repos/` | — | shallow clones for evidence (gitignored); cite as `repos/<name>/<path>`. `manifest.tsv` (tracked) lists url, commit and branch per clone; regenerate after adding a clone. |
| `facts/` | — | `README.md` and `queries.sql` tracked; `facts.duckdb` is built locally |
| `scripts/`, `_templates/`, `tasks/` | — | tooling, templates, lessons |

## Conventions that scripts enforce
- **Unique basenames** repo-wide; links are `[[basename]]`.
- **Frontmatter** per `_templates/note.md` (notes) or `_templates/pattern.md` (cards): `type`, `component` or `cluster`, `tags`, `status`, `sources`, `last-verified`, `related`; cards add `applies-to` and `gap-rows`.
- **Status** means: `draft` = written from sources; `reviewed` = re-read and checked against its sources in a second pass; `verified` = the recipe was executed and the observed output (with date) is in the note.
- **Evidence levels** used in synthesis notes: R = reproduced, C = read in upstream code or an open issue, P = derived from a pattern card.
- **Every claim has a source**: a URL, `repos/<path>`, or a wiki-link to the note that holds it. Mark the rest "(unverified)". Page snapshots are not published: cite the URL itself.

## Commands
```
python3 scripts/build_index.py          # regenerate index.md
python3 scripts/check_links.py          # broken [[links]] and duplicate basenames; exit 1 on failure
python3 scripts/build_matrix.py         # regenerate synthesis/integration-matrix.md from *-integration-notes.md
python3 scripts/build_design_index.py   # regenerate design/design-index.md below its marker
.venv/bin/python scripts/build_facts.py # rebuild facts/facts.duckdb from notes and repos/ (about 3 s)
.venv/bin/python scripts/build_drift.py # regenerate synthesis/dependency-drift.md from facts.duckdb
python3 scripts/stale.py --days 30      # notes to re-verify
python3 scripts/build_repo_manifest.py  # regenerate repos/manifest.tsv from the clones under repos/
```
**Facts layer**: `facts/facts.duckdb` holds tables of note frontmatter, links, integration claims, repo deps, container images, compose ports, axum routes and VSS paths, regenerated from scratch on every run. Use it before grepping `repos/` for questions about versions, images, ports or signals. Example queries are in `facts/queries.sql`, tables in `facts/README.md`. Do not cite the database itself; cite the `file_path`/`source_path` it points to.

Run `check_links.py` before you stop. Run `build_matrix.py` after touching any integration-notes table. Run `build_design_index.py` after adding or editing a card.

Dependencies (`install_deps.sh`, idempotent, combinable modes):
```
./install_deps.sh                 # --check (default): tool table, exit 1 if a required tool is missing; never installs
./install_deps.sh --vault         # .venv with duckdb, pyyaml, pytest, vss-tools 6.1, kuksa-client 0.6.0, eclipse-zenoh, iceoryx2 0.10.0
./install_deps.sh --tools         # user space: rustup + stable, bazelisk into ~/.local/bin
./install_deps.sh --pull          # pre-flight docker images (playbook/env-setup-matrix.md section 3); skips without docker
./install_deps.sh --clone         # recreate repos/ (shallow clones, about 4.7 GB) from repos/manifest.tsv
./install_deps.sh --all           # --vault --tools --pull --clone (everything that needs no sudo)
./install_deps.sh --system [--yes]  # apt packages via sudo, asks first; agents must not run this
```

Host prerequisites (`test_setup.sh`, idempotent; vcan0, tap0/tap0a0 (DoIP for OpenBSW POSIX) and openDuT `/etc/hosts` names; agents must not run --apply or --remove):
```
./test_setup.sh                   # --check (default): modules, vcan0, tap0/tap0a0, opendut.local hosts lines, info rows; exit 1 if any is missing
./test_setup.sh --apply [--yes]   # adds only the missing pieces via sudo, asks first; vcan0 and tap0/tap0a0 are lost on reboot, hosts lines persist
./test_setup.sh --remove [--yes]  # deletes vcan0, tap0a0, tap0 and the marked /etc/hosts block via sudo, asks first
```

## Workflows
- **Add a component**: `components/<slug>/` with the five files, conventions in `_templates/AGENT_CONVENTIONS.md`; then matrix + index.
- **Add a pattern card**: copy `_templates/pattern.md` into the right cluster, fill every section including the hackathon line and evidence, set `gap-rows`; then design index.
- **Verify a recipe**: run it exactly as written; on success set `status: verified` and append `## Observed on <date>`; on failure append `## Verification attempt <date>: FAILED` with the error and put any fix into `playbook/fixes/` and `playbook/known-broken-recipes.md`.
- **Correct a note**: fix in place, append "(corrected <date>, see the note or card that found it)"; do not leave the old claim standing.
- **Fan-out research**: one agent per topic, briefs must point at `_templates/AGENT_CONVENTIONS.md`, and every brief should include "verify these premises first" because briefs have been wrong before.

## Do not
- Name or describe private repositories, or quote non-public material (including non-public hackathon challenge repos).
- Attribute opinions, roles or advice to named individuals beyond what a published source says; point readers to "the coaches" and the official coach list instead.
- Add vendor products as components or sources; only generic patterns and gaps.
- Hand-edit generated files (`index.md`, `synthesis/integration-matrix.md`, the generated half of `design/design-index.md`, `synthesis/dependency-drift.md`).
- Claim `verified` without having run it.
- Use `sudo` or `docker swarm init`, or write outside this repo.
