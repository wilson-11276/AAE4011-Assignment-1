#!/usr/bin/env python3
import rospy
import tkinter as tk
from tkinter import ttk, filedialog
import cv2
from PIL import Image, ImageTk
import threading
import json
import os
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import subprocess

class DetectionUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vehicle Detection System")
        self.root.geometry("1200x800")
        
        # Initialize ROS
        self.bridge = CvBridge()
        self.current_image = None
        
        # Variables
        self.rosbag_path = tk.StringVar()
        self.is_playing = False
        self.detection_stats = {
            'total_frames': 0,
            'vehicles_detected': 0,
            'car': 0, 'truck': 0, 'bus': 0, 'motorcycle': 0, 'bicycle': 0
        }
        
        # Setup UI
        self.setup_ui()
        
        # ROS subscribers
        rospy.Subscriber('/detected_objects/image', Image, self.image_callback)
        rospy.Subscriber('/detection_stats', String, self.stats_callback)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # ROS bag selection
        ttk.Label(control_frame, text="ROS Bag File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(control_frame, textvariable=self.rosbag_path, width=40).grid(row=1, column=0, pady=5)
        ttk.Button(control_frame, text="Browse", command=self.browse_rosbag).grid(row=1, column=1, padx=5)
        
        # Playback controls
        ttk.Label(control_frame, text="Playback Controls:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(10,5))
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.play_button = ttk.Button(button_frame, text="Play", command=self.toggle_playback)
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="Stop", command=self.stop_playback).pack(side=tk.LEFT, padx=2)
        
        # Statistics display
        stats_frame = ttk.LabelFrame(main_frame, text="Detection Statistics", padding="10")
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.stats_labels = {}
        row = 0
        for stat in ['total_frames', 'vehicles_detected', 'car', 'truck', 'bus', 'motorcycle', 'bicycle']:
            ttk.Label(stats_frame, text=f"{stat.replace('_', ' ').title()}:", 
                     font=('Arial', 9)).grid(row=row, column=0, sticky=tk.W, pady=2)
            self.stats_labels[stat] = ttk.Label(stats_frame, text="0", font=('Arial', 9, 'bold'))
            self.stats_labels[stat].grid(row=row, column=1, sticky=tk.W, padx=10)
            row += 1
        
        # Video display (right side)
        video_frame = ttk.LabelFrame(main_frame, text="Detection Output", padding="10")
        video_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.grid(row=0, column=0)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def browse_rosbag(self):
        """Browse for ROS bag file"""
        filename = filedialog.askopenfilename(
            title="Select ROS Bag File",
            filetypes=[("ROS bag files", "*.bag"), ("All files", "*.*")]
        )
        if filename:
            self.rosbag_path.set(filename)
            
    def toggle_playback(self):
        """Toggle playback of ROS bag"""
        if not self.is_playing:
            self.start_playback()
        else:
            self.stop_playback()
            
    def start_playback(self):
        """Start playing ROS bag"""
        if not self.rosbag_path.get():
            return
            
        self.is_playing = True
        self.play_button.config(text="Pause")
        
        # Launch ROS bag playback in separate thread
        thread = threading.Thread(target=self.play_rosbag)
        thread.daemon = True
        thread.start()
        
    def play_rosbag(self):
        """Play ROS bag using rosbag play"""
        try:
            cmd = f"rosbag play {self.rosbag_path.get()} --rate 1.0"
            subprocess.run(cmd, shell=True)
        except Exception as e:
            rospy.logerr(f"Error playing rosbag: {e}")
            
    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        self.play_button.config(text="Play")
        
    def image_callback(self, msg):
        """Handle incoming detection images"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            height, width = cv_image.shape[:2]
            new_width = 800
            new_height = int((new_width / width) * height)
            cv_image = cv2.resize(cv_image, (new_width, new_height))
            
            # Convert to PhotoImage
            image = Image.fromarray(cv_image)
            photo = ImageTk.PhotoImage(image=image)
            
            # Update display
            self.video_label.config(image=photo)
            self.video_label.image = photo
            
        except Exception as e:
            rospy.logerr(f"Error displaying image: {e}")
            
    def stats_callback(self, msg):
        """Update statistics display"""
        try:
            stats = json.loads(msg.data)
            for key, value in stats.items():
                if key in self.stats_labels:
                    current = int(self.stats_labels[key].cget("text"))
                    if isinstance(value, dict):
                        # Handle nested vehicle counts
                        for vehicle, count in value.items():
                            if vehicle in self.stats_labels:
                                self.stats_labels[vehicle].config(text=str(count))
                    else:
                        self.stats_labels[key].config(text=str(value))
        except Exception as e:
            rospy.logerr(f"Error updating stats: {e}")
            
    def run(self):
        """Run the UI"""
        self.root.mainloop()

def main():
    rospy.init_node('detection_ui', anonymous=True)
    ui = DetectionUI()
    ui.run()

if __name__ == '__main__':
    main()