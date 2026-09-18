"""Pure control policy shared by the watchdog and its tests."""
import math


class VelocityPolicy:
    def __init__(self, timeout=0.35, max_linear=0.6, max_angular=1.2):
        self.timeout = timeout
        self.max_linear = max_linear
        self.max_angular = max_angular
        self.last_time = -math.inf
        self.command = (0.0, 0.0)

    def receive(self, linear, angular, now):
        if not all(math.isfinite(v) for v in (linear, angular)):
            self.command = (0.0, 0.0)
        else:
            self.command = (max(-self.max_linear, min(self.max_linear, linear)),
                            max(-self.max_angular, min(self.max_angular, angular)))
        self.last_time = now

    def sample(self, now):
        return self.command if 0 <= now - self.last_time < self.timeout else (0.0, 0.0)


def key_command(keys):
    forward = bool(keys & {'w', 'Up'}) - bool(keys & {'s', 'Down'})
    turn = bool(keys & {'a', 'Left'}) - bool(keys & {'d', 'Right'})
    return forward * 0.4, turn * 0.8
