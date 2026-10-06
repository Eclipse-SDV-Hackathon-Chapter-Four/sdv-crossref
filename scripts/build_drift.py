#!/usr/bin/env python3
"""Regenerate synthesis/dependency-drift.md from facts/facts.duckdb.

Compares the watch-list packages and images pinned in the cloned repos against the
version pin sheet and gives each (repo, package, version) a verdict. Needs the vault
venv for duckdb; rebuild the facts first with scripts/build_facts.py.
"""
import re
from collections import defaultdict
from pathlib import PurePosixPath

import duckdb

from build_index import VAULT

DB = VAULT / "facts" / "facts.duckdb"
OUT = VAULT / "synthesis" / "dependency-drift.md"

# References from playbook/env-setup-matrix.md section 4 "Version pin sheet" (prose, so hard-coded
# here). None = the sheet gives no pin; such rows get the verdict no-ref and appear only in the spread.
CARGO = {"up-rust": "0.9.0", "iceoryx2": "0.10.0", "kuksa-rust-sdk": None, "zenoh": "1.10.x",
         "ankaios_sdk": "1.0.4", "tonic": None, "axum": None}
PYPI = {"kuksa-client": "0.6.0", "eclipse-zenoh": "1.10.1", "iceoryx2": "0.10.0"}
DATABROKER = "0.7.1"
IMAGES = {"ghcr.io/eclipse-kuksa/kuksa-databroker": DATABROKER,
          "quay.io/eclipse-kuksa/kuksa-databroker": DATABROKER,
          "ghcr.io/eclipse/kuksa.val/databroker": DATABROKER,  # pre-2024 registry path of the same broker
          "eclipse/zenoh": "1.10.1"}
ANKAIOS_PREFIX = "ghcr.io/eclipse-ankaios/"
ANKAIOS_RUNTIME = {"ghcr.io/eclipse-ankaios/app-ankaios-dev": "1.0.4"}  # ships ank-server/ank-agent
VERDICTS = ["stale", "lagging", "ahead", "current", "no-ref"]
VERSION_RE = re.compile(r"^[\s=^~<>v]*(\d+)\.(\d+)")
MAX_PATHS = 3


def minor(v):
    m = VERSION_RE.match(v or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def verdict(version, ref):
    if ref is None:
        return "no-ref"
    have, want = minor(version), minor(ref)
    if have is None:
        return "stale"  # git rev, branch, `*`, `latest`, template variable
    if have > want:
        return "ahead"
    if have == want:
        return "current"
    return "lagging" if have[0] == want[0] and want[1] - have[1] <= 2 else "stale"


def dep_rows(con):
    """(repo, package, pinned, resolved, path) per effective dependency version."""
    q = ("SELECT repo, manifest_path, ecosystem, package, version_req, resolved_version FROM deps "
         "WHERE ecosystem IN ('cargo-toml', 'cargo-lock', 'pyproject') AND source_kind <> 'workspace' "
         "AND (source_kind <> 'path' OR repo = package) AND package IN ({})")
    names = sorted(set(CARGO) | set(PYPI))
    rows = con.execute(q.format(",".join("?" * len(names))), names).fetchall()
    locks = defaultdict(list)  # (repo, package) -> [(lock dir, resolved, path)]
    for repo, path, eco, pkg, _, res in rows:
        if eco == "cargo-lock" and res:
            locks[(repo, pkg)].append((PurePosixPath(path).parent, res, path))
    out = []
    for repo, path, eco, pkg, req, _ in rows:
        if eco == "pyproject" and req:
            out.append(("pypi", repo, pkg, req, None, path))
        elif eco == "cargo-toml" and req:
            d = PurePosixPath(path).parent
            if not any(d == ld or ld in d.parents for ld, _, _ in locks[(repo, pkg)]):
                out.append(("cargo", repo, pkg, req, None, path))  # no lock resolves this manifest
    for (repo, pkg), entries in locks.items():
        for ld, res, path in entries:
            reqs = sorted({req for r, p, e, k, req, _ in rows if r == repo and k == pkg and e == "cargo-toml"
                           and req and minor(req) in (minor(res), None)
                           and (PurePosixPath(p).parent == ld or ld in PurePosixPath(p).parent.parents)})
            out.append(("cargo", repo, pkg, ", ".join(reqs) or "(transitive)", res, path))
    return out


def image_rows(con):
    rows = con.execute("SELECT repo, file_path, image, tag, digest FROM images "
                       "WHERE image IN ({}) OR starts_with(image, ?)".format(",".join("?" * len(IMAGES))),
                       [*IMAGES, ANKAIOS_PREFIX]).fetchall()
    return [("image", repo, image, tag or (f"@{digest[:19]}" if digest else "(untagged)"), None, path)
            for repo, path, image, tag, digest in rows]


def reference(kind, pkg):
    if kind == "cargo":
        return CARGO[pkg]
    if kind == "pypi":
        return PYPI[pkg]
    return IMAGES.get(pkg) or ANKAIOS_RUNTIME.get(pkg)


def paths_cell(paths):
    paths = sorted(paths)
    cell = ", ".join(f"`{p}`" for p in paths[:MAX_PATHS])
    return cell + (f" (+{len(paths) - MAX_PATHS} more)" if len(paths) > MAX_PATHS else "")


def main():
    con = duckdb.connect(str(DB), read_only=True)
    head = dict(con.execute("SELECT name, head_date FROM repos").fetchall())
    groups = defaultdict(set)  # (repo, label, pinned, resolved, kind, pkg) -> paths
    for kind, repo, pkg, pinned, res, path in dep_rows(con) + image_rows(con):
        label = pkg if kind != "pypi" else f"{pkg} (pip)"
        groups[(repo, label, pinned, res, kind, pkg)].add(path)
    rows = []
    for (repo, label, pinned, res, kind, pkg), paths in groups.items():
        ref = reference(kind, pkg)
        rows.append({"repo": repo, "date": (head.get(repo) or "?")[:10], "label": label, "pinned": pinned,
                     "resolved": res, "ref": ref, "verdict": verdict(res or pinned, ref), "paths": paths})
    rows.sort(key=lambda r: (r["repo"].lower(), r["label"], r["pinned"], r["resolved"] or ""))
    counts = {v: sum(r["verdict"] == v for r in rows) for v in VERDICTS}

    out = ["---", "title: Dependency drift", "type: synthesis", "component: none",
           "tags: [dependencies, versions, generated]", "status: draft", "sources:",
           "  - facts/README.md", "  - playbook/env-setup-matrix.md", "last-verified: 2026-10-03", "related:",
           '  - "[[env-setup-matrix]]"', '  - "[[capability-map]]"', '  - "[[upstream-proposals]]"', "---", "",
           "# Dependency drift", "",
           "<!-- generated by scripts/build_drift.py, do not edit -->", "",
           "Which cloned repos pin old versions of the ecosystem's key packages, measured against the version "
           "pin sheet in [[env-setup-matrix]] section 4. Warn a team before they copy one of these repos as a "
           "starting point. Every row cites the manifest or image file it was read from.", "",
           "Verdict counts: " + ", ".join(f"{v} {counts[v]}" for v in VERDICTS) + ".", "",
           "## Repos with stale pins", "",
           "Only `lagging`, `stale` and `ahead` rows. `ahead` is usually the package's own upstream clone.", "",
           "| repo | last commit | package | pinned | resolved | reference | verdict | manifest |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["verdict"] in ("lagging", "stale", "ahead"):
            out.append(f"| {r['repo']} | {r['date']} | {r['label']} | `{r['pinned']}` | "
                       f"{'`' + r['resolved'] + '`' if r['resolved'] else '–'} | {r['ref'] or '–'} | "
                       f"**{r['verdict']}** | {paths_cell(r['paths'])} |")

    out += ["", "## Spread per package", "",
            "Effective version (lock resolution where a lock exists, else the requirement or image tag) "
            "and the repos that use it.", "", "| package | reference | versions seen (repos) |", "|---|---|---|"]
    spread = defaultdict(lambda: defaultdict(set))
    refs = {}
    for r in rows:
        spread[r["label"]][r["resolved"] or r["pinned"]].add(r["repo"])
        refs[r["label"]] = r["ref"]
    for label in sorted(spread):
        seen = "; ".join(f"`{v}` ({', '.join(sorted(spread[label][v], key=str.lower))})"
                         for v in sorted(spread[label], key=lambda v: (minor(v) or (-1, -1), v)))
        out.append(f"| {label} | {refs[label] or 'none in the sheet'} | {seen} |")

    by_repo = defaultdict(list)
    for r in rows:
        if r["verdict"] != "no-ref":
            by_repo[r["repo"]].append(r)
    clean = sorted((repo for repo, rs in by_repo.items() if all(r["verdict"] == "current" for r in rs)),
                   key=str.lower)
    out += ["", "## Clean repos", "",
            "Repos whose watch-list pins that have a reference are all `current`.", ""]
    for repo in clean:
        pkgs = sorted({r["label"] for r in by_repo[repo]})
        paths = set().union(*(r["paths"] for r in by_repo[repo]))
        out.append(f"- **{repo}** ({head.get(repo, '?')[:10]}): {', '.join(pkgs)}; {paths_cell(paths)}")
    if not clean:
        out.append("- none")

    out += ["", "## Method and limits", "",
            "- **Inputs.** The `deps` rows from `Cargo.toml`, `Cargo.lock` and `pyproject.toml`, and the `images` "
            "rows from compose files, Ankaios manifests and Dockerfiles, as extracted by `scripts/build_facts.py` "
            "(tables described in `facts/README.md`). Each row above cites the file it came from.",
            "- **Watch-list and references.** Hard-coded in `scripts/build_drift.py` from [[env-setup-matrix]] "
            "section 4. Cargo: up-rust 0.9.0, iceoryx2 0.10.0, zenoh 1.10.x, ankaios_sdk 1.0.4; kuksa-rust-sdk, "
            "tonic and axum have no pin in the sheet (`no-ref`, spread only). pip: kuksa-client 0.6.0, "
            "eclipse-zenoh 1.10.1, iceoryx2 0.10.0. Images: kuksa-databroker 0.7.1 (ghcr.io, quay.io and the old "
            "`ghcr.io/eclipse/kuksa.val/databroker` path), `eclipse/zenoh` 1.10.1, "
            "`ghcr.io/eclipse-ankaios/app-ankaios-dev` 1.0.4 (it bundles the Ankaios runtime); the other "
            "`ghcr.io/eclipse-ankaios/*` images (devcontainer base, test fixtures) are `no-ref`.",
            "- **Verdicts** compare numeric major.minor only. `current` = same minor as the reference; "
            "`lagging` = same major, one or two minors behind; `stale` = older major, more than two minors "
            "behind, or anything non-numeric (git rev, branch, `*`, `latest`, `master`), shown raw; "
            "`ahead` = newer than the reference (for example a `-SNAPSHOT` or `.999` development version in the "
            "package's own repo); `no-ref` = no reference. For 0.x crates a minor bump is a breaking change, so "
            "`lagging` there still means incompatible types.",
            "- **Lock beats requirement.** Where a `Cargo.lock` sits in the manifest's directory or an ancestor, "
            "the lock-resolved version is judged and the `Cargo.toml` requirements with the same major.minor are "
            "shown as `pinned`, together with any git rev or branch; `(transitive)` means no manifest under that lock names the package directly. "
            "Requirements with no lock are judged by their lower bound, so `>=1.5.1` counts as 1.5. "
            "`workspace = true` rows are skipped (the root manifest carries the version), and `path` rows are "
            "kept only in the package's own repo (elsewhere they are local crates with the same name).",
            "- **Images** with tag `latest` (or no tag) are `stale` because they are unpinned; this applies to "
            "images that have a reference. No image is resolved against a registry.",
            "- **Extractor limits**: everything is regex extraction, template variables "
            "such as `${TAG}` stay literal, compose long port syntax is skipped and routes with constant paths "
            "are skipped. Neither affects this note directly, but the same extractor feeds it.",
            "- **Regenerate** with `.venv/bin/python scripts/build_drift.py` after `scripts/build_facts.py`."]
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {len(rows)} rows (" + ", ".join(f"{v} {counts[v]}" for v in VERDICTS)
          + f"), {len(spread)} packages, {len(clean)} clean repos")


if __name__ == "__main__":
    main()
