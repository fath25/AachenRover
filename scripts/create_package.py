#!/usr/bin/env python3
"""Generate a ROS 2 package with repository integration, without requiring ROS."""
import argparse
import keyword
from pathlib import Path
import re
from string import Template
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Path(__file__).resolve().parent / 'templates/package'


def identifier(value):
    if not re.fullmatch(r'[a-z][a-z0-9_]*', value) or keyword.iskeyword(value):
        raise argparse.ArgumentTypeError('Use a lowercase identifier starting with a letter (not a Python keyword).')
    return value


def create_package(name, language='python', kind='node', node_name='worker',
                   destination=None, dependencies=()):
    for value in (name, node_name, *dependencies):
        identifier(value)
    if language not in {'python', 'cpp'} or kind not in {'node', 'camera'}:
        raise ValueError('Unsupported language or template')
    destination = Path(destination) if destination else ROOT / 'software/ros2_ws/src'
    target = destination / name
    if target.exists() or target.is_symlink():
        raise FileExistsError(f'Refusing to overwrite {target}')
    camera = kind == 'camera'
    client = 'rclpy' if language == 'python' else 'rclcpp'
    deps = sorted(set([client, *dependencies, *(['sensor_msgs'] if camera else [])]))
    values = dict(package=name, node=node_name, namespace='front_camera' if camera else name,
                  build_type='ament_python' if language == 'python' else 'ament_cmake',
                  buildtool='' if language == 'python' else '  <buildtool_depend>ament_cmake</buildtool_depend>',
                  dependencies='\n'.join(f'  <depend>{escape(dep)}</depend>' for dep in deps),
                  runtime_dependencies='\n'.join(f'  <exec_depend>{dep}</exec_depend>'
                                                 for dep in ['launch_ros', 'ament_index_python'] if dep not in deps),
                  cmake_find='\n'.join(f'find_package({dep} REQUIRED)' for dep in deps),
                  cmake_deps=' '.join(deps),
                  source=f'{name}/{node_name}.py' if language == 'python' else f'src/{node_name}.cpp',
                  camera_config='    device: ""\n    frame_id: "camera_optical_frame"\n' if camera else '')
    files = {}
    for source, output in [('package.xml.tmpl', 'package.xml'),
                           ('launch.py.tmpl', f'launch/{node_name}.launch.py'),
                           ('params.yaml.tmpl', 'config/params.yaml'), ('README.md.tmpl', 'README.md')]:
        files[output] = Template((TEMPLATES / source).read_text()).substitute(values)
    if language == 'python':
        mappings = [('setup.py.tmpl', 'setup.py'), ('setup.cfg.tmpl', 'setup.cfg'),
                    (f'{kind}.py.tmpl', values['source'])]
        files[f'{name}/__init__.py'] = ''
        files[f'resource/{name}'] = ''
    else:
        mappings = [('CMakeLists.txt.tmpl', 'CMakeLists.txt'),
                    (f'{kind}.cpp.tmpl', values['source'])]
    for source, output in mappings:
        files[output] = Template((TEMPLATES / source).read_text()).substitute(values)
    files['LICENSE'] = (ROOT / 'LICENSE').read_text()
    if camera:
        files['README.md'] += (TEMPLATES / 'camera_notes.md').read_text()
    # Resolve all templates before touching the destination. Never merge/overwrite.
    target.mkdir(parents=True, exist_ok=False)
    for relative, content in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', type=identifier, help='ROS package name, e.g. rover_camera')
    parser.add_argument('--language', choices=['python', 'cpp'], default='python')
    parser.add_argument('--template', choices=['node', 'camera'], default='node')
    parser.add_argument('--node-name', type=identifier, default='worker')
    parser.add_argument('--dependency', action='append', type=identifier, default=[],
                        help='Additional ROS dependency; repeat as needed')
    parser.add_argument('--destination', type=Path, help='Override the default workspace src directory')
    args = parser.parse_args()
    try:
        path = create_package(args.name, args.language, args.template, args.node_name,
                              args.destination, args.dependency)
    except (ValueError, OSError, argparse.ArgumentTypeError) as error:
        parser.exit(1, f'{error}\n')
    print(f'Created {path}\nImplement the worker in the source file listed in its README.')
    print(f'Build: ./scripts/rover build\nLaunch: ./scripts/rover launch {args.name} {args.node_name}.launch.py')
    if args.destination:
        print('Custom destination: build/source that workspace instead of the repository workspace.')


if __name__ == '__main__':
    main()
