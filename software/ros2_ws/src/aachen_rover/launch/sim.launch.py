"""Launch the simulation and optional desktop controls."""
from pathlib import Path
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def setup(context):
    share = Path(get_package_share_directory('aachen_rover'))
    value = lambda key: LaunchConfiguration(key).perform(context)
    description = xacro.process_file(str(share / 'urdf/rover.urdf.xacro')).toxml()
    command = ['gz', 'sim', '-r', str(share / 'worlds/mars_yard.sdf'),
               '--render-engine', value('render_engine')]
    if value('gui') == 'false':
        command += ['-s']
        if value('render_engine') == 'ogre2' and value('headless_rendering') == 'true':
            command += ['--headless-rendering']
    nodes = [
        ExecuteProcess(cmd=command, output='screen', on_exit=Shutdown(reason='Gazebo exited')),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': description, 'use_sim_time': True}]),
        Node(package='ros_gz_sim', executable='create',
             arguments=['-world', 'mars_yard', '-name', 'aachen_rover',
                        '-topic', '/robot_description', '-z', '0.28'], output='screen'),
        Node(package='ros_gz_bridge', executable='parameter_bridge',
             parameters=[{'config_file': str(share / 'config/bridge.yaml'), 'use_sim_time': True}],
             on_exit=Shutdown(reason='Simulation bridge exited')),
        Node(package='aachen_rover', executable='velocity_guard.py', output='screen',
             on_exit=Shutdown(reason='Velocity guard exited')),
    ]
    if value('teleop') == 'true':
        nodes.append(Node(package='aachen_rover', executable='teleop_gui.py', output='screen'))
    if value('rviz') == 'true':
        nodes.append(Node(package='rviz2', executable='rviz2',
                          arguments=['-d', str(share / 'config/rover.rviz')],
                          parameters=[{'use_sim_time': True}]))
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('render_engine', default_value='ogre2', choices=['ogre2', 'ogre']),
        DeclareLaunchArgument('headless_rendering', default_value='true', choices=['true', 'false'],
                              description='Use EGL for server-only Ogre 2; false uses the X11 display'),
        DeclareLaunchArgument('gui', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument('teleop', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument('rviz', default_value='true', choices=['true', 'false']),
        OpaqueFunction(function=setup),
    ])
