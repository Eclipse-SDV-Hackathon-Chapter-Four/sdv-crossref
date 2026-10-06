---
title: Same keys from simulator to bench to vehicle — swap the endpoint, not the service
type: pattern
cluster: robotics
component: none
tags: [simulation, carla, gazebo, hil, portability, hack-to-the-future, bridge]
status: draft
sources:
  - https://github.com/Eclipse-SDV-Hackathon-Chapter-Three/sdv_lab
  - https://gazebosim.org/docs
  - https://carla.readthedocs.io/en/0.9.15/
  - https://github.com/ros-controls/gz_ros2_control
last-verified: 2026-10-03
related:
  - "[[chapter3-retrospective]]"
  - "[[chapter4-challenge-hack-to-the-future]]"
  - "[[vss-kuksa-overview]]"
applies-to: [uprotocol, zenoh, vss-kuksa, openbsw, opendut]
gap-rows: [D4, D1]
---

# Same keys from simulator to bench to vehicle — swap the endpoint, not the service

**Problem.** The feature runs against a simulator, then the team rewrites its I/O for the bench ECU and again for the car, and nobody can say the same code was tested.

**Forces.**
- Simulators publish their own, rich, vendor-shaped data.
- Real hardware has fewer, noisier, differently timed signals.
- Time source and latency differ (sim time versus wall time).
- Timeboxed events punish any layer you have to write three times.

**The rule.** Define the service's interface **once, as keys and types** (VSS names, uProtocol resources, ROS topics) and put every environment behind an **endpoint adapter** that produces/consumes exactly those. In ROS, `gz_ros2_control` shows the principle: the same controllers run on the Gazebo hardware plugin or the real one because only the `ros2_control` hardware component changes. For the vehicle stack, the sdv_lab pattern is Component A (CARLA, heavy) -> Rust ego-vehicle bridges -> bus (uProtocol/Zenoh/MQTT5) -> Component B (your app); replacing A with a CAN provider leaves B untouched. Keep timestamps in the message, use sim time only through the clock, and put the simulator-only data (ground truth) under a clearly different key prefix so it cannot leak into the vehicle path.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| gz_ros2_control / ros2_control hardware abstraction | same controllers, swap the hardware component | interface-level portability |
| ROS 2 `use_sim_time` | clock is a topic | the same node on sim or wall time |
| Chapter 3 sdv_lab | CARLA bridges to uProtocol/Zenoh with Ankaios manifests | working template for the sim leg |
| CARLA ROS bridge, Gazebo ros_gz_bridge | translate simulator topics to ROS | adapter pattern |
| openDuT | virtual and real test rigs over a network | the bench leg ([[opendut-overview]]) |

**On the Eclipse SDV stack.** This is Hack to the Future ([[chapter4-challenge-hack-to-the-future]]): uProtocol is the stable surface; Zenoh or MQTT5 carries it; sim endpoints (CARLA bridge) and hardware endpoints (OpenBSW CAN to KUKSA, gap B6) both emit the same VSS names (D4, the cheapest demonstration). The embedded leg is the weak point: no official embedded uProtocol client (D1). Pitfalls recorded in [[chapter3-retrospective]]: `up-rust` 0.7.1 vs 0.7.0, case-sensitive CARLA `role_name`.

**The trap.** Letting the simulator's convenience signals (ground-truth pose, perfect lidar classes) into the service's inputs; the car then has no such key and the demo "works in the sim only".

**For a hackathon team.** One service, two feeders (CSV or CARLA, and a CAN/mock provider) behind identical key names, and a switch that is one command-line flag; show the service log unchanged. Pitch: "we changed the endpoint, not a line of service code".

**Evidence.** sdv_lab structure and pitfalls: [[chapter3-retrospective]] (verified from repo clone). gz_ros2_control swap-the-hardware-plugin claim: project README (not fetched; unverified). CARLA and Gazebo are not Eclipse projects.
