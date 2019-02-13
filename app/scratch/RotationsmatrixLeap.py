from LeapData import LeapData
from resources.pymo.pymo.parsers import BVHParser as Pymo_BVHParser
from resources.pymo.pymo.writers import BVHWriter as Pymo_BVHWriter
from resources.b3d.bvh_reader import BVH as B3D_BVHReader
from resources.b3d.c3d_convertor import Convertor as B3D_C3DWriter
from AnyWriter import AnyWriter

import os, sys, inspect, time

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = './resources/LeapSDK/lib/x64' if sys.maxsize > 2 ** 32 else './resources/LeapSDK/lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
from resources.LeapSDK.lib import Leap


class LeapRecord(Leap.Listener):
    def on_init(self, controller):
        print("Initialized")

        # Initialize Leap2DataFrame parser
        self.actual_frame = 0

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def on_frame(self, controller):
        # Get the most recent frame
        frame = controller.frame()

        if not frame.hands.is_empty:
            # Get the first hand
            hand = frame.hands[0]

            if hand.is_left:
                # sys.stdout.write("Please use your right hand\r")
                # sys.stdout.flush()
                print("Please use your right hand")

            if hand.is_right and hand.is_valid:
                # sys.stdout.write("Valid right hand found, recording data ...\r")
                # sys.stdout.flush()
                # print("Valid right hand found, recording data ...")

                # Check if the hand has any fingers
                fingers = hand.fingers
                if not fingers.is_empty:
                    fingerlist = hand.fingers.finger_type(Leap.Finger.TYPE_INDEX)
                    bone = fingerlist[0].bone(Leap.Bone.TYPE_PROXIMAL)


                    # sys.stdout.write("yaw: {}, pitch: {}, roll: {}\r".format(bone.direction.yaw, bone.direction.pitch, bone.direction.roll))

                    sys.stdout.write("\rpitch: {}, yaw: {}, roll: {}".format(bone.basis.x_basis.pitch*Leap.RAD_TO_DEG,
                                                                bone.basis.y_basis.yaw*Leap.RAD_TO_DEG,
                                                                bone.basis.z_basis.roll*Leap.RAD_TO_DEG))
                    sys.stdout.flush()
                    time.sleep(0.2)



def main():
    # Create a sample listener and controller
    listener = LeapRecord()
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
