import json
import numpy as np


# rotation matrix from anybody to LeapMotion
ROTATION_KS = np.array([[0, 0, 1],
                        [0, 1, 0],
                        [-1, 0, 0]])
ROTATION_FINGER = np.array([[0, -1, 0],
                            [-1, 0, 0],
                            [0, 0, -1]])
ROTATION_THUMB = np.array([[0.9497,    0.1712,   -0.2624],
                           [-0.0351,   -0.7742,   -0.6320],
                           [-0.3113,    0.6094,   -0.7292]])
ROTATION_HAND = np.array([[-1, 0, 0],
                          [0, 0, 1],
                          [0, 1, 0]])


class AnybodyFirstFrame:

    def __init__(self, update_values=False):
        self.joint_values = None
        if not update_values:
            self.load('config/anybody_joint_values_waagerecht.json')

    def load(self, filename):
        with open(filename) as o:
            self.joint_values = json.load(o)

    def get_basis(self, joint_name):
        anybody_basis = self.joint_values[joint_name]['Axes0']
        # print("joint: {}, basis: \n{}".format(joint_name, np.matmul(ROTATION_BASIS,
        # np.matmul(ROTATION_KS, np.array(anybody_basis)))))
        if joint_name in ('RightElbow', 'RightHand'):
            return np.matmul(ROTATION_HAND, np.transpose(np.array(anybody_basis)))
        if 'RightHandThumb' in joint_name:
            return np.matmul(ROTATION_THUMB, np.transpose(np.array(anybody_basis)))
        return np.matmul(ROTATION_FINGER, np.transpose(np.array(anybody_basis)))

    def get_position(self, joint_name):
        if '_Nub' in joint_name:
            anybody_position = self.joint_values[joint_name]['r']
        else:
            anybody_position = self.joint_values[joint_name]['r0']
        return np.matmul(ROTATION_KS, np.array(anybody_position) * 1000)
