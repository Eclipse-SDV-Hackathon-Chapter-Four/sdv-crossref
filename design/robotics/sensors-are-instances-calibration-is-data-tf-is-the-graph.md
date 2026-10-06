---
title: Sensors are instances, calibration is data, tf is the instance graph
type: pattern
cluster: robotics
component: none
tags: [perception, sensors, calibration, tf, trailer, body-builder, open-world]
status: draft
sources:
  - https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Tf2.html
  - https://www.ros.org/reps/rep-0105.html
  - https://github.com/ros-perception/camera_info_manager
  - https://wiki.ros.org/camera_calibration
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[vss-kuksa-overview]]"
  - "[[robot-description-is-a-reloadable-model]]"
applies-to: [vss-kuksa, opensovd, uprotocol]
gap-rows: [C8, B10]
---

# Sensors are instances, calibration is data, tf is the instance graph

**Problem.** A trailer camera, a body-builder radar or an extra lidar appears. Its measurements are useless unless you know where it is and how it distorts, and hard-coding either in a node means a redeploy per mount.

**Forces.**
- The same driver (type) runs for any number of devices.
- Mounting pose and intrinsics are per-instance and change with maintenance and coupling.
- Frames must form a tree so any consumer can transform any measurement.
- Stale calibration is worse than none.

**The rule.** One **driver type**, many **namespaced instances**; each stream carries a `frame_id` (instance key) and a timestamp; **extrinsics are a transform** in the tf tree (static or broadcast by whoever mounts the sensor), **intrinsics are a `CameraInfo`-style message** loaded from a calibration file by the driver. Consumers never know the mount, only "give me the transform from `sensor_x` to `base`". A coupled trailer is then a new subtree attached by a transform whose parent is the hitch frame, with a lifetime: when the trailer leaves, the transform stops and consumers must treat the subtree as absent rather than at its last pose.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| tf2 / REP-105 | frame tree with timestamped transforms; `map/odom/base_link` convention | geometry as a queryable graph |
| camera_info_manager, camera_calibration | calibration stored as YAML, published as `CameraInfo` | calibration as data |
| URDF/xacro sensor macros | mount point as a prefixed instance | sensors declared with the robot |
| VSS `instances` and sensor-position attributes (unverified) | static array instances | the closed-world tree analogue |
| ISO 11898/J1939 module addressing | instance by address claim | non-geometric identity |

**On the Eclipse SDV stack.** Map the tf instance key to the instance in the name ([[instance-in-the-name-type-in-the-hash]]): `.../sensors/<instance>/image`, with the type hash covering the message layout, and the *calibration blob as an announced attribute* of the instance, versioned with a hash. A VSS leaf has a value but no pose; the pose of a trailer sensor belongs in a separate geometry resource, not in [[vss-kuksa-overview]]. A SOVD component for the sensor can carry calibration state and age ([[opensovd-overview]]). Chapter 3 ran sensors through CARLA ego-vehicle controllers that publish sensor streams over uProtocol/Zenoh ([[chapter3-retrospective]]); the same keys serve real sensors.

**The trap.** Freezing the pose in the driver config, so the swapped sensor reports in the old position and the fused map shears.

**For a hackathon team.** Two simulated cameras of one type under two namespaces, one extrinsic file each, and a viewer that transforms both to `base` using only tf; then "couple" a third by publishing one transform. Pitch: "calibration is data, mounting is a transform".

**Evidence.** tf2, REP-105, camera_info_manager are standard ROS conventions (URLs listed; pages not fetched because docs.ros.org was blocked: unverified in detail). Chapter 3 sensor streams: [[chapter3-retrospective]]. No gap for geometry resources exists in the register; this card suggests one: "geometry/calibration resource for body-builder sensors".
