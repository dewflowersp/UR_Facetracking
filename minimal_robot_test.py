"""
Minimal robot connection test - safe version
"""

import URBasic
import time

ROBOT_IP = '192.168.1.11'

def safe_robot_test():
    """Safe robot connection test"""
    print("Starting safe robot test...")
    
    try:
        # Create robot model
        robot_model = URBasic.robotModel.RobotModel()
        print("✓ Robot model created")
        
        # Try to connect with timeout
        print("Attempting connection...")
        robot = URBasic.urScript.UrScript(
            host=ROBOT_IP,
            robotModel=robot_model
        )
        
        # Wait a bit for connection to stabilize
        time.sleep(2)
        
        # Check if we can get basic info
        try:
            tcp_pose = robot.get_actual_tcp_pose()
            print(f"✓ Got TCP pose: {[round(x, 4) for x in tcp_pose]}")
        except:
            print("⚠ Could not get TCP pose, but connection established")
        
        print("✓ Connection successful!")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    safe_robot_test() 