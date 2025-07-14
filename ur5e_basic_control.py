"""
UR5e Basic Control Program
A simple program to connect to a UR5e robot and send basic move commands.

This program demonstrates:
- Connecting to a UR5e robot
- Getting current robot state
- Moving to joint positions
- Moving to Cartesian positions
- Basic safety features

Author: Assistant
License: MIT
"""

import URBasic
import math
import numpy as np
import time
import sys

# Configuration
ROBOT_IP = '192.168.1.11'  # Change this to your robot's IP address
ACCELERATION = 0.5  # Robot acceleration [rad/s^2]
VELOCITY = 0.3      # Robot velocity [rad/s]
CARTESIAN_ACCEL = 0.5  # Cartesian acceleration [m/s^2]
CARTESIAN_VEL = 0.2    # Cartesian velocity [m/s]

# Safe joint positions (in radians)
HOME_POSITION = [
    math.radians(0),    # Base
    math.radians(-90),  # Shoulder
    math.radians(-90),  # Elbow
    math.radians(-90),  # Wrist 1
    math.radians(90),   # Wrist 2
    math.radians(0)     # Wrist 3
]

# Alternative positions for demonstration
POSITION_1 = [
    math.radians(45),   # Base
    math.radians(-60),  # Shoulder
    math.radians(-120), # Elbow
    math.radians(-60),  # Wrist 1
    math.radians(90),   # Wrist 2
    math.radians(45)    # Wrist 3
]

POSITION_2 = [
    math.radians(-45),  # Base
    math.radians(-60),  # Shoulder
    math.radians(-120), # Elbow
    math.radians(-60),  # Wrist 1
    math.radians(90),   # Wrist 2
    math.radians(-45)   # Wrist 3
]

class UR5eController:
    """Class to control UR5e robot with basic movement commands"""
    
    def __init__(self, robot_ip, acceleration=0.5, velocity=0.3):
        """
        Initialize the UR5e controller
        
        Args:
            robot_ip (str): IP address of the robot
            acceleration (float): Joint acceleration [rad/s^2]
            velocity (float): Joint velocity [rad/s]
        """
        self.robot_ip = robot_ip
        self.acceleration = acceleration
        self.velocity = velocity
        
        # Initialize robot model and connection
        self.robot_model = URBasic.robotModel.RobotModel()
        self.robot = None
        
        print(f"Initializing connection to UR5e at {robot_ip}...")
        
    def connect(self):
        """Connect to the robot"""
        try:
            # Create robot connection
            self.robot = URBasic.urScript.UrScript(
                host=self.robot_ip,
                robotModel=self.robot_model
            )
            
            # Wait for connection to be established
            time.sleep(2)
            
            # Check if robot is ready
            if self.robot.robotConnector.RobotModel.ActualTCPPose() is None:
                raise ConnectionError("Failed to get robot pose - connection may not be established")
                
            print("Successfully connected to UR5e robot!")
            return True
            
        except Exception as e:
            print(f"Error connecting to robot: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the robot"""
        if self.robot:
            try:
                self.robot.robotConnector.close()
                print("Disconnected from robot")
            except Exception as e:
                print(f"Error disconnecting: {e}")
    
    def get_robot_status(self):
        """Get current robot status"""
        if not self.robot:
            print("Robot not connected!")
            return None
            
        try:
            # Get current joint positions
            joint_positions = self.robot.get_actual_joint_positions()
            
            # Get current TCP pose
            tcp_pose = self.robot.get_actual_tcp_pose()
            
            # Get robot mode
            robot_mode = self.robot.robotConnector.RobotModel.dataDir['robot_mode']
            
            print(f"Robot Mode: {robot_mode}")
            print(f"Joint Positions (rad): {[round(pos, 4) for pos in joint_positions]}")
            print(f"Joint Positions (deg): {[round(math.degrees(pos), 2) for pos in joint_positions]}")
            print(f"TCP Pose (x, y, z, rx, ry, rz): {[round(pos, 4) for pos in tcp_pose]}")
            
            return {
                'joint_positions': joint_positions,
                'tcp_pose': tcp_pose,
                'robot_mode': robot_mode
            }
            
        except Exception as e:
            print(f"Error getting robot status: {e}")
            return None
    
    def move_to_joint_position(self, joint_positions, wait=True):
        """
        Move robot to specified joint positions
        
        Args:
            joint_positions (list): List of 6 joint angles in radians
            wait (bool): Whether to wait for movement to complete
        """
        if not self.robot:
            print("Robot not connected!")
            return False
            
        try:
            print(f"Moving to joint position: {[round(math.degrees(pos), 2) for pos in joint_positions]} degrees")
            
            self.robot.movej(
                q=joint_positions,
                a=self.acceleration,
                v=self.velocity,
                wait=wait
            )
            
            if wait:
                print("Movement completed!")
            
            return True
            
        except Exception as e:
            print(f"Error during joint movement: {e}")
            return False
    
    def move_to_cartesian_position(self, pose, wait=True):
        """
        Move robot to specified Cartesian position
        
        Args:
            pose (list): List of 6 values [x, y, z, rx, ry, rz] in meters and radians
            wait (bool): Whether to wait for movement to complete
        """
        if not self.robot:
            print("Robot not connected!")
            return False
            
        try:
            print(f"Moving to Cartesian position: {[round(pos, 4) for pos in pose]}")
            
            self.robot.movel(
                pose=pose,
                a=CARTESIAN_ACCEL,
                v=CARTESIAN_VEL,
                wait=wait
            )
            
            if wait:
                print("Movement completed!")
            
            return True
            
        except Exception as e:
            print(f"Error during Cartesian movement: {e}")
            return False
    
    def move_home(self, wait=True):
        """Move robot to home position"""
        return self.move_to_joint_position(HOME_POSITION, wait)
    
    def demo_movement(self):
        """Demonstrate basic movements"""
        print("\n=== Starting Demo Movement ===")
        
        # Move to home position
        print("\n1. Moving to home position...")
        if not self.move_home():
            return False
        
        time.sleep(1)
        
        # Move to position 1
        print("\n2. Moving to position 1...")
        if not self.move_to_joint_position(POSITION_1):
            return False
        
        time.sleep(1)
        
        # Move to position 2
        print("\n3. Moving to position 2...")
        if not self.move_to_joint_position(POSITION_2):
            return False
        
        time.sleep(1)
        
        # Return to home
        print("\n4. Returning to home position...")
        if not self.move_home():
            return False
        
        print("\n=== Demo Movement Completed ===")
        return True
    
    def interactive_control(self):
        """Interactive control mode"""
        print("\n=== Interactive Control Mode ===")
        print("Commands:")
        print("  'h' - Move to home position")
        print("  '1' - Move to position 1")
        print("  '2' - Move to position 2")
        print("  's' - Show robot status")
        print("  'q' - Quit")
        
        while True:
            try:
                command = input("\nEnter command: ").lower().strip()
                
                if command == 'q':
                    break
                elif command == 'h':
                    self.move_home()
                elif command == '1':
                    self.move_to_joint_position(POSITION_1)
                elif command == '2':
                    self.move_to_joint_position(POSITION_2)
                elif command == 's':
                    self.get_robot_status()
                else:
                    print("Unknown command. Try 'h', '1', '2', 's', or 'q'")
                    
            except KeyboardInterrupt:
                print("\nExiting interactive mode...")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function"""
    print("UR5e Basic Control Program")
    print("=" * 40)
    
    # Create robot controller
    controller = UR5eController(ROBOT_IP, ACCELERATION, VELOCITY)
    
    try:
        # Connect to robot
        if not controller.connect():
            print("Failed to connect to robot. Please check:")
            print("1. Robot IP address is correct")
            print("2. Robot is powered on and connected to network")
            print("3. Robot is in remote control mode")
            return
        
        # Show initial status
        print("\nInitial robot status:")
        controller.get_robot_status()
        
        # Ask user what to do
        print("\nWhat would you like to do?")
        print("1. Run demo movement")
        print("2. Interactive control")
        print("3. Just show status and exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            controller.demo_movement()
        elif choice == '2':
            controller.interactive_control()
        elif choice == '3':
            controller.get_robot_status()
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Always disconnect
        controller.disconnect()
        print("Program ended")

if __name__ == "__main__":
    main() 