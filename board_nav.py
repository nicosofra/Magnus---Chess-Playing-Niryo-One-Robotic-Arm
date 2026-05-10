#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy #type: ignore
import actionlib #type: ignore
import json

from niryo_robot_arm_commander.msg import RobotMoveAction, RobotMoveGoal, ArmMoveCommand #type: ignore
from niryo_robot_msgs.srv import SetBool, SetInt #type: ignore

board_map = '/home/niryo/chess_bot/board_map.json'
board = None

home_joints =   [0.008420763813745838, -0.4407678113983875, -0.35255650890285456, 0.18590334716601653, -0.6934519697141028, 0.7415179254695539]

#Service proxy para tareas cortas (respuesta inmediata, no cancelable, no feedback)
def calibrate():
    rospy.wait_for_service('/niryo_robot/joints_interface/calibrate_motors')
    service = rospy.ServiceProxy('/niryo_robot/joints_interface/calibrate_motors', SetInt)
    result = service(1)
    rospy.loginfo("Calibration: " + result.message)
    rospy.sleep(3)

def set_learning_mode(state):
    rospy.wait_for_service('/niryo_robot/learning_mode/activate')
    service = rospy.ServiceProxy('/niryo_robot/learning_mode/activate', SetBool)
    result = service(state)
    rospy.loginfo("Learning mode: " + result.message)
    rospy.sleep(1)

#ActionClient para tareas largas (cancelable, feedback)
def move_joints(joints):
    client = actionlib.SimpleActionClient('/niryo_robot_arm_commander/robot_action', RobotMoveAction)
    client.wait_for_server()
    goal = RobotMoveGoal()
    goal.cmd.cmd_type = ArmMoveCommand.JOINTS
    goal.cmd.joints = list(map(float, joints))
    client.send_goal(goal)
    client.wait_for_result()

def home():
    rospy.loginfo("home...")
    move_joints(home_joints)

def hover(square):
    if square not in board:
        return
    rospy.loginfo("hover[{}]".format(square.upper()))
    move_joints(board[square]['hover'])

def contact(square):
    if square not in board:
        return
    rospy.loginfo("contact[{}]".format(square.upper()))
    move_joints(board[square]['contact'])

def move_piece(src, dst):
    rospy.loginfo("move {} -> {}".format(src.upper(), dst.upper()))
    hover(src)
    rospy.sleep(0.5)
    contact(src)
    rospy.sleep(0.5)
    hover(src)
    rospy.sleep(0.5)
    home()
    rospy.sleep(0.5)
    hover(dst)
    rospy.sleep(0.5)
    contact(dst)

def main():
    rospy.init_node('board_navigator')
    print("Calibrating...")
    calibrate()

    set_learning_mode(False)

    global board
    with open(board_map, 'r') as f:
        board = json.load(f)

    print("Board Navigator. Squares loaded: {}".format(len(board)))
    print("a1 = home -> hover a1")
    print("a1 c = home -> hover a1 -> contact a1")
    print("home -> home")
    print ("q = quit")

    def valid(s):
        return (len(s) == 2
                and s[0] in 'abcdefgh'
                and s[1] in '12345678'
                and s in board)
    
    while not rospy.is_shutdown():
        raw = raw_input("\nSquare: ").strip().lower() #type: ignore
        parts = raw.split()
        sq = parts[0]

        if not raw:
            continue

        if raw == 'q':
            print("bye bye")
            break

        if raw == 'home':
            home()
            continue

        if len(parts) == 2 and valid(parts[0]) and valid(parts[1]):
            move_piece(parts[0], parts[1])
            continue

        if not valid(sq):
            print("Invalid square. Example: e4")
            continue

        home()
        hover(sq)

        if len(parts) > 1 and parts[1] == 'c':
            contact(sq)

if __name__ == '__main__':
    main()









    