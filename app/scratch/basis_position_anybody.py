from resources.AnyPyTools.anypytools import AnyPyProcess
from resources.AnyPyTools.anypytools import AnyMacro
from resources.AnyPyTools.anypytools import tools
from resources.AnyPyTools.anypytools.macro_commands import (MacroCommand, Load, SetValue, SetValue_random,  Dump,
                                                            SaveDesign, LoadDesign, SaveValues, LoadValues,
                                                            UpdateValues, SaveData, OperationRun)
import os
import json
import numpy as np


app = AnyPyProcess(num_processes=1,
                   return_task_info=True,
                   anybodycon_path="C:/Program Files/AnyBody Technology/AnyBody.7.1/AnyBodyCon.exe")
macrolist = [
    Load('FreeHand.Main.any'),
]

joint_values = ['Axes0', 'r0']
joint_prefix = 'Main.HumanModel.BodyModel.Right.ShoulderArm.Seg.'
joints = {
    'RightElbow': {'path': joint_prefix + 'Radius', 'values': joint_values},
    'RightHand': {'path': joint_prefix + 'WristJointSeg', 'values': joint_values},
    'RightHandThumb2': {'path': joint_prefix + 'Hand.Finger1.Seg.Metacarpal', 'values': joint_values},
    'RightHandThumb3': {'path': joint_prefix + 'Hand.Finger1.Seg.ProximalPhalanx', 'values': joint_values},
    'RightHandThumb4': {'path': joint_prefix + 'Hand.Finger1.Seg.DistalPhalanx', 'values': joint_values},
    'RightHandThumb4_End': {'path': joint_prefix + 'Hand.Finger1.Seg.DistalPhalanx.DistalJointSurfaceNode',
                            'values': ['r']},
    'RightHandIndex1': {'path': joint_prefix + 'Hand.Finger2.Seg.Metacarpal', 'values': joint_values},
    'RightHandIndex2': {'path': joint_prefix + 'Hand.Finger2.Seg.ProximalPhalanx', 'values': joint_values},
    'RightHandIndex3': {'path': joint_prefix + 'Hand.Finger2.Seg.MiddlePhalanx', 'values': joint_values},
    'RightHandIndex4': {'path': joint_prefix + 'Hand.Finger2.Seg.DistalPhalanx', 'values': joint_values},
    'RightHandIndex4_End': {'path': joint_prefix + 'Hand.Finger2.Seg.DistalPhalanx.DistalJointSurfaceNode',
                            'values': ['r']},
    'RightHandMiddle1': {'path': joint_prefix + 'Hand.Finger3.Seg.Metacarpal', 'values': joint_values},
    'RightHandMiddle2': {'path': joint_prefix + 'Hand.Finger3.Seg.ProximalPhalanx', 'values': joint_values},
    'RightHandMiddle3': {'path': joint_prefix + 'Hand.Finger3.Seg.MiddlePhalanx', 'values': joint_values},
    'RightHandMiddle4': {'path': joint_prefix + 'Hand.Finger3.Seg.DistalPhalanx', 'values': joint_values},
    'RightHandMiddle4_End': {'path': joint_prefix + 'Hand.Finger3.Seg.DistalPhalanx.DistalJointSurfaceNode',
                             'values': ['r']},
    'RightHandRing1': {'path': joint_prefix + 'Hand.Finger4.Seg.Metacarpal', 'values': joint_values},
    'RightHandRing2': {'path': joint_prefix + 'Hand.Finger4.Seg.ProximalPhalanx', 'values': joint_values},
    'RightHandRing3': {'path': joint_prefix + 'Hand.Finger4.Seg.MiddlePhalanx', 'values': joint_values},
    'RightHandRing4': {'path': joint_prefix + 'Hand.Finger4.Seg.DistalPhalanx', 'values': joint_values},
    'RightHandRing4_End': {'path': joint_prefix + 'Hand.Finger4.Seg.DistalPhalanx.DistalJointSurfaceNode',
                           'values': ['r']},
    'RightHandPinky1': {'path': joint_prefix + 'Hand.Finger5.Seg.Metacarpal', 'values': joint_values},
    'RightHandPinky2': {'path': joint_prefix + 'Hand.Finger5.Seg.ProximalPhalanx', 'values': joint_values},
    'RightHandPinky3': {'path': joint_prefix + 'Hand.Finger5.Seg.MiddlePhalanx', 'values': joint_values},
    'RightHandPinky4': {'path': joint_prefix + 'Hand.Finger5.Seg.DistalPhalanx', 'values': joint_values},
    'RightHandPinky4_End': {'path': joint_prefix + 'Hand.Finger5.Seg.DistalPhalanx.DistalJointSurfaceNode',
                            'values': ['r']}}

# Add the dumps to the macrolist
for joint_name in joints:
    for value in joints[joint_name]['values']:
        macrolist.append(Dump(joints[joint_name]['path'] + '.' + value))

cwd = os.getcwd()
os.chdir('D:\\RobinSean\\Sean\\5. Master\\Projekt CSE\\AnybodyModelle\\regensburg-ulm-hand-model\\AnyBody'
         '\\Application\\Examples\\FreeHandMove')

output = app.start_macro(macrolist)

os.chdir(cwd)

# save as json
result = {}
for joint_name in joints:
    result[joint_name] = {}
    for value in joints[joint_name]['values']:
        result[joint_name][value] = np.ndarray.tolist(output[0][joints[joint_name]['path'] + '.' + value])
json.dump(result, open('../config/anybody_joint_values.json', 'w'))
