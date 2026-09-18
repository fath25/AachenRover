# Create a new worker package

See the [visual integration overview](integration.md) for how packages and nodes
fit together, with a camera pipeline and a combined launch example.

In ROS 2, a **node** is a running worker. A **package** contains one or more nodes,
its dependencies, launch files, and configuration. Nodes can communicate across
languages through ROS messages. This generator supports Python and C++; other
languages need a compatible ROS client library and their own build integration.

ROS has a basic `ros2 pkg create` command. The repository's Python generator adds
the rover workspace location, installed launch/config files, executable entry
points, namespaces, and an optional camera interface. Generation needs only
Python's standard library; building and running need ROS 2 Jazzy.

## Camera example

From the repository root:

```bash
./scripts/rover create-package rover_camera --language python --template camera --node-name camera
./scripts/rover build
./scripts/rover launch rover_camera camera.launch.py
```

The equivalent direct invocation is:

```bash
python3 scripts/create_package.py rover_camera --language python --template camera --node-name camera
```

Use one invocation, not both; an existing package is never overwritten.

Generated Python package:

```text
software/ros2_ws/src/rover_camera/
├── package.xml                 # ROS dependencies
├── setup.py                    # Install data and executable entry point
├── setup.cfg                   # ROS executable installation path
├── resource/rover_camera       # Package discovery marker
├── rover_camera/
│   ├── __init__.py
│   └── camera.py               # Implement read_sample() here
├── launch/camera.launch.py     # Ready-to-use launch file
├── config/params.yaml          # Rate, device and optical frame
├── LICENSE
└── README.md
```

Implement `read_sample()` to return an `Image`/`CameraInfo` pair, or `None` when
no frame is ready. The generated shell handles timer scheduling and publishing
with sensor-data QoS. It deliberately produces no images before capture is
implemented. Device opening, capture, calibration, timestamp conversion, cleanup,
and the measured camera mounting transform still depend on your hardware.
Consider using an existing camera driver before writing a capture backend.

Topics default to `/front_camera/image_raw` and `/front_camera/camera_info`.
Configuration is loaded automatically. Override it or the namespace at launch:

```bash
./scripts/rover launch rover_camera camera.launch.py namespace:=rear_camera params_file:=/absolute/path/rear-camera.yaml
```

Give each camera a distinct optical frame as well as a namespace. Add measured
mount transforms to the robot description. This does not add a simulated camera
or automatically start physical devices in the simulation.

## C++ or a generic worker

```bash
./scripts/rover create-package rover_camera_cpp --language cpp --template camera --node-name camera
./scripts/rover create-package rover_monitor --language python --node-name monitor --dependency std_msgs
```

C++ packages contain `CMakeLists.txt` and `src/camera.cpp` in place of Python
packaging. Both languages receive the same configuration/launch interface.
The generic `node` template has a `tick()` method for your implementation.

Colcon discovers new packages automatically. No central registration is needed.
`./scripts/rover build` builds them; `./scripts/rover launch PACKAGE FILE` sources
the workspace and launches them. After implementation, include their launch files
in your deployment's bringup launch to start multiple workers together.

`--dependency` is repeatable and adds ROS dependencies to the manifest and C++
build configuration. It does not install dependencies. Use the documented
rosdep installation workflow for missing packages. Add dependencies introduced
later to package.xml (and CMake for C++). Set actual maintainer metadata before
publishing. Parameters are startup configuration, not dynamically reconfigured.

For experiments use `--destination /tmp/my_workspace/src`; build and source that
workspace separately. Generation refuses invalid names and existing paths.
Run `./scripts/rover create-package --help` for all options.

You do not need a new package for every Python file or C++ source. Group related
implementation modules within the generated package; create a new package for
an independently reusable component or a component with distinct dependencies.
