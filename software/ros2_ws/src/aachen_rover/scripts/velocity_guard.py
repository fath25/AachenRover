#!/usr/bin/env python3
"""Use wall time so paused simulation clocks cannot defeat the command timeout."""
import time
import signal
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from geometry_msgs.msg import Twist
from control import VelocityPolicy


class Guard(Node):
    def __init__(self):
        super().__init__('velocity_guard')
        self.policy = VelocityPolicy()
        self.publisher = self.create_publisher(Twist, '/cmd_vel_safe', 1)
        self.create_subscription(Twist, '/cmd_vel', self.receive, 1)
        self.create_timer(0.05, self.publish)

    def receive(self, message):
        self.policy.receive(message.linear.x, message.angular.z, time.monotonic())

    def publish(self):
        message = Twist()
        message.linear.x, message.angular.z = self.policy.sample(time.monotonic())
        self.publisher.publish(message)


def main():
    rclpy.init()
    node = Guard()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        if rclpy.ok():
            node.publisher.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
