#!/usr/bin/env python3
"""Explicit desktop check: Tk events through real callbacks, no robot required."""
import sys
import tkinter as tk
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from teleop_gui import Teleop
import rclpy
from rclpy.node import Node


class Recorder:
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append((message.linear.x, message.angular.z))


def main():
    rclpy.init()
    node = Node('gui_input_check')
    root = tk.Tk()
    ui = Teleop(root, node)
    recorder = Recorder()
    ui.publisher = recorder
    root.update()
    root.focus_force()
    root.update()

    def check_event(widget, event, expected, **kwargs):
        widget.event_generate(event, **kwargs)
        root.update()
        ui.tick()
        assert recorder.messages[-1] == expected, (event, recorder.messages[-1])

    check_event(root, '<KeyPress>', (0.4, 0.0), keysym='w')
    check_event(root, '<KeyRelease>', (0.0, 0.0), keysym='w')
    button = next(w for w in root.winfo_children() if isinstance(w, tk.Button) and w['text'] == 'Forward ↑')
    check_event(button, '<ButtonPress-1>', (0.4, 0.0))
    check_event(root, '<KeyPress>', (0.4, 0.0), keysym='a')
    check_event(button, '<ButtonRelease-1>', (0.0, 0.0))
    check_event(root, '<KeyPress>', (0.4, 0.0), keysym='w')
    check_event(root, '<KeyPress>', (0.0, 0.0), keysym='space')
    check_event(button, '<ButtonPress-1>', (0.4, 0.0))
    check_event(root, '<FocusOut>', (0.0, 0.0))
    ui.close()
    assert recorder.messages[-1] == (0, 0)
    node.destroy_node()
    rclpy.shutdown()
    print('PASS: Tk keyboard, mouse, release, Space, focus loss, close callbacks')


if __name__ == '__main__':
    main()
