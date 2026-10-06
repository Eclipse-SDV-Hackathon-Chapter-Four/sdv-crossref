#!/usr/bin/env python3
"""Regenerate synthesis/integration-matrix.md from every <slug>-integration-notes.md table.

Rows = the component whose notes made the claim, columns = the component claimed about.
"""
import datetime
import re

from build_index import VAULT, iter_notes, parse_frontmatter

OUT = VAULT / "synthesis" / "integration-matrix.md"
SLUGS = ["iceoryx2", "s-core", "opensovd", "vss-kuksa", "uprotocol", "ankaios", "opendut", "autosd",
         "openbsw", "sdv-blueprints", "zenoh", "symphony", "muto", "threadx", "kanto", "velocitas",
         "autowrx", "sommr", "chariott"]
CORE = SLUGS[:9]
# Regexes matched (word-bounded, case-insensitive) against the row's project name.
ALIASES = {
    "iceoryx2": ["iceoryx2"], "s-core": ["s-core", "score"], "opensovd": ["opensovd", "sovd"],
    "vss-kuksa": ["vss", "kuksa"], "uprotocol": ["uprotocol"], "ankaios": ["ankaios"],
    "opendut": ["opendut"], "autosd": ["autosd"], "openbsw": ["openbsw"],
    "sdv-blueprints": [r"sdv[ -]blueprints?", "blueprints?"], "zenoh": ["zenoh"],
    "symphony": ["symphony"], "muto": ["muto"], "threadx": ["threadx"], "kanto": ["kanto"],
    "velocitas": ["velocitas"], "autowrx": ["autowrx"], "sommr": ["sommr"], "chariott": ["chariott"],
}
LEVELS = ["none", "idea", "prototype", "demo", "production"]
SYMBOL = {"none": "·", "idea": "?", "prototype": "~", "demo": "+", "production": "●", "unknown": "–"}
MATURITY_WORDS = [  # (regex, level); the earliest match in the cell wins
    (r"\bnone\b|not found|\bno\b", "none"), (r"\bidea\b|\bplanned\b|\bproposed\b", "idea"),
    (r"prototype|\bpoc\b|experimental", "prototype"), (r"\bdemo", "demo"), (r"production", "production"),
]
WIKILINK_RE = re.compile(r"\[\[[^\]]*\]\]")


def split_row(line):
    cells = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip() for c in cells[1:-1]] if line.strip().endswith("|") else [c.strip() for c in cells[1:]]


def find_table(text):
    """Return (header cells, data rows) of the first integration table, or None."""
    lines = text.splitlines()
    for i, line in enumerate(lines[:-1]):
        if not line.lstrip().startswith("|"):
            continue
        header = split_row(line)
        low = line.lower()
        if len(header) >= 4 and ("project" in low or "integrat" in low) and re.match(r"^\s*\|[\s:|-]+$", lines[i + 1]):
            rows = []
            for row in lines[i + 2:]:
                if not row.lstrip().startswith("|"):
                    break
                rows.append(split_row(row))
            return header, rows
    return None


def column(header, word, default):
    return next((i for i, h in enumerate(header) if word in h.lower()), default)


def canonical(name):
    low = WIKILINK_RE.sub(" ", name).lower()
    return [s for s in SLUGS if any(re.search(rf"(?<![\w-]){a}(?![\w-])", low) for a in ALIASES[s])]


def maturity(text):
    low = text.lower()
    if re.search(r"\bpartial", low):
        return "demo" if re.search(r"\bdemo", low) else "prototype"
    hits = sorted((m.start(), lvl) for rx, lvl in MATURITY_WORDS for m in [re.search(rx, low)] if m)
    return hits[0][1] if hits else "unknown"


def best(claims):
    known = [c["maturity"] for c in claims if c["maturity"] != "unknown"]
    return max(known, key=LEVELS.index) if known else "unknown"


def main():
    claims, other, warnings, sources = {}, [], [], []
    nrows = 0
    paths = [p for p in iter_notes() if p.parent.parent.name == "components"
             and p.name == f"{p.parent.name}-integration-notes.md"]
    for path in paths:
        rel = path.relative_to(VAULT).as_posix()
        src = path.parent.name
        _, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        table = find_table(body)
        if table is None:
            warnings.append(f"{rel}: no integration table found")
            continue
        sources.append(rel)
        header, rows = table
        cols = {k: column(header, w, d) for k, w, d in [("name", "project", 0), ("how", "how", 2),
                ("maturity", "maturity", 3), ("evidence", "evidence", 4)]}
        for n, row in enumerate(rows, 1):
            if len(row) < len(header):
                warnings.append(f"{rel}: table row {n} has {len(row)} cells, expected {len(header)}: {row[:1]}")
                continue
            nrows += 1
            claim = {"from": src, "name": row[cols["name"]], "how": row[cols["how"]],
                     "raw": row[cols["maturity"]], "maturity": maturity(row[cols["maturity"]]),
                     "evidence": row[cols["evidence"]]}
            if claim["maturity"] == "unknown":
                warnings.append(f"{rel}: row {n} ({claim['name']}): maturity '{claim['raw']}' not recognised")
            targets = [t for t in canonical(claim["name"]) if t != src]
            if not targets:
                other.append(claim)
            for t in targets:
                claims.setdefault((src, t), []).append(claim)

    cell = {k: best(v) for k, v in claims.items()}
    today = datetime.date.today().isoformat()
    out = ["---", "title: SDV integration matrix", "type: synthesis", "component: none",
           "tags: [sdv, integration, generated]", "status: draft", "sources:"]
    out += [f"  - {s}" for s in sources]
    out += [f"last-verified: {today}", "related:"]
    out += [f'  - "[[{p.split("/")[-1][:-3]}]]"' for p in sources]
    out += ["---", "", "# SDV integration matrix", "",
            "<!-- Generated by scripts/build_matrix.py. Do not edit by hand; fix the source integration-notes tables. -->",
            "", f"Aggregated from {len(sources)} integration-notes tables ({nrows} rows). Each cell is the highest "
            "maturity claimed by the row component's note about the column component.", "",
            "## Grid", "", "Legend: " + ", ".join(f"`{SYMBOL[l]}` {l}" for l in LEVELS + ["unknown"])
            + ", blank = no claim. Rows = from (note author), columns = to.", "",
            "| from \\ to | " + " | ".join(SLUGS) + " |", "|---|" + "---|" * len(SLUGS)]
    for a in SLUGS:
        out.append(f"| **{a}** | " + " | ".join(
            "\\" if a == b else SYMBOL[cell[(a, b)]] if (a, b) in cell else " " for b in SLUGS) + " |")

    out += ["", "## Asymmetries", "", "Pairs where the two notes disagree by more than one maturity level "
            "(review hot-list).", ""]
    asym = []
    for i, a in enumerate(SLUGS):
        for b in SLUGS[i + 1:]:
            x, y = cell.get((a, b), "unknown"), cell.get((b, a), "unknown")
            if "unknown" not in (x, y) and abs(LEVELS.index(x) - LEVELS.index(y)) > 1:
                asym.append(f"- **{a} ↔ {b}**: {a} says {x}, {b} says {y} "
                            f"([[{a}-integration-notes]], [[{b}-integration-notes]])")
    out += asym or ["- none"]

    out += ["", "## Gaps", "", "Core pairs where every claim (either direction) is none/idea/unknown, "
            "or no claim exists.", ""]
    gaps = []
    for i, a in enumerate(CORE):
        for b in CORE[i + 1:]:
            pair = claims.get((a, b), []) + claims.get((b, a), [])
            if all(c["maturity"] in ("none", "idea", "unknown") for c in pair):
                gaps.append(f"- {a} ↔ {b}: " + (", ".join(sorted({c['maturity'] for c in pair})) or "no claim"))
    out += gaps or ["- none"]

    out += ["", "## Detail", ""]
    for a, b in sorted({tuple(sorted(k)) for k in claims}):
        out += [f"### {a} ↔ {b}", ""]
        for key in [(a, b), (b, a)]:
            for c in claims.get(key, []):
                out += [f"- [[{c['from']}-integration-notes]] → {key[1]} (row: {c['name']}): "
                        f"**{c['maturity']}** (original: {c['raw']})",
                        f"  - how: {c['how']}", f"  - evidence: {c['evidence']}"]
        out.append("")

    out += ["## Other", "", "Rows whose project name matched no canonical slug.", ""]
    for c in sorted(other, key=lambda c: (c["from"], c["name"])):
        out += [f"- [[{c['from']}-integration-notes]] → {c['name']}: **{c['maturity']}** (original: {c['raw']})",
                f"  - how: {c['how']}", f"  - evidence: {c['evidence']}"]
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    for w in warnings:
        print(f"warning: {w}")
    print(f"wrote {OUT}: {len(sources)} files, {nrows} rows, {sum(map(len, claims.values()))} claims, "
          f"{len(other)} other, {len(asym)} asymmetries, {len(gaps)} gaps")


if __name__ == "__main__":
    main()
