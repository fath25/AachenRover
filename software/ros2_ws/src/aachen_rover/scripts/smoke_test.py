#!/usr/bin/env python3
"""Live simulation acceptance check. Run without another velocity publisher."""
import math
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, JointState
from nav_msgs.msg import Odometry
from rosgraph_msgs.msg import Clock
from tf2_ros import Buffer, TransformListener


def main():
    rclpy.init()
    node = Node('rover_smoke_test')
    state = {}
    subscriptions = []
    for kind, topic, key in [(LaserScan, '/scan', 'scan'), (Odometry, '/odom', 'odom'),
                             (JointState, '/joint_states', 'joints'), (Clock, '/clock', 'clock')]:
        subscriptions.append(node.create_subscription(kind, topic, lambda msg, k=key: state.update({k: msg}), qos_profile_sensor_data))
    buffer = Buffer()
    listener = TransformListener(buffer, node)
    publisher = node.create_publisher(Twist, '/cmd_vel', 1)

    def wait(seconds, command=None, simulation_time=False):
        def elapsed_clock():
            stamp = state['clock'].clock
            return stamp.sec + stamp.nanosec * 1e-9
        clock = elapsed_clock if simulation_time else time.monotonic
        end = clock() + seconds
        deadline = time.monotonic() + (60 if simulation_time else seconds + 1)
        while clock() < end:
            assert time.monotonic() < deadline, 'Simulation clock stalled or too slow'
            if command is not None:
                publisher.publish(command)
            rclpy.spin_once(node, timeout_sec=0.05)

    try:
        deadline = time.monotonic() + 45
        while len(state) < 4 and time.monotonic() < deadline:
            wait(0.1)
        assert len(state) == 4, f'Missing topics: {set(["scan", "odom", "joints", "clock"]) - state.keys()}'
        wait(1)
        scan = state['scan']
        assert len(scan.ranges) == 720 and scan.header.frame_id == 'lidar_link'
        finite = [v for v in scan.ranges if math.isfinite(v)]
        assert finite and 0.15 < min(finite) < 4, 'No nearby obstacle detected'
        assert len(state['joints'].name) >= 6
        assert buffer.can_transform('odom', 'lidar_link', rclpy.time.Time()), 'Broken TF chain'
        front_before = min(scan.ranges[355:365])
        assert 1.8 < front_before < 2.6, f'Invalid front obstacle range in fresh yard: {front_before}'
        start = state['odom'].pose.pose.position
        command = Twist()
        command.linear.x = 0.3
        wait(2, command, simulation_time=True)
        finish = state['odom'].pose.pose.position
        assert math.hypot(finish.x-start.x, finish.y-start.y) > 0.25, 'Rover did not drive'
        wait(1)
        wait(0.2, simulation_time=True)
        front_after = min(state['scan'].ranges[355:365])
        assert front_before - front_after > 0.2, 'Odometry moved but obstacle range did not decrease'
        assert abs(state['odom'].twist.twist.linear.x) < 0.03, 'Watchdog did not stop rover'
        orientation = state['odom'].pose.pose.orientation
        start_yaw = 2 * math.atan2(orientation.z, orientation.w)
        command.linear.x, command.angular.z = 0.0, 0.6
        wait(2, command, simulation_time=True)
        orientation = state['odom'].pose.pose.orientation
        yaw = 2 * math.atan2(orientation.z, orientation.w)
        assert abs(math.atan2(math.sin(yaw-start_yaw), math.cos(yaw-start_yaw))) > 0.3, 'Rover did not turn'
        publisher.publish(Twist())
        wait(0.5)
        print('PASS: clock, 720-ray obstacle scan, wheel states, TF, forward motion, turning, timeout stop')
    finally:
        publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
