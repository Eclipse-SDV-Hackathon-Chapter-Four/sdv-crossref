---
title: Pick the model by layer, not by fashion
type: pattern
cluster: data-modelling
component: none
tags: [vss, dtdl, vorto, opcua, autosar, j1939, dbc, decision]
status: draft
sources:
  - https://github.com/Azure/opendigitaltwins-dtdl/blob/master/DTDL/v3/DTDL.v3.md
  - https://github.com/eclipse-vorto/vorto (Vorto language 1.0 docs)
  - https://reference.opcfoundation.org/Core/Part3/v105/docs/6.2
  - https://www.autosar.org/ (ARXML/FIBEX, E2E PRS; spec PDFs not fetched, unverified details)
  - https://www.sae.org/standards/content/j1939da_202309/ (J1939 Digital Annex, unverified, paywalled)
  - https://covesa.github.io/vehicle_signal_specification/
last-verified: 2026-10-03
related:
  - "[[chariott-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[opensovd-overview]]"
  - "[[mappings-are-overlays-the-source-model-stays-pristine]]"
applies-to: [vss-kuksa, opensovd, chariott, uprotocol, openbsw]
gap-rows: [B6, B11, A4]
---

# Pick the model by layer, not by fashion

**Problem.** Teams ask "VSS or DTDL or AAS?" and end up modelling frames in a twin language or services in a signal catalog. Each of these models answers a different question and fails at the others.

**Forces.**
- Signals, services, twins and frames have different identity and lifecycle.
- Every model has its own version story, so crossing layers multiplies drift.
- Tooling and ecosystem gravity pull toward one model for everything.

**The rule.** One model per layer, mappings between layers, nothing in a layer it cannot express. Wire layer: frames and PGNs. Signal layer: a physical, source-free catalog. Service layer: operations and their contracts. Twin/asset layer: a thing with state, relations and a lifecycle. Cross layers only through explicit mappings that are overlays on the upper model, not edits to the lower one.

| Model | Models | Versions and extension | Use it for |
|---|---|---|---|
| CAN DBC | frames, bit layout, factor/offset, per-bus | none in the format; file versioning by convention | bytes on one bus |
| AUTOSAR ARXML, FIBEX | frames, PDUs, signal groups, E2E, services (SOME/IP) with datatypes | AUTOSAR release plus per-element variants | ECU build and configuration |
| SAE J1939 DA | PGN/SPN, scaling, "not available" encodings, address claim NAME | annual Digital Annex edition | trucks, body builders, trailers |
| VSS | physical signals, tree, units; no service, no source | semantic releases, `deprecation`, overlays | the vehicle-wide signal vocabulary |
| DTDL v3 (Ibeji) | Interface with Telemetry, Property, Command, Relationship, Component | DTMI `;version`, published versions immutable, `extends` | twins, commands, graph |
| Vorto | Information Model of Function Blocks, namespace plus semver, platform mappings | semver, mapping models | device capability catalogs (Eclipse, quiet) |
| OPC UA companion specs | ObjectTypes, instances, ModellingRules, methods, subtyping | namespace URI plus publication date, subtype to specialise | industrial and body-builder machines |
| AAS submodels | asset with templates and instances | submodel template ids | lifecycle documentation, digital product passport (unverified detail) |

**Prior art.** The table above is the prior art; the shared lesson is that DTDL/Vorto/OPC UA carry commands and relations while VSS (signals only) and DBC (frames only) do not, and that each of DTDL, Vorto, OPC UA and VSS can carry unit and enum on a datum.

**On the Eclipse SDV stack.** [[vss-kuksa-overview]] is the signal layer; Ibeji (DTDL) and Chariott sit above it but are dormant ([[chariott-overview]]), so a hackathon "service layer" is uProtocol topics plus SOVD operations ([[opensovd-overview]]). A VSS-to-SOVD mapping (gap A4) is an overlay-style mapping from signal to data resource, not a merged model. OpenBSW supplies the DBC layer ([[openbsw-overview]]).

**The trap.** Using VSS as the schema for a command or a frame; it has actuators but no operation contract and no layout.

**For a hackathon team.** Draw one slide with four layers and one named mapping per boundary; implement exactly one boundary (DBC to VSS). Pitch: "we map layers, we do not merge them".

**Evidence.** DTDL element kinds, versioning and immutability: DTDL v3 spec (fetched). Vorto namespace/semver, mappings, units: Vorto language docs (fetched). OPC UA InstanceDeclaration and ModellingRule: Part 3 6.2 (fetched). DBC, ARXML, J1939 DA rows are from standard knowledge, not fetched this session (unverified).
