---
title: Lock before you clear, and expect the lock to break
type: pattern
cluster: diagnostics
component: none
tags: [sovd, locks, concurrency, 409, 423, uds, single-tester]
status: draft
sources:
  - https://www.asam.net/standards/detail/sovd/ (locks resource)
  - https://www.iso.org/standard/86587.html (ISO 17978-3)
  - https://github.com/eclipse-opensovd/classic-diagnostic-adapter (docs 02_sovd-api Locks; cda-sovd/src/sovd/locks.rs, error.rs)
  - https://www.rfc-editor.org/rfc/rfc9110 (409, 423 via WebDAV RFC 4918)
  - https://www.iso.org/standard/72439.html (UDS, one active session per ECU)
last-verified: 2026-10-03
related:
  - "[[opensovd-reference]]"
  - "[[client-token-and-ecu-unlock-are-different-locks]]"
  - "[[a-fault-is-a-state-machine-with-evidence-attached]]"
applies-to: [opensovd, openbsw]
gap-rows: [A1, H7, E7]
---

# Lock before you clear, and expect the lock to break

**Problem.** UDS has one tester per ECU in practice: a second tester's 0x10 or 0x14 silently disturbs the first. Two dashboards and a script on a hackathon laptop each "clear faults" and race each other. Evidence disappears mid-capture.

**Forces.**
- Destructive actions (clear DTCs, write coding, flash) must have one owner.
- A crashed client must not hold a lock forever.
- A workshop supervisor must be able to override a stuck tester.
- The loser must learn *that* and *why* it lost, not get a bare error.

**The rule.** Acquire, act, release, and treat loss as normal. SOVD locks are resources with scope (vehicle, ECU, functional group), an expiry set in seconds, renewal by PUT, and optional preemption (breakable). Clearing faults, writing configurations and starting flash require the lock; reads do not. A client that sees `409` with error code `lock-broken` must stop, re-read state and re-acquire only if it still should. Preempted locks stay visible as "defunct" with who broke them and when.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ASAM SOVD `locks` | create with expiry, modify, delete; breakable; lock-broken 409 | the REST form of tester exclusivity |
| OpenSOVD CDA | locks at `/locks`, `/components/{ecu}/locks`, functional-group locks; POST 201+Location, owner renewal 200, PUT 204; `break_lock`, priority plugin; `lock-broken` error returns 409 with `broken_by`, `broken_at`, `current_holder`; contention by another holder returns 423 (409 if no priority plugin) | a working reference incl. defunct locks |
| UDS 0x10 / S3 timeout | the session is the lock; it lapses without 0x3E | what the lock sits on top of |
| HTTP/WebDAV LOCK (RFC 4918) | exclusive lock with timeout | prior art for expiring locks |
| Distributed leases (Chubby, etcd leases) | lock = lease with TTL, fencing token | why expiry is mandatory |

**On the Eclipse SDV stack.**
- CDA: `DELETE /components/{ecu}/faults` needs the lock ([[opensovd-reference]]); `x-sovd2uds-isexclusive` chooses enforcement, default exclusive; lock lifetime is a background task per lock.
- Core has no `locks` and no `faults` today, so a `FaultProvider` (A1) must bring its own mutual exclusion, or the Guardian's own DFM-side clear races a tester.
- Hackathon rule: every script that clears runs `POST locks (expiry 60 s)` -> `DELETE faults` -> `DELETE locks`, and the evidence recorder never holds a lock (read-only), so a clear in the middle of an injection run is attributable to a named holder.
- Status codes differ by source: the vault reference says lock-broken is 409 (matches CDA); contention at the vehicle scope is 423 in CDA docs. Write clients to treat both 409 and 423 as "do not proceed".

**The trap.** Reading `owned: true` once and assuming it forever: a preempt or expiry turns your next write into a 409 that your retry loop happily re-sends.

**For a hackathon team.** Show two clients: A holds the lock and clears; B tries to clear, receives the denial and prints the holder. Then break the lock with a higher-priority token and show A's next call fail with `lock-broken`. Pitch line: "lock before clear; the lock tells you who".

**Evidence.** Behaviour from `repos/opensovd-cda/docs/03_architecture/02_sovd-api/02_sovd-api.rst` (Locks) and `cda-sovd/src/sovd/{locks.rs,error.rs}` (LockBroken maps to `StatusCode::CONFLICT`; tests assert `StatusCode::LOCKED`). Whether the standard mandates 423 is unverified.
