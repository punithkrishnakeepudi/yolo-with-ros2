import sys
import threading
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, QStackedWidget)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

# 80 COCO NAMES
COCO_NAMES = [
    'person', 'bicycle', 'car', 'motorbike', 'aeroplane', 'bus', 'train', 'truck', 'boat', 
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 
    'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 
    'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 
    'chair', 'sofa', 'pottedplant', 'bed', 'diningtable', 'toilet', 'tvmonitor', 'laptop', 
    'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

class ROSListener(Node):
    # This signal carries the decoded image to the main GUI thread
    image_received = pyqtSignal(QImage)

    def __init__(self, pyqt_app_node):
        super().__init__('ui_ros_node')
        self.pyqt_app_node = pyqt_app_node
        self.br = CvBridge()
        
        # Subscriptions
        self.raw_sub = self.create_subscription(
            Image, '/camera/image_raw', self.raw_callback, 10
        )
        self.yolo_sub = self.create_subscription(
            Image, '/camera/yolo_output', self.yolo_callback, 10
        )
        
        # Publishers
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.target_pub = self.create_publisher(String, '/yolo/target_class', 10)

    def raw_callback(self, data):
        if self.pyqt_app_node.mode == "CONTROL":
            self.process_and_emit(data)

    def yolo_callback(self, data):
        if self.pyqt_app_node.mode == "YOLO":
            self.process_and_emit(data)

    def process_and_emit(self, data):
        try:
            cv_img = self.br.imgmsg_to_cv2(data, desired_encoding="bgr8")
            rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, c = rgb_img.shape
            bytes_per_line = c * w
            qt_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            # Emit signal to update UI
            self.pyqt_app_node.update_image_signal.emit(qt_img)
        except Exception as e:
            print(f"Error processing image: {e}")

    def send_command(self, linear_x, angular_z):
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        self.cmd_pub.publish(msg)

    def send_target_class(self, class_name):
        msg = String()
        msg.data = class_name
        self.target_pub.publish(msg)

class SmartRobotUI(QMainWindow):
    update_image_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Robot Controller - ROS2 Jazzy")
        self.setMinimumSize(800, 700)
        
        self.mode = "MENU" # MENU, YOLO, CONTROL
        
        # Initialize ROS before setting up views
        rclpy.init()
        self.ros_node = ROSListener(self)
        self.thread = threading.Thread(target=rclpy.spin, args=(self.ros_node,), daemon=True)
        self.thread.start()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Setup Views
        self.setup_menu_view()
        self.setup_control_view()
        self.setup_yolo_view()

        # Connect signals
        self.update_image_signal.connect(self.display_image)

    def setup_menu_view(self):
        self.menu_widget = QWidget()
        layout = QVBoxLayout()
        title = QLabel("<h2>Smart Robot Dashboard</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        yolo_btn = QPushButton("YOLO Mode")
        yolo_btn.setFixedHeight(60)
        yolo_btn.clicked.connect(lambda: self.switch_mode("YOLO"))
        
        control_btn = QPushButton("Control Mode")
        control_btn.setFixedHeight(60)
        control_btn.clicked.connect(lambda: self.switch_mode("CONTROL"))
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(yolo_btn)
        layout.addWidget(control_btn)
        layout.addStretch()
        
        self.menu_widget.setLayout(layout)
        self.stack.addWidget(self.menu_widget)

    def setup_control_view(self):
        self.control_widget = QWidget()
        layout = QVBoxLayout()
        
        self.ctrl_video_label = QLabel("Waiting for Camera Feed...")
        self.ctrl_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ctrl_video_label.setMinimumSize(640, 480)
        self.ctrl_video_label.setStyleSheet("background-color: black; color: white;")
        
        btn_layout = QHBoxLayout()
        fwd_btn = QPushButton("FWD")
        back_btn = QPushButton("BACK")
        left_btn = QPushButton("LEFT")
        right_btn = QPushButton("RIGHT")
        stop_btn = QPushButton("STOP")
        stop_btn.setStyleSheet("background-color: red; color: white;")
        
        fwd_btn.clicked.connect(lambda: self.ros_node.send_command(0.5, 0.0))
        back_btn.clicked.connect(lambda: self.ros_node.send_command(-0.5, 0.0))
        left_btn.clicked.connect(lambda: self.ros_node.send_command(0.0, 0.5))
        right_btn.clicked.connect(lambda: self.ros_node.send_command(0.0, -0.5))
        stop_btn.clicked.connect(lambda: self.ros_node.send_command(0.0, 0.0))

        btn_layout.addWidget(left_btn)
        btn_layout.addWidget(fwd_btn)
        btn_layout.addWidget(stop_btn)
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(right_btn)

        back_to_menu = QPushButton("Back to Main Menu")
        back_to_menu.clicked.connect(lambda: self.switch_mode("MENU"))
        
        layout.addWidget(self.ctrl_video_label)
        layout.addLayout(btn_layout)
        layout.addWidget(back_to_menu)
        
        self.control_widget.setLayout(layout)
        self.stack.addWidget(self.control_widget)

    def setup_yolo_view(self):
        self.yolo_widget = QWidget()
        layout = QVBoxLayout()
        
        self.yolo_video_label = QLabel("Waiting for YOLO Feed...")
        self.yolo_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.yolo_video_label.setMinimumSize(640, 480)
        self.yolo_video_label.setStyleSheet("background-color: black; color: white;")
        
        settings_layout = QHBoxLayout()
        label = QLabel("Track Class:")
        self.class_dropdown = QComboBox()
        self.class_dropdown.addItems(COCO_NAMES)
        self.class_dropdown.currentTextChanged.connect(self.ros_node.send_target_class)
        
        settings_layout.addWidget(label)
        settings_layout.addWidget(self.class_dropdown)
        
        stop_btn = QPushButton("STOP ROBOT")
        stop_btn.setStyleSheet("background-color: red; color: white;")
        stop_btn.clicked.connect(lambda: self.ros_node.send_command(0.0, 0.0))
        
        back_to_menu = QPushButton("Back to Main Menu")
        back_to_menu.clicked.connect(lambda: self.switch_mode("MENU"))
        
        layout.addWidget(self.yolo_video_label)
        layout.addLayout(settings_layout)
        layout.addWidget(stop_btn)
        layout.addWidget(back_to_menu)
        
        self.yolo_widget.setLayout(layout)
        self.stack.addWidget(self.yolo_widget)

    def switch_mode(self, mode):
        self.mode = mode
        if mode == "MENU":
            self.stack.setCurrentIndex(0)
        elif mode == "CONTROL":
            self.stack.setCurrentIndex(1)
        elif mode == "YOLO":
            self.stack.setCurrentIndex(2)
            # Default to current selection
            self.ros_node.send_target_class(self.class_dropdown.currentText())

    @pyqtSlot(QImage)
    def display_image(self, qt_img):
        pixmap = QPixmap.fromImage(qt_img)
        if self.mode == "CONTROL":
            self.ctrl_video_label.setPixmap(pixmap.scaled(self.ctrl_video_label.size(), 
                                           Qt.AspectRatioMode.KeepAspectRatio))
        elif self.mode == "YOLO":
            self.yolo_video_label.setPixmap(pixmap.scaled(self.yolo_video_label.size(), 
                                           Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        rclpy.shutdown()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = SmartRobotUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
