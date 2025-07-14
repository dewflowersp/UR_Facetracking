"""
Ultra Safe Robot Test - No URBasic Library
This test only checks network connectivity without any robot control
"""

import socket
import subprocess
import time
import sys

ROBOT_IP = '192.168.1.11'

def test_basic_connectivity():
    """Test basic network connectivity"""
    print("Testing basic network connectivity...")
    
    try:
        # Test ping
        result = subprocess.run(['ping', '-c', '3', ROBOT_IP], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✓ Ping successful")
            return True
        else:
            print("✗ Ping failed")
            return False
    except Exception as e:
        print(f"✗ Ping test error: {e}")
        return False

def test_robot_ports():
    """Test robot ports without any library dependencies"""
    print("\nTesting robot ports...")
    
    ports = [
        (30002, "Primary Interface"),
        (30003, "Secondary Interface"),
        (30004, "RTDE Interface"),
        (29999, "Dashboard Server")
    ]
    
    results = {}
    
    for port, description in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # Very short timeout
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

def analyze_results(port_results):
    """Analyze port test results"""
    print("\nAnalysis:")
    
    if port_results.get(30002, False):
        print("✓ Primary interface (30002) is available")
        print("   - Basic robot communication should work")
        print("   - Robot is likely powered on and responding")
    else:
        print("✗ Primary interface (30002) is not available")
        print("   - Robot may not be powered on")
        print("   - Robot may not be in remote control mode")
        print("   - IP address may be incorrect")
    
    if port_results.get(30004, False):
        print("✓ RTDE interface (30004) is available")
        print("   - Real-time control should work")
        print("   - RTDE is enabled on robot")
    else:
        print("✗ RTDE interface (30004) is not available")
        print("   - RTDE may not be enabled")
        print("   - Robot firmware may not support RTDE")
        print("   - This is normal for some robot configurations")
    
    if port_results.get(29999, False):
        print("✓ Dashboard server (29999) is available")
        print("   - Dashboard commands should work")
    else:
        print("✗ Dashboard server (29999) is not available")
        print("   - Dashboard server may not be running")
    
    return port_results.get(30002, False)  # Return True if primary interface works

def main():
    print("Ultra Safe Robot Diagnostic Tool")
    print("=" * 40)
    print("This test only checks network connectivity")
    print("No robot control commands will be sent")
    print()
    
    # Test 1: Basic connectivity
    if not test_basic_connectivity():
        print("\n❌ Basic connectivity failed!")
        print("   - Check if robot is powered on")
        print("   - Check if IP address is correct")
        print("   - Check network connection")
        return False
    
    # Test 2: Port availability
    port_results = test_robot_ports()
    
    # Test 3: Analysis
    primary_available = analyze_results(port_results)
    
    # Test 4: Recommendations
    print("\nRecommendations:")
    
    if not primary_available:
        print("1. Power cycle the robot")
        print("2. Check robot mode on teach pendant")
        print("3. Verify IP address settings")
        print("4. Check network connection")
    else:
        print("1. Basic connectivity is working")
        print("2. Robot appears to be responding")
        print("3. Consider using basic interface instead of RTDE")
        print("4. The URBasic library may have compatibility issues")
    
    return primary_available

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Robot appears to be reachable!")
    else:
        print("\n❌ Robot connectivity issues detected!") 