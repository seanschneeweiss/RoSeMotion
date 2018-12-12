import inspect
import os
import re
import sys

import numpy as np
# import math
from pymo.RotationUtil import vec2eul

from leapmotion_setup_rot import root_name, skeleton, framerate
from pymo.data import MocapData

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = '../../lib/x64' if sys.maxsize > 2 ** 32 else '../../lib/x86'

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap


class Leap2BVH:
    """
    A class to parse a BVH file.

    Extracts the skeleton and channel values
    """

    def __init__(self, filename=None):
        self.reset()
        self.do()

    def reset(self):
        self._skeleton = {}
        self.bone_context = []
        self._motion_channels = []
        self._motions = []
        self.current_token = 0
        self.framerate = 0.0
        self.root_name = ''

        self.data = MocapData()

    def parse(self):
        self.data.skeleton = self._skeleton
        self.data.channel_names = self._motion_channels
        self.data.values = self._to_DataFrame()
        self.data.root_name = self.root_name
        self.data.framerate = self.framerate

        return self.data

    def do(self):
        self._skeleton = skeleton
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
                elif key == 'RightHand':
                    x_offset, y_offset, z_offset, _, _, _ = self._get_wrist_values(hand)
                elif 'End' in key:
                    # Workaround for getting motion data also from finger tip by adding a not used end
                    x_offset = y_offset = z_offset = 0.0
                else:
                    x_offset, y_offset, z_offset, _, _, _ = self._get_finger_offsets(key, hand)
                value['offsets'] = [x_offset, y_offset, z_offset]

                # print("pitch hand x = {}, angle hand x = {}".format(hand.basis.x_basis.pitch * Leap.RAD_TO_DEG,
                #                                                     hand.basis.x_basis.angle_to(Leap.Vector.x_axis) * Leap.RAD_TO_DEG))

            for channel in value['channels']:
                # motion data with rotations
                if key == 'Leap_Root':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = self._get_root_values()
                elif key == 'RightHand':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = self._get_wrist_values(hand)
                else:
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = self._get_finger_offsets(key, hand)

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

    def _get_root_values(self):
        return 0, 0, 0, 0, 0, 0

    def _get_wrist_values(self, hand):
        fingerlist = hand.fingers.finger_type(self._get_finger_type('RightHandMiddle'))
        bone = fingerlist[0].bone(self._get_bone_type(1))

        x_wrist = hand.wrist_position.x
        y_wrist = hand.wrist_position.y
        z_wrist = hand.wrist_position.z

        vec_prev = np.array([x_wrist, y_wrist, z_wrist])
        vec_next = np.array([bone.prev_joint.x - x_wrist,
                             bone.prev_joint.y - y_wrist,
                             bone.prev_joint.z - z_wrist])
        eul_x, eul_y, eul_z = vec2eul(vec_prev, vec_next)

        return \
            x_wrist, \
            y_wrist, \
            z_wrist, \
            eul_x * Leap.RAD_TO_DEG, \
            eul_y * Leap.RAD_TO_DEG, \
            eul_z * Leap.RAD_TO_DEG

    def _get_finger_offsets(self, key, hand):
        key, bone_number = self._split_key(key)

        fingerlist = hand.fingers.finger_type(self._get_finger_type(key))

        # vector between wrist and metacarpal proximal (carpals)
        if bone_number == 1 or ('Thumb' in key and bone_number == 2):
            bone = fingerlist[0].bone(self._get_bone_type(bone_number))
            x_wrist, y_wrist, z_wrist, _, _, _ = self._get_wrist_values(hand)
            # print("1: key: {}, bone_number: {}, bone: {}, prev_joint: {}"
            #       .format(key, bone_number, bone, bone.prev_joint))
            print("p1_rot = [{}; {}; {}];".format(x_wrist, y_wrist, z_wrist))
            print("p2_rot = [{}; {}; {}];".format(bone.prev_joint.x, bone.prev_joint.y, bone.prev_joint.z))
            print("p3_rot = [{}; {}; {}];".format(bone.next_joint.x, bone.next_joint.y, bone.next_joint.z))

            vec_prev = np.array([bone.prev_joint.x - x_wrist,
                                 bone.prev_joint.y - y_wrist,
                                 bone.prev_joint.z - z_wrist])
            print('bone.next_joint.x = {}, bone.prev_joint.x = {}, x_wrist = {}, vec_prev = {}'.format(bone.next_joint.x, bone.prev_joint.x, x_wrist, vec_prev[0]))
            print('bone.next_joint.y = {}, bone.prev_joint.y = {}, y_wrist = {}, vec_prev = {}'.format(bone.next_joint.y, bone.prev_joint.y, y_wrist, vec_prev[1]))
            print('bone.next_joint.z = {}, bone.prev_joint.z = {}, z_wrist = {}, vec_prev = {}'.format(bone.next_joint.z, bone.prev_joint.z, z_wrist, vec_prev[2]))

            # vec_next = np.array([bone.direction.x, bone.direction.y, bone.direction.z])
            vec_next = np.array([bone.next_joint.x - bone.prev_joint.x,
                                 bone.next_joint.y - bone.prev_joint.y,
                                 bone.next_joint.z - bone.prev_joint.z])

            eul_x, eul_y, eul_z = vec2eul(vec_prev, vec_next)
            print("euler = [{}; {}; {}];".format(eul_x, eul_y, eul_z))

            return \
                bone.prev_joint.x - x_wrist, \
                bone.prev_joint.y - y_wrist, \
                bone.prev_joint.z - z_wrist, \
                eul_x * Leap.RAD_TO_DEG, \
                eul_y * Leap.RAD_TO_DEG, \
                eul_z * Leap.RAD_TO_DEG

        # vector for bones metacarpal, proximal, intermediate, distal
        bone_prev = fingerlist[0].bone(self._get_bone_type(bone_number - 1))

        #  no rotation for finger tip
        if not bone_number == 5:
            bone_next = fingerlist[0].bone(self._get_bone_type(bone_number))

            vec_prev = np.array([bone_prev.next_joint.x - bone_prev.prev_joint.x,
                                 bone_prev.next_joint.y - bone_prev.prev_joint.y,
                                 bone_prev.next_joint.z - bone_prev.prev_joint.z])

            vec_next = np.array([bone_next.next_joint.x - bone_next.prev_joint.x,
                                 bone_next.next_joint.y - bone_next.prev_joint.y,
                                 bone_next.next_joint.z - bone_next.prev_joint.z])

            eul_x, eul_y, eul_z = vec2eul(vec_prev, vec_next)

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

    def _split_key(self, key):
        key_split = re.split('(\d)', key)
        key = key_split[0]
        if key_split[-1] == '_End':
            return key, 5
        else:
            return key, int(key_split[1])

    def _get_finger_type(self, key):
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

    def _get_bone_type(self, bone_number):
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

    # def mat2eul(self, rotmat):
    #     rotmat = np.array(rotmat.to_array_3x3()).reshape(3, 3)
    #
    #     # normalize?
    #     eul1 = Leap.Vector()
    #     eul2 = Leap.Vector()
    #
    #     cy = np.hypot(rotmat[0, 0], rotmat[0, 1])
    #
    #     # xyz order
    #     if cy > 16 * Leap.EPSILON:
    #         eul1.x = math.atan2(rotmat[1, 2], rotmat[2, 2])
    #         eul1.y = math.atan2(-rotmat[0, 2], cy)
    #         eul1.z = math.atan2(rotmat[0, 1], rotmat[0, 0])
    #
    #         eul2.x = math.atan2(-rotmat[1, 2], -rotmat[2, 2])
    #         eul2.y = math.atan2(-rotmat[0, 2], -cy)
    #         eul2.z = math.atan2(-rotmat[0, 1], -rotmat[0, 0])
    #
    #     else:
    #         eul1.x = math.atan2(-rotmat[2, 1], rotmat[1, 1])
    #         eul1.y = math.atan2(-rotmat[0, 2], cy)
    #         eul1.z = 0.0
    #
    #         eul2 = eul1
    #
    #     # return best, which is just the one with lowest values in it
    #     if eul1.magnitude > eul2.magnitude:
    #         return eul2
    #     else:
    #         return eul1

    def _to_DataFrame(self):
        '''Returns all of the channels parsed from the file as a pandas DataFrame'''

        import pandas as pd
        time_index = pd.to_timedelta([f[0] for f in self._motions], unit='s')
        frames = [f[1] for f in self._motions]
        channels = np.asarray([[channel[2] for channel in frame] for frame in frames])
        column_names = ['%s_%s' % (c[0], c[1]) for c in self._motion_channels]

        return pd.DataFrame(data=channels, index=time_index, columns=column_names)
