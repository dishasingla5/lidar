import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
import time
import xacro


def generate_launch_description():

    
    diff_drive_spawner = Node(package='controller_manager', executable='spawner',
                        arguments=["diff_cont"],)

    time.sleep(3)
    joint_broad_spawner = Node(package='controller_manager', executable='spawner',
                        arguments=["joint_broad"],)
    

    return LaunchDescription([
        diff_drive_spawner,
        joint_broad_spawner
    ])