#!/usr/bin/env python3
"""Report broken [[wiki-links]] and duplicate basenames. Exit 1 on any problem."""
import re
import sys

from build_index import VAULT, iter_notes

LINK_RE = re.compile(r"\[\[([^\]|#]*)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
# Links inside HTML comments, fenced code and inline code are examples, not links.
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def _blank(match):
    # Keep newlines so reported line numbers stay correct.
    return re.sub(r"[^\n]", " ", match.group(0))


def main():
    notes = list(iter_notes())
    by_stem = {}
    for path in notes:
        by_stem.setdefault(path.stem, []).append(path.relative_to(VAULT).as_posix())

    missing = 0
    for path in notes:
        text = path.read_text(encoding="utf-8")
        for rx in (COMMENT_RE, FENCE_RE, INLINE_CODE_RE):
            text = rx.sub(_blank, text)
        rel = path.relative_to(VAULT).as_posix()
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in LINK_RE.finditer(line):
                target = m.group(1).strip()
                if not target:  # [[#heading]] points into the same note
                    continue
                stem = target[:-3] if target.endswith(".md") else target
                if stem in by_stem or (VAULT / target).exists() or (VAULT / f"{stem}.md").exists():
                    continue
                print(f"{rel}:{lineno}: missing [[{target}]]")
                missing += 1

    dupes = {stem: paths for stem, paths in by_stem.items() if len(paths) > 1}
    for stem, paths in sorted(dupes.items()):
        print(f"duplicate basename {stem}.md: {', '.join(paths)}")

    if missing or dupes:
        print(f"FAIL: {missing} missing link(s), {len(dupes)} duplicate basename(s)")
        return 1
    print(f"OK: {len(notes)} notes, no missing links, no duplicate basenames")
    return 0


if __name__ == "__main__":
    sys.exit(main())
