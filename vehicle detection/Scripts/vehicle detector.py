#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
import torch
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String
import json
import yaml
import os

class VehicleDetector:
    def __init__(self):
        rospy.init_node('vehicle_detector', anonymous=True)
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize YOLOv5 model
        self.model = self.load_model()
        
        # Initialize bridge
        self.bridge = CvBridge()
        
        # Publishers and Subscribers
        self.image_pub = rospy.Publisher('/detected_objects/image', 
                                        Image, queue_size=10)
        self.stats_pub = rospy.Publisher('/detection_stats', 
                                        String, queue_size=10)
        
        self.image_sub = rospy.Subscriber('/camera/image_raw', 
                                         Image, self.image_callback)
        
        # Detection statistics
        self.total_detections = 0
        self.vehicle_counts = {
            'car': 0, 'truck': 0, 'bus': 0, 'motorcycle': 0, 'bicycle': 0
        }
        
        rospy.loginfo("Vehicle Detector initialized")
        
    def load_config(self):
        """Load configuration from YAML file"""
        config_path = rospy.get_param('~config_path', 
                                     'config/detector_config.yaml')
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            rospy.logwarn("Using default configuration")
            return {
                'model': 'yolov5s',
                'confidence_threshold': 0.5,
                'vehicle_classes': [2, 3, 5, 7],  # COCO classes: car, truck, bus, train
                'input_size': 640
            }
    
    def load_model(self):
        """Load YOLOv5 model"""
        model_name = self.config.get('model', 'yolov5s')
        try:
            model = torch.hub.load('ultralytics/yolov5', model_name, 
                                  pretrained=True)
            model.conf = self.config.get('confidence_threshold', 0.5)
            model.classes = self.config.get('vehicle_classes', [2, 3, 5, 7])
            return model
        except Exception as e:
            rospy.logerr(f"Failed to load model: {e}")
            return None
    
    def image_callback(self, msg):
        """Process incoming images"""
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Perform detection
            results = self.model(cv_image)
            
            # Get detection results
            detections = results.pandas().xyxy[0]
            
            # Update statistics
            if len(detections) > 0:
                vehicle_objects = detections[detections['class'].isin(
                    self.config.get('vehicle_classes', []))]
                
                for _, obj in vehicle_objects.iterrows():
                    class_name = obj['name']
                    if class_name in self.vehicle_counts:
                        self.vehicle_counts[class_name] += 1
                    self.total_detections += 1
            
            # Render detections on image
            rendered_image = results.render()[0]
            
            # Add statistics overlay
            rendered_image = self.add_stats_overlay(rendered_image)
            
            # Publish processed image
            ros_image = self.bridge.cv2_to_imgmsg(rendered_image, "bgr8")
            ros_image.header = msg.header
            self.image_pub.publish(ros_image)
            
            # Publish statistics
            stats = {
                'timestamp': msg.header.stamp.to_nsec(),
                'total_vehicles': len(detections[detections['class'].isin(
                    self.config.get('vehicle_classes', []))]),
                'vehicle_types': self.vehicle_counts.copy(),
                'confidence_scores': detections['confidence'].tolist() if len(detections) > 0 else []
            }
            self.stats_pub.publish(json.dumps(stats))
            
        except Exception as e:
            rospy.logerr(f"Error in image callback: {e}")
    
    def add_stats_overlay(self, image):
        """Add detection statistics overlay to image"""
        height, width = image.shape[:2]
        
        # Create semi-transparent overlay
        overlay = image.copy()
        cv2.rectangle(overlay, (10, 10), (300, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)
        
        # Add text
        y_pos = 35
        cv2.putText(image, f"Detections: {self.total_detections}", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        for i, (vehicle, count) in enumerate(self.vehicle_counts.items()):
            y_pos = 60 + i*25
            cv2.putText(image, f"{vehicle}: {count}", 
                       (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return image
    
    def run(self):
        """Main run loop"""
        rospy.spin()

def main():
    try:
        detector = VehicleDetector()
        detector.run()
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    main()