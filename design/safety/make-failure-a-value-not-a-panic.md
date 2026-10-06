---
title: Make failure a value, not a panic
type: pattern
cluster: safety
component: none
tags: [rust, safe-rust, ferrocene, scrc, clippy, unsafe, docs-as-code, s-core]
status: draft
sources:
  - https://coding-guidelines.arewesafetycriticalyet.org/ (Safety-Critical Rust Coding Guidelines, SCRC)
  - https://github.com/rustfoundation/safety-critical-rust-coding-guidelines
  - https://public-docs.ferrocene.dev/main/index.html (Ferrocene qualified toolchain docs)
  - https://ferrous-systems.com/blog/officially-qualified-ferrocene/ (ISO 26262 ASIL D, IEC 61508 SIL 4)
  - https://github.com/eclipse-score/score_rust_policies (relaxed and strict/ASIL lint profiles)
  - https://misra.org.uk/app/uploads/2025/03/MISRA-C-2025-ADD6.pdf (MISRA C:2025 Addendum 6, Rust applicability)
  - repos/s-core-score/docs/contribute/development/rust/coding_guidelines.rst
last-verified: 2026-10-03
related:
  - "[[s-core-overview]]"
  - "[[evidence-is-a-linked-record-not-a-log]]"
  - "[[decide-once-per-cycle-in-a-fixed-order]]"
applies-to: [s-core, iceoryx2, opensovd, uprotocol]
gap-rows: [A3, A8, E6]
---

# Make failure a value, not a panic

**Problem.** The Guardian parses a temperature with `.unwrap()`, a malformed sample arrives, the thread panics, the process exits, Ankaios restarts it, and for the restart window there is no thermal warning at all. Memory safety did not make it a safe function; an unplanned exit is an unhandled hazard.

**Forces.**
- Rust removes whole classes of memory bugs, but panics, overflow and lossy casts remain.
- Safety arguments need a qualified compiler and documented failure behaviour; hackathons need `cargo run`.
- `unsafe` is sometimes needed (FFI, shared memory); it must be small and argued.
- Contributor process (requirements, docs-as-code) is part of the evidence, not paperwork after it.

**The rule.** Every failure the function can meet is a typed value that reaches a decision: inputs return `Result<T, Reason>`, absent data is `Option`, and the cycle maps every `Err` to a policy ([[deciding-on-a-bad-state-is-wrong-not-degraded]]). Concretely: `#![forbid(unsafe_code)]` in the decider crate (unsafe lives in a separate, reviewed crate); no `unwrap`/`expect`/indexing on external data (`clippy::unwrap_used`, `indexing_slicing`, `panic_in_result_fn`); explicit-width integers and `checked_*`/`saturating_*` arithmetic with overflow checks on in release; no `as` casts (`TryFrom` instead); `panic = "abort"` so a panic that does slip through is a clean, supervised death, not an unwinding half-state. Build with the toolchain you will argue with (Ferrocene for qualified targets).

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Safety-Critical Rust Coding Guidelines (SCRC) | rules grouped by Rust Reference chapters: types, expressions, errors, concurrency, unsafety, FFI | the community guideline set; S-CORE expects it complete by end-2026 |
| Ferrocene | rustc qualified for ISO 26262 ASIL D and IEC 61508 SIL 4, with a language specification | the toolchain an assessor accepts; S-CORE's `.bazelrc` already uses it |
| S-CORE Rust coding guidelines + `score_rust_policies` | relaxed and strict/ASIL Clippy/rustc profiles; "panic-free … only APIs with a proper return value"; overflow checks in release; CodeQL and Miri | the exact lint set to copy |
| MISRA C:2025 Addendum 6 | MISRA C rules mapped to Rust applicability | cross-reference for C-trained assessors |
| S-CORE docs-as-code | requirements as sphinx-needs with `:safety:`, `:security:`, `:derived_from:`, `:satisfied_by:` | traceability from rule to code to test |

**On the Eclipse SDV stack.** S-CORE contributions need ECA + DCO and requirement/safety documentation; requirement objects carry `:safety: ASIL_B|QM` and link with `:derived_from:`/`:satisfied_by:` ([[s-core-overview]]). A Guardian that wants an S-CORE runtime link (gap A3) or a fault-lib reporter should adopt the strict profile from `score_rust_policies` and Ferrocene-compatible Rust. iceoryx2 payloads must be `#[repr(C)]` and self-contained ([[iceoryx2-overview]]); keep that `unsafe` boundary out of the decider crate.

**The trap.** Believing `forbid(unsafe_code)` makes the code safe while `unwrap()` on sensor input turns every malformed sample into a missing warning.

**For a hackathon team.** Copy the strict lint table into `Cargo.toml`, add `#![forbid(unsafe_code)]`, run `cargo clippy -- -D warnings` in CI, and show a fuzzed malformed payload that produces a fault event instead of a restart. Pitch: "our Guardian cannot panic on input; failure is a value with a name".

**Evidence.** S-CORE text and lint mapping: repos/s-core-score/docs/contribute/development/rust/coding_guidelines.rst. Ferrocene qualification: Ferrous Systems announcement (search result; page not fetched). SCRC chapter structure fetched from coding-guidelines.arewesafetycriticalyet.org on 2026-10-03; individual rule ids not verified. Specific Clippy lint names listed here are standard Clippy lints; whether each is in the strict profile is unverified except those quoted in coding_guidelines.rst (e.g. `panic_in_result_fn`, `as_conversions`, `cast_possible_truncation`).
