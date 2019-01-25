from LeapData import LeapData
from resources.pymo.pymo.parsers import BVHParser as Pymo_BVHParser
from resources.pymo.pymo.writers import BVHWriter as Pymo_BVHWriter
from resources.b3d.bvh_reader import BVH as B3D_BVHReader
from resources.b3d.c3d_convertor import Convertor as B3D_C3DWriter
from AnyWriter import AnyWriter

import os, sys, inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = './resources/LeapSDK/lib/x64' if sys.maxsize > 2 ** 32 else './resources/LeapSDK/lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
from resources.LeapSDK.lib import Leap


class LeapRecord(Leap.Listener):
    def on_init(self, controller):
        print("Initialized")

        # Initialize Leap2DataFrame parser
        self.leap2bvh = LeapData(channel_setting='rotation')
        self.write_c3d = False
        self.write_anybody = True
        self.file_name = 'LeapRecord'

        self.actual_frame = 0

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("\nExited")

        bvh_data = self.leap2bvh.parse()

        bvh_filepath = '../output/BVH/{}.bvh'.format(self.file_name)
        bvh_writer = Pymo_BVHWriter()
        bvh_file = open(bvh_filepath, 'w')
        # bvh_writer.write(self.leap2bvh.parse(), bvh_file)
        bvh_writer.write(bvh_data, bvh_file)
        bvh_file.close()
        print('"{}" written'.format(bvh_file.name))

        if self.write_c3d:
            bvh_reader = B3D_BVHReader()
            if not bvh_reader.load_from_file(bvh_file.name):
                raise Exception('error: can not read "{}"'.format(bvh_file.name))

            c3d_filepath = '../output/C3D/{}.c3d'.format(self.file_name)
            c3d_writer = B3D_C3DWriter()
            c3d_writer.convert(bvh_reader, c3d_filepath)
            print('"{}" written from "{}"'.format(c3d_filepath, bvh_file.name))

        if self.write_anybody:
            # AnyWriter().write(Pymo_BVHParser().parse(bvh_file.name))
            AnyWriter().write(bvh_data)
            print('Anybody files written from "{}"'.format(bvh_file.name))

    def on_frame(self, controller):
        # Get the most recent frame
        frame = controller.frame()

        if not frame.hands.is_empty:
            # Get the first hand
            hand = frame.hands[0]

            if hand.is_left:
                sys.stdout.write("\rPlease use your right hand")
                sys.stdout.flush()

            if hand.is_right and hand.is_valid:
                sys.stdout.write("\rValid right hand found, recording data. Current frame: {}"
                                 .format(self.actual_frame))
                sys.stdout.flush()

                # Check if the hand has any fingers
                fingers = hand.fingers
                if not fingers.is_empty:
                    self.leap2bvh.add_frame(self.actual_frame, hand)
                    self.actual_frame = self.actual_frame + 1


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
