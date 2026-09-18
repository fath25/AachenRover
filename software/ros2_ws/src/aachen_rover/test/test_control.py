import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from control import VelocityPolicy, key_command


def test_timeout_and_limits():
    policy = VelocityPolicy()
    assert policy.sample(1) == (0, 0)
    policy.receive(100, -100, 2)
    assert policy.sample(2.1) == (0.6, -1.2)
    assert policy.sample(2.36) == (0, 0)
    assert policy.sample(1) == (0, 0)


def test_nonfinite_stops():
    for value in [float('nan'), float('inf'), -float('inf')]:
        policy = VelocityPolicy()
        policy.receive(value, 1, 2)
        assert policy.sample(2) == (0, 0)


def test_keys_and_opposites():
    assert key_command({'w', 'a'}) == (0.4, 0.8)
    assert key_command({'w', 's', 'Left', 'Right'}) == (0, 0)
    assert key_command(set()) == (0, 0)
