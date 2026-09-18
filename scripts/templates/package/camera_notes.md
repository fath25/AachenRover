
## Camera implementation boundary

The scaffold registers relative `image_raw` and `camera_info` sensor-data
publishers (best effort). The default namespace produces
`/front_camera/image_raw` and `/front_camera/camera_info`. It publishes nothing
until `read_sample()` is implemented. It does not open a physical device.

Prefer an existing maintained ROS driver for your camera when one is available;
you may only need its launch/configuration instead of a custom capture node.
Otherwise, implement capture and release using your chosen SDK and populate
`sensor_msgs/Image` and `CameraInfo` with matching acquisition timestamps and
calibration. Uncalibrated CameraInfo must use the standard zero calibration
values rather than fabricated intrinsics. Convert hardware time to ROS time.

Set `device`, `rate_hz`, and `frame_id` in the configuration. Add the measured
camera mount transform to the robot description; this generator cannot know it.
The optical frame uses z forward, x right, y down. Use distinct namespaces AND
frame IDs for additional cameras. No camera is inserted into Gazebo by this
package; a simulated camera requires its own sensor and bridge configuration.
