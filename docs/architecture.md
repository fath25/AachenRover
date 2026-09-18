# Architecture and hardware boundary

See the [visual integration overview](integration.md) for how packages and nodes
fit together, with a camera pipeline and a combined launch example.

Application code talks ROS 2, never a particular GPIO library, motor board,
serial protocol, or lidar SDK. The simulation is one implementation of the
same interface a physical rover driver should expose. ROS 2 runs on Linux;
Ubuntu 24.04/Jazzy is the reproducible baseline, not a restriction on future
boards. A simulator workstation needs graphics support; the physical robot's
computer does not need to run Gazebo.

| Interface | Type | Owner / meaning |
| --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Operator/application request: x m/s, z rad/s |
| `/cmd_vel_safe` | `geometry_msgs/msg/Twist` | Guard output, simulation bridge input |
| `/odom` | `nav_msgs/msg/Odometry` | Drive implementation; wheel odometry |
| `/scan` | `sensor_msgs/msg/LaserScan` | Lidar, `lidar_link`, 720 rays, 10 Hz, 0.15–20 m |
| `/joint_states` | `sensor_msgs/msg/JointState` | Drive implementation, six moving wheel joints |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo only; consumers use simulation time |
| `/tf` | `tf2_msgs/msg/TFMessage` | Drive: `odom -> base_link`; state publisher: wheels |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | State publisher: `base_link -> lidar_link` |

Positive x is forward, y left, z up; positive yaw turns left. Units are metres,
seconds, kilograms, and radians. The base origin is the chassis centre. Only
one publisher owns each TF edge. No `map` frame exists until localization/SLAM
is added. Odometry is not world ground truth and can drift under wheel slip.

The URDF/Xacro is the single robot model source; `ros_gz_sim create` converts
it for Gazebo. The bridge only sends commands ROS-to-Gazebo; sensors, clock,
odometry, and dynamic drive TF flow Gazebo-to-ROS. Robot state publisher uses
sim time and publishes link transforms from joint states. The lidar fixed
joint is preserved through conversion, with an explicit scan frame.

The UI publishes 20 Hz while held. The separate guard clamps commands to
±0.6 m/s and ±1.2 rad/s and emits zero after 350 ms without input, using
monotonic wall time even when simulation is paused. Nonfinite commands stop.
This is an input watchdog, not a safety-rated emergency stop: the launch shuts the simulation down if the guard or bridge exits, but loss of
the supervisor or a hung process can still leave the last command active. Physical drivers must have
their own controller-side watchdog and hardware emergency stop. Run only one
command source; add an explicit mux before combining teleop with autonomy.

Next increments: CAD-derived dimensions and inertias, real suspension and
steering, board-specific ROS drivers, SLAM Toolbox and Nav2, then exploration.
A lidar scan is a local measurement; it does not itself build a map or prove
that every part of a world has been discovered.

New workers can use the Python/C++ [package generator](development.md). Colcon
automatically discovers their packages; launch them explicitly or compose their
launch files in a deployment bringup. Camera acquisition remains device-specific.
