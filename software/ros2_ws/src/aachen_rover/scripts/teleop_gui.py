#!/usr/bin/env python3
"""Hold mouse buttons or WASD/arrows to drive. Release/focus loss stops."""
import tkinter as tk
import signal
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from geometry_msgs.msg import Twist
from control import key_command


class Teleop:
    def __init__(self, root, node):
        self.root, self.node = root, node
        self.publisher = node.create_publisher(Twist, '/cmd_vel', 1)
        self.keys = set()
        self.mouse = (0.0, 0.0)
        self.mouse_active = False
        root.title('AachenRover — Drive')
        tk.Label(root, text='Hold WASD / arrow keys or a mouse button to drive.\nRelease to stop. Space / Esc stops. Keep this window focused.', padx=20, pady=15).grid(row=0, column=0, columnspan=3)
        for text, row, column, command in [('Forward ↑', 1, 1, (0.4, 0.0)), ('Left ↶', 2, 0, (0.0, 0.8)), ('STOP', 2, 1, (0.0, 0.0)), ('Right ↷', 2, 2, (0.0, -0.8)), ('Reverse ↓', 3, 1, (-0.4, 0.0))]:
            button = tk.Button(root, text=text, width=14, height=3, takefocus=False)
            button.grid(row=row, column=column, padx=4, pady=4)
            button.bind('<ButtonPress-1>', lambda event, c=command: self.press_mouse(c))
            button.bind('<Leave>', lambda event: self.stop())
        root.bind_all('<ButtonRelease-1>', lambda event: self.stop())
        root.bind('<KeyPress>', self.key_down)
        root.bind('<KeyRelease>', self.key_up)
        root.bind('<FocusOut>', lambda event: self.stop())
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.tick()

    def press_mouse(self, command):
        self.root.focus_set()
        self.keys.clear()
        self.mouse = command
        self.mouse_active = command != (0.0, 0.0)

    def key_down(self, event):
        if event.keysym in ('space', 'Escape'):
            self.stop()
        elif not self.mouse_active and event.keysym in {'w', 'a', 's', 'd', 'Up', 'Down', 'Left', 'Right'}:
            self.keys.add(event.keysym)

    def key_up(self, event):
        self.keys.discard(event.keysym)

    def publish(self, command):
        message = Twist()
        message.linear.x, message.angular.z = command
        self.publisher.publish(message)

    def stop(self):
        self.keys.clear()
        self.mouse = (0.0, 0.0)
        self.mouse_active = False
        if rclpy.ok():
            self.publish(self.mouse)

    def tick(self):
        if not rclpy.ok():
            self.root.destroy()
            return
        self.publish(key_command(self.keys) if self.keys else self.mouse)
        rclpy.spin_once(self.node, timeout_sec=0)
        self.root.after(50, self.tick)

    def close(self):
        self.stop()
        self.root.destroy()


def main():
    rclpy.init()
    node = Node('rover_teleop')
    try:
        root = tk.Tk()
        Teleop(root, node)
        root.mainloop()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
