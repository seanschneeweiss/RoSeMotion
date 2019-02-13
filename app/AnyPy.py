import os
import glob
import shutil

from resources.AnyPyTools.anypytools import AnyPyProcess
from resources.AnyPyTools.anypytools import AnyMacro
from resources.AnyPyTools.anypytools.macro_commands import (MacroCommand, Load, SetValue, SetValue_random,  Dump,
                                                            SaveDesign, LoadDesign, SaveValues, LoadValues,
                                                            UpdateValues, OperationRun)
from config.Configuration import env

class AnyPy:
    LOAD = 'load'
    INITIAL_CONDITIONS = 'initial_conditions'
    KINEMATICS = 'kinematics'
    INVERSE_DYNAMICS = 'inverse_dynamics'

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
                         AnyPy.INVERSE_DYNAMICS: OperationRun("Main.Study.InverseDynamics")}

        for operation in self.operations:
            self.macrolist.append(operation_cmd[operation])

        print('Starting Anybody with the operations: {}'.format(self.operations))
        print('Starting Anybody with the macros: {}'.format(AnyMacro(self.macrolist)))
        print('Executing "{}" in "{}"'.format(any_path, any_model))
        cwd = os.getcwd()
        os.chdir(any_path)
        app = AnyPyProcess(num_processes=1,
                           return_task_info=True,
                           anybodycon_path="C:/Program Files/AnyBody Technology/AnyBody.7.1/AnyBodyCon.exe")

        app.start_macro(macrolist=self.macrolist,
                        logfile='anybody.log')
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
        # TODO
        raise ValueError('Results not supported')

    anypy.initialize()
    # tools.parse_anybodycon_output()
