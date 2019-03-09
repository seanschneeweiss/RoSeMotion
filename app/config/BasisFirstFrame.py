import json
import numpy as np


class BasisFirstFrame:

    def __init__(self):
        self.joint_values = None
        self.load('config/basis_first_frame.json')

    def load(self, filename):
        with open(filename) as o:
            self.joint_values = json.load(o)

    def get_basis(self, joint_name):
        return np.array(self.joint_values[joint_name])
