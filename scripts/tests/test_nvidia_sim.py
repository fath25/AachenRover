import importlib.util
from pathlib import Path
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('nvidia_sim', Path(__file__).resolve().parents[1] / 'nvidia_sim.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_child_environment():
    original = {'LIBGL_ALWAYS_SOFTWARE': '1', 'DRI_PRIME': '1', 'PATH': '/usr/bin',
                'ROS_DOMAIN_ID': '73', '__GLX_VENDOR_LIBRARY_NAME': 'mesa'}
    child = module.nvidia_environment(original)
    assert 'LIBGL_ALWAYS_SOFTWARE' not in child and 'DRI_PRIME' not in child
    assert child['__GLX_VENDOR_LIBRARY_NAME'] == 'nvidia'
    assert child['__NV_PRIME_RENDER_OFFLOAD'] == '1'
    assert child['ROS_DOMAIN_ID'] == '73'
    assert original['LIBGL_ALWAYS_SOFTWARE'] == '1'


def test_driver_failure_never_launches(monkeypatch, capsys):
    monkeypatch.setattr(module.shutil, 'which', lambda name: '/usr/bin/nvidia-smi')
    monkeypatch.setattr(module.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=1, stdout='Driver/library version mismatch', stderr=''))
    def no_launch(*args):
        raise AssertionError('Should not start Gazebo')
    monkeypatch.setattr(module.os, 'execvpe', no_launch)
    assert module.main([]) == 1
    assert 'simulator not started' in capsys.readouterr().err
