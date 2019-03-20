import os
import datetime
import glob
import shutil
import subprocess

from resources.AnyPyTools.anypytools import AnyPyProcess
from resources.AnyPyTools.anypytools import AnyMacro
from resources.AnyPyTools.anypytools import abcutils
from resources.AnyPyTools.anypytools.macro_commands import (MacroCommand, Load, SetValue, SetValue_random,  Dump,
                                                            SaveDesign, LoadDesign, SaveValues, LoadValues,
                                                            UpdateValues, SaveData, OperationRun)
from AnyWriter import AnyWriter
from config.Configuration import env
from AnybodyResults import AnybodyResults


class AnyPy:
    LOAD = 'load'
    INITIAL_CONDITIONS = 'initial_conditions'
    KINEMATICS = 'kinematics'
    INVERSE_DYNAMICS = 'inverse_dynamics'
    SAVE_H5 = 'save_h5'
    LOAD_H5 = 'load_h5'
    DUMP_JOINT_ANGLES = 'dump_angles'
    DUMP_STEPS = 'dump_steps'
    DUMP_LEAP_VECTORS = 'dump_leap_vectors'
    REPLAY = 'replay'
    LOG_FILE = 'AnyPy{}.log'.format(datetime.datetime.today().strftime('%Y%m%d_%H%M%S'))

    INTERPOL_DIR = '/Model/InterpolVec'

    def __init__(self, main_filepath, template_directory):
        self.any_path, self.any_model = os.path.split(main_filepath)
        self.main_filepath = main_filepath
        self.template_directory = template_directory
        self.operations = []
        self.macrolist = []
        self.output = None

        if env.args('any_interpol_files'):
            print("Using interpolation files from {}".format(os.path.normpath(self.any_path + AnyPy.INTERPOL_DIR)))

        if env.args('any_bvh_file'):
            print("Convert bvh file to anybody interpolation files")
            from resources.pymo.pymo.parsers import BVHParser as Pymo_BVHParser
            any_writer = AnyWriter(template_directory='config/anybody_templates/',
                                   output_directory=os.path.normpath(self.any_path + AnyPy.INTERPOL_DIR) + '/')
            any_writer.write(Pymo_BVHParser().parse(env.config.any_bvh_file))

        if env.args('any_files_dir'):
            self.copy_files()

        # remove frames from start and end (cut)
        if env.config.start_frame or env.config.end_frame:
            start_frame = int(env.config.start_frame) - 1 if env.config.start_frame else 0
            end_frame = int(env.config.end_frame) - 1 if 'end' not in env.config.end_frame.lower() else None
            any_writer = AnyWriter(output_directory=os.path.normpath(self.any_path + AnyPy.INTERPOL_DIR) + '/')
            any_writer.extract_frames(start_frame, end_frame)
            any_writer.extract_frame_timeseries(start_frame, end_frame)

        self.output_path = ''
        if env.args('output_file_path'):
            self.output_path = os.path.normpath(
                os.path.join(os.path.split(env.config.output_file_path)[0],
                             os.path.split(env.config.output_file_path)[1].replace(".anydata.h5", "") + '.anydata.h5'))

        self.initialize_operations()

    def initialize_operations(self):
        """build the macrolist executed by AnyPyTools"""
        operation_cmd = {AnyPy.LOAD: Load(self.main_filepath),
                         AnyPy.INITIAL_CONDITIONS: OperationRun("Main.Study.InitialConditions"),
                         AnyPy.KINEMATICS: OperationRun("Main.Study.Kinematics"),
                         AnyPy.INVERSE_DYNAMICS: OperationRun("Main.Study.InverseDynamics"),
                         AnyPy.SAVE_H5: SaveData('Main.Study', self.output_path),
                         AnyPy.DUMP_JOINT_ANGLES: Dump('Main.Study.Output.JointAngleOutputs'),
                         AnyPy.DUMP_STEPS: Dump('Main.Study.nStep'),
                         AnyPy.DUMP_LEAP_VECTORS: Dump('Main.HumanModel.Mannequin.Posture.Right')}

        if env.config.load:
            self.add_operation(AnyPy.LOAD)
        if env.config.initial_conditions:
            self.add_operation(AnyPy.INITIAL_CONDITIONS)
        if env.config.kinematic:
            self.add_operation(AnyPy.KINEMATICS)
        if env.config.inverse_dynamics:
            self.add_operation(AnyPy.INVERSE_DYNAMICS)
        if env.config.plot:
            # dump interpolated joint angles
            self.add_operation(AnyPy.DUMP_JOINT_ANGLES)
            # dump nStep
            self.add_operation(AnyPy.DUMP_STEPS)
            # dump Mannequin vectors including the joint angles from the bvh file
            self.add_operation(AnyPy.DUMP_LEAP_VECTORS)

        if self.output_path:
            # save study output to hdf5, to view and replay analysis later
            self.add_operation(AnyPy.SAVE_H5)

        for operation in self.operations:
            self.macrolist.append(operation_cmd[operation])

    def post_operations(self):
        macro_output_path = 'classoperation Main.Study.Output "Load data" --file="{}"'.format(self.output_path)

        """build the macrolist executed by AnyPyTools"""
        operation_cmd = {AnyPy.LOAD: Load(self.main_filepath),
                         AnyPy.LOAD_H5: MacroCommand(macro_output_path),
                         AnyPy.REPLAY: OperationRun("Main.Study.ReplayKinematics")}

        self.macrolist = []
        for operation in operation_cmd:
            self.macrolist.append(str(operation_cmd[operation]))

        print('Starting Anybody with the macros:\n{}'.format(self.macrolist))
        print('Executing "{}" in "{}"'.format(self.any_path, self.any_model))

        # save current working directory and change to Anybody project folder
        cwd = os.getcwd()
        os.chdir(self.any_path)

        # write macro file to be opened by AnyBody GUI
        macro_replay_path = os.path.join(self.any_path, 'replay.anymcr')
        with open(macro_replay_path, 'wb') as macro_file:
            macro_file.write("\n".join(self.macrolist).encode("UTF-8"))
            macro_file.flush()
            anybodycmd = [os.path.realpath('C:/Program Files/AnyBody Technology/AnyBody.7.1/AnyBody.exe'),
                          "-m", macro_file.name]

        # execute AnyBody GUI with the command from anybodycmd
        subprocess.Popen(anybodycmd)

        # change back to original folder
        os.chdir(cwd)

    def add_operation(self, operation):
        """add operation to a list if not already in the list (unique)"""
        if operation not in self.operations:
            self.operations.append(operation)

    def copy_files(self):
        """"copy interpolation files"""
        for file in glob.glob(self.template_directory + r'/*.any'):
            print('copying "{}" to "{}"'.format(file,
                                                os.path.normpath(self.any_path +
                                                                 AnyPy.INTERPOL_DIR + "/" + os.path.split(file)[-1])))
            shutil.copy(file, self.any_path + AnyPy.INTERPOL_DIR)

    def run(self):
        if not self.macrolist:
            raise Exception("No operation for AnyBody was selected -> will terminate now")

        # print('Starting Anybody with the operations: {}'.format(self.operations))
        print('Starting Anybody with the macros:\n{}'.format(AnyMacro(self.macrolist)))
        print('Executing "{}" in "{}"'.format(self.any_path, self.any_model))

        # save current working directory and change to Anybody project folder
        cwd = os.getcwd()
        os.chdir(self.any_path)
        # app = AnyPyProcess(return_task_info=True,
        #                   anybodycon_path=tools.get_anybodycon_path())
        app = AnyPyProcess(return_task_info=True,
                           anybodycon_path="C:/Program Files/AnyBody Technology/AnyBody.7.1/AnyBodyCon.exe")

        self.output = app.start_macro(macrolist=self.macrolist,
                                      logfile=AnyPy.LOG_FILE)

        # change back to original folder
        os.chdir(cwd)

    def plot(self):
        """open the plot for the joint angles"""
        print('Loading the plot ...')
        AnybodyResults(self.output).plot()
