#!/usr/bin/env python3
"""Launch Gazebo with NVIDIA PRIME offload, failing early on driver problems."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NVIDIA_EGL = Path('/usr/share/glvnd/egl_vendor.d/10_nvidia.json')


def nvidia_environment(base):
    environment = dict(base)
    for key in ('LIBGL_ALWAYS_SOFTWARE', 'GALLIUM_DRIVER', 'MESA_LOADER_DRIVER_OVERRIDE',
                'DRI_PRIME', '__NV_PRIME_RENDER_OFFLOAD_PROVIDER'):
        environment.pop(key, None)
    environment.update(__NV_PRIME_RENDER_OFFLOAD='1', __GLX_VENDOR_LIBRARY_NAME='nvidia',
                       __EGL_VENDOR_LIBRARY_FILENAMES=str(NVIDIA_EGL))
    return environment


def main(args=None):
    args = sys.argv[1:] if args is None else args
    if '--help' in args or '-h' in args:
        print('Usage: ./scripts/rover sim-nvidia [ROS launch arguments]\n'
              'Checks the NVIDIA driver, selects NVIDIA GLX/EGL, then launches sim.\n'
              'Example: ./scripts/rover sim-nvidia gui:=false teleop:=false rviz:=false')
        return 0
    if not shutil.which('nvidia-smi'):
        print('nvidia-smi is unavailable. See docs/gpu-rendering.md.', file=sys.stderr)
        return 1
    try:
        check = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        print('NVIDIA driver check timed out; simulator not started.', file=sys.stderr)
        return 1
    if check.returncode:
        print(check.stdout + check.stderr, file=sys.stderr)
        print('NVIDIA driver check failed; simulator not started. A driver/library version\n'
              'mismatch often needs a reboot after an update. Compare the loaded module\n'
              '(/proc/driver/nvidia/version) with modinfo -F version nvidia.\n'
              'See docs/gpu-rendering.md. Run outside a sandbox that hides GPU devices.', file=sys.stderr)
        return 1
    if not NVIDIA_EGL.is_file():
        print(f'Missing NVIDIA EGL vendor file: {NVIDIA_EGL}. See docs/gpu-rendering.md.', file=sys.stderr)
        return 1
    os.execvpe(str(ROOT / 'scripts/rover'), ['rover', 'sim', *args], nvidia_environment(os.environ))


if __name__ == '__main__':
    raise SystemExit(main())
