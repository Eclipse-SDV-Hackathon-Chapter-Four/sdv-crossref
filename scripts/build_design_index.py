#!/usr/bin/env python3
"""Regenerate the catalogue section of design/design-index.md from pattern-card frontmatter.

Everything above MARKER is hand-written and kept; everything below it is rewritten.
"""
import re

from build_index import VAULT, parse_frontmatter

MARKER = "<!-- generated below: python3 scripts/build_design_index.py -->"
INDEX = VAULT / "design" / "design-index.md"
GAP_REGISTER = VAULT / "synthesis" / "gap-register.md"
GAP_ROW_RE = re.compile(r"^\|\s*([A-Z]\d+[a-z]?)\s*\|\s*\*\*(.+?)\*\*")
RULE_MAX = 140


def _list(value):
    if isinstance(value, list):
        return [v for v in value if v]
    return [value] if value else []


def _cell(text):
    return text.replace("|", "\\|")


def _gap_key(gid):
    m = re.match(r"([A-Z]+)(\d+)(.*)", gid)
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (gid, 0, "")


def one_line_rule(body):
    for line in body.splitlines():
        if line.startswith("**The rule.**"):
            text = line[len("**The rule.**"):].strip()
            m = re.search(r"(?<=[.!?])\s", text)
            sentence = text[:m.start()] if m else text
            if len(sentence) > RULE_MAX:
                cut = sentence[:RULE_MAX].rsplit(" ", 1)[0]
                if cut.count("`") % 2:  # never leave inline code open
                    cut = cut[:cut.rfind("`")].rstrip()
                if cut.rfind("[[") > cut.rfind("]]"):  # nor a wiki-link
                    cut = cut[:cut.rfind("[[")].rstrip()
                sentence = cut + " …"
            return sentence
    return ""


def load_cards():
    cards = []
    for path in sorted((VAULT / "design").rglob("*.md")):
        if path == INDEX:
            continue
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("type") != "pattern":
            continue
        cards.append({
            "stem": path.stem,
            "cluster": meta.get("cluster") or "none",
            "status": meta.get("status") or "none",
            "applies": sorted(_list(meta.get("applies-to"))),
            "gaps": sorted(set(_list(meta.get("gap-rows"))), key=_gap_key),
            "rule": one_line_rule(body),
        })
    return cards


def gap_titles():
    titles = {}
    for line in GAP_REGISTER.read_text(encoding="utf-8").splitlines():
        m = GAP_ROW_RE.match(line)
        if m:
            titles.setdefault(m.group(1), m.group(2).strip().rstrip(".:"))
    return titles


def _counts(cards, key):
    counts = {}
    for c in cards:
        counts[c[key]] = counts.get(c[key], 0) + 1
    return ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))


def _links(stems):
    return ", ".join(f"[[{s}]]" for s in sorted(stems))


def render(cards):
    out = ["", "## Catalogue", "",
           f"**{len(cards)} patterns.** Clusters: {_counts(cards, 'cluster')}. "
           f"Status: {_counts(cards, 'status')}.", ""]
    for cluster in sorted({c["cluster"] for c in cards}):
        group = sorted((c for c in cards if c["cluster"] == cluster), key=lambda c: c["stem"])
        out += [f"### {cluster} ({len(group)})", "",
                "| Pattern | One-line rule | Applies to | Gap rows |",
                "|---|---|---|---|"]
        for c in group:
            out.append(f"| [[{c['stem']}]] | {_cell(c['rule'])} | {', '.join(c['applies'])} "
                       f"| {', '.join(c['gaps'])} |")
        out.append("")

    by_gap, by_comp = {}, {}
    for c in cards:
        for g in c["gaps"]:
            by_gap.setdefault(g, []).append(c["stem"])
        for a in c["applies"]:
            by_comp.setdefault(a, []).append(c["stem"])

    titles = gap_titles()
    out += ["## By gap row", "",
            "Gap ids refer to [[gap-register]].", "",
            "| Gap | Title | Patterns |", "|---|---|---|"]
    for g in sorted(by_gap, key=_gap_key):
        out.append(f"| {g} | {_cell(titles.get(g, '—'))} | {_links(by_gap[g])} |")
    out += ["", "## By component", "", "| Component | Patterns |", "|---|---|"]
    for a in sorted(by_comp):
        out.append(f"| {a} | {_links(by_comp[a])} |")
    out.append("")
    return out


def build():
    text = INDEX.read_text(encoding="utf-8")
    head = text.split(MARKER, 1)[0].rstrip("\n") if MARKER in text else text.rstrip("\n")
    cards = load_cards()
    INDEX.write_text("\n".join([head, "", MARKER] + render(cards)), encoding="utf-8")
    print(f"wrote {INDEX}: {len(cards)} patterns")


if __name__ == "__main__":
    build()
