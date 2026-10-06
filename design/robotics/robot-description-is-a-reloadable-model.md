---
title: The robot description is a reloadable model; tools are templates plus instances
type: pattern
cluster: robotics
component: none
tags: [urdf, xacro, ros2_control, moveit, end-effector, tool-changer, open-world]
status: draft
sources:
  - https://wiki.ros.org/xacro
  - https://control.ros.org/rolling/index.html
  - https://raw.githubusercontent.com/ros-planning/moveit_msgs/master/msg/AttachedCollisionObject.msg
  - https://moveit.picknik.ai/main/index.html
last-verified: 2026-10-03
related:
  - "[[instance-in-the-name-type-in-the-hash]]"
  - "[[opensovd-overview]]"
  - "[[vss-kuksa-overview]]"
applies-to: [opensovd, vss-kuksa, muto]
gap-rows: [C8, B10]
---

# The robot description is a reloadable model; tools are templates plus instances

**Problem.** A robot changes its gripper or a truck gets a body-builder crane. The planner, the controllers and the collision model all believed in a fixed kinematic tree, so the new tool is invisible or crashes the arm.

**Forces.**
- Safety-relevant geometry (reach, collision) must be known to the planner before motion.
- Tools come from third parties and were not known at build time.
- A description must be generated, not hand-edited per variant.
- Drivers for the new hardware must be loadable without rebuilding the controller stack.

**The rule.** Make the description a *model with parameters*, and treat a tool as a **template** (xacro macro: links, joints, `ros2_control` block) that you **instantiate** with a prefix and a mounting pose. xacro expands to URDF, which is published on the `robot_description` parameter/topic; consumers rebuild their state from it. In `ros2_control`, the `<ros2_control>` tag in that URDF names a hardware plugin and the joints/interfaces it offers, and the resource manager loads the plugin from the description, so a tool's driver arrives with its description. MoveIt covers the part URDF cannot: an `AttachedCollisionObject` fixes a collision object to a link (`link_name`), lists `touch_links` it may contact and a `detach_posture`, so an unknown payload becomes known geometry at runtime.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| xacro macros | parameterised URDF fragments with prefixes | tool template, many instances |
| `robot_description` + `robot_state_publisher` | description published; tf derived from it | one source for the kinematic tree |
| ros2_control `<hardware><plugin>` | description names the hardware plugin and interfaces; Sensor/Actuator/System component types with a lifecycle (configure/activate) | driver loaded from the description |
| MoveIt `AttachedCollisionObject`, SRDF end effector | attach shapes to a link with `touch_links`, `detach_posture`, `weight` | payload and tool as runtime geometry |
| Sparkplug DBIRTH / AAS submodel template | a device announces its metric template on arrival | the same shape for non-ROS stacks |

**On the Eclipse SDV stack.** The robot description plays the role of the VSS tree plus its overlay: a body-builder or trailer module brings a *fragment* (a vspec overlay in [[vss-kuksa-overview]], an SOVD sub-component in [[opensovd-overview]]) that is mounted under a named parent. xacro prefix = VSS `instances`/instance key. The honest limit: VSS instances only cover static arrays; the dynamic "mount a fragment under a parent at runtime" step has no equivalent (cf. [[instance-in-the-name-type-in-the-hash]]). A vspec-to-xacro or xacro-to-vspec exporter does not exist (unverified).

**The trap.** Hot-reloading the description without re-validating the safety limits and collision pairs: the new tool is then planned with the old robot's limits.

**For a hackathon team.** Show a xacro macro for a two-link "tool" instantiated as `tool_a` and `tool_b`, published as `robot_description`, with a viewer showing it appear; narrate that the same pattern is a trailer overlay. Pitch: "tool = template, mount = instance".

**Evidence.** AttachedCollisionObject fields verified from msg file above. ros2_control plugin loading from URDF, hardware types and lifecycle: control.ros.org search summary (class `ResourceManager::load_and_initialize_components`); exact current API unverified. xacro/robot_state_publisher behaviour is standard ROS practice (unverified here, docs.ros.org blocked during research).
