#!/usr/bin/env python

import rospy #type: ignore
from tools_interface.srv import ToolCommand #type: ignore
from niryo_robot_msgs.srv import Trigger #type: ignore

def register_tool():
    rospy.wait_for_service('/niryo_robot_tools_commander/update_tool')
    update = rospy.ServiceProxy('/niryo_robot_tools_commander/update_tool', Trigger)
    result = update()
    print("Tool: " + result.message)
    rospy.sleep(0.5)

def open_gripper(position, speed, hold_torque, max_torque):
    register_tool()
    rospy.wait_for_service('/niryo_robot/tools/open_gripper')
    gripper = rospy.ServiceProxy('/niryo_robot/tools/open_gripper', ToolCommand)
    result = gripper(id=13, position=position, speed=speed, hold_torque=hold_torque, max_torque=max_torque)
    print("State: " + str(result.state))  # 16 = OK

def close_gripper(position, speed, hold_torque, max_torque):
    register_tool()
    rospy.wait_for_service('/niryo_robot/tools/close_gripper')
    gripper = rospy.ServiceProxy('/niryo_robot/tools/close_gripper', ToolCommand)
    result = gripper(id=13, position=position, speed=speed, hold_torque=hold_torque, max_torque=max_torque)
    print("State: " + str(result.state))  # 17 = OK

def main():
    rospy.init_node('gripper_tester')
    print("=== GRIPPER TESTER ===")
    print("o=open  c=close  q=quit")
    print("Default Open: pos = 450, speed = 300, hold torque = 128, max torque = 1023*")
    print("Default Close: pos = 220, speed = 300, hold torque = 160, max torque = 1023*")
    

    while not rospy.is_shutdown():
        action = raw_input("\nAction: ").strip().lower() #type: ignore
        if action == 'q':
            break
        elif action in ['o', 'c']:
            position = int(raw_input("Position:    ")) #type: ignore
            speed    = int(raw_input("Speed:       ")) #type: ignore
            hold     = int(raw_input("Hold torque: ")) #type: ignore
            max_t    = int(raw_input("Max torque:  ")) #type: ignore
            if action == 'o':
                open_gripper(position, speed, hold, max_t)
            else:
                close_gripper(position, speed, hold, max_t)
        else:
            print("Use o, c or q")

if __name__ == '__main__':
    main()