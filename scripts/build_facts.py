#!/usr/bin/env python3
"""Rebuild facts/facts.duckdb from the vault notes and the clones under repos/.

Run with the vault venv (it has duckdb):  .venv/bin/python scripts/build_facts.py
The database is deleted and rebuilt from scratch on every run. Example queries: facts/queries.sql.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import tomllib

import duckdb

from build_index import VAULT, iter_notes, note_title, parse_frontmatter
from build_matrix import canonical, column, find_table, maturity
from check_links import COMMENT_RE, FENCE_RE, INLINE_CODE_RE, LINK_RE, _blank

DB = VAULT / "facts" / "facts.duckdb"
REPOS = VAULT / "repos"
SKIP_DIRS = {".git", "target", "node_modules", "vendor", "build"}
VSS_EXT = {".rs", ".py", ".json", ".yaml", ".yml", ".vspec", ".csv", ".toml"}
VSS_RE = re.compile(r"(?<![A-Za-z0-9_])Vehicle\.[A-Za-z0-9_.]+")
IMAGE_LINE_RE = re.compile(r"^\s*-?\s*image:\s*[\"']?([^\"'\s#]+)", re.M)
ROUTE_RE = re.compile(r"\.(api_route|route|nest)\(\s*(?:&?format!\(\s*)?\"([^\"]*)\"")
METHOD_RE = re.compile(r"(?<![.\w])(get|post|put|delete|patch|head|options|any)(?:_with)?\(")
BASE_CONST_RE = re.compile(r"const\s+\w*(?:BASE|PREFIX|ROOT)\w*\s*:\s*&(?:'static\s+)?str\s*=\s*\"(/[^\"]*)\"")
BAZEL_DEP_RE = re.compile(r"bazel_dep\(([^)]*)\)")
WATCH = ["up-rust", "up-transport-zenoh", "up-transport-mqtt5", "zenoh", "eclipse-zenoh", "iceoryx2",
         "kuksa-rust-sdk", "kuksa-client", "vss-tools", "ankaios"]
warnings = []


def as_list(value):
    if value in (None, ""):
        return []
    return [str(v) for v in value] if isinstance(value, list) else [str(value)]


def as_str(value):
    return ", ".join(value) if isinstance(value, list) else (value or None)


# ---- vault -------------------------------------------------------------------------------------

def vault_facts(notes, links, claims):
    paths = list(iter_notes())
    stems = {p.stem for p in paths}
    for path in paths:
        rel = path.relative_to(VAULT).as_posix()
        text = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        notes.append((rel, path.stem, as_str(meta.get("type")), as_str(meta.get("component")),
                      as_str(meta.get("cluster")), as_str(meta.get("status")), as_str(meta.get("last-verified")),
                      note_title(meta, body, path), as_list(meta.get("tags")), as_list(meta.get("applies-to")),
                      as_list(meta.get("gap-rows"))))
        for rx in (COMMENT_RE, FENCE_RE, INLINE_CODE_RE):
            text = rx.sub(_blank, text)
        for target in sorted({m.group(1).strip() for m in LINK_RE.finditer(text)} - {""}):
            stem = target[:-3] if target.endswith(".md") else target
            ok = stem in stems or (VAULT / target).exists() or (VAULT / f"{stem}.md").exists()
            links.append((rel, stem, ok))
        if path.parent.parent.name == "components" and path.name == f"{path.parent.name}-integration-notes.md":
            table = find_table(body)
            if table is None:
                warnings.append(f"{rel}: no integration table")
                continue
            header, rows = table
            c = {k: column(header, w, d) for k, w, d in [("name", "project", 0), ("how", "how", 2),
                 ("maturity", "maturity", 3), ("evidence", "evidence", 4)]}
            src = path.parent.name
            for row in rows:
                if len(row) < len(header):
                    continue
                targets = [t for t in canonical(row[c["name"]]) if t != src] or [row[c["name"]]]
                for t in targets:
                    claims.append((src, t, maturity(row[c["maturity"]]), row[c["how"]], row[c["evidence"]], rel))


# ---- repos -------------------------------------------------------------------------------------

def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout.strip() or None


def split_image(ref):
    digest = None
    if "@" in ref:
        ref, digest = ref.split("@", 1)
    if ":" in ref.rsplit("/", 1)[-1]:
        name, tag = ref.rsplit(":", 1)
        return name, tag, digest
    return ref, None, digest


def cargo_dep(name, spec):
    if isinstance(spec, str):
        return name, spec.strip(), "crates-io"
    pkg = spec.get("package", name)
    req = (spec.get("version") or spec.get("tag") or spec.get("branch") or spec.get("rev") or "").strip() or None
    kind = ("git" if "git" in spec else "path" if "path" in spec
            else "workspace" if spec.get("workspace") else "crates-io")
    return pkg, req, kind


def deps_of(name, rel, text, out):
    """Append (manifest_path, ecosystem, package, version_req, resolved_version, source_kind) rows."""
    if name == "Cargo.toml":
        data = tomllib.loads(text)
        for section in (data, data.get("workspace", {})):
            for key in ("dependencies", "dev-dependencies"):
                for dep, spec in section.get(key, {}).items():
                    pkg, req, kind = cargo_dep(dep, spec)
                    out.append((rel, "cargo-toml", pkg, req, None, kind))
    elif name == "Cargo.lock":
        for p in tomllib.loads(text).get("package", []):
            src = p.get("source", "")
            kind = "git" if src.startswith("git+") else "crates-io" if src.startswith("registry+") else "path"
            out.append((rel, "cargo-lock", p["name"], None, p.get("version"), kind))
    elif name == "pyproject.toml":
        for req in tomllib.loads(text).get("project", {}).get("dependencies", []):
            m = re.match(r"\s*([A-Za-z0-9._-]+)(\[[^\]]*\])?\s*(.*)", req)
            if m:
                out.append((rel, "pyproject", m.group(1).lower(), m.group(3).strip() or None, None, "pypi"))
    elif name == "package.json":
        data = json.loads(text)
        for key in ("dependencies", "devDependencies"):
            for dep, ver in (data.get(key) or {}).items():
                out.append((rel, "package-json", dep, str(ver), None, "npm"))
    elif name == "MODULE.bazel":
        for m in BAZEL_DEP_RE.finditer(text):
            n = re.search(r"name\s*=\s*\"([^\"]+)\"", m.group(1))
            v = re.search(r"version\s*=\s*\"([^\"]+)\"", m.group(1))
            if n:
                out.append((rel, "bazel-module", n.group(1), v.group(1) if v else None, None, "bcr"))


def images_of(name, text, out):
    """Append (kind, image reference) rows for the container image files we know."""
    low = name.lower()
    if low.endswith(".aib.yml"):
        block = re.search(r"^([ \t]*)container_images:[ \t]*\n((?:\1[ \t]+.*\n|[ \t]*\n)*)", text + "\n", re.M)
        for item in re.split(r"^\s*-\s", block.group(2), flags=re.M)[1:] if block else []:
            f = dict(re.findall(r"(source|tag|digest):\s*[\"']?([^\"'\s#]+)", item))
            if "source" in f:
                out.append(("aib", f["source"] + (f":{f['tag']}" if "tag" in f else "")
                            + (f"@{f['digest']}" if "digest" in f else "")))
        return
    if low.endswith(".container"):
        refs, kind = re.findall(r"^Image=(\S+)", text, re.M), "quadlet"
    elif low.startswith(("dockerfile", "containerfile")) or low.endswith(".dockerfile"):
        stages, refs, kind = set(), [], "dockerfile"
        for m in re.finditer(r"^\s*FROM\s+(?:--\S+\s+)*(\S+)(?:\s+AS\s+(\S+))?", text, re.M | re.I):
            if m.group(1).lower() not in stages and m.group(1) != "scratch":
                refs.append(m.group(1))
            if m.group(2):
                stages.add(m.group(2).lower())
    elif low.endswith((".yml", ".yaml")) and "compose" in low:
        refs, kind = IMAGE_LINE_RE.findall(text), "compose"
    elif low.endswith((".yml", ".yaml")) and "runtimeConfig" in text:
        refs, kind = IMAGE_LINE_RE.findall(text), "ankaios"
    else:
        return
    out.extend((kind, r) for r in refs)


def ports_of(text, out):
    indent = None
    for line in text.splitlines():
        m = re.match(r"(\s*)ports:\s*$", line)
        if m:
            indent = len(m.group(1))
            continue
        if indent is None or not line.strip() or line.strip().startswith("#"):
            continue
        if len(line) - len(line.lstrip()) < indent or not line.strip().startswith("-"):
            if len(line) - len(line.lstrip()) <= indent:
                indent = None
            continue
        value = line.strip()[1:].strip().strip("\"'").split("/")[0]
        parts = value.split(":")
        if value and "=" not in value and not value.endswith(":"):
            out.append((parts[-2] if len(parts) >= 2 else None, parts[-1]))


def routes_of(text, out):
    """Axum/aide registrations; `{CONST}` in a path is filled from the file's &str consts."""
    consts = dict(re.findall(r"const\s+(\w+)\s*:\s*&(?:'static\s+)?str\s*=\s*\"([^\"]*)\"", text))
    found = [(m, re.sub(r"\{([A-Z_][A-Z0-9_]*)\}", lambda c: consts.get(c.group(1), c.group(0)), m.group(2)))
             for m in ROUTE_RE.finditer(text)]
    base = BASE_CONST_RE.search(text)
    base = base.group(1) if base else next((p for m, p in found if m.group(1) == "nest"), None)
    for m, path in found:
        if m.group(1) == "nest":
            out.append(("NEST", path, None))
            continue
        depth, i = 1, m.end()
        while i < len(text) and depth and i - m.end() < 4000:
            depth += {"(": 1, ")": -1}.get(text[i], 0)
            i += 1
        methods = sorted({x.upper() for x in METHOD_RE.findall(text[m.end():i])}) or [None]
        out.extend((meth, path, base) for meth in methods)


def repo_facts(repos, deps, images, ports, routes, vss):
    for repo in sorted(p for p in REPOS.iterdir() if p.is_dir()):
        head = (git(repo, "log", "-1", "--format=%H|%cI") or "|").split("|")
        repos.append((repo.name, f"repos/{repo.name}", git(repo, "remote", "get-url", "origin"),
                      head[0] or None, head[1] or None))
    for root, dirs, files in os.walk(REPOS):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("bazel-"))
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, VAULT)
            parts = rel.split(os.sep)
            if len(parts) < 3:
                continue
            repo, ext, low = parts[1], os.path.splitext(name)[1].lower(), name.lower()
            manifest = name in ("Cargo.toml", "Cargo.lock", "pyproject.toml", "package.json", "MODULE.bazel")
            imagey = (low.endswith((".container", ".dockerfile")) or low.startswith(("dockerfile", "containerfile"))
                      or ext in (".yml", ".yaml"))
            if not (manifest or imagey or ext in VSS_EXT):
                continue
            try:
                if os.path.islink(path) or os.path.getsize(path) > 2_000_000:
                    continue
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()
                if manifest:
                    rows = []
                    deps_of(name, rel, text, rows)
                    deps.extend((repo, *r) for r in rows)
                if imagey:
                    rows = []
                    images_of(name, text, rows)
                    images.extend((repo, rel, kind, *split_image(ref)) for kind, ref in rows)
                    if "compose" in low:
                        rows = []
                        ports_of(text, rows)
                        ports.extend((repo, rel, *r) for r in rows)
                if ext == ".rs" and ("route(" in text or "nest(" in text):
                    rows = []
                    routes_of(text, rows)
                    routes.extend((repo, rel, *r) for r in rows)
                if ext in VSS_EXT and "Vehicle." in text:
                    vss.extend((repo, rel, p) for p in sorted({p.rstrip(".") for p in VSS_RE.findall(text)}))
            except Exception as e:  # noqa: BLE001 - one bad file must not stop the build
                warnings.append(f"{rel}: {type(e).__name__}: {e}")


# ---- load --------------------------------------------------------------------------------------

def load(con, table, columns, rows, tmp):
    """Bulk-load rows via a JSON-lines file (executemany is too slow for 100k rows)."""
    names = [c.split()[0] for c in columns]
    path = os.path.join(tmp, f"{table}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for row in sorted(set(tuple(tuple(v) if isinstance(v, list) else v for v in r) for r in rows),
                          key=lambda r: tuple("" if v is None else str(v) for v in r)):
            f.write(json.dumps(dict(zip(names, row))) + "\n")
    schema = ", ".join(f"'{c.split()[0]}': '{c.split(None, 1)[1]}'" for c in columns)
    con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_json('{path}', format='newline_delimited', "
                f"columns={{{schema}}})")
    print(f"{table}: {con.execute(f'SELECT count(*) FROM {table}').fetchone()[0]} rows")


SCHEMA = {
    "notes": ["path VARCHAR", "basename VARCHAR", "type VARCHAR", "component VARCHAR", "cluster VARCHAR",
              "status VARCHAR", "last_verified VARCHAR", "title VARCHAR", "tags VARCHAR[]",
              "applies_to VARCHAR[]", "gap_rows VARCHAR[]"],
    "links": ["from_path VARCHAR", "to_basename VARCHAR", "resolves BOOLEAN"],
    "claims": ["from_component VARCHAR", "to_component VARCHAR", "maturity VARCHAR", "how VARCHAR",
               "evidence VARCHAR", "source_path VARCHAR"],
    "repos": ["name VARCHAR", "path VARCHAR", "remote_url VARCHAR", "head_commit VARCHAR", "head_date VARCHAR"],
    "deps": ["repo VARCHAR", "manifest_path VARCHAR", "ecosystem VARCHAR", "package VARCHAR",
             "version_req VARCHAR", "resolved_version VARCHAR", "source_kind VARCHAR"],
    "images": ["repo VARCHAR", "file_path VARCHAR", "kind VARCHAR", "image VARCHAR", "tag VARCHAR",
               "digest VARCHAR"],
    "ports": ["repo VARCHAR", "file_path VARCHAR", "host_port VARCHAR", "container_port VARCHAR"],
    "routes": ["repo VARCHAR", "file_path VARCHAR", "method VARCHAR", "path VARCHAR", "base_path_hint VARCHAR"],
    "vss_paths": ["repo VARCHAR", "file_path VARCHAR", "vss_path VARCHAR"],
}

PINS_VIEW = f"""
CREATE VIEW pins_vs_current AS
SELECT ecosystem, package, list(DISTINCT v ORDER BY v) AS versions_seen,
       list(DISTINCT repo ORDER BY repo) AS repos
FROM (
  SELECT ecosystem, package, coalesce(resolved_version, version_req) AS v, repo FROM deps
  WHERE package IN ({", ".join(f"'{w}'" for w in WATCH)}) OR package LIKE 'ankaios%'
  UNION ALL
  SELECT 'image', image, tag, repo FROM images
  WHERE image ILIKE '%databroker%' OR image ILIKE '%zenoh%' OR image ILIKE '%ankaios%'
) WHERE v IS NOT NULL
GROUP BY ecosystem, package
ORDER BY package, ecosystem
"""


def main():
    start = time.time()
    tables = {k: [] for k in SCHEMA}
    vault_facts(tables["notes"], tables["links"], tables["claims"])
    repo_facts(tables["repos"], tables["deps"], tables["images"], tables["ports"], tables["routes"],
               tables["vss_paths"])
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    DB.parent.mkdir(exist_ok=True)
    for p in (DB, DB.with_suffix(".duckdb.wal")):
        p.unlink(missing_ok=True)
    con = duckdb.connect(str(DB))
    with tempfile.TemporaryDirectory() as tmp:
        for table, columns in SCHEMA.items():
            load(con, table, columns, tables[table], tmp)
    con.execute(PINS_VIEW)
    print(f"pins_vs_current: {con.execute('SELECT count(*) FROM pins_vs_current').fetchone()[0]} rows (view)")
    con.close()
    print(f"wrote {DB} with {len(warnings)} warning(s) in {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
