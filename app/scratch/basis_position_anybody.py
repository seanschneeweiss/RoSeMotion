from resources.AnyPyTools.anypytools import AnyPyProcess
from resources.AnyPyTools.anypytools import AnyMacro
from resources.AnyPyTools.anypytools import tools
from resources.AnyPyTools.anypytools.macro_commands import (MacroCommand, Load, SetValue, SetValue_random,  Dump,
                                                            SaveDesign, LoadDesign, SaveValues, LoadValues,
                                                            UpdateValues, SaveData, OperationRun)
import os
import json
import numpy as np


cwd = os.getcwd()
os.chdir('D:\\RobinSean\\Sean\\5. Master\\Projekt CSE\\AnybodyModelle\\regensburg-ulm-hand-model\\AnyBody\\Application\\Examples\\FreeHandMove')
print(os.getcwd())
# patella_tendon_lengths = [
#     0.02 + i*0.01
#     for i in range(7)
# ]
# print(patella_tendon_lengths)

app = AnyPyProcess(num_processes=1,
                   return_task_info=True,
                   anybodycon_path="C:/Program Files/AnyBody Technology/AnyBody.7.1/AnyBodyCon.exe")
# macrolist = [
#     Load('Knee.any'),
#     # SetValue('Main.MyModel.PatellaLigament.DriverPos', patella_tendon_lengths ),
#     SetValue('Main.MyStudy.tStart', 1),
#     SetValue('Main.MyStudy.tEnd', 2),
#     OperationRun('Main.MyStudy.InitialConditions'),
#     OperationRun('Main.MyStudy.Kinematics'),
#     OperationRun('Main.MyStudy.InverseDynamics'),
#     # Dump('Main.MyStudy.Output.Abscissa.t'),
#     # Dump('Main.MyStudy.Output.MaxMuscleActivity'),
#     # Dump('Main.MyModel.PatellaLigament.DriverPos'),
# ]

macrolist = [
    Load('FreeHand.Main.any'),
    # OperationRun('Main.RunMotionAndParameterOptimizationSequence')
    # OperationRun('Main.MyStudy.InverseDynamics'),
]

joint_values = ['Axes0', 'r0']

# dump of joint_values for all fingers
finger_joints = {
    'Finger1': {'DistalPhalanx': {}, 'ProximalPhalanx': {}, 'Metacarpal': {}},
    'Finger2': {'DistalPhalanx': {}, 'MiddlePhalanx': {}, 'ProximalPhalanx': {}, 'Metacarpal': {}},
    'Finger3': {'DistalPhalanx': {}, 'MiddlePhalanx': {}, 'ProximalPhalanx': {}, 'Metacarpal': {}},
    'Finger4': {'DistalPhalanx': {}, 'MiddlePhalanx': {}, 'ProximalPhalanx': {}, 'Metacarpal': {}},
    'Finger5': {'DistalPhalanx': {}, 'MiddlePhalanx': {}, 'ProximalPhalanx': {}, 'Metacarpal': {}}}
finger_joint_path = 'Main.HumanModel.BodyModel.Right.ShoulderArm.Seg.Hand.{}.Seg.{}.{}'
finger_dumps = []
for finger_name in finger_joints:
    for joint_name in finger_joints[finger_name]:
        for value in joint_values:
            macrolist.append(Dump(finger_joint_path.format(finger_name, joint_name, value)))
            finger_dumps.append({'finger_name': finger_name, 'joint_name': joint_name, 'value': value})
    macrolist.append(Dump(finger_joint_path.format(finger_name, 'DistalPhalanx', 'DistalJointSurfaceNode') + '.r'))
    finger_dumps.append({'finger_name': finger_name, 'joint_name': 'DistalJointSurfaceNode', 'value': 'r'})

# dump of joint_values for elbow and wrist
other_joints = {'WristJointSeg': {},
                'Radius': {}}
other_joint_path = 'Main.HumanModel.BodyModel.Right.ShoulderArm.Seg.{}.{}'
other_dumps = []
for joint_name in other_joints:
    for value in joint_values:
        macrolist.append(Dump(other_joint_path.format(joint_name, value)))
        other_dumps.append({'joint_name': joint_name, 'value': value})

output = app.start_macro(macrolist)

# save finger joints dumps into finger_joints dictionary
for d in finger_dumps:
    finger_joints[d['finger_name']][d['joint_name']][d['value']] = np.ndarray.tolist(
        output[0][finger_joint_path.format(d['finger_name'], d['joint_name'], d['value'])])
print(finger_joints)

# save other joints dumps into other_joints dictionary
for d in other_dumps:
    other_joints[d['joint_name']][d['value']] = np.ndarray.tolist(
        output[0][other_joint_path.format(d['joint_name'], d['value'])])
print(other_joints)
# parameter_study_macro = AnyMacro(macro, number_of_macros= len(patella_tendon_lengths))
os.chdir(cwd)

anybody_joint_values = finger_joints
anybody_joint_values.update(other_joints)
json.dump(anybody_joint_values, open('../config/anybody_joint_values.json', 'w'))
