################################################################################
# Copyright (C) 2012-2016 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap
# from pymo.Leap2BVH_pos import Leap2BVH
from pymo.Leap2BVH_rot import Leap2BVH
from pymo.writers import BVHWriter


class BVHListener(Leap.Listener):
    # finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    # bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']

    def on_init(self, controller):
        print("Initialized")
        # Initialize BVH Parser
        self.leap2bvh = Leap2BVH()
        self.actual_frame = 0

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")
        writer = BVHWriter()
        f = open("test_output.bvh", 'w')
        writer.write(self.leap2bvh.parse(), f)
        f.close()

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        if not frame.hands.is_empty:
            # Get the first hand
            hand = frame.hands[0]

            if hand.is_left:
                print("Please use right hand")

            if hand.is_right and hand.is_valid:
                # Check if the hand has any fingers
                fingers = hand.fingers
                if not fingers.is_empty:
                    self.leap2bvh.add_frame(self.actual_frame, hand)
                    self.actual_frame = self.actual_frame + 1


        #print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d" % (
        #    frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools))

        # if not frame.hands.is_empty:
        #     # Get the first hand
        #     hand = frame.hands[0]
        #
        #     # Check if the hand has any fingers
        #     fingers = hand.fingers
        #     if not fingers.is_empty:
        #         # Calculate the hand's average finger tip position
        #         avg_pos = Leap.Vector()
        #         for finger in fingers:
        #             avg_pos += finger.tip_position
        #         avg_pos /= len(fingers)
        #         print "Hand has %d fingers, average finger tip position: %s" % (
        #             len(fingers), avg_pos)
        #
        #     # Get the hand's sphere radius and palm position
        #     print "Hand sphere radius: %f mm, palm position: %s" % (
        #         hand.sphere_radius, hand.palm_position)
        #
        #     # Get the hand's normal vector and direction
        #     normal = hand.palm_normal
        #     direction = hand.direction
        #
        #     # Calculate the hand's pitch, roll, and yaw angles
        #     print "Hand pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
        #         direction.pitch * Leap.RAD_TO_DEG,
        #         normal.roll * Leap.RAD_TO_DEG,
        #         direction.yaw * Leap.RAD_TO_DEG)


def main():
    # Create a sample listener and controller
    listener = BVHListener()
    controller = Leap.Controller()
   
    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print("Press Enter to quit...")
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
