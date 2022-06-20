import re
import numpy as np
import pandas
import sys

from config.Skeleton import Skeleton
from config.AnybodyFirstFrame import AnybodyFirstFrame
from config.BasisFirstFrame import BasisFirstFrame
from resources.pymo.pymo.data import MocapData
from RotationUtil import rot2eul, get_order
from resources.LeapSDK.v53_python39 import Leap


class LeapData:
    """
    A class to convert LeapMotion frames to PyMO data structure (MocapData)

    Calculates translations (offsets) and rotation data for the joints
    """

    def __init__(self, channel_setting='rotation', frame_rate=0.033333, anybody_basis=True):
        self._skeleton = {}
        self._setting = Skeleton(channel_setting)
        self._motion_channels = []
        self._motions = []
        self._root_name = ''
        self.data = MocapData()

        self.first_frame = None
        self.anybody_first_frame = AnybodyFirstFrame()
        self.basis_first_frame = BasisFirstFrame()
        # anybody_reference = True -> Use Anybody basis from config/*.json (see AnybodyFirstFrame)
        # anybody_reference = False -> Use Leap Motion First Frame for basis
        self.anybody_basis = anybody_basis
        self.status = 0
        self._frame_rate = frame_rate

        self._skeleton = self._setting.skeleton
        # fill channels into skeleton in selected order (i.e. xyz)
        self._skeleton_apply_channels(self._setting.channel_setting)
        self._root_name = self._setting.root_name

        # initialize offsets for each joint
        for joint_name, joint_value in self._skeleton.items():
            joint_value['offsets'] = [0, 0, 0]
            for channel in joint_value['channels']:
                self._motion_channels.append((joint_name, channel))

    def parse(self):
        self.data.skeleton = self._skeleton
        self.data.channel_names = self._motion_channels
        if not self.first_frame:
            sys.exit("No data was recorded - will terminate now!")
        self.data.values = self._motion2dataframe()
        self.data.root_name = self._root_name
        self.data.framerate = self._frame_rate

        return self.data

    def _check_frame(self, frame):
        """
        Check whether frame and hand and fingers are valid, produce error when left hand is shown
        """
        status_no_hand = 1
        status_no_finger = 2
        status_left_hand = 3
        status_valid = 4

        if frame.hands.is_empty:
            if self.status != status_no_hand:
                print("-- No hand found. --")
                self.status = status_no_hand
            return False

        # Get the first hand
        hand = frame.hands[0]

        if hand.is_left:
            if self.status != status_left_hand:
                print("-- Please use your right hand. --")
                self.status = status_left_hand
            return False

        if not hand.is_right and not hand.is_valid:
            return False

        # Check if the hand has any fingers
        fingers = hand.fingers
        if fingers.is_empty:
            if self.status != status_no_finger:
                print("-- No valid fingers found. --")
                self.status = status_no_finger
            return False

        # frame_number = 0 if not self.first_frame else frame.id - self.first_frame.id
        if self.status != status_valid:
            print("-- Valid right hand found, recording data. --")
            self.status = status_valid
        return True

    def add_frame(self, frame):
        if not self._check_frame(frame):
            return None

        # Get the first hand
        hand = frame.hands[0]
        if not self.first_frame:
            self.first_frame = frame
            channel_values = self._get_channel_values(hand, firstframe=True)
            self._motions.append((0, channel_values))
            return

        channel_values = self._get_channel_values(hand)
        self._motions.append((frame.timestamp - self.first_frame.timestamp, channel_values))
        return frame

    def _get_channel_values(self, hand, firstframe=False):
        channel_values = []
        # export_basis = {}
        for joint_name, joint_value in self._skeleton.items():
            # motion data with rotations
            if joint_name == self._root_name:
                x_pos, y_pos, z_pos = LeapData._get_root_offset()
            elif joint_name == 'RightElbow':
                x_pos, y_pos, z_pos = LeapData._get_elbow_offset(hand)
            elif joint_name == 'RightHand':
                x_pos, y_pos, z_pos = LeapData._get_wrist_offset(hand)
            else:
                x_pos, y_pos, z_pos = LeapData._get_finger_offset(joint_name, hand)

            x_rot, y_rot, z_rot = self._calculate_euler_angles(hand, joint_name)

            x_rot *= Leap.RAD_TO_DEG
            y_rot *= Leap.RAD_TO_DEG
            z_rot *= Leap.RAD_TO_DEG

            # if joint_name == 'RightHand':
            #     print(x_rot, y_rot, z_rot)

            if firstframe:
                if self.anybody_basis:
                    x_pos, y_pos, z_pos = self._calculate_offset(joint_name, [x_pos, y_pos, z_pos])
                joint_value['offsets'] = [x_pos, y_pos, z_pos]

                # # dump the basis of leap motion bones
                # if 'End' not in joint_name and 'Root' not in joint_name:
                #     export_basis[joint_name] = np.ndarray.tolist(self._get_basis(hand, joint_name))

            for channel in joint_value['channels']:
                if channel == 'Xposition':
                    channel_values.append((joint_name, channel, x_pos))
                if channel == 'Yposition':
                    channel_values.append((joint_name, channel, y_pos))
                if channel == 'Zposition':
                    channel_values.append((joint_name, channel, z_pos))
                if channel == 'Xrotation':
                    channel_values.append((joint_name, channel, x_rot))
                if channel == 'Yrotation':
                    channel_values.append((joint_name, channel, y_rot))
                if channel == 'Zrotation':
                    channel_values.append((joint_name, channel, z_rot))

        # # dump the basis of leap motion bones
        # if firstframe:
        #     import json
        #     import datetime
        #     with open('../output/{}basis.json'.format(datetime.datetime.today().strftime('%Y%m%d_%H%M%S')), 'w') as o:
        #         json.dump(export_basis, o)

        return channel_values

    def _calculate_euler_angles(self, hand, joint_name):
        initial_hand = self.first_frame.hands[0]

        # special case for root and finger tip
        if joint_name == self._root_name or not self._skeleton[joint_name]['children']:
            return 0.0, 0.0, 0.0

        if self.anybody_basis:
            # compare basis to anybody basis
            parent_initial_basis = self._get_basis_first_frame(self._skeleton[joint_name]['parent'])
            initial_basis = self._get_basis_first_frame(joint_name)
        else:
            # compare basis to first frame from Leap Motion
            parent_initial_basis = self._get_basis(initial_hand, self._skeleton[joint_name]['parent'])
            initial_basis = self._get_basis(initial_hand, joint_name)

        parent_basis = self._get_basis(hand, self._skeleton[joint_name]['parent'])
        basis = self._get_basis(hand, joint_name)

        # if joint_name == 'RightHand':
        #     print(basis)

        # calculation of local rotation matrix - important!!!
        rot = np.matmul(
                np.matmul(
                    initial_basis, np.transpose(basis)
                ),
                np.transpose(
                    np.matmul(
                        parent_initial_basis, np.transpose(parent_basis)
                    )
                )
        )
        return rot2eul(rot)

    def _get_basis(self, hand, joint_name):
        if joint_name == self._root_name:
            return np.array([[1, 0, 0],
                             [0, 1, 0],
                             [0, 0, 1]])
        if joint_name == 'RightElbow':
            return LeapData._basismatrix(hand.arm.basis)
        if joint_name == 'RightHand':
            return LeapData._basismatrix(hand.basis)

        # else, return basis of the finger
        finger, bone_number = LeapData._split_key(joint_name)
        fingerlist = hand.fingers.finger_type(LeapData._get_finger_type(finger))
        bone = fingerlist[0].bone(LeapData._get_bone_type(bone_number))
        return LeapData._basismatrix(bone.basis)

    def _get_basis_first_frame(self, joint_name):
        if joint_name == self._root_name:
            return np.array([[1, 0, 0],
                             [0, 1, 0],
                             [0, 0, 1]])
        return self.anybody_first_frame.get_basis(joint_name)

    def _calculate_offset(self, joint_name, leap_offset):
        if joint_name == self._root_name:
            return 0, 0, 0

        leap_length = np.linalg.norm(leap_offset)

        position = self._get_anybody_position(joint_name)
        position_parent = self._get_anybody_position(self._skeleton[joint_name]['parent'])
        offset_anybody = position - position_parent
        # make a unit vector
        offset_anybody = np.divide(offset_anybody, np.linalg.norm(offset_anybody))
        offset = offset_anybody * leap_length
        return offset[0], offset[1], offset[2]

    def _get_anybody_position(self, joint_name):
        if joint_name == self._root_name:
            return np.array([0, 0, 0])
        return self.anybody_first_frame.get_position(joint_name)

    @staticmethod
    def _get_root_offset():
        return 0, 0, 0

    @staticmethod
    def _get_elbow_offset(hand):
        arm = hand.arm
        return arm.elbow_position.x, arm.elbow_position.y, arm.elbow_position.z

    @staticmethod
    def _get_wrist_offset(hand):
        arm = hand.arm
        x_wrist = hand.wrist_position.x - arm.elbow_position.x
        y_wrist = hand.wrist_position.y - arm.elbow_position.y
        z_wrist = hand.wrist_position.z - arm.elbow_position.z

        return x_wrist, y_wrist, z_wrist

    @staticmethod
    def _get_finger_offset(key, hand):
        key, bone_number = LeapData._split_key(key)

        fingerlist = hand.fingers.finger_type(LeapData._get_finger_type(key))

        # vector between wrist and joint metacarpal proximal (length of carpals)
        if bone_number == 1 or ('Thumb' in key and bone_number == 2):
            bone = fingerlist[0].bone(LeapData._get_bone_type(bone_number))
            return \
                bone.prev_joint.x - hand.wrist_position.x, \
                bone.prev_joint.y - hand.wrist_position.y, \
                bone.prev_joint.z - hand.wrist_position.z

        # vector for bones metacarpal, proximal, intermediate, distal
        bone = fingerlist[0].bone(LeapData._get_bone_type(bone_number - 1))
        return \
            bone.next_joint.x - bone.prev_joint.x, \
            bone.next_joint.y - bone.prev_joint.y, \
            bone.next_joint.z - bone.prev_joint.z

    @staticmethod
    def _split_key(key):
        key_split = re.split('(\d)', key)
        key = key_split[0]
        if key_split[-1] == '_Nub':
            return key, 5
        else:
            return key, int(key_split[1])

    @staticmethod
    def _get_finger_type(key):
        if key == 'RightHandThumb':
            return Leap.Finger.TYPE_THUMB
        if key == 'RightHandIndex':
            return Leap.Finger.TYPE_INDEX
        if key == 'RightHandMiddle':
            return Leap.Finger.TYPE_MIDDLE
        if key == 'RightHandRing':
            return Leap.Finger.TYPE_RING
        if key == 'RightHandPinky':
            return Leap.Finger.TYPE_PINKY
        else:
            raise Exception('Key ({}) did not match'.format(key))

    @staticmethod
    def _get_bone_type(bone_number):
        if bone_number == 4:
            return Leap.Bone.TYPE_DISTAL
        if bone_number == 3:
            return Leap.Bone.TYPE_INTERMEDIATE
        if bone_number == 2:
            return Leap.Bone.TYPE_PROXIMAL
        if bone_number == 1:
            return Leap.Bone.TYPE_METACARPAL
        else:
            raise Exception('bone number ({}) did not match'.format(bone_number))

    @staticmethod
    def _basismatrix(basis):
        return np.array([[basis.x_basis.x, basis.y_basis.x, basis.z_basis.x],
                        [basis.x_basis.y, basis.y_basis.y, basis.z_basis.y],
                        [basis.x_basis.z, basis.y_basis.z, basis.z_basis.z]])

    def _get_channels(self, joint_name, channel_setting):
        if '_Nub' in joint_name:
            return []

        channels_position = ['Xposition', 'Yposition', 'Zposition']
        channels_rotation = ['Xrotation', 'Yrotation', 'Zrotation']

        order = get_order()  # rotation order, i.e. xyz
        channels_rotation = \
            [channels_rotation[order[0]]] + [channels_rotation[order[1]]] + [channels_rotation[order[2]]]

        if channel_setting == 'position' or joint_name == self._root_name:
            return channels_position + channels_rotation

        return channels_rotation

    def _skeleton_apply_channels(self, channel_setting):
        for joint_name, joint_dict in self._skeleton.items():
            joint_dict['channels'] = self._get_channels(joint_name, channel_setting)

    def _motion2dataframe(self):
        """Returns all of the channels parsed from the LeapMotion sensor as a pandas DataFrame"""

        time_index = pandas.to_timedelta([f[0] for f in self._motions], unit='s')
        frames = [f[1] for f in self._motions]
        channels = np.asarray([[channel[2] for channel in frame] for frame in frames])
        column_names = ['%s_%s' % (c[0], c[1]) for c in self._motion_channels]

        return pandas.DataFrame(data=channels, index=time_index, columns=column_names)
