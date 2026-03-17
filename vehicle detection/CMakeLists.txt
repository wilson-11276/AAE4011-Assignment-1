cmake_minimum_required(VERSION 3.0.2)
project(vehicle_detection)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  sensor_msgs
  cv_bridge
  image_transport
  message_generation
)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES vehicle_detection
  CATKIN_DEPENDS roscpp rospy std_msgs sensor_msgs cv_bridge
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)

# Install Python scripts
catkin_install_python(PROGRAMS
  scripts/extract_images.py
  scripts/vehicle_detector.py
  scripts/detection_ui.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# Install launch files
install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)

# Install config files
install(DIRECTORY config/
  DESTINATION ${CATIN_PACKAGE_SHARE_DESTINATION}/config
)
