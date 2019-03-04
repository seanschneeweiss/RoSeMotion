import json
import numpy as np


class AnybodyFirstFrame:

    def __init__(self, update_values=False):
        self.joint_values = None
        if not update_values:
            self.load('anybody_joint_values.json')

    def load(self, filename):
        self.joint_values = json.load(open(filename))

    def get_basis(self, joint_name):
        translate = {
            'RightElbow': np.array(self.joint_values['Radius']['Axes0']),
            'RightHand': np.array(self.joint_values['WristJointSeg']['Axes0']),
            'RightHandThumb2': np.array(self.joint_values['Finger1']['Metacarpal']['Axes0']),
            'RightHandThumb3': np.array(self.joint_values['Finger1']['ProximalPhalanx']['Axes0']),
            'RightHandThumb4': np.array(self.joint_values['Finger1']['DistalPhalanx']['Axes0']),
            'RightHandIndex1': np.array(self.joint_values['Finger2']['Metacarpal']['Axes0']),
            'RightHandIndex2': np.array(self.joint_values['Finger2']['ProximalPhalanx']['Axes0']),
            'RightHandIndex3': np.array(self.joint_values['Finger2']['MiddlePhalanx']['Axes0']),
            'RightHandIndex4': np.array(self.joint_values['Finger2']['DistalPhalanx']['Axes0']),
            'RightHandMiddle1': np.array(self.joint_values['Finger3']['Metacarpal']['Axes0']),
            'RightHandMiddle2': np.array(self.joint_values['Finger3']['ProximalPhalanx']['Axes0']),
            'RightHandMiddle3': np.array(self.joint_values['Finger3']['MiddlePhalanx']['Axes0']),
            'RightHandMiddle4': np.array(self.joint_values['Finger3']['DistalPhalanx']['Axes0']),
            'RightHandRing1': np.array(self.joint_values['Finger4']['Metacarpal']['Axes0']),
            'RightHandRing2': np.array(self.joint_values['Finger4']['ProximalPhalanx']['Axes0']),
            'RightHandRing3': np.array(self.joint_values['Finger4']['MiddlePhalanx']['Axes0']),
            'RightHandRing4': np.array(self.joint_values['Finger4']['DistalPhalanx']['Axes0']),
            'RightHandPinky1': np.array(self.joint_values['Finger5']['Metacarpal']['Axes0']),
            'RightHandPinky2': np.array(self.joint_values['Finger5']['ProximalPhalanx']['Axes0']),
            'RightHandPinky3': np.array(self.joint_values['Finger5']['MiddlePhalanx']['Axes0']),
            'RightHandPinky4': np.array(self.joint_values['Finger5']['DistalPhalanx']['Axes0']),
        }
        anybody_basis = translate[joint_name]
        anybody2leap_rotation = np.array([[0, 0, -1], [0, 1, 0], [0, 0, 1]])
        return np.matmul(anybody2leap_rotation, anybody_basis)
