# Simulation setup and operation

## Install once

On Ubuntu 24.04, install ROS 2 Jazzy using the
[official ROS installation instructions](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).
Use the [supported Jazzy/Harmonic pairing](https://gazebosim.org/docs/harmonic/ros_installation/).
After configuring the ROS apt repository:

```bash
sudo apt update
sudo apt install ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher python3-colcon-common-extensions \
  python3-rosdep python3-pytest python3-tk python3-yaml \
  ros-jazzy-ament-cmake-pytest
# Only if rosdep has never been initialized:
sudo rosdep init
rosdep update
rosdep install --from-paths software/ros2_ws/src --ignore-src -r -y --rosdistro jazzy
```

Then run `./scripts/rover doctor`, `build`, and `sim` from the repository root.
The scripts source ROS and the overlay automatically. Standard colcon/ros2
commands also work after sourcing `/opt/ros/jazzy/setup.bash` and
`software/ros2_ws/install/setup.bash`.

## Driving and viewing lidar

The default launch opens Gazebo, RViz, and the Tk driving panel. Focus the panel;
hold W/Up to drive, S/Down to reverse, A/Left or D/Right to turn. Keyboard
combinations allow arcs. Mouse buttons are hold-to-drive. Releasing, leaving
a mouse button, losing focus, Space/Esc, or closing the panel stops the input.
Ctrl-C in the launch terminal stops the entire launch.

RViz uses `odom` and displays the robot and scan. The scan is 2D at roughly
0.49 m above the ground. Low objects outside that plane will not be seen.
The model approximates a terrestrial scale rover with Earth gravity and
skid steering, not a flight-accurate Perseverance dynamics model.

## Add objects

Edit `software/ros2_ws/src/aachen_rover/worlds/mars_yard.sdf`, copy one of the
static obstacle models, give it a unique name and a new pose, and restart.
Keep both `<collision>` and `<visual>` geometry. Put an object through the
scan plane (for example a 1 m cube centred at z=0.5). Existing obstacles are
at (3, 0) and (0, 3) metres. Gazebo's GUI can also insert primitives for a
single session; save persistent changes in the source world. No Fuel download
or internet connection is needed for the bundled world.

## Automated acceptance

In terminal 1:

```bash
ROS_DOMAIN_ID=73 GZ_PARTITION=aachen_test ./scripts/rover sim gui:=false teleop:=false rviz:=false
```

In terminal 2:

```bash
ROS_DOMAIN_ID=73 GZ_PARTITION=aachen_test ./scripts/rover smoke
```

The live test waits up to 45 seconds for startup and checks clock, scan size and
frame, obstacle returns, wheel states, TF connectivity, translation, turning, decreasing lidar distance to the front obstacle,
and stopping after command input ceases. Use a fresh world and no other command
publisher. Stop the server with Ctrl-C after testing. `check` and `test` do not
start a simulator; they are fast structural and control-policy checks.

## Troubleshooting

- Missing package: run `doctor` and install dependencies above; build the overlay.
- No display: disable all three GUIs as shown. GPU lidar still needs an EGL/
  OpenGL-capable render path. With Mesa, `LIBGL_ALWAYS_SOFTWARE=1` can help on
  machines without a usable GPU, at reduced speed. First check the
  [GPU diagnostics](gpu-rendering.md); the current workstation has an NVIDIA
  driver/library mismatch and a working Intel hardware-rendering path. If Ogre 2 still crashes while
  probing EGL devices, use the supported Ogre 1 fallback on an X11 display:

  ```bash
  LIBGL_ALWAYS_SOFTWARE=1 ./scripts/rover sim render_engine:=ogre
  ```

  For software-rendered server-only fallback add `gui:=false teleop:=false rviz:=false`; this still
  needs `DISPLAY` (or Xvfb). Ogre 1 does not support the EGL headless flag. This
  launch keeps the renderer selectable instead of changing system GPU drivers.
  See [Gazebo rendering troubleshooting](https://gazebosim.org/docs/harmonic/troubleshooting/).
- Empty `/scan`: inspect Gazebo Sensors/Ogre2 errors and the ROS bridge. A server
  without rendering cannot synthesize GPU lidar. RViz's scan reliability should
  be Best Effort; all sensor consumers should use simulation time.
- No cross-process topics: use the same ROS domain and Gazebo partition in both
  terminals; allow local DDS/Gazebo sockets. Sandboxed agent runners may require
  an explicit execution permission for these sockets and desktop/log access.
- No motion: unpause Gazebo and focus the control panel. Only publish to
  `/cmd_vel`; `/cmd_vel_safe` is owned by the guard. Do not run two teleops.
- KDL root-inertia warning: harmless for this visualization; Gazebo still uses
  the chassis inertia. A future kinematics model can add a massless root frame.

## Desktop event check

With a desktop display and ROS sourced:

```bash
source /opt/ros/jazzy/setup.bash
python3 software/ros2_ws/src/aachen_rover/test/gui_input_check.py
```

This opens a temporary Tk window and exercises actual event bindings, recording
published commands without driving a robot. It is deliberately separate from
headless unit tests.

For this workstation's working Intel GPU, the server-only command is:

```bash
./scripts/rover sim gui:=false teleop:=false rviz:=false headless_rendering:=false
```

It uses Ogre 2 via the existing display. Plain `./scripts/rover sim` uses the same
GPU path with desktop windows. See [GPU rendering](gpu-rendering.md) for the
NVIDIA driver mismatch and the post-reboot NVIDIA launch command.
