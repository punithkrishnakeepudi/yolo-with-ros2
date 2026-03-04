# YOLO Pipeline ROS2 (Jazzy)

This package implements a simple two-node ROS2 pipeline:

1.  **Camera Publisher**: Captures frames from the webcam and publishes them to `/camera/image_raw` as `sensor_msgs/Image`.
2.  **YOLO Detector**: Subscribes to `/camera/image_raw`, processes each frame with YOLOv8 for object detection, and displays the annotated output.

## Prerequisites

Ensure you have ROS2 Jazzy installed. You may also need to install dependencies:

```bash
pip install ultralytics opencv-python --break-system-packages
```

## Build

From the workspace root:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select yolo_pipeline
```

## Run

### 1. Start the Camera Publisher
Open a new terminal:
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run yolo_pipeline camera_publisher
```

### 2. Start the YOLO Detector
Open a second terminal:
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run yolo_pipeline yolo_detector
```

**Note**: On first run, the detector will automatically download the YOLOv8 nano model (`yolov8n.pt`).
