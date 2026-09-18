---
name: rover-simulation
description: Build, run, or modify the AachenRover ROS 2 and Gazebo simulation, lidar, world, and desktop driving controls.
---

Read `docs/simulation.md` and `docs/architecture.md` from the repository root.
Use `./scripts/rover doctor` to inspect dependencies before installing anything.
Keep URDF as the single robot geometry source. Gazebo consumes its conversion;
do not hand-maintain a second robot SDF. World objects need collision geometry
and visuals to work physically and appear in the GPU lidar.

Preserve directional bridge mappings and the `odom -> base_link -> lidar_link`
TF chain. Publish joint states for moving wheels. GPU lidar requires the world
Sensors system and rendering even in server-only mode. Keep sensor-frame names
explicit, and simulation time enabled on consumers of sensor timestamps.

Run `build`, `check`, and `test`. Start `sim gui:=false teleop:=false rviz:=false`
with a dedicated ROS domain and Gazebo partition, then run `smoke` with the same
values. Stop the simulation after testing. For control edits also exercise
press/release, focus loss, close, and command timeout. Report separately what
was validated headlessly and on a desktop. Do not equate scans with mapping:
SLAM and autonomous exploration are future work.
