#!/usr/bin/env python3
import rospy
import rosbag
import cv2
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import argparse

class ImageExtractor:
    def __init__(self, bag_file, image_topic, output_dir):
        self.bag_file = bag_file
        self.image_topic = image_topic
        self.output_dir = output_dir
        self.bridge = CvBridge()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def extract_images(self):
        """Extract all images from rosbag"""
        rospy.loginfo(f"Opening bag file: {self.bag_file}")
        image_count = 0
        
        try:
            with rosbag.Bag(self.bag_file, 'r') as bag:
                # Get bag info
                info = bag.get_type_and_topic_info()
                rospy.loginfo(f"Bag topics: {info.topics.keys()}")
                
                for topic, msg, t in bag.read_messages(topics=[self.image_topic]):
                    try:
                        # Convert ROS Image to OpenCV image
                        cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
                        
                        # Save image
                        timestamp = msg.header.stamp.to_nsec()
                        filename = f"frame_{timestamp}_{image_count:06d}.jpg"
                        filepath = os.path.join(self.output_dir, filename)
                        cv2.imwrite(filepath, cv_image)
                        
                        image_count += 1
                        
                        # Print progress every 100 images
                        if image_count % 100 == 0:
                            rospy.loginfo(f"Extracted {image_count} images")
                            
                    except Exception as e:
                        rospy.logwarn(f"Error processing image: {e}")
                        continue
                        
            rospy.loginfo(f"Successfully extracted {image_count} images")
            
            # Report image properties
            if image_count > 0:
                sample_image = cv2.imread(os.path.join(self.output_dir, 
                                          f"frame_{timestamp}_{image_count-1:06d}.jpg"))
                height, width, channels = sample_image.shape
                rospy.loginfo(f"Image properties: {width}x{height}, {channels} channels")
                
            return image_count
            
        except Exception as e:
            rospy.logerr(f"Failed to extract images: {e}")
            return 0

def main():
    parser = argparse.ArgumentParser(description='Extract images from rosbag')
    parser.add_argument('--bag', type=str, required=True, help='Path to rosbag file')
    parser.add_argument('--topic', type=str, default='/camera/image_raw', 
                       help='Image topic name')
    parser.add_argument('--output', type=str, default='./extracted_images',
                       help='Output directory')
    
    args = parser.parse_args()
    
    rospy.init_node('image_extractor', anonymous=True)
    extractor = ImageExtractor(args.bag, args.topic, args.output)
    extractor.extract_images()

if __name__ == '__main__':
    main()