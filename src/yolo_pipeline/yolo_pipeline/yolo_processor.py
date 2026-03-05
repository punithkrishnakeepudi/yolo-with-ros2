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
        
        # Internal model names mapping (normalized: no spaces, lowercase)
        model_names = {v.lower().replace(" ", ""): k for k, v in self.model.names.items()}
        
        # Manual overrides for discrepancies between user list and YOLOv8 labels
        self.manual_mapping = {
            'motorbike': 3,     # motorcycle
            'motorcycle': 3,
            'aeroplane': 4,     # airplane
            'airplane': 4,
            'sofa': 57,         # couch
            'couch': 57,
            'pottedplant': 58,  # potted plant
            'potted plant': 58,
            'diningtable': 60,  # dining table
            'dining table': 60,
            'tvmonitor': 62,    # tv
            'tv': 62
        }
        
        # Prepare final mapping: check manual first, then fallback to model_names
        self.name_to_id = {}
        all_possible_names = list(model_names.keys()) + list(self.manual_mapping.keys())
        
        for name in all_possible_names:
            if name in self.manual_mapping:
                self.name_to_id[name] = self.manual_mapping[name]
            elif name in model_names:
                self.name_to_id[name] = model_names[name]

        # Default target
        self.target_id = 0  # person
        
        # Subscriptions
        self.raw_image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        
        self.target_class_sub = self.create_subscription(
            String, '/yolo/target_class', self.target_class_callback, 10)
        
        # Publisher
        self.yolo_output_pub = self.create_publisher(Image, '/camera/yolo_output', 10)
        
        self.get_logger().info('YOLO Processor Backend Started. Enhanced for 80 COCO classes.')

    def target_class_callback(self, msg):
        requested_name = msg.data.lower().strip().replace(" ", "")
        if requested_name in self.name_to_id:
            self.target_id = self.name_to_id[requested_name]
            self.get_logger().info(f'Switching YOLO target to: {msg.data} (ID: {self.target_id})')
        else:
            # Fallback: try to see if any model name contains the requested string
            found = False
            for m_id, m_name in self.model.names.items():
                if requested_name in m_name.lower().replace(" ", ""):
                    self.target_id = m_id
                    self.get_logger().info(f'Fuzzy match: {msg.data} -> {m_name} (ID: {self.target_id})')
                    found = True
                    break
            if not found:
                self.get_logger().warn(f'Requested class "{msg.data}" not found in mapping.')

    def image_callback(self, data):
        try:
            cv_image = self.br.imgmsg_to_cv2(data, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f'Failed to convert ROS Image: {e}')
            return

        # Perform Inference - filter by the specific target_id
        results = self.model(cv_image, verbose=False, classes=[self.target_id])
        
        # Draw results
        annotated_frame = results[0].plot()

        # Publish
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
        try:
            rclpy.shutdown()
        except Exception:
            pass

if __name__ == '__main__':
    main()
