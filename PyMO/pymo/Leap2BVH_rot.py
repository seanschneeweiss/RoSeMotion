import inspect
import os
import re
import sys

import numpy as np
from pymo.RotationUtil import rot2eul, get_order

from leapmotion_setup_rot import root_name, skeleton_no_channels, framerate
from pymo.data import MocapData

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = '../../lib/x64' if sys.maxsize > 2 ** 32 else '../../lib/x86'

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap


class Leap2BVH:
    """
    A class to convert LeapMotion frames to PyMO data structure (MocapData) to be parsed to a BVH file

    Calculates translations (offsets) and rotation data for the joints
    """

    def __init__(self, filename=None):
        self._skeleton = {}
        self.bone_context = []
        self._motion_channels = []
        self._motions = []
        self.current_token = 0
        self.framerate = 0.0
        self.root_name = ''
        self.data = MocapData()

        self.do()

    def parse(self):
        self.data.skeleton = self._skeleton
        self.data.channel_names = self._motion_channels
        self.data.values = self._to_DataFrame()
        self.data.root_name = self.root_name
        self.data.framerate = self.framerate

        return self.data

    def do(self):
        self._skeleton = skeleton_no_channels
        self._skeleton_apply_channels()  # fill channels into skeleton in selected order (i.e. xyz)

        # self._motion_channels = motion_channels
        self.root_name = root_name
        self.framerate = framerate  # TODO: framerate

        # frame_count = 188#TODO:frame_count
        # frame_time = 0.0
        # self._motions = [()] * frame_count

        for key, value in self._skeleton.items():
            value['offsets'] = [0, 0, 0]
            for channel in value['channels']:
                self._motion_channels.append((key, channel))

        # for ii in range(frame_count):
        #     channel_values = []
        #     for key, value in self._skeleton.items():
        #         for channel in value['channels']:
        #             channel_values.append((key, channel, float(1)))
        #     self._motions[ii] = (frame_time, channel_values)
        #     frame_time = frame_time + framerate

    def add_frame(self, frame_id, hand):
        channel_values = []
        for key, value in self._skeleton.items():
            if frame_id == 0:
                # offsets
                if key == 'Leap_Root':
                    x_offset, y_offset, z_offset, _, _, _ = self._get_root_values()
                elif key == 'RightElbow':
                    x_offset, y_offset, z_offset, _, _, _ = self._get_elbow_values(hand)
                elif key == 'RightHand':
                    x_offset, y_offset, z_offset, _, _, _ = self._get_wrist_values(hand)
                elif 'End' in key:
                    # Workaround for getting motion data also from finger tip by adding a not used end
                    x_offset = y_offset = z_offset = 0.0
                else:
                    x_offset, y_offset, z_offset, _, _, _ = self._get_finger_values(key, hand)
                value['offsets'] = [x_offset, y_offset, z_offset]  # y, z, x

                # print("pitch hand x = {}, angle hand x = {}".format(hand.basis.x_basis.pitch * Leap.RAD_TO_DEG,
                #                                                     hand.basis.x_basis.angle_to(Leap.Vector.x_axis) * Leap.RAD_TO_DEG))

            for channel in value['channels']:
                # motion data with rotations
                if key == 'Leap_Root':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = self._get_root_values()
                elif key == 'RightElbow':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = self._get_elbow_values(hand)
                elif key == 'RightHand':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = self._get_wrist_values(hand)
                else:
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = self._get_finger_values(key, hand)

                if channel == 'Xposition':
                    channel_values.append((key, channel, x_pos))
                if channel == 'Yposition':
                    channel_values.append((key, channel, y_pos))
                if channel == 'Zposition':
                    channel_values.append((key, channel, z_pos))
                if channel == 'Xrotation':
                    channel_values.append((key, channel, x_rot))
                if channel == 'Yrotation':
                    channel_values.append((key, channel, y_rot))
                if channel == 'Zrotation':
                    channel_values.append((key, channel, z_rot))

        self._motions.append((frame_id, channel_values))

    @staticmethod
    def _get_root_values():
        return 0, 0, 0, 0, 0, 0

    def _get_elbow_values(self, hand):
        arm = hand.arm

        x_elbow = arm.elbow_position.x
        y_elbow = arm.elbow_position.y
        z_elbow = arm.elbow_position.z

        # rotation matrix from basis vectors
        rotmat = self._basis2rot(arm.basis)
        eul_x, eul_y, eul_z = rot2eul(rotmat)

        return \
            x_elbow, \
            y_elbow, \
            z_elbow, \
            eul_x * Leap.RAD_TO_DEG, \
            eul_y * Leap.RAD_TO_DEG, \
            eul_z * Leap.RAD_TO_DEG

    def _get_wrist_values(self, hand):
        arm = hand.arm

        x_wrist = hand.wrist_position.x - arm.elbow_position.x
        y_wrist = hand.wrist_position.y - arm.elbow_position.y
        z_wrist = hand.wrist_position.z - arm.elbow_position.z

        # rotation matrix from basis vectors

        rotmat_prev = self._basis2rot(arm.basis)
        rotmat_next = self._basis2rot(hand.basis)
        eul_x, eul_y, eul_z = rot2eul(np.matmul(rotmat_next, np.transpose(rotmat_prev)))

        return \
            x_wrist, \
            y_wrist, \
            z_wrist, \
            eul_x * Leap.RAD_TO_DEG, \
            eul_y * Leap.RAD_TO_DEG, \
            eul_z * Leap.RAD_TO_DEG

    def _get_finger_values(self, key, hand):
        key, bone_number = self._split_key(key)

        fingerlist = hand.fingers.finger_type(self._get_finger_type(key))

        # vector between wrist and metacarpal proximal (carpals)
        if bone_number == 1 or ('Thumb' in key and bone_number == 2):
            bone = fingerlist[0].bone(self._get_bone_type(bone_number))

            # print("1: key: {}, bone_number: {}, bone: {}, prev_joint: {}"
            #       .format(key, bone_number, bone, bone.prev_joint))
            # print("p1_rot = [{}; {}; {}];".format(x_wrist, y_wrist, z_wrist))
            # print("p2_rot = [{}; {}; {}];".format(bone.prev_joint.x, bone.prev_joint.y, bone.prev_joint.z))
            # print("p3_rot = [{}; {}; {}];".format(bone.next_joint.x, bone.next_joint.y, bone.next_joint.z))

            # print('bone.next_joint.x = {}, bone.prev_joint.x = {}, x_wrist = {}, vec_prev = {}'.format(bone.next_joint.x, bone.prev_joint.x, x_wrist, vec_prev[0]))
            # print('bone.next_joint.y = {}, bone.prev_joint.y = {}, y_wrist = {}, vec_prev = {}'.format(bone.next_joint.y, bone.prev_joint.y, y_wrist, vec_prev[1]))
            # print('bone.next_joint.z = {}, bone.prev_joint.z = {}, z_wrist = {}, vec_prev = {}'.format(bone.next_joint.z, bone.prev_joint.z, z_wrist, vec_prev[2]))

            return \
                bone.prev_joint.x - hand.wrist_position.x, \
                bone.prev_joint.y - hand.wrist_position.y, \
                bone.prev_joint.z - hand.wrist_position.z, \
                0.0, \
                0.0, \
                0.0

        # vector for bones metacarpal, proximal, intermediate, distal
        bone_prev = fingerlist[0].bone(self._get_bone_type(bone_number - 1))

        #  no rotation for finger tip
        if not bone_number == 5:
            bone_next = fingerlist[0].bone(self._get_bone_type(bone_number))

            # rotation matrix from basis vectors
            rotmat_prev = self._basis2rot(bone_prev.basis)
            rotmat_next = self._basis2rot(bone_next.basis)

            # rotation matrix between rotmat_prev and rotmat_next by multiplying
            eul_x, eul_y, eul_z = rot2eul(np.matmul(rotmat_next, np.transpose(rotmat_prev)))

            return \
                bone_prev.next_joint.x - bone_prev.prev_joint.x, \
                bone_prev.next_joint.y - bone_prev.prev_joint.y, \
                bone_prev.next_joint.z - bone_prev.prev_joint.z, \
                eul_x * Leap.RAD_TO_DEG, \
                eul_y * Leap.RAD_TO_DEG, \
                eul_z * Leap.RAD_TO_DEG

        return \
            bone_prev.next_joint.x - bone_prev.prev_joint.x, \
            bone_prev.next_joint.y - bone_prev.prev_joint.y, \
            bone_prev.next_joint.z - bone_prev.prev_joint.z, \
            0.0, \
            0.0, \
            0.0

    @staticmethod
    def _split_key(key):
        key_split = re.split('(\d)', key)
        key = key_split[0]
        if key_split[-1] == '_End':
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
    def _basis2rot(basis):
        return np.array([[basis.x_basis.x, basis.y_basis.x, basis.z_basis.x],
                        [basis.x_basis.y, basis.y_basis.y, basis.z_basis.y],
                        [basis.x_basis.z, basis.y_basis.z, basis.z_basis.z]])

    @staticmethod
    def _get_channels(joint_name):
        if '_End' in joint_name:
            return []

        channels_position = ['Xposition', 'Yposition', 'Zposition']
        channels_rotation = ['Xrotation', 'Yrotation', 'Zrotation']

        order = get_order()
        # order = [0, 1, 2]
        channels_rotation = [channels_rotation[order[0]]] + [channels_rotation[order[1]]] + [
            channels_rotation[order[2]]]

        if joint_name in ('Leap_Root', 'RightElbow'):
            return channels_position + channels_rotation

        return channels_rotation

    def _skeleton_apply_channels(self):
        for joint_name, joint_dict in self._skeleton.items():
            joint_dict['channels'] = self._get_channels(joint_name)

    def _to_DataFrame(self):
        """Returns all of the channels parsed from the file as a pandas DataFrame"""

        import pandas as pd
        time_index = pd.to_timedelta([f[0] for f in self._motions], unit='s')
        frames = [f[1] for f in self._motions]
        channels = np.asarray([[channel[2] for channel in frame] for frame in frames])
        column_names = ['%s_%s' % (c[0], c[1]) for c in self._motion_channels]

        return pd.DataFrame(data=channels, index=time_index, columns=column_names)
