# Facts layer

`facts.duckdb` holds tables extracted from the vault notes and the clones in `repos/`. It answers questions like "who pins up-rust 0.7" or "which KUKSA notes are still draft" in milliseconds, where grep over the 9 GB of clones would take much longer. The file is generated. Do not edit it, cite it as a source or add it to any index. Cite the `source_path`/`file_path` it points to instead.

```
.venv/bin/python scripts/build_facts.py     # rebuild from scratch (~3 s); prints row counts per table
```

`.venv/bin/python scripts/build_drift.py` turns the `deps` and `images` tables into `synthesis/dependency-drift.md` (old pins per repo against the version pin sheet).

The script needs the vault venv because that is where duckdb is installed. Rebuild after pulling repos or editing notes. Two runs on the same inputs produce identical tables.

## Tables

| Table | Source | Columns |
|---|---|---|
| `notes` | note frontmatter (same scope as `build_index.py`) | path, basename, type, component, cluster, status, last_verified, title, tags[], applies_to[], gap_rows[] |
| `links` | `[[...]]` outside code and comments (`check_links.py` matcher) | from_path, to_basename, resolves |
| `claims` | `*-integration-notes.md` tables (`build_matrix.py` parser) | from_component, to_component, maturity, how, evidence, source_path |
| `repos` | `git remote` / `git log -1` per clone | name, path, remote_url, head_commit, head_date |
| `deps` | Cargo.toml, Cargo.lock, pyproject.toml, package.json, MODULE.bazel | repo, manifest_path, ecosystem, package, version_req, resolved_version, source_kind |
| `images` | compose files, `*.container`, Ankaios manifests, Dockerfiles, `*.aib.yml` | repo, file_path, kind, image, tag, digest |
| `ports` | compose `ports:` | repo, file_path, host_port, container_port |
| `routes` | axum/aide `.route(` / `.api_route(` / `.nest(` in `.rs` | repo, file_path, method, path, base_path_hint |
| `vss_paths` | `Vehicle.*` strings in code and data files under 2 MB | repo, file_path, vss_path |
| `pins_vs_current` (view) | deps + images for the watch-list | ecosystem, package, versions_seen[], repos[] |

## Caveats

- **Regex extraction.** Nothing here is resolved by cargo, npm, pip or Docker. Template variables such as `${TAG}` stay literal.
- **`claims.to_component`** is a canonical slug. Rows whose project matches no slug keep the raw project name.
- **`deps.source_kind`** is `workspace` for `foo = { workspace = true }`. The version for those rows is in the `[workspace.dependencies]` row of the root manifest.
- **`routes.path`** takes only string-literal paths. A `{CONST}` in the path is filled from the same file's `&str` constants. `base_path_hint` is a `*BASE*`/`*PREFIX*`/`*ROOT*` constant, or else the first `.nest(` prefix in the file. It can be NULL.
- **Identical rows are collapsed.** For example, the same port listed twice in one file gives one row.

## Queries

`queries.sql` holds commented example queries. They cover version drift on the watch-list, who pins up-rust 0.7, draft notes per component, draft KUKSA notes, dangling links, core-nine gaps, databroker/zenoh image tags, host-port collisions, SOVD routes, shared VSS paths and repo freshness. To run one:

```
.venv/bin/python -c "import duckdb; print(duckdb.connect('facts/facts.duckdb', read_only=True).sql(\"SELECT * FROM pins_vs_current\"))"
```
