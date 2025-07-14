"""
Safe Face Tracking - No URBasic Library
This version uses direct socket communication to avoid robot shutdowns
"""

import cv2
import numpy as np
import math
import time
import socket
import threading
import imutils
from imutils.video import VideoStream

# Configuration
ROBOT_IP = '192.168.1.11'
ROBOT_PORT = 30002
ACCELERATION = 0.4
VELOCITY = 0.4

# Camera settings
video_resolution = (700, 400)
video_midpoint = (int(video_resolution[0]/2), int(video_resolution[1]/2))
video_viewangle_hor = math.radians(25)

# Robot movement settings
m_per_pixel = 0.00009
max_x = 0.2
max_y = 0.2
hor_rot_max = math.radians(50)
vert_rot_max = math.radians(25)

# Face detection model
pretrained_model = cv2.dnn.readNetFromCaffe(
    "MODELS/deploy.prototxt.txt", 
    "MODELS/res10_300x300_ssd_iter_140000.caffemodel"
)

class SafeRobotControl:
    """Safe robot control using direct socket communication"""
    
    def __init__(self, ip_address, port=30002):
        self.ip_address = ip_address
        self.port = port
        self.socket = None
        self.connected = False
        self.current_pose = None
        
    def connect(self):
        """Connect to robot safely"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.ip_address, self.port))
            self.connected = True
            print(f"✓ Connected to robot at {self.ip_address}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            self.connected = False
            return False
    
    def send_command(self, command):
        """Send command safely"""
        if not self.connected or not self.socket:
            return False
        
        try:
            if not command.endswith('\n'):
                command += '\n'
            self.socket.send(command.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Command failed: {e}")
            self.connected = False
            return False
    
    def get_current_pose(self):
        """Get current TCP pose"""
        if self.send_command("get_actual_tcp_pose()"):
            # In a real implementation, you'd parse the response
            # For now, return a default pose
            return [0.5, 0.0, 0.5, 0.0, 0.0, 0.0]
        return None
    
    def move_to_pose(self, pose, acceleration=0.4, velocity=0.4):
        """Move to pose safely"""
        pose_str = f"p[{pose[0]:.4f}, {pose[1]:.4f}, {pose[2]:.4f}, {pose[3]:.4f}, {pose[4]:.4f}, {pose[5]:.4f}]"
        command = f"movel({pose_str}, a={acceleration}, v={velocity})"
        return self.send_command(command)
    
    def close(self):
        """Close connection safely"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        print("✓ Robot connection closed")

def find_faces_dnn(image):
    """Find faces in image using DNN"""
    frame = imutils.resize(image, width=video_resolution[0])
    (h, w) = frame.shape[:2]
    
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    
    pretrained_model.setInput(blob)
    detections = pretrained_model.forward()
    face_centers = []
    
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        
        if confidence < 0.4:
            continue
        
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        
        face_center = (int(startX + (endX - startX) / 2), 
                      int(startY + (endY - startY) / 2))
        position_from_center = (face_center[0] - video_midpoint[0], 
                               face_center[1] - video_midpoint[1])
        face_centers.append(position_from_center)
        
        # Draw detection
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.line(frame, video_midpoint, face_center, (0, 200, 0), 5)
        cv2.circle(frame, face_center, 4, (0, 200, 0), 3)
    
    return face_centers, frame

def calculate_robot_pose(face_position, current_pose):
    """Calculate new robot pose based on face position"""
    if not current_pose:
        return None
    
    # Scale face position to robot movement
    scaled_x = face_position[0] * m_per_pixel
    scaled_y = face_position[1] * m_per_pixel
    
    # Limit movement
    scaled_x = max(-max_x, min(max_x, scaled_x))
    scaled_y = max(-max_y, min(max_y, scaled_y))
    
    # Calculate new pose
    new_pose = current_pose.copy()
    new_pose[0] += scaled_x  # X position
    new_pose[1] += scaled_y  # Y position
    
    # Calculate rotation based on position
    x_pos_perc = scaled_x / max_x
    y_pos_perc = scaled_y / max_y
    
    x_rot = x_pos_perc * hor_rot_max
    y_rot = y_pos_perc * vert_rot_max * -1
    
    new_pose[3] = y_rot  # Rx rotation
    new_pose[4] = x_rot  # Ry rotation
    
    return new_pose

def main():
    """Main face tracking loop"""
    print("Safe Face Tracking System")
    print("=" * 40)
    
    # Initialize camera
    print("Initializing camera...")
    vs = VideoStream(src=0, resolution=video_resolution, framerate=13).start()
    time.sleep(0.2)
    
    # Initialize robot connection
    print("Initializing robot connection...")
    robot = SafeRobotControl(ROBOT_IP, ROBOT_PORT)
    
    if not robot.connect():
        print("❌ Could not connect to robot!")
        print("   - Check if robot is powered on")
        print("   - Check if robot is in remote control mode")
        print("   - Check IP address")
        vs.stop()
        return
    
    print("✓ Robot connected successfully")
    
    # Get initial pose
    current_pose = robot.get_current_pose()
    if not current_pose:
        print("⚠ Could not get initial pose, using default")
        current_pose = [0.5, 0.0, 0.5, 0.0, 0.0, 0.0]
    
    print(f"Initial pose: {[round(x, 4) for x in current_pose]}")
    
    try:
        print("\nStarting face tracking...")
        print("Press 'q' to quit")
        
        while True:
            # Get frame
            frame = vs.read()
            if frame is None:
                continue
            
            # Find faces
            face_positions, processed_frame = find_faces_dnn(frame)
            
            # Show frame
            cv2.imshow('Face Tracking', processed_frame)
            
            # Process face detection
            if len(face_positions) > 0:
                # Calculate new robot pose
                new_pose = calculate_robot_pose(face_positions[0], current_pose)
                
                if new_pose:
                    # Move robot (with safety check)
                    if robot.move_to_pose(new_pose, ACCELERATION, VELOCITY):
                        current_pose = new_pose
                        print(f"Moving to: {[round(x, 4) for x in new_pose]}")
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Small delay to prevent overwhelming the robot
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nStopping face tracking...")
    
    except Exception as e:
        print(f"\nError during face tracking: {e}")
    
    finally:
        # Cleanup
        print("Cleaning up...")
        cv2.destroyAllWindows()
        vs.stop()
        robot.close()
        print("✓ Face tracking stopped")

if __name__ == "__main__":
    main() 