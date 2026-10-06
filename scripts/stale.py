#!/usr/bin/env python3
"""List notes whose last-verified is older than --days (or missing)."""
import argparse
from datetime import date, timedelta

from build_index import VAULT, iter_notes, load_note


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=30, help="age threshold in days (default 30)")
    ap.add_argument("--status", help="only notes with this status, e.g. draft (default: any)")
    args = ap.parse_args()
    cutoff = date.today() - timedelta(days=args.days)

    rows = []
    for path in iter_notes():
        meta, _ = load_note(path)
        status = meta.get("status") or "-"
        if args.status and status != args.status:
            continue
        verified = meta.get("last-verified") or ""
        try:
            fresh = date.fromisoformat(verified) >= cutoff
        except (TypeError, ValueError):
            fresh = False  # missing or unparseable counts as stale
        if not fresh:
            rows.append((path.relative_to(VAULT).as_posix(), str(status), verified or "-"))

    width = max((len(r[0]) for r in rows), default=0)
    for rel, status, verified in rows:
        print(f"{rel:<{width}}  {status:<9}  {verified}")


if __name__ == "__main__":
    main()
