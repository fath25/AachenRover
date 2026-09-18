# Validation record

Tested locally on 2026-09-18, Ubuntu 24.04, ROS 2 Jazzy, Gazebo Sim 8.9.0.

- `./scripts/rover doctor`: required tools and ROS packages found.
- `./scripts/rover build`: colcon build and install succeeded.
- `./scripts/rover check`: repository discovery links, skill metadata, Python/XML
  syntax, bridge structure, and three control-policy tests passed.
- `./scripts/rover test`: ament/CTest passed, no failures.
- All three skills passed the bundled OpenAI skill-creator validator.
- `gui_input_check.py`: actual Tk bindings passed keyboard/mouse press, release,
  mouse priority, Space, focus-loss, and close checks on the desktop.
- Combined Gazebo/RViz/Tk desktop launch ran with the Ogre 1 fallback; RViz
  initialized OpenGL 4.5. This was a process/log check, not a visual layout review.
- Live simulation `smoke`: clock, 720 lidar rays with obstacle returns, wheel
  states, `odom -> lidar_link` TF, forward motion, decreasing obstacle range,
  turning, and stop after stale input all passed. Used `render_engine:=ogre`,
  `LIBGL_ALWAYS_SOFTWARE=1`, `gui:=false teleop:=false rviz:=false`, ROS domain
  73, and an isolated Gazebo partition. Ogre 1 server rendering used the existing
  X11 display; this was **not** a display-free EGL test.

Ogre 2 failed on this workstation while initializing EGL devices (including a
failed NVIDIA-specific attempt); software rendering alone did not fix Ogre 2.
The launch supports an explicit Ogre 1 fallback. No graphics drivers or system
configuration were changed. A compatible Ogre 2/EGL host is still needed to
validate truly display-free rendering. GPU requirements concern the simulator,
not the physical rover computer.

The installed Claude CLI completed a read-only architecture/code review.
Its feedback prompted simulator shutdown on guard/bridge exit, stronger motion
validation, and deterministic mouse priority. Its suggested launch-order race
was not reproduced: local spawns succeeded. The live acceptance test checks
readiness with a bounded wait rather than assuming a fixed startup delay. An OnProcessStart event would not
itself prove service readiness. The small initial wheel-ground gap is deliberate
for spawning and the live test allows settling.

CI configuration was added but has not run on GitHub. Native discovery by every
provider, a CAD-accurate rover, physical hardware, SLAM, navigation, and autonomous
exploration have not been tested or implemented. Adapter files and plain-text
context enable onboarding; they do not guarantee every host follows instructions.

During cleanup, this Gazebo installation also reported a segmentation fault on
server shutdown after the successful Ogre 1 acceptance run. The desktop launch
was checked separately. Earlier Python processes received duplicate SIGINTs
from the terminal and launch supervisor; cleanup now ignores repeated SIGINTs.
The Gazebo shutdown issue remains a vendor/runtime limitation to investigate,
not an acceptance-test pass for clean Gazebo teardown.

## Package generator and GPU follow-up (2026-09-18)

- Repository checks now pass 16 tests, including package generation, invalid
  names, refusal to overwrite existing files, and NVIDIA preflight behavior.
- Generated all four variants (Python/C++, generic/camera) in an isolated
  temporary workspace. All four built with colcon and launched successfully.
  Live ROS checks verified installed entry points, namespace overrides, loaded
  rate/simulation-time parameters, and camera topic types. No physical camera
  was opened and no capture backend is supplied.
- Added template builds to CI; this configuration has not yet run on GitHub.
- Host diagnostics identified the NVIDIA problem: loaded module 580.173.02
  versus libraries/on-disk module 580.178.04. The NVIDIA launcher correctly
  refuses to start while `nvidia-smi` reports this mismatch. Its successful
  NVIDIA rendering path cannot be tested until the driver state is repaired.
- Ogre 1 on the Intel GPU rendered but produced constant minimum-range lidar
  values. The live motion/range test caught this; this path is not recommended.
- Ogre 2 with `gui:=false teleop:=false rviz:=false headless_rendering:=false`
  passed the live scan/TF/motion/turn/timeout acceptance test. Its Ogre log
  reported `GL_VENDOR = Intel` and `GL_RENDERER = Mesa Intel(R) Iris(R) Xe
  Graphics (ADL GT2)`, confirming hardware acceleration without forcing software
  rendering. This supersedes the earlier software-only recommendation.
- Rebooting should load the already-installed matching NVIDIA module; no reboot
  or driver changes were performed. See `gpu-rendering.md`.
- The combined Ogre 2 Gazebo/RViz desktop launch also passed the live acceptance
  test on Intel. Motion durations now use simulation time with a 60-second wall
  deadline, so GUI load does not cause a false distance failure. The initial
  front-obstacle range is checked explicitly to reject constant-minimum scans.
