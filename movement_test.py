"""
Movement Test - Test different movement approaches
"""

import socket
import time
import math

ROBOT_IP = '192.168.1.11'
PRIMARY_PORT = 30002

class MovementTest:
    def __init__(self, ip_address, port=30002):
        self.ip_address = ip_address
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to robot"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.ip_address, self.port))
            print(f"✓ Connected to robot")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def send_command(self, command):
        """Send command and wait for response"""
        if not self.socket:
            return False
        
        try:
            if not command.endswith('\n'):
                command += '\n'
            
            print(f"Sending: {command.strip()}")
            self.socket.send(command.encode('utf-8'))
            time.sleep(0.5)  # Wait for command to be processed
            return True
        except Exception as e:
            print(f"Command failed: {e}")
            return False
    
    def get_current_pose(self):
        """Get current TCP pose"""
        if self.send_command("get_actual_tcp_pose()"):
            # In a real implementation, you'd parse the response
            # For now, return a default pose
            return [0.5, 0.0, 0.5, 0.0, 0.0, 0.0]
        return None
    
    def test_joint_movement(self):
        """Test joint movement (safer than Cartesian)"""
        print("\nTesting joint movement...")
        
        # Get current joint positions
        self.send_command("get_actual_joint_positions()")
        time.sleep(1)
        
        # Move joint 1 slightly
        self.send_command("movej([0.1, 0.0, 0.0, 0.0, 0.0, 0.0], a=0.1, v=0.05)")
        time.sleep(3)
        
        # Move back
        self.send_command("movej([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], a=0.1, v=0.05)")
        time.sleep(3)
    
    def test_cartesian_movement(self):
        """Test Cartesian movement"""
        print("\nTesting Cartesian movement...")
        
        # Get current pose
        current_pose = self.get_current_pose()
        print(f"Current pose: {current_pose}")
        
        # Move slightly in Z direction
        new_pose = current_pose.copy()
        new_pose[2] += 0.01  # Move 1cm up
        
        pose_str = f"p[{new_pose[0]:.4f}, {new_pose[1]:.4f}, {new_pose[2]:.4f}, {new_pose[3]:.4f}, {new_pose[4]:.4f}, {new_pose[5]:.4f}]"
        command = f"movel({pose_str}, a=0.1, v=0.05)"
        
        self.send_command(command)
        time.sleep(3)
        
        # Move back
        pose_str = f"p[{current_pose[0]:.4f}, {current_pose[1]:.4f}, {current_pose[2]:.4f}, {current_pose[3]:.4f}, {current_pose[4]:.4f}, {current_pose[5]:.4f}]"
        command = f"movel({pose_str}, a=0.1, v=0.05)"
        
        self.send_command(command)
        time.sleep(3)
    
    def test_simple_commands(self):
        """Test simple commands"""
        print("\nTesting simple commands...")
        
        # Test basic commands
        commands = [
            "get_actual_tcp_pose()",
            "get_actual_joint_positions()",
            "get_robot_status()",
            "get_safety_status()"
        ]
        
        for cmd in commands:
            self.send_command(cmd)
            time.sleep(0.5)
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.socket = None

def main():
    print("Robot Movement Test")
    print("=" * 20)
    
    test = MovementTest(ROBOT_IP, PRIMARY_PORT)
    
    if not test.connect():
        print("❌ Could not connect to robot")
        return
    
    try:
        # Test simple commands first
        test.test_simple_commands()
        
        # Test joint movement
        test.test_joint_movement()
        
        # Test Cartesian movement
        test.test_cartesian_movement()
        
        print("\n✓ Movement tests completed")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    finally:
        test.close()

if __name__ == "__main__":
    main() 