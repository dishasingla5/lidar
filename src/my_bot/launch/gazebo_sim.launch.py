import os

from ament_index_python.packages import get_package_share_directory

from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='my_bot' #<--- CHANGE ME

    world_description=os.path.join(get_package_share_directory('my_bot'), 'worlds', 'my_world.world')

    param_file_description=os.path.join(get_package_share_directory('my_bot'), 'config', 'mapper_params_online_async.yaml')

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
                    launch_arguments={'world':LaunchConfiguration('world'),'gui': 'true'}.items()
                
             )
    
    declare_world_cmd = DeclareLaunchArgument(
                                    name='world',
                                    default_value=world_description,
                                    description='world_description')
    declare_params = DeclareLaunchArgument(
                                    name='params_file',
                                    default_value=param_file_description,
                                    description='param_file_description')

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_bot'],
                        output='screen')
    real = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','real.launch.py'
                )])
    )


    mapping_node = IncludeLaunchDescription(
                        PythonLaunchDescriptionSource([os.path.join(
                            get_package_share_directory(package_name),'launch','online_async_launch.py')]),
                                  launch_arguments={'params_file':LaunchConfiguration('params_file')}.items()

    )

    amcl_node = IncludeLaunchDescription(
                         PythonLaunchDescriptionSource([os.path.join(
                            get_package_share_directory(package_name),'launch','navigation_launch.py')]),
                                # launch_arguments={'params_file':'param_file_description'}.items()

    )
    real_nav = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','navigation_launch.py'
                )])
    )

    # Launch them all!
    return LaunchDescription([
        rsp,
        declare_world_cmd,
        declare_params,
        gazebo,
        spawn_entity,
         mapping_node,
         real,
        real_nav
    ])