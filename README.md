# Smart Robot ROS2 Pipeline (Jazzy)

This project implements a real-time object detection pipeline for a robot using **ROS2 Jazzy**, **OpenCV**, and **YOLOv8**. It is split into two modular nodes to demonstrate the power of ROS2 messaging.

## 🚀 Overview

The pipeline consists of:

1. **Camera Publisher (`camera_publisher`)**:
    - Captures frames from the system webcam using OpenCV.
    - Converts OpenCV images to ROS2 Image messages (`sensor_msgs/Image`).
    - Publishes them to the `/camera/image_raw` topic.
2. **YOLO Detector (`yolo_detector`)**:
    - Subscribes to the `/camera/image_raw` topic.
    - Processes each incoming frame through the **YOLOv8 nano** model.
    - Annotates the frame with detection boxes and labels.
    - Displays the output in a real-time window.

---

## 🛠️ Installation & Setup

### 1. System Dependencies

Ensure you have **ROS2 Jazzy** installed on your Ubuntu 24.04 system. You will also need `colcon` to build the workspace.

### 2. Python Dependencies

The project requires `ultralytics` for YOLOv8 and `opencv-python`. Since Ubuntu 24.04 (Jazzy's base) uses a managed environment, run the following command to install them:

```bash
pip install ultralytics "numpy<2.0.0" "opencv-python<4.10.0" --break-system-packages
```

> **Note**: We specifically use `numpy<2.0.0` to maintain compatibility with ROS2 Jazzy's pre-compiled libraries.

---

## 🏗️ Building the Workspace

Clone the repository and build the package:

```bash
# Navigate to your workspace
cd ~/Documents/ros2/smart-robot

# Build the package
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select yolo_pipeline
```

---

## 🚦 How to Run

To run the pipeline, you need to open two separate terminals.

### Terminal 1: Camera Feed

Starts the webcam capture and begins broadcasting the video stream over the ROS2 network.

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run yolo_pipeline camera_publisher
```

### Terminal 2: AI Detection

Starts the subcriber node which applies YOLOv8 to the incoming stream.

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run yolo_pipeline yolo_detector
```

*On the first run, it will automatically download the `yolov8n.pt` model weights.*

---

## 📂 Project Structure

- `yolo_pipeline/camera_publisher.py`: Node logic for image acquisition.
- `yolo_pipeline/yolo_detector.py`: Node logic for AI inference and visualization.
- `setup.py`: Defines entry points and package metadata.
- `package.xml`: Management of ROS2 dependencies (rclpy, sensor_msgs, etc.).

---

## 📝 Tips

- Press **'q'** in the YOLO detection window to stop the display (the node will continue running).
- Use `ros2 topic hz /camera/image_raw` in a third terminal to check the frequency of your video stream!
