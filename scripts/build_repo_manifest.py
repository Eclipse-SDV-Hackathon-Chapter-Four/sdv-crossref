#!/usr/bin/env python3
"""Regenerate repos/manifest.tsv: one row per shallow clone under repos/.

Columns: name, remote_url, head_commit, branch_or_ref, head_date, notes.
`./install_deps.sh --clone` reads this file to recreate repos/ on another machine.
"""
import pathlib
import subprocess

VAULT = pathlib.Path(__file__).resolve().parent.parent
REPOS = VAULT / "repos"
OUT = REPOS / "manifest.tsv"
COLUMNS = ["name", "remote_url", "head_commit", "branch_or_ref", "head_date", "notes"]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def row(repo):
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    notes = []
    if (repo / ".git" / "shallow").exists():
        notes.append("shallow")
    if (repo / ".gitmodules").exists():
        notes.append("submodules")
    if git(repo, "status", "--porcelain"):
        notes.append("worktree-dirty")
    return [repo.name, git(repo, "remote", "get-url", "origin"), git(repo, "rev-parse", "HEAD"),
            "detached" if branch == "HEAD" else branch, git(repo, "log", "-1", "--format=%cI"),
            ",".join(notes)]


def main():
    dirs = sorted((d for d in REPOS.iterdir() if d.is_dir()), key=lambda d: d.name)
    clones = [d for d in dirs if (d / ".git").exists()]
    others = [d.name for d in dirs if d not in clones]
    lines = ["\t".join(COLUMNS)] + ["\t".join(row(d)) for d in clones]
    if others:
        lines.append("# not a clone: " + " ".join(others))
    OUT.write_text("\n".join(lines) + "\n")
    print(f"{OUT.relative_to(VAULT)}: {len(clones)} clones")


if __name__ == "__main__":
    main()
