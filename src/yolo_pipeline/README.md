# Smart Robot ROS2 Pipeline (Jazzy) - Phase 2 (UI & Backend Implementation)

This project is an advanced real-time object detection and robot control pipeline with a dedicated Graphical User Interface (GUI) built using **PyQt6**.

## 🚀 Architecture Overview

The pipeline is split into three modular ROS2 nodes:

1. **Camera Publisher (`camera_publisher`)**:
    - Captures raw webcam feed.
    - Publishes to `/camera/image_raw`.

2. **YOLO Processor Backend (`yolo_processor`)**:
    - Listens for a **Target Class** from the UI.
    - Applies YOLOv8 to the raw feed, filtering only for that specific class.
    - Publishes the annotated AI feed to `/camera/yolo_output`.

3. **UI Controller Node (`ui_node`)**:
    - Built using **PyQt6**.
    - **Control Mode**: Displays a direct low-latency raw feed. Includes buttons for FWD, BACK, LEFT, RIGHT, and STOP. Commands are sent to `/cmd_vel`.
    - **YOLO Mode**: Displays the AI-annotated feed. Features a dropdown with **80 COCO Classes** (person, car, cat, etc.) for real-time tracking.

---

## 🛠️ Installation & Setup

### 1. System Dependencies

Ensure you have **ROS2 Jazzy** installed on Ubuntu 24.04.

### 2. Python Dependencies

Install the required libraries (including PyQt6 and the compatible NumPy version):

```bash
pip install ultralytics PyQt6 "numpy<2.0.0" "opencv-python<4.10.0" --break-system-packages
```

---

## 🏗️ Building the Workspace

```bash
cd ~/Documents/ros2/smart-robot
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select yolo_pipeline
```

---

## 🚦 How to Run

You need **three** separate terminals:

### Terminal 1: Camera

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run yolo_pipeline camera_publisher
```

### Terminal 2: AI Backend

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run yolo_pipeline yolo_processor
```

### Terminal 3: Graphical Interface (GUI)

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run yolo_pipeline ui_node
```

---

## 🗺️ UI Features

- **Main Menu**: Choose between YOLO Tracking and Manual Control.
- **YOLO Mode**: Use the dropdown to select one of 80 objects to track. The backend will switch detection on-the-fly.
- **Control Mode**: Visual drive mode with movement controls.
- **Latency Optimization**: Control mode uses the direct feed from Node 1 for minimal lag, while YOLO mode uses the processed feed from Node 2.
