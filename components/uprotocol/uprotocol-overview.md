---
title: Eclipse uProtocol - overview
type: overview
component: uprotocol
tags: [uprotocol, communication, middleware, zenoh, mqtt, someip, ustreamer, chapter4]
status: draft
sources:
  - repos/up-spec/README.adoc
  - repos/up-spec/up-l1/README.adoc
  - repos/up-spec/up-l3/README.adoc
  - repos/up-spec/basics/uri.adoc
  - repos/up-spec/up-core-api/uprotocol/v1/uattributes.proto
  - repos/up-rust/Cargo.toml
  - repos/up-streamer-rust/README.md
  - https://github.com/orgs/eclipse-uprotocol/repositories
  - https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340
  - https://github.com/eclipse-uprotocol/up-spec/releases
last-verified: 2026-10-03
related:
  - "[[uprotocol-quickstart]]"
  - "[[uprotocol-howto]]"
  - "[[uprotocol-reference]]"
  - "[[uprotocol-integration-notes]]"
  - "[[zenoh-overview]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[chapter3-retrospective]]"
---

# Eclipse uProtocol - overview

Looked at: up-spec `c89dc48` (2026-09-22), up-rust `27e4ce6` (2026-09-30, version 0.10.0-SNAPSHOT), up-streamer-rust `4e01e89` (2026-02-23), up-transport-zenoh-rust `1ebc37b` (2026-08-13, v0.9.1). All under `repos/`.

## What it is
A **transport-agnostic, layered messaging spec** (not a broker, not a middleware) that gives every software component ("uEntity") one addressing scheme (UUri), one message envelope (UMessage = UAttributes + payload) and three messaging patterns (publish/subscribe, notification, RPC), on top of whatever middleware is available (Zenoh, MQTT 5, SOME/IP, iceoryx2, Android binder ...). Source: repos/up-spec/README.adoc ("run on top of any other communication middleware (transport) such as SOME/IP, MQTT, zenoh, HTTP").

## What it is NOT
- Not a data model: payloads are opaque (protobuf, JSON, raw, SOME/IP ...; see UPayloadFormat). It does not define VSS signals; see [[vss-kuksa-overview]].
- Not a broker or router: it needs a transport. Zenoh in peer mode with multicast scouting needs no router at all ([[zenoh-overview]]).
- Not an orchestrator ([[ankaios-overview]]) and not diagnostics ([[opensovd-overview]]).
- uStreamer is a *gateway* between transports, not a transport. It forwards only what a (static) subscription list says.

## Layers (spec)
| Layer | What | Where defined |
|---|---|---|
| Basics | UUri, UUID (v7 in 1.6), UAttributes, UMessage, UCode/UStatus, priority (CS0-CS6), permissions | repos/up-spec/basics/ |
| uP-L1 Transport | `UTransport` interface: `send`, `receive` (pull), `register_listener`/`unregister_listener` (push) with source/sink UUri filters; plus per-protocol mappings | repos/up-spec/up-l1/{README,zenoh,mqtt_5,someip,iceoryx2,cloudevents}.adoc |
| uP-L2 Communication | `Publisher`, `Subscriber`, `Notifier`, `NotificationListener`, `RpcClient`, `RpcServer` - transport-agnostic API implemented once per language library | repos/up-spec/up-l2/api.adoc |
| uP-L3 Core services | uSubscription (v3, v4), uDiscovery (v3), uTwin (v2), uStreamer (proto stub only, service id 4) | repos/up-spec/up-l3/, up-core-api/uprotocol/core/ |

Delivery semantics (up-l3/README.adoc): RPC at-least-once, publish and notification at-most-once.

## Data model in 60 seconds
- **UUri** = `authority_name` (string, max 128 chars, lowercase unreserved chars, empty = local) + `ue_id` (u32: low 16 bits = service/type id, high 16 bits = instance id) + `ue_version_major` (u8) + `resource_id` (u16). String form `//authority/UE_ID/VERSION/RESOURCE` in upper-case hex without leading zeros, e.g. `//publisher/3B1DA/1/8001`. Wildcards: service `0xFFFF`, instance `0xFFFF`, version `0xFF`, resource `0xFFFF` (repos/up-spec/basics/uri.adoc). By convention resource ids >= 0x8000 are topics and < 0x8000 are RPC methods (convention seen in examples; treat as unverified in spec text).
- **UAttributes**: id (UUID), type (PUBLISH/REQUEST/RESPONSE/NOTIFICATION), source, sink, priority (CS0..CS6), ttl, permission_level, commstatus, reqid, token, traceparent, payload_format (repos/up-spec/up-core-api/uprotocol/v1/uattributes.proto).
- **UMessage**: attributes + optional bytes payload. Pub = source only; notification/request/response = source + sink.
- Zenoh mapping: key `up/<src authority>/<src ue_type>/<src ue_instance>/<src version>/<src resource>/<sink ...>` (sink parts `{}` for publish); UAttributes protobuf goes in the Zenoh *attachment* (first byte 0x01 = uProtocol major version); CS0..CS6 map to Zenoh priorities; Zenoh major version 1 mandatory (repos/up-spec/up-l1/zenoh.adoc).

## Versions and maturity
- **Spec**: `v1.6.0-alpha.7` is what the libraries target (up-rust README, zenoh/mqtt5/vsomeip transport READMEs). There is no final 1.6.0 tag that we saw; the older stable line is 1.5.x (1.5.8 last). 1.5 -> 1.6 is breaking: UUID v8 -> v7, uEntity id/instance restructuring, transports must validate inbound messages, UCode split from UStatus, uDiscovery redesigned, uSubscription rewritten, iceoryx2 transport spec added (https://github.com/eclipse-uprotocol/up-spec/releases; web summary, dates unverified).
- **up-rust**: crates.io `0.9.0` (2025-11-12); git main is `0.10.0-SNAPSHOT`, MSRV 1.88. Most mature SDK. Feature flags: `communication` (L2), `usubscription`, `udiscovery`, `symphony`, `test-util`, `cloudevents` (repos/up-rust/Cargo.toml).
- **Other SDKs** (org listing, https://github.com/orgs/eclipse-uprotocol/repositories): up-cpp (+ up-transport-zenoh-cpp; its README pins up-core-api 1.6.0-alpha4, zenoh-c 1.2.1, "under active development"), up-java, up-kotlin, up-python (all pushed Sep 2026, low star counts; per-repo maturity unverified), up-android-core (uBus + uSubscription on Android).
- **Transports** (maturity is our judgement from READMEs and crates.io):
| Transport | Repo | State |
|---|---|---|
| Zenoh (Rust) | up-transport-zenoh-rust v0.9.1 | Best-supported; crates.io current (2026-08); needs zenoh ^1.9.0 |
| MQTT 5 (Rust) | up-transport-mqtt5-rust v0.4.0 | Maintained (push Oct 2026), crates.io from Nov 2025, uses paho-mqtt (C lib build) |
| SOME/IP | up-transport-vsomeip-rust v0.6.0 | Works with bundled/own vsomeip; heavy C++ build; used by streamer examples |
| Zenoh (C++) | up-transport-zenoh-cpp | "under active development" |
| iceoryx2 | up-transport-iceoryx2-rust | Early: ~5 commits, ~50 open issues (WebFetch summary); spec pins iceoryx2 0.6.1 (repos/up-spec/up-l1/iceoryx2.adoc) |
| socket | up-transport-socket | Test-only toy transport in C++/Rust/Python/Java |
| Android binder | up-client-android-* / up-android-core | Android only; unverified for this event |
| Embedded | none official; Chapter 3 ThreadX board hand-rolled a no_std `UTransport` over `minimq` (MQTT) | repos/sdv_lab/android_treadx/threadx/threadx-app/cross/app/src/ |

## uStreamer
`up-streamer-rust`: a library (`up-streamer`) plus ready binaries. Each *endpoint* = (authority, transport instance); `add_route(in, out)` registers a forwarding listener on `in` for sources of authority X and re-sends on `out`. Reference binaries: `configurable-streamer` (Zenoh + MQTT5, JSON5 config, Docker images amd/arm) and `example-streamer-implementations` (zenoh_mqtt, zenoh_someip). Pub/sub is forwarded **only** for topics listed in a static `subscription_data.json` (live uSubscription mode is "reserved" in the config but not usable in the config we read). RPC and notifications are routed by sink authority. (repos/up-streamer-rust/{README.md,up-streamer/README.md,configurable-streamer/{README.md,CONFIG.json5}})

## Where it appears at the events
- **Chapter 4 (6-8 Oct 2026, Friedrichshafen)**: Doctor Whodunit uses uProtocol for "heartbeat, fault, and mitigation events" around the Battery Thermal Guardian; Hack to the Future uses it so services stay portable across simulated, embedded and real setups ([[chapter4-challenge-doctor-whodunit]], [[chapter4-challenge-hack-to-the-future]], https://www.eventbrite.com/e/eclipse-sdv-hackathon-chapter-four-registration-1998344883340).
- **Correction to the brief**: Doctor Whodunit is a *Chapter 4* challenge, not Chapter 3. Chapter 3 (30 Sep - 2 Oct 2025, Berlin/Porto) used uProtocol in the SDV Lab, see below and [[chapter3-retrospective]]. We found no public Chapter 4 reference code yet (the Chapter-Four GitHub org had only a `.github` repo at snapshot time), so the exact event schema (topic URIs, payloads, authorities) for heartbeat/fault/mitigation is **unverified** - expect the organisers to provide it; see [[uprotocol-howto]] for a proposed layout.
- **Chapter 3 SDV Lab** (repos/sdv_lab): `uprotocol/zenoh` (ego_vehicle, cruise_control, up-rust 0.5 + up-transport-zenoh 0.6, zenoh 1.2.1), `uprotocol/mqtt` (aaos, threadx; up-rust 0.7 + git mqtt5), `uprotocol/cruise-control-app` (Zenoh or MQTT5, run via Ankaios), `uprotocol/ustreamer/config` (docker-compose with configurable streamer bridging authorities EGOVehicle / CruiseControl / threadx / AAOS over Zenoh and MQTT), `pid_controller/rust-uprotocol` (up-rust 0.7 + zenoh 0.8, Ankaios manifest), Android digital cluster apps (Kotlin, MQTT).

## Pros / cons / when not to use
Pros: one addressing + envelope across Zenoh/MQTT/SOME/IP, so services are portable and bridgeable; protobuf typed; QoS classes; first-class RPC with correlation; spec has conformance (Gherkin, OpenFastTrace); Rust library is clean and mockable (`LocalTransport`, `test-util`).
Cons: version churn (0.5 -> 0.7 -> 0.9 -> 0.10 in a year, spec alpha), pin everything together; SDK maturity uneven outside Rust; uStreamer needs hand-maintained static subscription JSON; extra overhead vs raw Zenoh (protobuf attributes per message); little ecosystem tooling (no inspector/recorder); no data model.
Skip it when: all components are one process/host on iceoryx2 and you need zero-copy and latency ([[iceoryx2-overview]]); you only need signal read/write ([[vss-kuksa-overview]] gRPC); a team knows plain Zenoh/MQTT and has no cross-transport requirement.

## Hackathon ideas
See [[uprotocol-howto]] section "Ideas". Highlights: heartbeat watchdog uEntity; fault-injecting uStreamer-style proxy for openDuT; live-uSubscription for the streamer; iceoryx2 transport smoke test; Python/Kotlin parity checks; mini-"uprotocol-tap" recorder.
