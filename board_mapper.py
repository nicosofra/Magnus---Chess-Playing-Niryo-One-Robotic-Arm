#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy #type: ignore
import json
from sensor_msgs.msg import JointState #type: ignore
from niryo_robot_msgs.srv import SetBool #type: ignore

OUTPUT = '/home/niryo/chess_bot/board_map.json'

latest_joints = None

def on_joints(msg):
    global latest_joints
    latest_joints = list(msg.position)

def set_learning_mode(state):
    rospy.wait_for_service('/niryo_robot/learning_mode/activate')
    service = rospy.ServiceProxy('/niryo_robot/learning_mode/activate', SetBool)
    result = service(state)
    rospy.loginfo("Learning mode: " + result.message)
    rospy.sleep(1)

def read_joints():
    if latest_joints is None:
        print("ERROR: no joint data")
        return None
    return list(latest_joints)

def record_square(name):
    print("\n── {} ──────────────────────────────".format(name.upper()))

    print("1. Move arm to HOVER position above {}".format(name.upper()))
    raw_input("   Press Enter when ready...") #type: ignore
    hover = read_joints()
    if hover is None:
        return None
    print("   hover: {}".format([round(j, 4) for j in hover]))

    print("2. Move arm to CONTACT position of {}".format(name.upper()))
    raw_input("   Press Enter when ready...") #type: ignore
    contact = read_joints()
    if contact is None:
        return None
    print("   contact: {}".format([round(j, 4) for j in contact]))

    return {'hover': hover, 'contact': contact}

def main():
    rospy.init_node('board_mapper')
    rospy.Subscriber('/joint_states', JointState, on_joints)
    rospy.sleep(0.5)

    set_learning_mode(True)

    try:
        with open(OUTPUT) as f:
            board = json.load(f)
        print("Loaded existing board_map ({} squares)".format(len(board)))
    except:
        board = {}
        print("Starting new board_map")

    print("\nBoard Mapper")
    print("  e4    -> record square e4")
    print("  save  -> save and quit")
    print("  q     -> quit without saving\n")

    def valid(s):
        return len(s) == 2 and s[0] in 'abcdefgh' and s[1] in '12345678'

    while not rospy.is_shutdown():
        raw = raw_input("Square: ").strip().lower() #type: ignore
        if not raw:
            continue
        if raw == 'q':
            break
        if raw == 'save':
            with open(OUTPUT, 'w') as f:
                json.dump(board, f, indent=2)
            print("Saved {} squares to {}".format(len(board), OUTPUT))
            break
        if not valid(raw):
            print("Invalid. Example: e4")
            continue
        data = record_square(raw)
        if data:
            board[raw] = data
            print("  Recorded {}. Total: {} squares".format(raw, len(board)))

    set_learning_mode(False)

if __name__ == '__main__':
    main()