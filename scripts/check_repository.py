#!/usr/bin/env python3
"""Dependency-light structural checks for the portable harness and assets."""
import ast
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

root = Path(__file__).resolve().parents[1]
for name in ['AGENTS.md', 'CLAUDE.md', 'QWEN.md', 'GEMINI.md', 'README.md']:
    assert (root / name).is_file(), f'Missing {name}'
for adapter in ['.agents/skills', '.claude/skills']:
    assert (root / adapter).resolve() == root / 'skills', f'Broken {adapter}'
for skill in (root / 'skills').glob('*/SKILL.md'):
    metadata = yaml.safe_load(skill.read_text().split('---', 2)[1])
    assert metadata['name'] == skill.parent.name
    assert isinstance(metadata['description'], str) and metadata['description']
package = root / 'software/ros2_ws/src/aachen_rover'
for path in package.rglob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
for pattern in ['*.xml', '*.xacro', '*.sdf']:
    for path in package.rglob(pattern):
        ET.parse(path)
bridges = yaml.safe_load((package / 'config/bridge.yaml').read_text())
assert len({b['ros_topic_name'] for b in bridges}) == len(bridges)
assert all(b['direction'] in {'ROS_TO_GZ', 'GZ_TO_ROS'} for b in bridges)
print('PASS: harness discovery, skill metadata, Python/XML syntax, bridge structure')
