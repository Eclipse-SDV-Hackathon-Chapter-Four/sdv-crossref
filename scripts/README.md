# Vault scripts

Python 3 stdlib only. Run from any directory; the vault root is the parent of `scripts/`.
Scanned: every `.md` file except those under `repos/`, `sources/`, `_templates/`, `tasks/`, `scripts/`, `.git/`, and `index.md`.

| Script | What it does |
|---|---|
| `python3 scripts/build_index.py` | Regenerates `index.md`: summary (note count, per-status counts), then one table per `type` (event, synthesis, playbook, overview, quickstart, howto, reference, other), sorted by component then title. |
| `python3 scripts/check_links.py` | Prints `path:line: missing [[target]]` for unresolved wiki-links, then duplicate basenames. Exit 1 if any, else 0. Links inside HTML comments and code are ignored. |
| `python3 scripts/stale.py [--days 30] [--status draft]` | Lists `path  status  last-verified` for notes not verified within N days (or with no `last-verified`). |

A link `[[target]]` (also `[[target|alias]]`, `[[target#heading]]`) resolves if some scanned note is named `target.md`, or `target` is a path relative to the vault root.

`build_index.py` also holds the shared helpers (frontmatter parser, note scanner) that the other two import.
