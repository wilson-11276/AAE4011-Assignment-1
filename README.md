# Vehicle Detection ROS Package

## Overview
This ROS package implements a real-time vehicle detection system using YOLOv5 deep learning model. It processes images from a ROS bag file, detects vehicles (cars, trucks, buses, motorcycles), and displays results with a user-friendly GUI.

## Method Description
### Detection Architecture
- **Model**: YOLOv5s (You Only Look Once version 5 small)
- **Why YOLOv5?**
  - Real-time performance suitable for UAS applications
  - Good balance between accuracy and speed
  - Pre-trained on COCO dataset with vehicle classes
  - Easy integration with ROS and Python

### Pipeline Components
1. **Image Extraction**: Extracts frames from ROS bag
2. **Vehicle Detection**: YOLOv5 processes each frame
3. **Visualization**: Bounding boxes with class labels
4. **Statistics**: Real-time detection counting
5. **GUI**: Tkinter-based interface for playback control

## Requirements
- Ubuntu 20.04 / 22.04
- ROS Noetic / Melodic
- Python 3.8+
- PyTorch
- OpenCV
- YOLOv5

## Installation
```bash
# Create catkin workspace
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src

# Clone repository
git clone https://github.com/YOUR_USERNAME/vehicle_detection_ros.git

# Install dependencies
cd ~/catkin_ws
rosdep install --from-paths src --ignore-src -r -y

# Build package
catkin_make
source devel/setup.bash
