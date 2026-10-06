---
title: A ROS 2 executor is not a schedule — fix the order or prove it
type: pattern
cluster: robotics
component: none
tags: [ros2, executor, callback-groups, real-time, determinism, feo, s-core]
status: draft
sources:
  - https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Executors.html
  - https://discourse.openrobotics.org/t/the-ros-2-c-executors/38296
  - https://roscon.ros.org/2024/talks/Executors_in_ROS_2.pdf
  - https://github.com/eclipse-score/feo
  - https://docs.ros.org/en/jazzy/p/rclc/
last-verified: 2026-10-03
related:
  - "[[s-core-overview]]"
  - "[[iceoryx2-overview]]"
applies-to: [s-core, iceoryx2]
gap-rows: [C8]
---

# A ROS 2 executor is not a schedule — fix the order or prove it

**Problem.** A perception callback, a control loop and a watchdog share a process; under load the control tick jitters or a subscription starves, and nobody can say what the worst case is.

**Forces.**
- Executors decide *which ready callback runs next*, driven by incoming events, not by a declared period or order.
- Callback groups only say what may run in parallel (mutually exclusive or reentrant).
- Safety arguments need bounded, analysable ordering.
- Dynamic allocation, locking and DDS threads in the path hurt real time.

**The rule.** Use ROS 2 executors for the flexible, event-driven part, and take the **deterministic loop out of the executor**: either a fixed, declared execution order (the FEO model: activities in a static order per cycle, ASIL_B target) or a single-threaded, statically scheduled loop (rclc executor for MCUs with explicit trigger conditions and callback order). Published analyses found the multi-threaded executor not starvation-free and the single-threaded one starvation-free by design; the events executor (experimental) pushes events instead of polling a wait set. None of them gives a response-time bound for free.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| rclcpp Single/MultiThreaded/StaticSingleThreaded executors, events executor | event-driven dispatch, callback groups | flexibility, not bounds |
| rclc executor | explicit callback order and trigger semantics for micro-ROS | sequential, analysable processing |
| S-CORE FEO | fixed execution order, activities per cycle, communication backends `com_iox2`, `com_linux_shm`, `com_mw` | declared order, ASIL_B goal |
| AUTOSAR Adaptive / Classic OS schedule tables | static tasks and periods | the safety-industry baseline |
| Response-time analysis papers (Teper et al., EMSOFT'24) | worst-case analysis for ROS 2 executors | proves bounds only under assumptions |

**On the Eclipse SDV stack.** Draw the line the same way the vehicle does: ROS 2 for planning and perception, FEO ([[s-core-overview]]) for the cyclic control chain, joined by iceoryx2 ([[iceoryx2-overview]]), which FEO already uses as a backend (`com_iox2`). The seam is a fixed-layout service, not a ROS topic. FEO is Bazel-only, in "released v0.1.2, not in known_good.json" state per the overview, so it is a bring-your-own-build choice. A placement manifest (C8) must say which loop each node belongs to.

**The trap.** Putting the control loop in a ROS 2 timer callback in a multi-threaded executor and calling it real-time because the CPU was idle on the demo.

**For a hackathon team.** Measure it: run a 100 Hz loop beside a heavy callback in a MultiThreadedExecutor, plot the jitter, then move the loop to its own thread behind an iceoryx2 service. Pitch: "we measured the jitter, then moved the loop out".

**Evidence.** Executor types, starvation, callback groups: web search summary of ROS docs and papers (docs.ros.org page itself blocked; verify details). FEO facts: [[s-core-overview]] (read on GitHub only). rclc statement from rclc docs listing (unverified in detail).
