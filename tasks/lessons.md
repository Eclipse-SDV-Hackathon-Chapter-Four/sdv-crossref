# Lessons

## 2026-10-03 — verify brief facts before fanning out (self-observed, not a user correction)
What went wrong: my agent briefs stated "Doctor Whodunit was used in Chapter 3", "S-CORE uses iceoryx2 for IPC" and "S-CORE is at v0.5" from a quick web-search summary. Three agents had to correct the brief; the errors were caught only because agents were told to source every claim.
Rule: before writing 10+ parallel briefs, spend one scout on "verify these five premises against primary sources" and feed the corrected facts into the briefs. Keep the "every claim needs a source" convention; it is what made the errors self-healing.

## 2026-10-03 — source snapshot filenames must be namespaced per agent
What went wrong: two agents wrote `sources/2026-10-03-github-org-repo-lists.md`; the second overwrote the first.
Rule: the conventions file now should say `sources/<date>-<component-or-event-slug>-<page>.md`; when many agents write to a shared folder, give each a filename prefix in its brief.

## 2026-10-03 — /tmp is tmpfs here: scratch builds and images cost RAM, and four verifiers in parallel killed the session
What went wrong: four verifiers (S-CORE Bazel, AutoSD QEMU, two cargo-heavy recipe runs) were launched in one message. Each wrote cargo targets, venvs and a 3.5 GB qcow2 into the session scratchpad under /tmp, which is a tmpfs on this machine; 15 GB of scratch sat in RAM next to a Bazel server and QEMU, and the OOM killer took the session.
Rule: run heavy verifiers one at a time (QEMU, Bazel, large cargo builds never together). Put anything over a few MB under `.local-<slug>/` in the vault (on disk, excluded in `scripts/build_index.py`), never in the scratchpad or /tmp. Give every verifier brief an explicit memory cap (QEMU `-m`, Bazel `--local_ram_resources`/`--jobs`) and the sentence "/tmp is RAM".
