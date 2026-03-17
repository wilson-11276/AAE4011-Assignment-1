# AAE4011 Assignment 1 — Q3: ROS-Based Vehicle Detection from Rosbag

> **Student Name:** [Wu Chun Him] | **Student ID:** [25016333D] | **Date:** [16-3-2026]

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
## Repository Structure
```text
vehicle_detection_ros/
├── src/
│   └── vehicle_detection/
│       ├── __init__.py
│       ├── scripts/
│       │   ├── extract_images.py
│       │   ├── vehicle_detector.py
│       │   └── detection_ui.py
│       ├── launch/
│       │   └── detection_pipeline.launch
│       ├── config/
│       │   └── detector_config.yaml
│       ├── CMakeLists.txt
│       └── package.xml
├── README.md
└── .gitignore
```
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
```
## Video
## Reflection

### (a) What Did You Learn?

ROS Integration with Deep Learning: Learned how to bridge ROS messages with PyTorch models using cv_bridge and create seamless image processing pipelines.

 Real-time Visualization: Developed skills in creating interactive UIs that display detection results in real-time while maintaining ROS communication.

### (b) How Did You Use AI Tools?

I used GitHub Copilot and ChatGPT to:

· Generate boilerplate code for ROS nodes
· Debug YOLOv5 integration issues
· Optimize image processing pipeline

Benefits: Faster development, learning best practices
Limitations: Sometimes generated code needed manual adjustment for ROS-specific features

### (c) How to Improve Accuracy?

Fine-tune on UAS Dataset: Train YOLOv5 on drone-captured vehicle images to adapt to aerial viewpoints

Implement Multi-scale Detection: Process images at multiple resolutions to detect vehicles at different altitudes

### (d) Real-World Challenges

Processing Speed: Limited onboard computing on drones requires model optimization (quantization, pruning)

Environmental Factors: Changing lighting conditions, weather, and motion blur affect detection reliability
