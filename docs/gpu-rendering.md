# GPU rendering

Gazebo supports hardware rendering. Ogre is a rendering engine; choosing Ogre 1
instead of Ogre 2 does **not** by itself imply CPU rendering. Setting
`LIBGL_ALWAYS_SOFTWARE=1` explicitly forces software rendering. The physics and
ROS processes still consume CPU when graphics and lidar use a GPU.

## NVIDIA launch

```bash
./scripts/rover sim-nvidia
# Server with GPU lidar and no desktop windows:
./scripts/rover sim-nvidia gui:=false teleop:=false rviz:=false
```

This wrapper checks `nvidia-smi`, clears software/alternate-device overrides in
its child environment, selects NVIDIA PRIME offload and NVIDIA GLX/EGL, and uses
the regular launch with Ogre 2. It changes no system configuration. A working
NVIDIA kernel module and matching user-space graphics libraries are required.
The EGL vendor file path targets this project's Ubuntu baseline.

NVIDIA documents the offload variables in its
[PRIME render offload guide](https://download.nvidia.com/XFree86/Linux-x86_64/580.76.05/README/primerenderoffload.html).
The helper sets `__NV_PRIME_RENDER_OFFLOAD=1` and
`__GLX_VENDOR_LIBRARY_NAME=nvidia`; it also limits EGL vendor selection to
`/usr/share/glvnd/egl_vendor.d/10_nvidia.json` for Gazebo's sensor renderer.
This avoids selecting a different GPU for rendering sensors.

Verify the actual renderer rather than assuming a successful launch proves it:

```bash
nvidia-smi
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia glxinfo -B
rg 'GL_RENDERER|GL_VENDOR|Device Name' ~/.gz/rendering/ogre2.log
```

The renderer should identify NVIDIA, not `llvmpipe`. For Ogre 1 inspect
`~/.gz/rendering/ogre.log` instead. `glxinfo` is supplied by `mesa-utils`.

## This workstation: driver mismatch found 2026-09-18

Outside the agent sandbox, diagnostics showed:

- Loaded NVIDIA kernel module: **580.173.02** (`/proc/driver/nvidia/version`).
- Installed NVIDIA libraries: **580.178.04**.
- NVIDIA module on disk: **580.178.04** (`modinfo -F version nvidia`).
- `nvidia-smi`: **Driver/library version mismatch**.

The on-disk module matches the libraries, so rebooting to load the updated module
is the appropriate next step. Save work and reboot when convenient, then confirm
`nvidia-smi` succeeds before using `sim-nvidia`. If it still fails, check installed
packages/DKMS for the booted kernel; do not assume a Gazebo flag will fix it.
No reboot, module unload, package replacement, or graphics configuration change
was performed by this task. NVIDIA rendering remains unverified until the driver
mismatch is resolved. Sandboxed diagnostics may hide devices entirely, so run
these checks in the normal desktop terminal.

## GPU acceleration available immediately

Ogre 2 on the Intel Iris Xe GPU passed lidar and motion acceptance on the active
display. Use:

```bash
./scripts/rover sim
```

Ensure `LIBGL_ALWAYS_SOFTWARE` is unset in your shell. This uses the display's
normal GPU driver, not NVIDIA offload. To run only the server on this display:

```bash
./scripts/rover sim gui:=false teleop:=false rviz:=false headless_rendering:=false
```

Retain `DISPLAY`; disabling the GUI and disabling display-based rendering are
separate choices. Ogre 1 on Intel rendered but returned invalid constant-minimum
lidar scans, so it is not a validated sensor fallback. Use the previously tested
software Ogre 1 fallback only if the Ogre 2 hardware path fails:

```bash
LIBGL_ALWAYS_SOFTWARE=1 ./scripts/rover sim render_engine:=ogre
```
