import os
import glob
import shutil

from resources.AnyPyTools.anypytools import AnyPyProcess
from resources.AnyPyTools.anypytools import AnyMacro
from resources.AnyPyTools.anypytools import tools
from resources.AnyPyTools.anypytools.macro_commands import (MacroCommand, Load, SetValue, SetValue_random,  Dump,
                                                            SaveDesign, LoadDesign, SaveValues, LoadValues,
                                                            UpdateValues, SaveData, OperationRun)
from config.Configuration import env


class AnyPy:
    LOAD = 'load'
    INITIAL_CONDITIONS = 'initial_conditions'
    KINEMATICS = 'kinematics'
    INVERSE_DYNAMICS = 'inverse_dynamics'
    SAVE_HDF5 = 'hdf5'
    # SAVE_CSV = 'csv'
    LOG_FILE = 'AnyPy.log'

    def __init__(self, main_filepath, template_directory):
        self.main_filepath = main_filepath
        self.template_directory = template_directory
        self.operations = [AnyPy.LOAD]
        self.macrolist = []

    def initialize(self):
        any_path, any_model = os.path.split(self.main_filepath)

        # copy interpolation files
        if self.template_directory:
            for file in glob.glob(self.template_directory + r'/*.any'):
                shutil.copy(file, any_path + '/Model/InterpolVec')

        # build macrolist
        operation_cmd = {AnyPy.LOAD: Load(any_model),
                         AnyPy.INITIAL_CONDITIONS: OperationRun("Main.Study.InitialConditions"),
                         AnyPy.KINEMATICS: OperationRun("Main.Study.Kinematics"),
                         AnyPy.INVERSE_DYNAMICS: OperationRun("Main.Study.InverseDynamics"),
                         AnyPy.SAVE_HDF5: SaveData('Main.Study', 'output.anydata.h5')}

        for operation in self.operations:
            self.macrolist.append(operation_cmd[operation])

        print('Starting Anybody with the operations: {}'.format(self.operations))
        print('Starting Anybody with the macros: {}'.format(AnyMacro(self.macrolist)))
        print('Executing "{}" in "{}"'.format(any_path, any_model))
        cwd = os.getcwd()
        os.chdir(any_path)
        app = AnyPyProcess(return_task_info=True,
                           anybodycon_path=tools.get_anybodycon_path())

        app.start_macro(macrolist=self.macrolist,
                        logfile=AnyPy.LOG_FILE)
        os.chdir(cwd)

    def add_operation(self, operation):
        if operation not in self.operations:
            self.operations.append(operation)


def run():
    anypy = AnyPy(env.config.any_main_file, env.config.any_files_dir)
    if env.config.load:
        anypy.add_operation(AnyPy.LOAD)
    if env.config.initial_conditions:
        anypy.add_operation(AnyPy.INITIAL_CONDITIONS)
    if env.config.kinematic:
        anypy.add_operation(AnyPy.KINEMATICS)
    if env.config.inverse_dynamics:
        anypy.add_operation(AnyPy.INVERSE_DYNAMICS)
    if env.config.results:
        anypy.add_operation(AnyPy.SAVE_HDF5)

    anypy.initialize()