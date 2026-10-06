---
title: uProtocol quickstart - pub/sub over Zenoh in 15 minutes
type: quickstart
component: uprotocol
tags: [uprotocol, zenoh, up-rust, quickstart]
status: verified
sources:
  - repos/up-transport-zenoh-rust/README.md
  - repos/up-transport-zenoh-rust/examples/publisher.rs
  - repos/up-rust/examples/simple_publish.rs
  - components/uprotocol/examples-hb/main.rs
last-verified: 2026-10-03
related:
  - "[[uprotocol-overview]]"
  - "[[uprotocol-howto]]"
  - "[[zenoh-overview]]"
---

# uProtocol quickstart

Goal: two uEntities (publisher, subscriber) exchange uProtocol messages over Zenoh on one machine. No broker, no router, no Docker.

## Prerequisites
- Rust >= 1.88 (`rustc --version`; verified with cargo 1.98.1). C toolchain is NOT needed for Zenoh; it IS needed for MQTT5 (paho) and SOME/IP (vsomeip).
- Linux; two terminals. Same host or same LAN (Zenoh multicast scouting; see pitfalls if it does not find peers).
- Network access to crates.io the first time.

## Path A (shortest): run the official examples
```bash
git clone --depth 1 https://github.com/eclipse-uprotocol/up-transport-zenoh-rust
cd up-transport-zenoh-rust
cargo build --examples            # first build ~1.5 min on 32 cores
# terminal 1
./target/debug/examples/subscriber
# terminal 2
./target/debug/examples/publisher
```
Other examples in the same folder: `notifier`/`notification_receiver`, `rpc_server`/`rpc_client`, `l2_rpc_client`. Zenoh options: `-m peer|client|router`, `-e tcp/host:7447` (connect), `-l tcp/0.0.0.0:7447` (listen), `--no-multicast-scouting`, `-c zenoh.json5`.

## Path B: your own crate (what a team would actually do)
```bash
cargo new hb && cd hb
cat >> Cargo.toml <<'T'
up-rust = { version = "0.9", features = ["communication"] }
up-transport-zenoh = "0.9.1"
tokio = { version = "1", features = ["macros","rt-multi-thread","time","sync"] }
async-trait = "0.1"
T
cp <vault>/components/uprotocol/examples-hb/main.rs src/main.rs
cargo build
./target/debug/hb sub &      # subscriber, filter //*/FFFF1001/1/8001
./target/debug/hb pub        # publisher //guardian/1001/1/8001, one "hb N" per second
```
`examples-hb/main.rs` is a ~40 line heartbeat publisher/subscriber using the L1 `UTransport` API. Note the builder is a typestate: `UPTransportZenoh::builder(authority)?.with_config(zenoh_config::Config::default()).build().await?` - `build()` does not exist before `with_config`.

## Path C: in-process, no network
```bash
git clone --depth 1 https://github.com/eclipse-uprotocol/up-rust && cd up-rust
cargo run --example simple_publish --features "up-l2-publisher,protobuf-support,util"
```
Also `simple_notify`, `simple_rpc`. Uses `LocalTransport` (same process).

## Observed on 2026-10-03
Machine: Linux 7.0, cargo 1.98.1, 32 cores, up-transport-zenoh-rust `1ebc37b` (v0.9.1, zenoh 1.9.0).
Path A: `cargo build --examples` -> `Finished dev profile in 1m 32s`. Subscriber (started first) then publisher:
```
uProtocol subscriber example
Registering message listener [source filter: //*/FFFFB1DA/1/8001]
Received message [topic: //publisher/3B1DA/1/8001, payload: event 1]
Received message [topic: //publisher/3B1DA/1/8001, payload: event 2]
...
```
Path B (crates.io up-rust 0.9.0 + up-transport-zenoh 0.9.1):
```
got Some("hb 0") from Some("//guardian/1001/1/8001")
got Some("hb 1") from Some("//guardian/1001/1/8001")
...
```
Path C: 
```
received event [priority: CS2]: Hello plain text
received event [priority: CS3]: Hello protobuf
```
NOT run: uStreamer (needs MQTT broker / Docker pull of the streamer image), MQTT5 and SOME/IP transports, other-language SDKs.

## If it does not work
- Nothing received: start subscriber first; check both processes are on the same multicast domain, else run `-m router -l tcp/0.0.0.0:7447` on one side and `-m client -e tcp/<ip>:7447` on the others (many Wi-Fi networks drop multicast; the default Docker bridge passed it on one host (corrected 2026-10-03, see [[zenoh-overview]])).
- `RUST_LOG=info` (or `trace`) is needed to see transport logs.
- Compile error pairing crates: keep `up-rust` and `up-transport-zenoh` on the same minor line (0.9.x with 0.9.x). Mixing 0.7/0.8 with 0.9 gives duplicate/mismatching `UMessage` types.
