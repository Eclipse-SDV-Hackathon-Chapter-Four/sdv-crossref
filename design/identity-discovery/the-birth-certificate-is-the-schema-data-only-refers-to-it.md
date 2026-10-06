---
title: The birth certificate is the schema; data only refers to it
type: pattern
cluster: identity-discovery
component: none
tags: [identity, discovery, sparkplug, mqtt, birth, rebirth, templates, aliases, fleet]
status: draft
sources:
  - https://sparkplug.eclipse.org/specification/version/3.0/documents/sparkplug-specification-3.0.0.pdf (Eclipse Sparkplug 3.0.0)
  - https://github.com/eclipse-sparkplug/sparkplug (spec sources, TCK)
last-verified: 2026-10-03
related:
  - "[[a-vehicle-is-gone-when-its-death-certificate-says-so]]"
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[let-the-instance-declare-its-own-template]]"
  - "[[open-on-arrival-age-by-your-own-deadline]]"
  - "[[uprotocol-overview]]"
  - "[[vss-kuksa-overview]]"
applies-to: [uprotocol, zenoh, vss-kuksa, iceoryx2, sdv-blueprints]
gap-rows: [A5, A10, B1, C8]
---

# The birth certificate is the schema; data only refers to it

**Problem.** A host joins late, or a message is lost, and from then on it receives numbers whose meaning it never saw. Either it guesses (and charts nonsense), or every message repeats the full name and type of every value and the link drowns.

**Forces.**
- Bandwidth: data messages must be small (aliases, report-by-exception).
- Late joiners and lossy links must still reach a complete picture.
- The schema of a node can change (a trailer couples, a tool is swapped).
- Consumers must notice when they are out of sync rather than drift.

**The rule.** On arrival a node publishes a **birth certificate** that is the complete schema of what it will send: every metric with name, datatype, current value and (optionally) a numeric alias, plus all template definitions it will instantiate. Afterwards data messages carry only aliases and changed values, each with a wrapping sequence number. A data message that refers to anything not in the current birth is an error, and the consumer's remedy is to **ask for a rebirth**, not to guess. Sparkplug B makes all of this normative: NBIRTH "at a minimum each metric MUST include the metric name, datatype, and current value", "all Template definitions MUST be published in the NBIRTH", DBIRTHs follow immediately after NBIRTH, `seq` runs 0–255 and wraps, and a host whose reorder timeout elapses "MUST send an NCMD … with a Node Control/Rebirth request". Receiving an NDATA/DDATA metric or alias not in the previous birth is listed as a reason to request a rebirth. A schema change means a new birth, never an in-band addition.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| Eclipse Sparkplug B 3.0 | NBIRTH/DBIRTH carry full metric set + templates + aliases; `seq`; rebirth via `Node Control/Rebirth` | late-join and gap recovery by re-announcing, not by polling |
| SOME/IP-SD | offers repeat cyclically; subscribers re-subscribe after reboot | periodic re-announcement as the sync mechanism |
| DDS-XTypes TypeLookup | discovery carries hashes; full TypeObject fetched on demand | "schema by reference, fetch on miss" variant |
| HTTP/2 HPACK | header table built once, later frames refer by index; desync is a connection error | aliasing with hard failure on unknown index |
| MQTT 5 topic alias | per-connection integer replaces topic string | same bandwidth trick at the transport layer |

**On the Eclipse SDV stack.**
- uProtocol / Zenoh: a vehicle or trailer publishes a retained "birth" on `…/birth` with its VSS paths, datatypes, units and schema hashes, then compact updates; a consumer that sees an unknown id publishes a rebirth request. This is the missing heartbeat/fault event schema (gap A10) done properly ([[uprotocol-overview]]).
- KUKSA: the databroker assigns numeric ids per loaded tree; a client resolves path→id via `ListMetadata` after (re)connect — the same "birth then alias" discipline, so never cache ids across broker restarts ([[vss-kuksa-reference]]).
- iceoryx2: the service's static config *is* the birth (type, attributes, QoS) and is readable before the first sample; the discovery service `Added` event delivers it ([[open-on-arrival-age-by-your-own-deadline]]).
- Evidence recorder (gap A5): record births as well as data, or the recording cannot be decoded later.

**The trap.** Letting a node "just start sending" a new metric after birth because the consumer happens to accept it, so late joiners and replays never learn what it is.

**For a hackathon team.** A Python edge node publishes NBIRTH with aliases and NDATA by alias; a dashboard joins late, sees an unknown alias, sends Rebirth, and renders correctly. Pitch: "the arrival message is the schema; anything else is a request for a rebirth".

**Evidence.** Sparkplug 3.0.0 normative ids: `tck-id-topics-nbirth-metrics`, `tck-id-topics-nbirth-templates`, `tck-id-topics-nbirth-rebirth-metric`, `tck-id-payloads-dbirth-order`, `tck-id-payloads-sequence-num-incrementing`, `tck-id-operational-behavior-host-reordering-rebirth`; §5.15 lists "Receiving a metric in an NDATA message that was not included in the previous NBIRTH" and unknown aliases as rebirth reasons (text extracted from the PDF, pp. 21, 45, 54, 85). Death handling (NDEATH Will, `bdSeq`) is covered in [[a-vehicle-is-gone-when-its-death-certificate-says-so]] and not repeated here. KUKSA id behaviour: [[vss-kuksa-reference]].
