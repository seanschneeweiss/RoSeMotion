import sys

from config.Configuration import env
from resources.LeapSDK.v4_python37 import Leap
from LeapData import LeapData
from resources.pymo.pymo.writers import BVHWriter as Pymo_BVHWriter
# from resources.b3d.bvh_reader import BVH as B3D_BVHReader
# from resources.b3d.c3d_convertor import Convertor as B3D_C3DWriter
from AnyWriter import AnyWriter


class LeapRecord(Leap.Listener):
    def __init__(self):
        super(LeapRecord, self).__init__()
        # Initialize Leap2DataFrame parser
        self.leap2bvh = LeapData(channel_setting=env.config.channels)

        self.bvh_write = env.config.bvh
        if self.bvh_write:
            self.bvh_filename = env.config.bvh_path + '\\' + env.config.bvh_filename + '.bvh'

        self.c3d_write = env.config.c3d
        if self.c3d_write:
            self.c3d_filename = env.config.c3d_path + '\\' + env.config.c3d_filename + '.c3d'

        self.anybody_write = env.config.anybody
        if self.anybody_write:
            self.anybody_template_path = env.config.anybody_template_path + '\\'
            self.anybody_output_path = env.config.anybody_output_path + '\\'

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

        bvh_data = self.leap2bvh.parse()

        if self.bvh_write:
            bvh_writer = Pymo_BVHWriter()
            bvh_file = open(self.bvh_filename, 'w')
            bvh_writer.write(bvh_data, bvh_file)
            bvh_file.close()
            print('"{}" written'.format(bvh_file.name))

        # if self.c3d_write:
        #     # workaround, need bvh
        #     bvh_writer = Pymo_BVHWriter()
        #     bvh_file = open(self.c3d_filename.strip('.c3d') + '-tmp.bvh', 'w')
        #     bvh_writer.write(bvh_data, bvh_file)
        #     bvh_file.close()
        #     print('"{}" written'.format(bvh_file.name))
        #
        #     bvh_reader = B3D_BVHReader()
        #     if not bvh_reader.load_from_file(bvh_file.name):
        #         raise Exception('error: can not read "{}"'.format(bvh_file.name))
        #
        #     c3d_writer = B3D_C3DWriter()
        #     c3d_writer.convert(bvh_reader, self.c3d_filename)
        #     print('"{}" written from "{}"'.format(self.c3d_filename, bvh_file.name))
        #
        #     os.remove(bvh_file.name)
        #     print('"{}" deleted'.format(bvh_file.name))

        if self.anybody_write:
            AnyWriter(template_directory=self.anybody_template_path,
                      output_directory=self.anybody_output_path
                      ).write(bvh_data)
            print('Anybody files written to "{}"'.format(self.anybody_output_path))

    def on_frame(self, controller):
        # Get the most recent frame
        self.leap2bvh.add_frame(controller.frame())


def start_recording():
    # Create a sample listener and controller
    listener = LeapRecord()
    controller = Leap.Controller()
   
    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print("Listener added")
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)
        print("Listener removed")
