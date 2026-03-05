import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class YOLOProcessor(Node):
    def __init__(self):
        super().__init__('yolo_processor')
        self.br = CvBridge()
        self.model = YOLO('yolov8n.pt')
        
        # Create a reverse mapping and normalize names
        self.name_to_id = {v.lower().strip(): k for k, v in self.model.names.items()}
        
        # Default target
        self.target_id = 0 # person
        self.target_class_name = "person"
        
        # Subscriptions
        self.raw_image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        
        self.target_class_sub = self.create_subscription(
            String, '/yolo/target_class', self.target_class_callback, 10)
        
        # Publisher
        self.yolo_output_pub = self.create_publisher(Image, '/camera/yolo_output', 10)
        
        self.get_logger().info('YOLO Processor Backend Started. Defaulting to: person')

    def target_class_callback(self, msg):
        requested_name = msg.data.lower().strip()
        if requested_name in self.name_to_id:
            self.target_id = self.name_to_id[requested_name]
            self.target_class_name = requested_name
            self.get_logger().info(f'Switching YOLO target to: {requested_name} (ID: {self.target_id})')
        else:
            self.get_logger().warn(f'Requested class "{requested_name}" not found in model names.')

    def image_callback(self, data):
        # Skip if no UI is watching
        if self.yolo_output_pub.get_subscription_count() == 0:
            return

        try:
            cv_image = self.br.imgmsg_to_cv2(data, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f'Failed to convert ROS Image: {e}')
            return

        # Perform Inference - SPECIFICALLY track only the target class
        # This is more efficient and handles name discrepancies correctly
        results = self.model(cv_image, verbose=False, classes=[self.target_id])
        
        # Draw results on frame
        # If there are detections, plot them. If not, results.plot() returns clean frame.
        annotated_frame = results[0].plot()

        # Convert back to ROS and publish
        try:
            output_msg = self.br.cv2_to_imgmsg(annotated_frame, encoding="bgr8")
            self.yolo_output_pub.publish(output_msg)
        except Exception as e:
            self.get_logger().error(f'Failed to publish YOLO output: {e}')

def main(args=None):
    rclpy.init(args=args)
    yolo_processor = YOLOProcessor()
    try:
        rclpy.spin(yolo_processor)
    except KeyboardInterrupt:
        pass
    finally:
        yolo_processor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
