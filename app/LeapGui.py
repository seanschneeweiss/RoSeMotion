import json
from multiprocessing import Process
import os

import LeapRecord
from AnyPy import AnyPy
from config.Configuration import env
from BVHAnimation import bvh_animation
from resources.pymo.pymo.parsers import BVHParser as Pymo_BVHParser
from resources.Gooey.gooey.gui import application
from resources.Gooey.gooey.gui import processor
from resources.Gooey.gooey.gui.containers import application as containers_application
from resources.Gooey.gooey.python_bindings import gooey_decorator, gooey_parser

# strings for the actions in the Gooey side-menu
ACTION_RECORD = 'Record'
ACTION_ANYBODY = 'Anybody'
ACTION_CONVERTER = 'Converter'
ACTION_ANIMATION = 'Animation'
EXECUTED_COMMAND = 'command'


class GooeyModification:
    # overwrite the Gooey default stop method to cancel Leap Motion recording
    def on_stop(self):
        """Overload the stop method to allow stopping of Leap Motion Recording"""
        executed_command = LeapGui.StoredArgs().load().stored_args[EXECUTED_COMMAND]
        if executed_command == ACTION_RECORD:
            return self.clientRunner.stop_leap()
        self.clientRunner.stop()

    def stop_leap(self):
        """Send Keyboard Interrupt to stop Leap Motion recording and parse bvh / interpolation / c3d"""
        self._process.stdin.write(b"\n")
        self._process.stdin.close()

    # overwrite classes and methods of the stop button
    containers_application.GooeyApplication.onStopExecution = on_stop
    processor.ProcessController.stop_leap = stop_leap

    containers_application.ProcessController = processor.ProcessController
    application.GooeyApplication = containers_application.GooeyApplication
    gooey_decorator.application = application

    # create alias
    Gooey = gooey_decorator.Gooey
    GooeyParser = gooey_parser.GooeyParser


class LeapGui:
    """Implementation of the Gooey including some adaptions"""

    Gooey = GooeyModification.Gooey
    GooeyParser = GooeyModification.GooeyParser

    @staticmethod
    @Gooey(program_name="Leap Motion Recorder (c) Robin, Sean",
           sidebar_title='Actions',
           # return_to_config=True,
           language='leap-english',
           tabbed_groups=True,
           default_size=(1000, 700))
    def parse_args():
        """ Use GooeyParser to build up the arguments we will use in our script
        Save the arguments in a default json file so that we can retrieve them
        every time we run the script.
        """

        # load default values from json (saved from last run)
        stored_args = LeapGui.StoredArgs().load()

        parser = LeapGui.GooeyParser(description='Record Leap Motion data and export to bvh/c3d/any')
        env.add_parser(parser)
        subs = parser.add_subparsers(help='Tools', dest='command')

        # === record === #
        record_parser = subs.add_parser(ACTION_RECORD, help='Leap Recording')

        # bvh Group
        bvh_group = record_parser.add_argument_group(
            "BVH",
            gooey_options={
                'show_border': True,
                'columns': 1
            }
        )
        bvh_group.add_argument('-bvh',
                               metavar='Write BVH-File',
                               action='store_true')

        bvh_group.add_argument('-bvh_path',
                               metavar='BVH File',
                               action='store',
                               default=stored_args.get(
                                   ACTION_RECORD, 'bvh_path', LeapGui.StoredArgs.path('../output/BVH/RightHand.bvh')),
                               widget='FileSaver',
                               help='Choose location, where to save the BVH File')

        bvh_group.add_argument('frames_per_second',
                               metavar='Frames per second',
                               action='store',
                               default=stored_args.get(ACTION_RECORD, 'frames_per_second', '30'),
                               gooey_options={
                                   'validator': {
                                       'test': '1 <= int(user_input) <= 150',
                                       'message': 'Must be between 1 and 150'
                                   }
                               }
                               )

        bvh_group.add_argument('channels',
                               metavar='BVH Channels',
                               action='store',
                               default=stored_args.get(ACTION_RECORD, 'channels', 'rotation'),
                               widget='Dropdown',
                               help='Rotation: (X,Y,Z) rotation only\n'
                                    'Position: (X,Y,Z) rotation and position for all channels',
                               choices=['rotation', 'position'],
                               gooey_options={
                                   'validator': {
                                       'test': 'user_input != "Select Option"',
                                       'message': 'Choose a channel setting'
                                   }
                               })

        # interpol Group
        interpol_group = record_parser.add_argument_group(
            "Interpolation Vector",
            gooey_options={
                'show_border': True,
                'columns': 1
            }
        )
        interpol_group.add_argument('-anybody',
                                    metavar='Write Interpolation-Files',
                                    action='store_true')

        interpol_group.add_argument('-anybody_template_path',
                                    metavar='Anybody templates',
                                    action='store',
                                    default=stored_args.get(
                                        ACTION_RECORD, 'anybody_template_path',
                                        LeapGui.StoredArgs.path('config/anybody_templates')),
                                    widget='DirChooser',
                                    help='Source directory that contains *.template files for Anybody')

        interpol_group.add_argument('-anybody_output_path',
                                    metavar=' ',
                                    action='store',
                                    default=stored_args.get(
                                        ACTION_RECORD, 'anybody_output_path',
                                        LeapGui.StoredArgs.path('../output/Anybody')),
                                    widget='DirChooser',
                                    help='Output directory for interpolation files')

        # c3d Group
        c3d_group = record_parser.add_argument_group(
            "C3D",
            gooey_options={
                'show_border': True,
                'columns': 2
            }
        )
        c3d_group.add_argument('-c3d',
                               metavar='Write C3D-File',
                               action='store_true')

        c3d_group.add_argument('-c3d_filename',
                               metavar=' ',
                               action='store',
                               default=stored_args.get(ACTION_RECORD, 'c3d_filename', 'RightHand'),
                               help='Filename')

        c3d_group.add_argument('-c3d_path',
                               metavar=' ',
                               action='store',
                               default=stored_args.get(
                                   ACTION_RECORD, 'c3d_path', LeapGui.StoredArgs.path('../output/C3D')),
                               widget='DirChooser',
                               help='Output directory for c3d file')

        # === anybody === #
        anybody_parser = subs.add_parser(ACTION_ANYBODY, help='Anybody Simulation')
        anybody_group = anybody_parser.add_argument_group(
            "Source files",
            "Make a selection for the source files used for the Anybody analysis",
            gooey_options={
                'show_border': True,
                'columns': 1
            }
        )
        anybody_file_group = anybody_group.add_mutually_exclusive_group(
            required=True,
            gooey_options={
                'initial_selection': 0
            })

        anybody_file_group.add_argument('-any_interpol_files',
                                        metavar='Use existing vector files',
                                        help='Use interpolation vector files from Anybody project default directory',
                                        action='store_true')

        anybody_file_group.add_argument('-any_bvh_file',
                                        metavar='Source of the *.bvh file',
                                        action='store',
                                        default=stored_args.get(
                                            ACTION_ANYBODY, 'any_bvh_file',
                                            LeapGui.StoredArgs.path('../output/BVH/RightHand.bvh')),
                                        widget='FileChooser',
                                        help='Choose a bvh file to be converted to the interpolation vector files')

        anybody_file_group.add_argument('-any_files_dir',
                                        metavar='Source (.any)',
                                        action='store',
                                        default=stored_args.get(
                                            ACTION_ANYBODY, 'any_files_dir',
                                            LeapGui.StoredArgs.path('../output/Anybody')),
                                        widget='DirChooser',
                                        help='Source directory that contains interpolation *.any files for Anybody')

        anybody_group.add_argument('any_main_file',
                                   metavar='Source of HAND.Main.any',
                                   action='store',
                                   default=stored_args.get(ACTION_ANYBODY, 'any_main_file', ''),
                                   widget='FileChooser',
                                   help='Choose the main anybody file for the calculation')

        anybody_group.add_argument('-start_frame',
                                   metavar='Start Frame',
                                   help='default: 1',
                                   action='store',
                                   # default=stored_args.get(ACTION_ANYBODY, 'start_frame', '0'),
                                   gooey_options={
                                       'validator': {
                                           'test': '1 <= int(user_input)',
                                           'message': 'Must be greater or equal than 0'
                                       }
                                   },
                                   type=int)

        anybody_group.add_argument('-end_frame',
                                   metavar='End Frame',
                                   help='default: end',
                                   action='store',
                                   # default=stored_args.get(ACTION_ANYBODY, 'end_frame', 'end'),
                                   gooey_options={
                                       'validator': {
                                           'test': '("end" in user_input.lower()) or (1 <= int(user_input))',
                                           'message': 'Must be a positive value and greater than the start frame'
                                       }
                                   })

        operation_group = anybody_parser.add_argument_group(
            "Operations",
            "Select which operations should be executed by Anybody",
            gooey_options={
                'show_border': True,
                'columns': 1
            }
        )

        operation_group.add_argument('-load',
                                     metavar='Load Anybody model',
                                     action='store_true')

        operation_group.add_argument('-initial_conditions',
                                     metavar='Calc initial conditions',
                                     action='store_true')

        operation_group.add_argument('-kinematic',
                                     metavar='Calc kinematic analysis',
                                     action='store_true')

        operation_group.add_argument('-inverse_dynamics',
                                     metavar='Calc inverse dynamics',
                                     action='store_true')

        result_group = anybody_parser.add_argument_group(
            "Plots",
            gooey_options={
                'show_border': True,
                'columns': 1
            }
        )

        result_group.add_argument('-results',
                                  metavar='Open plots for selected joints',
                                  action='store_true')

        result_group.add_argument('-result_type',
                                  metavar='Select the joint values to make a plot for:',
                                  widget='Listbox',
                                  nargs='+',
                                  default=stored_args.get(ACTION_ANYBODY, 'result_type', None),
                                  choices=[
                                      "Finger1.Jnt.CMCFlexion.Pos",
                                      "Finger1.Jnt.CMCAbduction.Pos",
                                      "Finger1.Jnt.MCPFlexion.Pos",
                                      "Finger1.Jnt.MCPAbduction.Pos",
                                      "Finger1.Jnt.DIP.Pos",
                                      "Finger2.Jnt.MCP.Pos",
                                      "Finger2.Jnt.PIP.Pos",
                                      "Finger2.Jnt.DIP.Pos",
                                      "Finger3.Jnt.MCP.Pos",
                                      "Finger3.Jnt.PIP.Pos",
                                      "Finger3.Jnt.DIP.Pos",
                                      "Finger4.Jnt.MCP.Pos",
                                      "Finger4.Jnt.PIP.Pos",
                                      "Finger4.Jnt.DIP.Pos",
                                      "Finger5.Jnt.MCP.Pos",
                                      "Finger5.Jnt.PIP.Pos",
                                      "Finger5.Jnt.DIP.Pos"
                                  ])

        # === converter === #
        converter_parser = subs.add_parser(ACTION_CONVERTER, help='Convert a BVH-File in .any-Files or C3d-File')
        converter_group = converter_parser.add_argument_group(
            "Converter",
            "Convert a BVH-File in .any-Files or C3d-File",
            gooey_options={
                'show_border': True,
                'columns': 1
            }
        )

        converter_group.add_argument('bvh_file',
                                     metavar='Source (.bvh)',
                                     action='store',
                                     default=stored_args.get(
                                         ACTION_CONVERTER, 'bvh_file',
                                         LeapGui.StoredArgs.path('../output/BVH/RightHand.bvh')),
                                     widget='FileChooser',
                                     help='Source bvh-file to convert')

        converter_group.add_argument('-any_file',
                                     metavar='Convert to .any files',
                                     action='store_true')

        converter_group.add_argument('-c3d',
                                     metavar='Convert to .c3d files',
                                     action='store_true')

        converter_group.add_argument('file_dir',
                                     metavar='Store files',
                                     action='store',
                                     default=stored_args.get(
                                         ACTION_CONVERTER, 'file_dir', LeapGui.StoredArgs.path('../output')),
                                     widget='DirChooser',
                                     help='Directory to store the converted files')

        # === bvh animation === #
        animation_parser = subs.add_parser(ACTION_ANIMATION, help='Show an animation for a BVH file')
        animation_group = animation_parser.add_argument_group(
            "Animation",
            "Select a BVH file to be animated",
            gooey_options={
                'show_border': True,
                'columns': 1
            }
        )

        animation_group.add_argument('bvh_animation',
                                     metavar='BVH file path',
                                     action='store',
                                     default=stored_args.get(
                                         ACTION_ANIMATION, 'bvh_animation',
                                         LeapGui.StoredArgs.path('../output/BVH/RightHand.bvh')),
                                     widget='FileChooser')

        # start the UI and save arguments to json for next run
        stored_args.save(parser.parse_args())

    class StoredArgs:
        """class for loading and saving arguments from/to json, also to handle default values"""

        def __init__(self):
            self.stored_args = {}
            self.loaded_actions = {}
            # get the script name without the extension & use it to build up the json filename
            script_name = os.path.splitext(os.path.basename(__file__))[0]
            self.args_file = "{}-args.json".format(script_name)

        def load(self):
            # Read in the prior arguments as a dictionary
            if os.path.isfile(self.args_file):
                with open(self.args_file) as data_file:
                    self.stored_args = json.load(data_file)
                    self.loaded_actions = self.stored_args.keys()
            return self

        def get(self, action, arg, default):
            return self.stored_args[action].get(arg) if action in self.loaded_actions else default

        @staticmethod
        def path(relative_path):
            return os.path.normpath(os.path.join(os.getcwd(), relative_path))

        def save(self, args):
            # Store the values of the arguments to the environment to access them in the code
            env.save_arguments(args)
            # Store the values of the arguments so we have them next time we run
            with open(self.args_file, 'w') as data_file:
                # Using vars(args) returns the data as a dictionary
                self.stored_args[EXECUTED_COMMAND] = args.command
                self.stored_args[args.command] = vars(args)
                json.dump(self.stored_args, data_file)

    @staticmethod
    def run():
        """Open the Gooey GUI and then run the selected action with the chosen arguments"""
        LeapGui.parse_args()

        # Record, Anybody, Converter
        if env.config.command == ACTION_RECORD:
            from GuiControl import GuiControl
            gui = GuiControl()
            gui.set_windows_record()

            import time
            countdown = 5
            for ii in range(countdown):
                print("Record starting in {} seconds ...".format(countdown-ii))
                time.sleep(1)

            LeapRecord.start_recording()

            gui.end_record()
            print("End of recording\n")

            print("Loading the animation ...")
            p = Process(target=bvh_animation.animate)
            p.start()
            # wait for bvh_animation to be closed
            p.join()
            return True

        if env.config.command == ACTION_ANYBODY:
            from LogWatcher import log_watcher
            anypy = AnyPy(env.config.any_main_file, env.config.any_files_dir)
            log_watcher.start(os.path.join(anypy.any_path, AnyPy.LOG_FILE))
            anypy.run()
            log_watcher.stop()
            return True

        if env.config.command == ACTION_CONVERTER:
            if env.config.any_file:
                from AnyWriter import AnyWriter
                any_writer = AnyWriter(template_directory='config/anybody_templates/',
                                       output_directory=env.config.file_dir + '/')
                any_writer.write(Pymo_BVHParser().parse(env.config.bvh_file))
            return True

        if env.config.command == ACTION_ANIMATION:
            print("Loading the animation ...")
            bvh_animation.bvh_data = Pymo_BVHParser().parse(env.config.bvh_animation)
            bvh_animation.animate()


if __name__ == "__main__":
    LeapGui.run()
