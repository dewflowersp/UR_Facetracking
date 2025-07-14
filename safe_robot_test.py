"""
Safe Robot Connection Test
This script tests robot connectivity without causing shutdowns
"""

import socket
import time
import sys

ROBOT_IP = '192.168.1.11'

def test_ports_safely():
    """Test robot ports without causing shutdowns"""
    print("Testing robot ports safely...")
    
    ports_to_test = [
        (30002, "Primary Interface"),
        (30003, "Secondary Interface"), 
        (30004, "RTDE Interface"),
        (29999, "Dashboard Server")
    ]
    
    results = {}
    
    for port, description in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)  # Short timeout
            result = sock.connect_ex((ROBOT_IP, port))
            sock.close()
            
            if result == 0:
                print(f"✓ Port {port} ({description}) - OPEN")
                results[port] = True
            else:
                print(f"✗ Port {port} ({description}) - CLOSED")
                results[port] = False
                
        except Exception as e:
            print(f"✗ Port {port} ({description}) - ERROR: {e}")
            results[port] = False
    
    return results

def check_robot_status():
    """Check if robot is responding to basic commands"""
    print("\nChecking robot status...")
    
    # Test basic ping
    try:
        import subprocess
        result = subprocess.run(['ping', '-c', '3', ROBOT_IP], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Robot responds to ping")
            return True
        else:
            print("✗ Robot does not respond to ping")
            return False
    except Exception as e:
        print(f"✗ Ping test failed: {e}")
        return False

def main():
    print("Safe Robot Diagnostic Tool")
    print("=" * 40)
    
    # Step 1: Check network connectivity
    print("\n1. Testing network connectivity...")
    if check_robot_status():
        print("✓ Network connectivity OK")
    else:
        print("✗ Network connectivity failed")
        print("   - Check if robot is powered on")
        print("   - Check if IP address is correct")
        print("   - Check network connection")
        return False
    
    # Step 2: Test ports
    print("\n2. Testing robot ports...")
    port_results = test_ports_safely()
    
    # Step 3: Analyze results
    print("\n3. Analysis:")
    
    if port_results.get(30002, False):
        print("✓ Primary interface (30002) is available")
        print("   - Basic robot communication should work")
    else:
        print("✗ Primary interface (30002) is not available")
        print("   - Robot may not be in remote control mode")
        print("   - Or robot may be in a different state")
    
    if port_results.get(30004, False):
        print("✓ RTDE interface (30004) is available")
        print("   - Real-time control should work")
    else:
        print("✗ RTDE interface (30004) is not available")
        print("   - RTDE may not be enabled on robot")
        print("   - Or robot firmware doesn't support RTDE")
    
    if port_results.get(29999, False):
        print("✓ Dashboard server (29999) is available")
        print("   - Dashboard commands should work")
    else:
        print("✗ Dashboard server (29999) is not available")
        print("   - Dashboard server may not be running")
    
    # Step 4: Recommendations
    print("\n4. Recommendations:")
    
    if not port_results.get(30002, False):
        print("   - Power cycle the robot")
        print("   - Check robot mode on teach pendant")
        print("   - Verify IP address settings")
    
    if not port_results.get(30004, False):
        print("   - RTDE may need to be enabled in robot settings")
        print("   - Check robot firmware version")
        print("   - Consider using basic interface instead of RTDE")
    
    return True

if __name__ == "__main__":
    main() 