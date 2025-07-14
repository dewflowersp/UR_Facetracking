"""
Simple Robot Control - Direct Socket Communication
This bypasses the problematic URBasic library
"""

import socket
import time
import json

ROBOT_IP = '192.168.1.11'
PRIMARY_PORT = 30002

class SimpleRobotControl:
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
            print(f"✓ Connected to robot at {self.ip_address}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def send_command(self, command):
        """Send a simple command to robot"""
        if not self.socket:
            print("Not connected to robot")
            return False
        
        try:
            # Add newline to command
            if not command.endswith('\n'):
                command += '\n'
            
            self.socket.send(command.encode('utf-8'))
            print(f"✓ Sent command: {command.strip()}")
            return True
        except Exception as e:
            print(f"✗ Command failed: {e}")
            return False
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("✓ Connection closed")

    def send_command_and_get_response(self, command):
        """Send a command and get the response from robot"""
        if not self.socket:
            print("Not connected to robot")
            return None
        
        try:
            # Add newline to command
            if not command.endswith('\n'):
                command += '\n'
            
            self.socket.send(command.encode('utf-8'))
            print(f"✓ Sent command: {command.strip()}")
            
            # Read response - handle binary data
            try:
                response = self.socket.recv(1024)
                # Try to decode as UTF-8 first
                try:
                    return response.decode('utf-8').strip()
                except UnicodeDecodeError:
                    # If UTF-8 fails, return hex representation
                    return f"Binary data: {response.hex()[:50]}..."
            except Exception as e:
                print(f"✗ Failed to read response: {e}")
                return None
            
        except Exception as e:
            print(f"✗ Command failed: {e}")
            return None

    def get_current_positions(self):
        """Get current robot positions using dashboard commands"""
        if not self.socket:
            print("Not connected to robot")
            return None
        
        try:
            print("\n=== Current Robot Positions ===")
            
            # Try different approaches to get position data
            print("Attempting to get position data...")
            
            # Method 1: Try to get robot mode first
            self.send_command("Robotmode")
            time.sleep(0.2)
            
            # Method 2: Try to get loaded program
            self.send_command("get loaded program")
            time.sleep(0.2)
            
            # Method 3: Try to get robot state
            self.send_command("get robot state")
            time.sleep(0.2)
            
            print("=== End Positions ===\n")
            print("Note: Position data may require RTDE interface or specific UR script")
            return True
            
        except Exception as e:
            print(f"✗ Failed to get positions: {e}")
            return False

def test_simple_control():
    """Test simple robot control"""
    print("Testing simple robot control...")
    
    robot = SimpleRobotControl(ROBOT_IP)
    
    if not robot.connect():
        print("❌ Could not connect to robot")
        return False
    
    try:
        # Test simple commands
        print("\nTesting basic commands...")
        
        # Get current pose
        robot.send_command("get_actual_tcp_pose()")
        time.sleep(1)
        
        # Get joint positions
        robot.send_command("get_actual_joint_positions()")
        time.sleep(1)
        
        print("✓ Basic commands sent successfully")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        robot.close()

def print_current_positions():
    """Standalone function to print current positions"""
    print("Getting current robot positions...")
    
    robot = SimpleRobotControl(ROBOT_IP)
    
    if not robot.connect():
        print("❌ Could not connect to robot")
        return False
    
    try:
        robot.get_current_positions()
        return True
        
    except Exception as e:
        print(f"✗ Failed to get positions: {e}")
        return False
    finally:
        robot.close()

if __name__ == "__main__":
    print_current_positions() 