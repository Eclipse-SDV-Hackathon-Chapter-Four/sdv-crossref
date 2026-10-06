---
title: OpenBSW - Integration notes
type: reference
component: openbsw
tags: [openbsw, integration, opensovd, kuksa, uprotocol, zenoh]
status: draft
sources:
  - https://blogs.eclipse.org/post/christian-heissenberger/first-sdv-hackfest-esslingen-2026-hands-integration-real-vehicles-and
  - repos/OpenBSW-Playground/OpenBSW-SOVD-Demo/README.md
  - repos/openbsw
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust
last-verified: 2026-10-03
related:
  - "[[openbsw-overview]]"
  - "[[opensovd-overview]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[s-core-overview]]"
  - "[[threadx-overview]]"
---

# OpenBSW - Integration notes

Evidence method: grep of repos/openbsw and repos/OpenBSW-Playground for project names (only hits were unrelated: "score" substrings, a mention in naming guidelines) plus web search (no result tying OpenBSW to KUKSA/uProtocol/iceoryx2/S-CORE/Ankaios). "none found" means exactly that, not "impossible".

| other project | integrates? | how (protocol / library / adapter) | maturity (none / idea / prototype / demo / production) | evidence |
|---|---|---|---|---|
| OpenSOVD (CDA) | yes | OpenBSW DoIP server (TCP/UDP 13400) + UDS; CDA translates SOVD REST to UDS/DoIP; needs ACK-handling overlay patch to DoIpServerConnectionHandler | demo | OpenBSW-Playground/OpenBSW-SOVD-Demo; HackFest blog |
| Grafana (non-SDV tool) | yes | Infinity datasource polling the SOVD REST API | demo | OpenBSW-SOVD-Demo/grafana |
| ThreadX | yes | OpenBSW has `asyncThreadX`, presets `posix-threadx`, `s32k148-threadx-*`, `nucleo-*-threadx-*`; vendored libs/3rdparty/threadx | prototype (builds; POSIX threadx link verified 2026-10-03, not run) | CMakePresets.json; repos/openbsw/libs/3rdparty/threadx |
| FreeRTOS (non-SDV) | yes | default RTOS | production-style (default target) | CMakePresets.json |
| Rust / embassy | yes (in-repo) | embassy-executor on the C++ async runtime, FFI | prototype | Cargo.toml, rustHelloWorld; ran on 2026-10-03 |
| threadx-rust (Chapter 3) | none found | separate ThreadX+NetX Rust project on MXAZ3166; no OpenBSW reference | none | https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/threadx-rust |
| openDuT | none found | HackFest agenda lists openDuT-based connectivity next to OpenBSW but no OpenBSW+openDuT artifact seen; idea: expose tap0/vcan via openDuT | idea | HackFest blog |
| S-CORE | none found | HackFest mentioned S-CORE integration in general; no OpenBSW link | none | HackFest blog |
| KUKSA / VSS | none found | CAN feeder on vcan0: kuksa-can-provider 0.5.0 (dbc2val, `--network host`, no privileges) reads 0x558 and sets `Vehicle.Speed` in databroker 0.7.1; read back with kuksa-client (observed 2026-10-03, [[openbsw-howto]] section 9) | prototype (reproduced here) | components/openbsw/examples-can-feeder/; .local-verify/can-feeder/ |
| uProtocol | none found | idea: uProtocol over Zenoh on a Linux gateway reading vcan0/DoIP; embedded uProtocol C++ client on OpenBSW unverified (threadx-rust has a uMessage example, not OpenBSW) | none | none found |
| iceoryx2 | none found | n/a (OpenBSW POSIX build is a single process; iceoryx2 would sit in a Linux gateway) | none | none found |
| Ankaios | none found | idea: run the POSIX ELF as an Ankaios workload (needs tap/vcan privileges, host network) | none | none found |
| AutoSD | none found | ELF could run in a container on AutoSD; no evidence | none | none found |
| Zenoh | none found | idea: gateway on vcan0 | none | none found |
| SOME/IP | yes (in-repo) | `libs/bsw/cpp2someip` (RpcSomeIpStack, SdSomeIpStack), SomeIpSystem in ref app | prototype (not run) | repos/openbsw/libs/bsw/cpp2someip/doc/index.rst |

## Practical integration patterns
- **Diagnostics path (best supported):** ECU ELF -> DoIP -> OpenSOVD CDA -> REST -> any client. See [[opensovd-overview]].
- **Signal path (reproduced 2026-10-03):** ECU ELF -> vcan0 CAN frame 0x558 -> kuksa-can-provider (dbc2val) -> KUKSA databroker 0.7.1, see [[openbsw-howto]] section 9. vcan itself needs root once (`test_setup.sh`).
- Everything in one container needs `--cap-add=NET_ADMIN` and `/dev/net/tun` for the TAP; vcan needs host kernel module `vcan` (host-global, not namespaced for creation unless privileged).
