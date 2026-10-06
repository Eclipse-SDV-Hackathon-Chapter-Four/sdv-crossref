---
title: ROS 2 over Zenoh needs a router, and MCUs join through zenoh-pico or an agent
type: pattern
cluster: robotics
component: none
tags: [rmw_zenoh, zenoh-pico, micro-ros, router, bridge, uprotocol, mcu]
status: draft
sources:
  - https://github.com/ros2/rmw_zenoh
  - https://raw.githubusercontent.com/ros2/rmw_zenoh/rolling/docs/design.md
  - https://micro.ros.org/docs/overview/features/
  - https://discourse.openrobotics.org/t/reference-implementation-of-zenoh-pico-to-micro-ros/40750
  - https://github.com/eclipse-zenoh/zenoh-pico
last-verified: 2026-10-03
related:
  - "[[zenoh-overview]]"
  - "[[uprotocol-overview]]"
  - "[[threadx-overview]]"
applies-to: [zenoh, uprotocol, threadx]
gap-rows: [D1, B8]
---

# ROS 2 over Zenoh needs a router, and MCUs join through zenoh-pico or an agent

**Problem.** A ROS 2 robot must talk to an SDV stack that is on Zenoh/uProtocol, and a motor-controller MCU must join without a DDS stack.

**Forces.**
- rmw_zenoh disables multicast discovery by default; discovery goes through a router's gossip.
- ROS semantics (services, liveliness, QoS) must be mapped to Zenoh primitives.
- MCUs have no room for DDS; micro-ROS uses XRCE-DDS plus an **agent** proxy.
- The SDV side speaks UUri, not ROS names.

**The rule.** One Zenoh router per robot (or per site) is part of the system, not an optional extra. rmw_zenoh maps publishers/subscribers to Zenoh pub/sub, services to queryables, and announces entities with liveliness tokens under the hermetic `@ros2_lv` prefix; data keys are `<domain>/<fqn>/<type>/<hash>` with metadata (sequence, timestamp, GID) in the attachment. Because it is a *documented* key scheme, a non-ROS peer can join by following the same keys, attachments and liveliness, which is exactly how a zenoh-pico MCU joins agent-less (rmw_zenoh_pico for micro-ROS exists; its maturity is uneven). To reach uProtocol, do not re-publish ROS keys as UUris blindly: write one explicit mapping node (ROS topic -> UUri resource, payload bytes unchanged) and keep the ROS type hash as UAttributes metadata.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| rmw_zenoh | ROS 2 RMW on Zenoh; router with gossip; SHM optional (48 MiB pool, 512 B threshold by default) | a defined key/attachment/liveliness scheme |
| micro-ROS + Micro XRCE-DDS Agent | MCU client with static memory; agent proxies into DDS (FreeRTOS, Zephyr, NuttX) | proven MCU path, but one agent hop |
| rmw_zenoh_pico (eSOL) | zenoh-pico in micro-ROS, agent-less to rmw_zenoh | MCU as a native Zenoh peer (maintenance uneven; unverified current state) |
| zenoh-plugin-ros2dds | bridge DDS ROS 2 to Zenoh | the older route for DDS-based robots |
| up-transport-zenoh | UUri to Zenoh key `up/<authority>/...`, UAttributes in attachment | the SDV-side key scheme |

**On the Eclipse SDV stack.** Both ends are Zenoh: ROS side `<domain>/<fqn>/<type>/<hash>`, uProtocol side `up/<authority>/...` ([[uprotocol-overview]]). A gateway is a Zenoh subscriber on one pattern and a publisher on the other ([[zenoh-overview]]), roughly half a day (gap B8); the harder one is zenoh-pico carrying UMessage bytes on an MCU (gap D1, ThreadX in [[threadx-overview]]). Chapter 3's A-kiki team already bridged ROS 2 and Kuksa onto Zenoh ([[chapter3-retrospective]]).

**The trap.** Forgetting the router: nodes start, the router check fails (default one attempt; `ZENOH_ROUTER_CHECK_ATTEMPTS`), or nodes on two hosts never see each other because multicast is off.

**For a hackathon team.** Run `zenohd`, two ROS nodes on rmw_zenoh, and one gateway that republishes a ROS topic as a UUri message for an SDV consumer. Pitch: "the robot is a Zenoh citizen, the bridge is 100 lines".

**Evidence.** Router, env var, SHM numbers, Humble incompatibility: rmw_zenoh README (verified). Key/liveliness/attachment layout: design.md (verified). micro-ROS features: micro.ros.org (verified). rmw_zenoh_pico status: discourse threads (search snippets only; unverified).
