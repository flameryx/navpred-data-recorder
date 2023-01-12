cmake_minimum_required(VERSION 3.0.2)
project(navpred-data-recorder)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  nav_msgs
  roscpp
  rospy
  sensor_msgs
  std_msgs
)

# catkin_python_setup()

catkin_package()
include_directories(${catkin_INCLUDE_DIRS})


catkin_install_python(PROGRAMS
  task-generator/scripts/task_generator_node.py

  task-generator/scripts/scenario_helper.py

  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)