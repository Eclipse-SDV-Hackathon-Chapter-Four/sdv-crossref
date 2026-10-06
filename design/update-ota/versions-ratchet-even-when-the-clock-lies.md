---
title: Versions ratchet even when the clock lies
type: pattern
cluster: update-ota
component: none
tags: [tuf, uptane, freeze-attack, rollback-attack, key-rotation, time, snapshot, timestamp]
status: draft
sources:
  - https://theupdateframework.github.io/specification/latest/ (TUF specification, roles and client workflow)
  - https://uptane.org/docs/2.1.0/deployment/best-practices (Uptane Best Practices 2.1.0, secure source of time)
  - https://ssl.engineering.nyu.edu/blog/2022-03-29-uptane-v2 (Uptane 2.0.0 removed the Uptane-specific time server)
  - https://www.rfc-editor.org/rfc/rfc8915 (Network Time Security)
  - "[[opensovd-reference]] (JWT checks read the system clock)"
last-verified: 2026-10-03
related:
  - "[[two-keys-who-may-run-what-may-install]]"
  - "[[security-version-is-not-build-order]]"
  - "[[verify-offline-against-a-pinned-root]]"
applies-to: [opensovd, symphony, ankaios, autosd]
gap-rows: [H5, H8, H4]
---

# Versions ratchet even when the clock lies

**Problem.** A parked vehicle has no trustworthy clock. An attacker who controls the network (or the RTC battery) can replay last year's metadata, which was validly signed and still lists a vulnerable image, and every `expires` check passes because the clock was wound back.

**Forces.**
- Expiry needs time; time is the thing the vehicle cannot vouch for.
- Version monotonicity needs only persistent storage, which the vehicle has.
- Keys must rotate, and a car offline for two years must still follow the rotation.
- Small ECUs cannot run NTS; they inherit time from a gateway.

**The rule.** Split freshness into what needs a clock and what does not. Rollback and mix-and-match are defeated clock-free: store the last verified version of every metadata role and refuse any lower one (TUF snapshot binds targets versions, timestamp binds the snapshot version). Freeze is defeated only with time, so make time a ratchet too: `now = max(rtc, floor)`, where `floor` is raised from signed sources only (verified timestamp metadata, NTS, a Primary's signed time message) and held in secure storage. Key rotation is a chain: root N+1 must be signed by a threshold of root N's keys and its own, so an old client walks 1.root, 2.root, ... in order and never trusts a jump.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| TUF specification | four roles; timestamp (short expiry, binds snapshot), snapshot (binds every targets version), targets, root; client refuses decreasing versions and checks expiry against a fixed update start time | freeze, rollback and mix-and-match each have a named defender |
| TUF root rotation | versioned `N.root.json`, each signed by old and new thresholds | offline clients can catch up across many rotations |
| Uptane 2.0.0 / 2.1.0 | removed the Uptane-specific time server; Primaries "SHALL use some other secure external means", Secondaries take time from the Primary; GPS "SHOULD NOT be used as a secure time source" | time is a deployment decision, not a protocol given |
| RFC 8915 NTS | authenticated NTP | the recommended secure time source for a connected Primary |
| Android Verified Boot | stored rollback indexes in tamper-evident storage, no clock involved | monotonic floors work without time |

**On the Eclipse SDV stack.** No Eclipse SDV component keeps a time floor or a version store for update metadata today ([[gap-register]] H8). The HPC update agent (whatever sits behind SOVD `/updates` or a Symphony target provider) is the natural Primary: it runs NTS when online, raises the floor from every verified timestamp document, and serves signed time to MCUs behind it ([[the-hpc-is-the-mcus-update-gateway]]). The same floor fixes JWT `exp`/`nbf` in opensovd-core, which reads the system clock ([[opensovd-reference]], [[verify-offline-against-a-pinned-root]]).

**The trap.** Dropping expiry checks "because the car has no clock", which silently reopens the freeze attack; the opposite trap is trusting the RTC.

**For a hackathon team.** A JSON file `trust-state.json` with `{root_version, snapshot_version, timestamp_version, time_floor}`; the agent refuses any lower version and computes `now = max(clock, time_floor)`. Demo: replay an old signed manifest and wind the clock back; both are refused. Pitch: "our car cannot be lied to about time or versions".

**Evidence.** TUF roles and checks: TUF spec (fetched 2026-10-03). Uptane time server removal: NYU SSL blog on 2.0.0; best-practices quotes from 2.1.0 §3.1 (fetched). AVB stored rollback indexes: AOSP `external/avb` README "Rollback Protection". The time-floor ratchet as such is a design pattern, not quoted from Uptane; Uptane only requires "a sufficiently recent attestation of the time".
