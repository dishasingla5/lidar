import os

from ament_index_python.packages import get_package_share_directory

from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def generate_launch_description():

    package_name = 'my_bot'
    param_file_description=os.path.join(get_package_share_directory('my_bot'), 'config', 'mapper_params_online_async.yaml')
    declare_params = DeclareLaunchArgument(
                                    name='params_file',
                                    default_value=param_file_description,
                                    description='param_file_description')

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
   
    # real = IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource([os.path.join(
    #                 get_package_share_directory(package_name),'launch','real.launch.py'
    #             )])
    # )


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
       
        
        declare_params,
        mapping_node
        #real,
        
        #real_nav

    ])