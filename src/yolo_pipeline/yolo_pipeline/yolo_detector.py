import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
try:
    from ultralytics import YOLO
except ImportError:
    import subprocess
    import sys
    # Proactively installing missing dependencies for the user 
    print("ultralytics not found, trying to install it...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])
    from ultralytics import YOLO

class YOLODetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')
        # Subscribing to the 'camera/image_raw' topic
        self.subscription = self.create_subscription(
            Image,
            'camera/image_raw',
            self.listener_callback,
            10
        )
        self.br = CvBridge()
        # Loading YOLOv8 nano model for efficiency
        self.model = YOLO('yolov8n.pt')
        self.get_logger().info('YOLO Detector Node Started')

    def listener_callback(self, data):
        # Convert ROS Image to OpenCV Image
        try:
            cv_image = self.br.imgmsg_to_cv2(data, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f'Failed to convert ROS Image: {e}')
            return

        # Perform Inference
        results = self.model(cv_image, verbose=False)

        # Draw results on frame
        annotated_frame = results[0].plot()

        # Display the result
        cv2.imshow("YOLOv8 Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass

def main(args=None):
    rclpy.init(args=args)
    yolo_detector = YOLODetector()
    try:
        rclpy.spin(yolo_detector)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        yolo_detector.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
