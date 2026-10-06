---
title: iceoryx2 quickstart (Rust, C++, Python, two processes, Zenoh tunnel)
type: quickstart
component: iceoryx2
tags: [iceoryx2, quickstart, rust, cpp, cmake, python, zenoh]
status: verified
sources:
  - repos/iceoryx2/examples/rust/publish_subscribe/README.md
  - repos/iceoryx2/examples/cxx/README.md
  - repos/iceoryx2/examples/cxx/publish_subscribe/README.md
  - repos/iceoryx2/examples/python/README.md
  - repos/iceoryx2/integrations/zenoh/link-tunnel-cli/README.md
  - repos/iceoryx2/benchmarks/README.md
last-verified: 2026-10-03
related:
  - "[[iceoryx2-overview]]"
  - "[[iceoryx2-howto]]"
  - "[[iceoryx2-reference]]"
  - "[[zenoh-overview]]"
---

# iceoryx2 quickstart

Goal: two processes exchange `TransmissionData` over shared memory in under 15 minutes.

## Prerequisites
- Linux (x86_64 or aarch64). macOS, Windows and FreeBSD also work (tier 2), but these commands were only run on Linux.
- Rust >= 1.89 via rustup (`rust-version = "1.89"` in repos/iceoryx2/Cargo.toml). The C++ build also needs cargo, because CMake builds the Rust core.
- For C++: CMake >= 3.22 and gcc/g++ or clang. On Ubuntu, `sudo ./internal/scripts/install_dependencies_ubuntu.sh` installs everything (repos/iceoryx2/examples/cxx/README.md).
- git, about 3 GB disk for `target/`.
- Both processes must run as **the same Unix user** and be built from **the same iceoryx2 version**.

## 1. Clone
```sh
git clone --depth 1 https://github.com/eclipse-iceoryx/iceoryx2
cd iceoryx2
# for a released version instead of main:  git clone --depth 1 --branch v0.10.0 https://github.com/eclipse-iceoryx/iceoryx2
```

## 2. Rust publish/subscribe (two terminals)
```sh
cargo build --example publish_subscribe_subscriber --example publish_subscribe_publisher   # ~20 s here, minutes on a cold cache
# Terminal 1
cargo run --example publish_subscribe_subscriber
# Terminal 2
cargo run --example publish_subscribe_publisher
```
Expected: the publisher prints `Send sample N ...` every second. The subscriber prints `received: TransmissionData { x: N, y: 3N, funky: N*812.12 }`. Ctrl-C prints `exit`. You can start several subscribers. With the default config, a service allows at most 8 subscribers and 2 publishers.

## 3. C++ publish/subscribe (CMake)
```sh
cmake -S . -B target/ff/cc/build -DBUILD_EXAMPLES=ON
cmake --build target/ff/cc/build -j8          # or: --target example_cxx_publish_subscribe_publisher example_cxx_publish_subscribe_subscriber
# Terminal 1
./target/ff/cc/build/examples/cxx/publish_subscribe/example_cxx_publish_subscribe_subscriber
# Terminal 2
./target/ff/cc/build/examples/cxx/publish_subscribe/example_cxx_publish_subscribe_publisher
```
Expected: the same output format as the Rust example (`Send sample 1...`, `received: TransmissionData { x: 1, y: 3, funky: 812.12 }`).
**Do not mix** the Rust `publish_subscribe` publisher with the C++ subscriber: the type names differ, so you get `PublishSubscribeOpenError(IncompatibleTypes)`. For cross-language tests use the `cross_language_communication_basics` examples.

## 4. Python (released wheel)
```sh
python3 -m venv .venv && . .venv/bin/activate
pip install iceoryx2==0.10.0        # the README on main says 0.10.999 - that version does not exist on PyPI
python examples/python/publish_subscribe/subscriber.py    # terminal 1
python examples/python/publish_subscribe/publisher.py     # terminal 2
```
A Python process from PyPI 0.10.0 **cannot** talk to Rust/C++ built from `main` (0.10.999): you get `VersionMismatch`. Check out tag `v0.10.0` for the Rust/C++ side if you want cross-language communication with the wheel. For Python built from source, use poetry (`poetry --project iceoryx2-ffi/python install && poetry --project iceoryx2-ffi/python build-into-venv`), see repos/iceoryx2/examples/python/README.md.

## 5. Introspect with the CLI
```sh
cargo build -p iceoryx2-cli          # builds iox2, iox2-service, iox2-node, iox2-config, iox2-link
export PATH=$PWD/target/debug:$PATH
iox2 service list
iox2 service details "My/Funk/ServiceName"
iox2 service subscribe "My/Funk/ServiceName"     # hex dump of header + payload, -f JSON|YAML|RON
iox2 service hz "My/Funk/ServiceName"
iox2 node list
iox2 config show
```
(Or install the CLI with `cargo install iceoryx2-cli`. It is on crates.io at 0.10.0.)

## 6. Two "hosts" over Zenoh (link tunnel, prototype)
```sh
cargo build --manifest-path integrations/zenoh/Cargo.toml -p iceoryx2-integrations-zenoh-link-tunnel-cli   # ~1-5 min
R=$PWD; T=$R/integrations/zenoh/target/debug/iox2-link-tunnel-zenoh
# simulate two hosts on one machine with two iceoryx2 domains (different file prefixes)
for h in hosta hostb; do mkdir -p /tmp/$h/config; printf '[global]\nprefix = "%s_"\n' $h > /tmp/$h/config/iceoryx2.toml; done
(cd /tmp/hosta && $T --allow 'My/Funk/*') &      # tunnel A
(cd /tmp/hostb && $T --allow 'My/Funk/*') &      # tunnel B
(cd /tmp/hostb && $R/target/debug/examples/publish_subscribe_subscriber) &
(cd /tmp/hosta && $R/target/debug/examples/publish_subscribe_publisher)
```
iceoryx2 reads `$PWD/config/iceoryx2.toml` first. Each process therefore runs in its own "domain", and data only crosses through Zenoh. On real hosts, run one tunnel per host with the default config. The default Zenoh config uses multicast scouting on the LAN. Use `-z zenoh.json5` for routers or endpoints.

## 7. Latency benchmark (optional, 1 min)
```sh
cargo run --release --bin benchmark-publish-subscribe -- --bench-ipc -p 8 -i 1000000
cargo run --release --bin benchmark-publish-subscribe -- --bench-ipc -p 4194304 -i 100000
```

## Observed on 2026-10-03
Machine: AMD Ryzen 9 5950X (32 threads), Linux 7.0.0-31-generic, rustc/cargo 1.98.1, Python 3.14.4, repo commit `ae9be314` (main, 0.10.999).

Rust build: `Finished dev profile … in 19.42s`. Rust run (subscriber started first, publisher killed after 4 s by `timeout`):
```
==PUB
0 [W] "Config::global_config()"
| No config file was loaded, a config with default values will be used.
Send sample 1 ...
Send sample 2 ...
Send sample 3 ...
exit
==SUB
0 [W] "Config::global_config()"
| No config file was loaded, a config with default values will be used.
Subscriber ready to receive data!
received: TransmissionData { x: 1, y: 3, funky: 812.12 }
received: TransmissionData { x: 2, y: 6, funky: 1624.24 }
received: TransmissionData { x: 3, y: 9, funky: 2436.36 }
exit
```
The `[W] No config file was loaded` warning is normal.

C++: configure + build of the two targets took 54.7 s. The output is identical in format (`Send sample 1...` … `received: TransmissionData { x: 4, y: 12, funky: 3248.48 }`).

Rust publisher -> C++ subscriber: `Error: PublishSubscribeOpenError(IncompatibleTypes)` (expected, see step 3).

Python wheel 0.10.0: Python pub -> Python sub received `TransmissionData { x: 1, y: 3, funky: 812.12 }` etc. Rust (main) pub -> Python (0.10.0) sub: `Error: PublishSubscribeOpenError(VersionMismatch)`.

CLI: `iox2 service list` -> `[ PublishSubscribe("My/Funk/ServiceName"), ]`. `iox2 service details` showed `max_subscribers: 8, max_publishers: 2, max_nodes: 20, history_size: 0, subscriber_max_buffer_size: 2`, payload `type_name: "TransmissionData", size: 16, alignment: 8`, header size 48, and both nodes with pid/executable.

Zenoh tunnel (step 6): the tunnel logs showed `Using config file at "config/iceoryx2.toml"`, `Allowing ["My/Funk/*"]`, `Polling at 100ms`. The subscriber in domain hostb received all 7 samples from the publisher in domain hosta. Control run without tunnels: the subscriber received nothing. Tunnel CLI build: 51 s.

Benchmark (release): `ipc 251 ns @ 8 B`, `283 ns @ 4194304 B`, `ipc_threadsafe 339 ns / 363 ns`.

This machine had **2858 stale `iox2_*` files in /dev/shm**, left over from earlier runs and crashed processes. See the cleanup pitfall in [[iceoryx2-howto]].
