---
title: Instance in the name, type in the hash, placement in the announcement
type: pattern
cluster: identity-discovery
component: none
tags: [identity, discovery, open-world, iceoryx2, vss, trailer, fleet]
status: reviewed
sources:
  - https://www.sae.org/standards/content/j1939-81/ (address claim, NAME)
  - https://sparkplug.eclipse.org/specification/ (NBIRTH/DBIRTH)
  - https://www.omg.org/spec/DDS-XTypes/ (TypeObject in discovery)
  - https://docs.ros.org/en/rolling/Concepts/Advanced/About-Type-Hashes.html (ROS 2 type hash)
  - "[[iceoryx2-reference]] (service attributes, discovery service, FlatBuffers payloads in 0.10)"
  - "[[vss-kuksa-reference]] (VSS instances)"
  - "[[opensovd-reference]] (entity model, applicability)"
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[opensovd-overview]]"
  - "[[zenoh-overview]]"
applies-to: [iceoryx2, vss-kuksa, opensovd, zenoh, uprotocol]
gap-rows: [B2, B10, C8, H2]
---

# Instance in the name, type in the hash, placement in the announcement

**Problem.** A trailer couples, a body builder adds a module, a robot changes its tool, or a fleet of a thousand vehicles reports in. The signal model was written for one vehicle with a fixed tree, and ids were allocated for things known at build time. Either the model becomes incomplete, or every new thing re-mints identities and orphans every archive and every consumer.

**Forces.**
- Safety consumers must only read layouts they were built against; an unknown type must be refused, not guessed.
- Instances must be allowed to appear without a registry round-trip or a redeploy.
- Two independently built parties must agree on names and ids without talking.
- Evidence and diagnostics must still see things nobody compiled against.
- Shared-memory IPC has no wildcard subscription; the fleet does.

**The rule.** Keep three things apart. The **type** (layout) is hashed and closed-world. The **instance** is open-world and carries its own identity, which goes into the *name*, never into the type hash. The **placement** (who produces it, where, how often) is announced at runtime instead of written in the model. Then "an array of small models" is one type tree, a dynamic set of instance keys, and announcements that bind them. Any party can still compute every id from the model plus the instance's self-declared identity, so there is still no registry.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| SAE J1939 address claim | a 64-bit NAME is the identity, the bus address is dynamic, PGNs are the types | the exact truck case: trailer and body-builder modules announce themselves |
| MQTT Sparkplug B | NBIRTH/DBIRTH publish a node's metric template on arrival, NDEATH on loss | the birth-certificate pattern for a vehicle, trailer or tool under a group |
| DDS XTypes, ROS 2 type hashes | discovery carries a type descriptor hash; consumers match on it | the layout id carried in discovery rather than assumed |
| SOME/IP SD | service id + instance id + version; offer/find | instance as a first-class part of the name |
| OPC UA, Asset Administration Shell, W3C Thing Description | object types versus instances, submodel templates, discovery | the template-plus-instances vocabulary for body builders |
| VSS `instances`, SOVD entity model | VSS instantiates static arrays (Row, Pos); SOVD components appear with subcomponents and variant applicability | VSS covers only the static case; SOVD already treats a trailer as a component that shows up |
| ROS 2, URDF, ros2_control | composed descriptions, hardware interfaces loaded at runtime, tools attached to end effectors | robotics is namespaces plus reloadable descriptions, not a fixed tree |

**On the Eclipse SDV stack.**
- iceoryx2: service name `model/type-path/instance-key`; service **attributes** carry the type hash, schema version, instance identity and producer, so a consumer refuses a mismatched layout before the first sample (iceoryx2 already refuses mismatched type name and size). The discovery service and events are the birth and death channel; consumers open ports lazily and age instances with their own deadline, no heartbeat. There is no wildcard subscription on one node, and that is correct.
- Zenoh / uProtocol: above the node, instance keys become key prefixes or authorities, and `**` wildcards give the fleet view ([[zenoh-overview]], [[uprotocol-overview]]).
- KUKSA/VSS: VSS deliberately has no vehicle id in paths; a fleet is many trees keyed by VIN, which the fleet-management blueprint already does crudely ([[sdv-blueprints-overview]]).
- OpenSOVD: a new instance is a new entity under a component, discoverable, with `include-schema` for anyone without generated code ([[opensovd-reference]]).
- Two consumer classes: closed-world generated ports for anything that decides; open-world generic consumers (evidence, logging, dashboards) that forward bytes verbatim and decode through a descriptor registry. FlatBuffers payloads in iceoryx2 0.10 give self-describing bytes for the second class ([[iceoryx2-reference]]).

**The trap.** Letting the instance leak into the type hash, so every trailer becomes a new type and the archive orphans on every coupling.

**For a hackathon team.** Demonstrate one type (say, a seat occupancy set), two instances that appear at runtime with their own ids, a consumer that opens the second one without a restart, and a dashboard that shows both without knowing the ids in advance. Pitch line: "instance in the name, type in the hash, placement in the announcement".

**Evidence.** Prior-art rows are standard behaviour of the named specifications (links in `sources`). iceoryx2 attribute matching and discovery service: [[iceoryx2-reference]]. The claim that VSS has no dynamic instantiation beyond `instances` is from [[vss-kuksa-reference]] (unverified against VSS 6.1 release notes).
