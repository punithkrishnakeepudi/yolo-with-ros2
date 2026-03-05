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
        
        # Default target class
        self.target_class_name = "person"
        
        # ROS2 Subscriptions
        self.raw_image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        
        self.target_class_sub = self.create_subscription(
            String, '/yolo/target_class', self.target_class_callback, 10)
        
        # ROS2 Publisher
        self.yolo_output_pub = self.create_publisher(Image, '/camera/yolo_output', 10)
        
        # Initialization
        self.br = CvBridge()
        self.model = YOLO('yolov8n.pt')
        self.get_logger().info('YOLO Processor (Backend) Node Started')

    def target_class_callback(self, msg):
        self.target_class_name = msg.data.lower()
        self.get_logger().info(f'Switching YOLO target class to: {self.target_class_name}')

    def image_callback(self, data):
        # Only process if we have a subscriber to the output
        if self.yolo_output_pub.get_subscription_count() == 0:
            return

        try:
            cv_image = self.br.imgmsg_to_cv2(data, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f'Failed to convert ROS Image: {e}')
            return

        # Perform Inference
        results = self.model(cv_image, verbose=False)
        
        # If target class is set, search for it
        annotated_frame = cv_image.copy()
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class ID
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                
                # Check if it matches the target class
                if label.lower() == self.target_class_name:
                    # Draw only target bounding boxes
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, f'{label} {conf:.2f}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert back to ROS message and publish
        output_msg = self.br.cv2_to_imgmsg(annotated_frame, encoding="bgr8")
        self.yolo_output_pub.publish(output_msg)

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
