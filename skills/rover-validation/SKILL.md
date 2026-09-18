---
name: rover-validation
description: Review or validate AachenRover changes using repository checks, ROS package tests, and live simulation acceptance criteria.
---

Inspect the diff and choose checks based on the behavior changed. Use
`./scripts/rover check` for repository structure and control policy tests,
`build` and `test` for installed ROS packaging, and the live `smoke` procedure in
`docs/simulation.md` for motion, lidar, and TF changes. Read the smoke assertions
before interpreting a pass; wheel odometry alone does not prove ground truth
motion or physically accurate steering.

Prioritize incorrect frame ownership, stale velocity commands, missing install
rules, bridge type/direction errors, and inaccurate hardware claims. Keep
review findings actionable with file locations. Report tests that ran, failures,
and untested paths. Do not call a provider supported merely because an adapter
file exists; distinguish portable context from native discovery verification.
