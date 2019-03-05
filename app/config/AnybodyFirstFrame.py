import json
import numpy as np


# rotation matrix from anybody to LeapMotion
ROTATION_KS = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])
ROTATION_BASIS = np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]])
ROTATION_WRIST = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])


class AnybodyFirstFrame:

    def __init__(self, update_values=False):
        self.joint_values = None
        if not update_values:
            self.load('config/anybody_joint_values.json')

    def load(self, filename):
        self.joint_values = json.load(open(filename))

    def get_basis(self, joint_name):
        anybody_basis = self.joint_values[joint_name]['Axes0']
        # print("joint: {}, basis: \n{}".format(joint_name, np.matmul(ROTATION_BASIS, np.matmul(ROTATION_KS, np.array(anybody_basis)))))
        if joint_name in ('RightElbow', 'RightHand'):
            rotation = ROTATION_WRIST
        else:
            rotation = ROTATION_BASIS
        return np.matmul(rotation, np.matmul(ROTATION_KS, np.transpose(np.array(anybody_basis))))
    
    def get_position(self, joint_name):
        if '_End' in joint_name:
            anybody_position = self.joint_values[joint_name]['r']
        else:
            anybody_position = self.joint_values[joint_name]['r0']
        return np.matmul(ROTATION_KS, np.array(anybody_position) * 1000)
