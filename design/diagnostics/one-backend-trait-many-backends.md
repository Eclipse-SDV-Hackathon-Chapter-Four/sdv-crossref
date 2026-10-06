---
title: One backend trait, many backends
type: pattern
cluster: diagnostics
component: none
tags: [sovd, gateway, proxy, federation, backend, traits, uds, app-entity]
status: draft
sources:
  - https://github.com/eclipse-opensovd/opensovd (docs/design/design.md: Gateway, CDA, UDS2SOVD, topology)
  - https://github.com/eclipse-opensovd/opensovd-core (opensovd-core/src/data.rs DataProvider, bulkdata.rs BulkDataProvider; docs/architecture.md)
  - https://github.com/eclipse-opensovd/classic-diagnostic-adapter
  - https://www.asam.net/standards/detail/sovd/
  - https://www.iso.org/standard/72439.html (UDS behind the UDS backend)
last-verified: 2026-10-03
related:
  - "[[opensovd-overview]]"
  - "[[spec-pure-server-integrator-mounted-extensions]]"
  - "[[an-hpc-app-is-an-entity-not-an-ecu]]"
applies-to: [opensovd, s-core, openbsw]
gap-rows: [A1, A4, H11]
---

# One backend trait, many backends

**Problem.** Every way to reach a thing to diagnose (a UDS ECU over DoIP, an app on the HPC, another SOVD server, a supplier's container) ends up with its own HTTP surface, paths and models. The client sees four products.

**Forces.**
- One external API per vehicle (a single base path and model) versus many internal sources.
- Supplier boxes arrive with their own SOVD server and own an ECU.
- Backends fail independently; the router must not.
- A trait too wide makes every backend implement what it cannot.

**The rule.** One router, one resource-level trait per collection, many implementors; where a thing lives is a *configuration* choice, not a URL. Four backend kinds cover everything: **UDS** (translate resources to services using a description), **gateway** (forward by entity id to child servers, nestable), **proxy** (front another server's tree under a local name, translating path and model), **app-entity** (a container that owns an ECU and serves its own SOVD, mounted under that entity). Auth, locks and error shape live in the router, so the same 409 means the same thing everywhere.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| ASAM SOVD / ISO 17978 | entities with relations (`hosts`, `contains`, `belongs-to`), SOVD gateway concept | topology independent of transport |
| OpenSOVD design.md | Gateway "forwards to adapters, proxies, clients"; CDA = sovd2uds; apps register via Diagnostic Library; `FaultManager` serves `faults/`, apps serve `data/` | the intended split by resource, not by server |
| opensovd-core `DataProvider` / `BulkDataProvider` | per-entity `Arc<dyn …>`; `list/read/write` and `categories/list/download/upload/delete` | a narrow trait per collection (no faults, operations, locks traits yet) |
| AUTOSAR Dcm / Dem | one Dcm front, SW-C ports and DSL/DSD routing to sub-services | one front for many services behind it |
| Envoy / API gateway routing | route by prefix, filter chain | the router role |
| ISO 13400 DoIP routing | logical address to node, entity gateway | the lower layer's version of nesting |

**On the Eclipse SDV stack.**
- Core's seam is `DataProvider` per entity in `opensovd-providers`; `BulkDataProvider` likewise. There is no `FaultProvider` (issue #156) and no backend that forwards: the gateway forwarding in [[opensovd-overview]] is on the MVP list, not in `routes/`. Gap H11 is exactly "add a `proxy` backend fronting the CDA at `:20002/vehicle/v15`".
- Mounted shape: `components/Hpc1` (hosts Guardian app, FaultManager), `components/OpenBSW` (UDS backend through the CDA), a supplier container as `apps/<id>` with its own server nested behind a gateway entry.
- Model drift is the hard part: CDA fault flags are snake_case, DFM's camelCase ([[opensovd-reference]]); the proxy must translate or both must converge (#553).
- Note the design says FaultManager's `faults/` does not aggregate other apps, so a cross-entity view needs a `functions/VehicleHealth` entity.

**The trap.** Letting the proxy pass bytes through unchanged: two models and two path schemes leak to the client and "one base path" is a lie.

**For a hackathon team.** Show one URL tree where `components/Guardian` is served in-process and `components/OpenBSW` is served by the CDA through a thin forwarding layer. Pitch line: "one endpoint, four ways to reach the thing".

**Evidence.** Trait signatures from `repos/opensovd-core/opensovd-core/src/{data,bulkdata}.rs`; topology from `repos/opensovd-main/docs/design/design.md`; CDA port and path from [[opensovd-reference]]. The "app-entity with own server" and nested-gateway shapes are from the SOVD concept and the OpenSOVD design (no code in the vault implements them; unverified in the ISO text).
