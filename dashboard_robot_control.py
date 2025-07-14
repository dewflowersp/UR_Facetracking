"""
Dashboard Robot Control
Uses the robot's dashboard server for safer control
"""

import socket
import time

ROBOT_IP = '192.168.1.11'
DASHBOARD_PORT = 29999

class DashboardRobotControl:
    def __init__(self, ip_address, port=29999):
        self.ip_address = ip_address
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to dashboard server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.ip_address, self.port))
            
            # Read welcome message
            response = self.socket.recv(1024).decode('utf-8')
            print(f"Dashboard response: {response}")
            return True
        except Exception as e:
            print(f"Dashboard connection failed: {e}")
            return False
    
    def send_command(self, command):
        """Send dashboard command"""
        if not self.socket:
            return False
        
        try:
            command += '\n'
            self.socket.send(command.encode('utf-8'))
            response = self.socket.recv(1024).decode('utf-8')
            print(f"Command: {command.strip()} -> Response: {response.strip()}")
            return True
        except Exception as e:
            print(f"Command failed: {e}")
            return False
    
    def close(self):
        """Close dashboard connection"""
        if self.socket:
            self.socket.close()
            self.socket = None

def test_dashboard_control():
    """Test dashboard control"""
    print("Testing dashboard control...")
    
    robot = DashboardRobotControl(ROBOT_IP, DASHBOARD_PORT)
    
    if not robot.connect():
        print("❌ Could not connect to dashboard")
        return False
    
    try:
        # Test basic commands
        print("\nTesting dashboard commands...")
        
        # Get robot mode
        robot.send_command("robotmode")
        time.sleep(1)
        
        # Get loaded program
        robot.send_command("get loaded program")
        time.sleep(1)
        
        # Check if robot is running
        robot.send_command("running")
        time.sleep(1)
        
        print("✓ Dashboard commands successful")
        return True
        
    except Exception as e:
        print(f"✗ Dashboard test failed: {e}")
        return False
    finally:
        robot.close()

if __name__ == "__main__":
    test_dashboard_control() 