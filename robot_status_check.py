"""
Robot Status Check
Check robot mode, status, and movement capabilities
"""

import socket
import time

ROBOT_IP = '192.168.1.11'
PRIMARY_PORT = 30002
DASHBOARD_PORT = 29999

class RobotDiagnostic:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        
    def check_dashboard_status(self):
        """Check robot status via dashboard"""
        print("Checking robot status via dashboard...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.ip_address, DASHBOARD_PORT))
            
            # Read welcome message
            welcome = sock.recv(1024).decode('utf-8')
            print(f"Dashboard welcome: {welcome.strip()}")
            
            # Check robot mode
            sock.send(b"robotmode\n")
            mode_response = sock.recv(1024).decode('utf-8')
            print(f"Robot mode: {mode_response.strip()}")
            
            # Check if running
            sock.send(b"running\n")
            running_response = sock.recv(1024).decode('utf-8')
            print(f"Running status: {running_response.strip()}")
            
            # Check loaded program
            sock.send(b"get loaded program\n")
            program_response = sock.recv(1024).decode('utf-8')
            print(f"Loaded program: {program_response.strip()}")
            
            sock.close()
            return True
            
        except Exception as e:
            print(f"Dashboard check failed: {e}")
            return False
    
    def test_basic_movement(self):
        """Test basic movement commands"""
        print("\nTesting basic movement commands...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.ip_address, PRIMARY_PORT))
            
            # Get current pose
            sock.send(b"get_actual_tcp_pose()\n")
            time.sleep(0.5)
            
            # Try a simple movement command
            print("Sending test movement command...")
            test_command = b"movel(p[0.5, 0.0, 0.5, 0.0, 0.0, 0.0], a=0.1, v=0.05)\n"
            sock.send(test_command)
            time.sleep(2)
            
            # Check if command was accepted
            print("Movement command sent")
            
            sock.close()
            return True
            
        except Exception as e:
            print(f"Movement test failed: {e}")
            return False

def main():
    print("Robot Status Diagnostic")
    print("=" * 30)
    
    diagnostic = RobotDiagnostic(ROBOT_IP)
    
    # Check dashboard status
    if not diagnostic.check_dashboard_status():
        print("❌ Could not check robot status")
        return
    
    # Test basic movement
    diagnostic.test_basic_movement()
    
    print("\nDiagnostic complete!")

if __name__ == "__main__":
    main() 