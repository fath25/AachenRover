# Hardware baseline

The original mechanical assets remain in [`3D Models/`](../3D%20Models/), mostly
SolidWorks parts. The original [fasteners and bearings list](../List%20of%20bolt,%20nuts,%20bearings%20and%20other%20stuff%20for%20the%20DIY%20Mars%20Rover.txt)
is retained unchanged. Its quantities are source data, not a verified complete
BOM. No assembly validation, motor sizing, wiring diagram, electronics BOM,
CAD license verification, or physical test has been performed here.

The application layer requires a Linux computer that can run the selected ROS 2
distribution. It does not prescribe Raspberry Pi, Jetson, x86, or a motor vendor.
A real build additionally needs appropriately rated motors/controllers,
feedback, power conversion and protection, communications, a lidar with a ROS 2
driver, and a physical emergency stop. ROS 2 capability alone does not establish
actuator or electrical suitability.

Integrate electronics through the [ROS interface contract](../docs/architecture.md).
A drive adapter converts body velocity to the actual wheel/steering kinematics,
publishes odometry/joints, and independently times out stale commands. A lidar
adapter publishes `/scan` with the calibrated frame and timestamp. Document
power, pinout, firmware, transport, gear ratios, measured geometry, and tested
limits alongside each selected adapter. No board-specific driver is selected yet.

Keep CAD originals intact. Store derived export units and source revision with
any future STL/STEP/URDF assets. The current simulation uses illustrative
primitives, masses, and dimensions; do not manufacture or size loads from them.

For a new ROS worker or camera adapter, use the [package generator](../docs/development.md).
It supplies packaging and launch integration for Python/C++; it cannot infer
the device SDK, calibration, or measured mounting transform.
