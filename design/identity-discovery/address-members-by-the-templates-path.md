---
title: Address members by the template's path, find instances by browsing
type: pattern
cluster: identity-discovery
component: none
tags: [identity, templates, instances, opc-ua, aas, wot, thing-model, browse-path, vss, sovd]
status: draft
sources:
  - https://reference.opcfoundation.org/Core/Part3/v105/docs/6.4 (OPC UA Part 3: InstanceDeclarations, ModellingRules, BrowsePaths)
  - https://reference.opcfoundation.org/Core/Part4/v105/docs/5.8.4 (TranslateBrowsePathsToNodeIds)
  - https://industrialdigitaltwin.org/wp-content/uploads/2023/04/IDTA-01001-3-0_SpecificationAssetAdministrationShell_Part1_Metamodel.pdf (AAS Part 1: ModellingKind Template/Instance, semanticId, assetKind, derivedFrom)
  - https://www.w3.org/TR/wot-thing-description11/ (Thing Model vs Thing Description, `tm:ref`, `tm:optional`, placeholders, link rel="type")
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[opcua-robotics-types-and-instances]]"
  - "[[let-the-instance-declare-its-own-template]]"
  - "[[the-birth-certificate-is-the-schema-data-only-refers-to-it]]"
  - "[[vss-kuksa-reference]]"
  - "[[opensovd-reference]]"
applies-to: [vss-kuksa, opensovd, iceoryx2, zenoh]
gap-rows: [A4, B10, C8]
---

# Address members by the template's path, find instances by browsing

**Problem.** A body builder adds a crane, a robot gets a new gripper. If consumer code names members by instance-specific ids, it has to be regenerated for every new instance; if it names nothing and reads whatever is there, it cannot decide anything safely.

**Forces.**
- Code is written once against a type; instances arrive at runtime.
- Instances differ: optional parts present or absent, vendor subtypes add members.
- A generic client (dashboard, diagnostics) must work on instances it has never seen.
- The template itself must be identifiable and versioned, independently of instances.

**The rule.** Split the world into **templates** (types with named, ruled members) and **instances** (roots that declare which template they follow). A consumer finds instances by browsing or querying for "instances of template T", and then reaches each member by the **template's relative path**, which is identical on every instance. OPC UA is the reference: an ObjectType's InstanceDeclarations carry ModellingRules (Mandatory: "for each existing BrowsePath on the instance a similar Node shall exist"; Optional: may exist), and a client passes the type-relative BrowsePath to `TranslateBrowsePathsToNodeIds` to get the NodeId on any instance. AAS uses `kind = Template | Instance` on submodels, with the instance's `semanticId` pointing at the template; W3C WoT derives Thing Descriptions from Thing Models and links back with `rel="type"`. Optional members are tested for, never assumed.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| OPC UA Part 3/4 | ObjectType + InstanceDeclarations + ModellingRules; BrowsePath resolution per instance | one client, many instances, vendor subtypes |
| OPC UA companion specs (e.g. OPC 40010 Robotics) | industry-agreed ObjectTypes under a namespace URI | templates shared across vendors |
| AAS Part 1 (IDTA 01001-3-0) | Submodel `kind` Template/Instance, `semanticId`, `assetKind` Type/Instance, `derivedFrom` | template-plus-instances for supplier hand-over |
| W3C WoT TD 1.1 | Thing Model (template, placeholders, `tm:optional`) → Thing Description (instance) | the web version, with discovery |
| VSS `instances` | static expansion (`Row1.DriverSide`) at build time | the static special case; no runtime instances |

**On the Eclipse SDV stack.**
- VSS: treat a branch like `Trailer.Brake` as the template and put the instance in the *key prefix* (`trailer/<NAME>/Trailer.Brake.Pressure`), so the leaf path under the prefix is the template path; do not expand instances into the tree ([[vss-kuksa-reference]], [[instance-in-the-name-type-in-the-hash]]).
- OpenSOVD: components appear with `variant` and subcomponents; a KUKSA data provider (gap A4) should expose the same data ids under every instance entity so a client uses one path per template ([[opensovd-reference]]).
- iceoryx2 / Zenoh: service names `<template-path>` under an instance prefix; a `template.hash` attribute plays the role of `semanticId`.

**The trap.** Copying the template into each instance and letting copies drift, so "the same member" has a different path or type on the third trailer.

**For a hackathon team.** Define one small template (three VSS leaves), start two instances under different prefixes, and show one consumer that lists instances by attribute and reads the same relative path on each, handling an optional leaf being absent on one. Pitch: "code against the template, browse for the instances".

**Evidence.** OPC UA Part 3 §6.4 quotes for Mandatory/Optional and BrowsePath use (reference.opcfoundation.org). AAS Part 1 V3.0 RC03 text: "The kind enumeration is used to denote whether an element is of kind Template or Instance. It is used to distinguish between submodels and submodel templates" and `derivedFrom` example (PDF pp. on ModellingKind and AssetInformation). WoT TD 1.1 §10 Thing Model. VSS `instances` static only: [[vss-kuksa-reference]]. OPC 40010 example: [[opcua-robotics-types-and-instances]].
