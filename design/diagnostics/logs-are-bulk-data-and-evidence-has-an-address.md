---
title: Logs are bulk data, and evidence needs an address a tester can fetch
type: pattern
cluster: diagnostics
component: none
tags: [dlt, rfc5424, logs, bulk-data, communication-logs, evidence, sovd]
status: draft
sources:
  - https://www.rfc-editor.org/rfc/rfc5424 (syslog)
  - https://github.com/COVESA/dlt-daemon (DLT, AUTOSAR DLT protocol)
  - https://www.asam.net/standards/detail/sovd/ (logs, communication-logs, bulk-data)
  - https://github.com/eclipse-opensovd/classic-diagnostic-adapter (cda-tracing dlt-tracing feature)
  - https://github.com/eclipse-opensovd/opensovd-core (bulk-data routes, BulkDataProvider)
  - https://www.autosar.org/standards/foundation (AUTOSAR DLT; not fetched)
last-verified: 2026-10-03
related:
  - "[[opensovd-reference]]"
  - "[[let-the-standard-timestamp-your-evidence]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
applies-to: [opensovd, ankaios, s-core]
gap-rows: [A5, H1, E13]
---

# Logs are bulk data, and evidence needs an address a tester can fetch

**Problem.** The Guardian writes a perfect evidence trail into its container's stdout. The judge, or a workshop tester, needs it after the run, from outside, without `ssh` or `docker cp`.

**Forces.**
- Log *configuration* (levels, destinations) is small and live; log *content* is large and file-shaped.
- DLT is binary, structured and industry-standard; RFC 5424 is text and universal.
- Developer traffic traces (communication logs) must not leak into the same channel as customer-facing logs.
- Evidence must be stable (an id and a hash), not "the last 100 lines".

**The rule.** Configuration through the `logs` resource, content through `bulk-data`, address by category and id. SOVD splits `logs` into entries and config (read/write/reset: level, target; RFC 5424 or DLT format), retrieves logged content as bulk-data downloads, and offers `communication-logs` as a separate dev/QA surface (traces of UDS/DoIP traffic). Evidence follows the same path: write one file per run (`evidence/<run-id>.json` plus `.sha256`), publish it as bulk-data in an `x-guardian-evidence` category, and let the verdict record its id.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 17978 `logs`, `communication-logs`, `bulk-data` | config resource, entries via bulk-data, separate comm-log channel | the standard split |
| AUTOSAR DLT / COVESA dlt-daemon | app and context ids, log levels, verbose and non-verbose, trace load control | the HPC logging convention |
| RFC 5424 syslog | PRI, timestamp, hostname, app-name, structured data | the text alternative with structured-data |
| OpenSOVD CDA `dlt-tracing` feature, `dlt-tracing-lib` repo | tracing appender to DLT, load-control feature | DLT out of the adapter today |
| opensovd-core `BulkDataProvider` + `/bulk-data/{category}/{id}` | list/download/upload/delete, 1 GiB body limit | a ready channel for evidence files |
| fault-lib design (design.md) | "reporting of faults additionally results in a log entry" | fault and log correlated by design |

**On the Eclipse SDV stack.**
- Core has `bulk-data` but no `logs` ([[opensovd-reference]]): the evidence file route works today via `BulkDataProvider` on `apps/guardian`, category `x-guardian-evidence`.
- `logs` config and `communication-logs` are unimplemented; if needed, serve a minimal `logs/config` (level) and keep content in bulk-data.
- Container logs under Ankaios are reachable with `ank logs`, not via SOVD ([[ankaios-reference]]): the bridge is a sidecar that rotates logs into the `BulkDataProvider` directory.
- Fault tie-in: put the fault code and run-id in every structured line so a `faults/{code}` record and the bulk file join ([[a-fault-is-a-state-machine-with-evidence-attached]]).

**The trap.** Storing evidence only in a time-series DB the judge cannot reach, then losing the story when the stack is torn down.

**For a hackathon team.** One bulk-data category with the run's evidence JSON and a SHA-256; a `curl` line in the README that downloads it. Pitch line: "evidence is a resource with an address".

**Evidence.** Logs/bulk-data/communication-logs rows: [[opensovd-reference]] coverage table (standard paywalled; unverified at clause level). CDA DLT feature flags: `repos/opensovd-cda/cda-tracing/Cargo.toml`. Bulk-data trait: `repos/opensovd-core/opensovd-core/src/bulkdata.rs`. Category name `x-guardian-evidence` is a proposal.
