---
name: rover-hardware
description: Maintain AachenRover CAD and mechanical inventory or integrate physical ROS 2 motor and lidar drivers without coupling application code to a board.
---

Read `hardware/README.md` and `docs/architecture.md`. Preserve the original CAD
and shopping list; document derived exports, units, source parts, and assembly
revision. Do not infer measured mass, strength, gearing, voltage, or load ratings
from simulation primitives or filenames.

For new Python/C++ adapters, use `./scripts/rover create-package` and read
`docs/development.md`. Prefer an existing camera driver when appropriate; the
camera template only supplies the ROS shell, not capture or calibration.

Implement board-specific behavior behind the ROS topic and TF contract. A Linux
computer capable of ROS 2 is the compute baseline, but actuators still need
appropriate drivers, power, feedback, and a physical emergency stop. Verify
the chosen driver's architecture and ROS distribution support.

Before physical actuation, obtain the user's authorization and establish a
safe test setup. Use mock or simulation tests for interface development. Record
which results were measured on hardware and which remain assumptions.
