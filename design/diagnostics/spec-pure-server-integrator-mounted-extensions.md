---
title: A spec-pure server, with extensions mounted by the integrator and disclosed
type: pattern
cluster: diagnostics
component: none
tags: [sovd, extensions, conformance, x-prefix, openapi, vendor]
status: draft
sources:
  - https://www.asam.net/standards/detail/sovd/ (ASAM SOVD; extension and vendor-specific naming)
  - https://www.iso.org/standard/86587.html (ISO 17978-3 API; paywalled, rule as in [[opensovd-reference]])
  - https://github.com/eclipse-opensovd/classic-diagnostic-adapter (cda-sovd, x-sovd2uds-* routes)
  - https://github.com/eclipse-opensovd/opensovd-core (opensovd-models DataCategory, x-… custom)
  - https://www.rfc-editor.org/rfc/rfc8615 (well-known URIs)
  - https://spec.openapis.org/oas/v3.1.0
last-verified: 2026-10-03
related:
  - "[[opensovd-reference]]"
  - "[[opensovd-overview]]"
  - "[[one-backend-trait-many-backends]]"
applies-to: [opensovd]
gap-rows: [H10, H11, H12, E7]
---

# A spec-pure server, with extensions mounted by the integrator and disclosed

**Problem.** A server that mixes standard routes with vendor ones cannot be certified, and a client written against it breaks on every other vehicle. The opposite, a server with no room for vendors, gets forked.

**Forces.**
- Conformance means a scanner can say "nothing outside the catalogue unless prefixed".
- Real vehicles need flashing, comparams, ODX jobs the standard does not carry.
- Integrators, not the library author, know their vendor routes.
- Clients need a way to learn what is non-standard before calling it.

**The rule.** The core serves only the standard surface; everything else is a mounted extension named `x-<ext>-...` (the prefix `x-sovd-` is reserved), and the extension list is itself an endpoint. Mounting is the integrator's act (a router merged into the server at build or config time), so the library stays spec-pure and the product owns its vendor surface. Disclosure is a small JSON document (name, version, routes, owner) that a scanner and a human can both read; the standard's per-path `{path}/docs` OpenAPI description should mark which operations are extensions.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ISO 17978 / ASAM SOVD | custom data categories and resources use `x-` names; `x-sovd-` reserved | the naming rule |
| HTTP well-known URIs (RFC 8615) | a fixed path where a server advertises metadata | the shape for a disclosure endpoint (path is a proposal, not in SOVD) |
| OpenAPI 3.1 `x-` specification extensions | vendor keys allowed anywhere, ignored by consumers | the same convention in schemas |
| OpenSOVD CDA | `x-sovd2uds-download/*`, `x-sovd2uds-bulk-data/*`, `x-single-ecu-jobs`, `x-sovd2uds-can-ecus` | a real, well-prefixed extension set (undisclosed) |
| OpenSOVD core | `DataCategory::Custom("x-…")`, axum router merge, gateway `--serve-dir` | an embeddable server where the integrator mounts routes |

**On the Eclipse SDV stack.**
- Counter-example in [[opensovd-overview]]: core serves `/sovd/v1`, the CDA serves `/vehicle/v15` with its own models. A client that works on one fails on the other, and the CDA's vendor routes sit beside standard ones at the same level.
- Good news: the CDA's extension names already follow the rule. Missing piece (H12): an endpoint listing them. Propose `GET /.well-known/sovd-extensions` returning `[{name, prefix, routes[], owner}]`; nothing in the 5 cloned repos has it (grep `well-known` finds none in CDA or core).
- Custom data like a Guardian's `x-guardian-` category goes through core's `DataProvider` ([[opensovd-reference]]) and needs no new route at all.

**The trap.** Putting your vendor operation at `/components/{id}/flash` because it "feels standard": it is now a conformance failure and a name collision with the next revision.

**For a hackathon team.** Keep your Guardian-specific routes under one `x-guardian-` prefix, add the one-endpoint disclosure, and show a generic client listing it. Pitch line: "spec-pure core, our extensions are disclosed".

**Evidence.** Prefix rule and reserved `x-sovd-` are from [[opensovd-reference]] (ISO text paywalled; unverified against the standard). CDA route names from the same note and `cda-sovd`. The `/.well-known/sovd-extensions` path is a proposal from gap H12, not part of SOVD.
