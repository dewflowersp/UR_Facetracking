"""
UR5e Diagnostic Program
This program will help diagnose why the robot is not moving.

Common issues:
1. Robot not in remote control mode
2. Safety stops active
3. Wrong IP address
4. Network connectivity issues
5. Robot program already running
6. Emergency stop active
"""

import URBasic
import math
import numpy as np
import time
import sys
import socket

# Configuration
ROBOT_IP = '192.168.1.11'  # Change this to your robot's IP address

def test_network_connectivity(ip_address, port=30002):
    """Test if we can reach the robot on the network"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip_address, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Network test error: {e}")
        return False

def diagnose_robot():
    """Comprehensive robot diagnosis"""
    print("UR5e Robot Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Network connectivity
    print("\n1. Testing network connectivity...")
    if test_network_connectivity(ROBOT_IP):
        print(f"✓ Network connection to {ROBOT_IP} is working")
    else:
        print(f"✗ Cannot reach {ROBOT_IP} on the network")
        print("   - Check if robot is powered on")
        print("   - Check if IP address is correct")
        print("   - Check network connection")
        return False
    
    # Test 2: Try to connect to robot
    print("\n2. Testing robot connection...")
    try:
        robot_model = URBasic.robotModel.RobotModel()
        robot = URBasic.urScript.UrScript(
            host=ROBOT_IP,
            robotModel=robot_model
        )
        print("✓ Successfully connected to robot")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return False
    
    # Test 3: Check robot status
    print("\n3. Checking robot status...")
    try:
        # Get robot mode
        robot_mode = robot.robotConnector.RobotModel.dataDir['robot_mode']
        print(f"Robot Mode: {robot_mode}")
        
        # Check if robot is powered on
        power_on = robot.robotConnector.RobotModel.RobotStatus().PowerOn
        print(f"Robot Powered On: {power_on}")
        
        # Check safety status
        safety_stopped = robot.robotConnector.RobotModel.SafetyStatus().StoppedDueToSafety
        print(f"Safety Stop Active: {safety_stopped}")
        
        # Get current pose
        tcp_pose = robot.get_actual_tcp_pose()
        print(f"Current TCP Pose: {[round(x, 4) for x in tcp_pose]}")
        
        # Check if RTDE is running
        rtde_running = robot.robotConnector.RTDE.isRunning()
        print(f"RTDE Running: {rtde_running}")
        
    except Exception as e:
        print(f"✗ Error getting robot status: {e}")
        return False
    
    # Test 4: Try a simple movement
    print("\n4. Testing simple movement...")
    try:
        current_pose = robot.get_actual_tcp_pose()
        print(f"Current pose: {[round(x, 4) for x in current_pose]}")
        
        # Try to move slightly in Z direction
        test_pose = current_pose.copy()
        test_pose[2] += 0.01  # Move 1cm up
        
        print(f"Attempting to move to: {[round(x, 4) for x in test_pose]}")
        robot.movel(pose=test_pose, a=0.1, v=0.05, wait=True)
        print("✓ Movement successful!")
        
        # Move back
        robot.movel(pose=current_pose, a=0.1, v=0.05, wait=True)
        print("✓ Return movement successful!")
        
    except Exception as e:
        print(f"✗ Movement failed: {e}")
        return False
    
    print("\n✓ All tests passed! Robot should be working correctly.")
    return True

if __name__ == "__main__":
    diagnose_robot() 