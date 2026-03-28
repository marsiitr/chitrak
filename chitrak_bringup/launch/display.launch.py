from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
import os


def generate_launch_description():

    # Path to URDF file
    pkg_path = FindPackageShare("chitrak_description").find("chitrak_description")
    urdf_path = os.path.join(pkg_path, "urdf", "chitrak.urdf")

    # Path to RViz config
    bringup_pkg_path = FindPackageShare("chitrak_bringup").find("chitrak_bringup")
    rviz_config_path = os.path.join(bringup_pkg_path, "config", "display.rviz")

    with open(urdf_path, 'r') as f:
        robot_description_content = f.read()

    robot_description = {"robot_description": robot_description_content}

    # Robot State Publisher
    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description]
    )

    # Joint State Publisher (GUI for sliders)
    jsp_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui"
    )

    # RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", rviz_config_path]
    )

    return LaunchDescription([
        rsp_node,
        jsp_node,
        rviz_node
    ])