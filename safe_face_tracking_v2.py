
"""
Safe Face Tracking v2 - Improved Movement
"""

import cv2
import numpy as np
import math
import time
import socket
import imutils
from imutils.video import VideoStream

# Configuration
ROBOT_IP = '192.168.1.11'
ROBOT_PORT = 30002
ACCELERATION = 0.3  # Increased for faster movement
VELOCITY = 0.15     # Increased for faster movement

# Camera settings
video_resolution = (700, 400)
video_midpoint = (int(video_resolution[0]/2), int(video_resolution[1]/2))

# Robot movement settings
m_per_pixel = 0.00008  # Increased for larger movements
max_x = 0.08           # Increased movement range
max_y = 0.08
hor_rot_max = math.radians(15)  # Increased rotation
vert_rot_max = math.radians(8)

# Face movement detection settings
face_movement_threshold = 10  # Minimum pixel movement to trigger robot movement
last_face_position = None     # Track last face position

# Face detection model
pretrained_model = cv2.dnn.readNetFromCaffe(
    "MODELS/deploy.prototxt.txt", 
    "MODELS/res10_300x300_ssd_iter_140000.caffemodel"
)

class ImprovedRobotControl:
    def __init__(self, ip_address, port=30002):
        self.ip_address = ip_address
        self.port = port
        self.socket = None
        self.connected = False
        self.current_pose = None
        self.last_movement_time = 0
        self.movement_cooldown = 0.2  # Reduced cooldown for faster response
        
    def connect(self):
        """Connect to robot"""
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
        """Send command with error handling"""
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
        """Get current TCP pose from robot"""
        try:
            # Send command to get actual TCP pose
            command = "get_actual_tcp_pose()\n"
            self.socket.send(command.encode('utf-8'))
            
            # Wait for response
            time.sleep(0.1)
            
            # Try to receive response (non-blocking)
            self.socket.settimeout(0.5)
            try:
                response = self.socket.recv(1024).decode('utf-8')
                # Parse the response - UR robots return pose as [x, y, z, rx, ry, rz]
                if '[' in response and ']' in response:
                    start = response.find('[')
                    end = response.find(']')
                    pose_str = response[start+1:end]
                    pose_values = [float(x.strip()) for x in pose_str.split(',')]
                    if len(pose_values) == 6:
                        print(f"✓ Retrieved current pose: {[round(x, 4) for x in pose_values]}")
                        return pose_values
            except socket.timeout:
                pass
            
            # Fallback: try alternative command
            command = "get_actual_joint_positions()\n"
            self.socket.send(command.encode('utf-8'))
            time.sleep(0.1)
            
            print("⚠ Could not parse pose response, using fallback method")
            return None
            
        except Exception as e:
            print(f"✗ Error getting current pose: {e}")
            return None
    
    def move_to_pose(self, pose, acceleration=0.3, velocity=0.15):
        """Move to pose with safety checks"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_movement_time < self.movement_cooldown:
            return False
        
        # Check if pose is significantly different
        if self.current_pose:
            pose_diff = sum(abs(a - b) for a, b in zip(pose, self.current_pose))
            if pose_diff < 0.0005:  # Reduced threshold for more responsive movement
                return False
        
        # Send movement command
        pose_str = f"p[{pose[0]:.4f}, {pose[1]:.4f}, {pose[2]:.4f}, {pose[3]:.4f}, {pose[4]:.4f}, {pose[5]:.4f}]"
        command = f"movel({pose_str}, a={acceleration}, v={velocity})"
        
        if self.send_command(command):
            self.current_pose = pose
            self.last_movement_time = current_time
            print(f"Moving to: {[round(x, 4) for x in pose]}")
            return True
        
        return False
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False
        print("✓ Robot connection closed")

def find_faces_dnn(image):
    """Find faces in image"""
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
        
        # Add position text
        cv2.putText(frame, f"({position_from_center[0]}, {position_from_center[1]})", 
                   (face_center[0] + 10, face_center[1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
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

def has_face_moved(current_face_pos, last_face_pos):
    """Check if face has moved significantly enough to warrant robot movement"""
    if last_face_pos is None:
        return True  # First detection, always move
    
    # Calculate distance between current and last face position
    distance = math.sqrt((current_face_pos[0] - last_face_pos[0])**2 + 
                        (current_face_pos[1] - last_face_pos[1])**2)
    
    return distance > face_movement_threshold

def main():
    """Main face tracking loop"""
    print("Safe Face Tracking v2 - Fast Movement")
    print("=" * 40)
    
    # Initialize camera
    print("Initializing camera...")
    vs = VideoStream(src=1, resolution=video_resolution, framerate=20).start()  # Increased framerate
    time.sleep(0.2)
    
    # Initialize robot connection
    print("Initializing robot connection...")
    robot = ImprovedRobotControl(ROBOT_IP, ROBOT_PORT)
    
    if not robot.connect():
        print("❌ Could not connect to robot!")
        vs.stop()
        return
    
    print("✓ Robot connected successfully")
    
    # Get initial pose from robot's current position
    print("Getting robot's current position...")
    current_pose = robot.get_current_pose()
    
    if not current_pose:
        print("⚠ Could not get current pose from robot, using default")
        current_pose = [0.43, -0.575, 0.138, 0.0, 0.1672, 0.0]
    else:
        print(f"✓ Robot initialized from current position: {[round(x, 4) for x in current_pose]}")
    
    robot.current_pose = current_pose
    
    face_count = 0
    movement_count = 0
    last_face_position = None  # Track last face position
    
    try:
        print("\nStarting face tracking...")
        print("Press 'q' to quit")
        print(f"Face movement threshold: {face_movement_threshold} pixels")
        
        while True:
            # Get frame
            frame = vs.read()
            if frame is None:
                continue
            
            # Find faces
            face_positions, processed_frame = find_faces_dnn(frame)
            
            # Update face count
            if len(face_positions) > 0:
                face_count += 1
                if face_count % 20 == 0:  # More frequent updates
                    print(f"Face detected at: {face_positions[0]}")
            
            # Process face detection
            if len(face_positions) > 0:
                current_face_pos = face_positions[0]
                
                # Check if face has moved significantly
                if has_face_moved(current_face_pos, last_face_position):
                    # Calculate new robot pose
                    new_pose = calculate_robot_pose(current_face_pos, current_pose)
                    
                    if new_pose:
                        # Move robot
                        if robot.move_to_pose(new_pose, ACCELERATION, VELOCITY):
                            current_pose = new_pose
                            movement_count += 1
                            last_face_position = current_face_pos  # Update last position
                            if movement_count % 5 == 0:  # More frequent movement updates
                                print(f"Movement {movement_count}: {[round(x, 4) for x in new_pose]}")
                else:
                    # Face hasn't moved significantly, don't send movement command
                    if face_count % 50 == 0:  # Log occasionally
                        print("Face stationary - no movement needed")
            else:
                # No face detected, reset last position
                last_face_position = None
            
            # Add status text to frame
            cv2.putText(processed_frame, f"Faces: {len(face_positions)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(processed_frame, f"Movements: {movement_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(processed_frame, f"Speed: {VELOCITY} m/s", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add face movement status
            if len(face_positions) > 0 and last_face_position is not None:
                distance = math.sqrt((face_positions[0][0] - last_face_position[0])**2 + 
                                   (face_positions[0][1] - last_face_position[1])**2)
                status_color = (0, 255, 0) if distance > face_movement_threshold else (0, 165, 255)  # Green if moving, orange if stationary
                status_text = "Moving" if distance > face_movement_threshold else "Stationary"
                cv2.putText(processed_frame, f"Face: {status_text} ({distance:.1f}px)", (10, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Show frame
            cv2.imshow('Face Tracking v2 - Fast', processed_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Reduced delay for faster response
            time.sleep(0.003)
    
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
        print(f"✓ Face tracking stopped. Total movements: {movement_count}")

if __name__ == "__main__":
    main() 