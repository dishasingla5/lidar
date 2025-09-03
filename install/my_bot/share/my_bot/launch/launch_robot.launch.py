import os

from ament_index_python.packages import get_package_share_directory

from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='my_bot' #<--- CHANGE ME

    #world_description=os.path.join(get_package_share_directory('my_bot'), 'worlds', 'my_world.world')

    param_file_description=os.path.join(get_package_share_directory('my_bot'), 'config', 'mapper_params_online_async.yaml')

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false', 'use_ros2_control':'true'}.items()
    )

    # Include the Gazebo launch file, provided by the gazebo_ros package
  
    declare_params = DeclareLaunchArgument(
                                    name='params_file',
                                    default_value=param_file_description,
                                    description='param_file_description')


    robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])
    controller_params_file = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')


    controller_manager = Node(package='controller_manager', executable='ros2_control_node',
                        parameters=[{'robot_description':robot_description},controller_params_file],output='screen')

    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])


    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    diff_drive_spawner = Node(package='controller_manager', executable='spawner',
                        arguments=["diff_cont"],)

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )
    joint_broad_spawner = Node(package='controller_manager', executable='spawner',
                        arguments=["joint_broad"],)
    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
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

    static_tf_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link']
    )

    # Launch them all!
    return LaunchDescription([
        rsp,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
        static_tf_publisher
    ])