# Modified version that doesn't use RTDE
# This would use basic movement commands instead of real-time control

# Replace the real-time control section with:
# robot.init_realtime_control()  # Comment this out
# robot.set_realtime_pose(next_pose)  # Comment this out

# Use basic movement instead:
# robot.movel(pose=next_pose, a=0.1, v=0.05, wait=False) 