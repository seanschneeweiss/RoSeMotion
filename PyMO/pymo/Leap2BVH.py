from pymo.data import MocapData
import numpy as np
import re
from leapmotion_setup import root_name, skeleton, framerate

import os, sys, inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = '../../lib/x64' if sys.maxsize > 2**32 else '../../lib/x86'

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap

class Leap2BVH():
    '''
    A class to parse a BVH file.

    Extracts the skeleton and channel values
    '''

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
        #self._motion_channels = motion_channels
        self.root_name = root_name
        self.framerate = framerate #TODO: framerate

        #frame_count = 188#TODO:frame_count
        #frame_time = 0.0
        #self._motions = [()] * frame_count

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
                if key == 'Leap_Root':
                    x_offset, y_offset, z_offset, _, _, _ = self._get_root_values()
                elif key == 'RightHand':
                    x_offset, y_offset, z_offset, _, _, _ = self._get_wrist_values(hand)
                else:
                    x_offset, y_offset, z_offset = self._get_finger_offsets(key, hand)
                value['offsets'] = [x_offset, y_offset, z_offset]
            for channel in value['channels']:
                if key == 'Leap_Root':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = self._get_root_values()
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

    def _get_root_values(self):
        return 0, 0, 0, 0, 0, 0

    def _get_wrist_values(self, hand):
        return hand.wrist_position.x, \
               hand.wrist_position.y, \
               hand.wrist_position.z, \
               0.0, \
               0.0, \
               0.0

    def _get_finger_values(self, key, hand):
        x_pos, y_pos, z_pos = self._get_finger_offsets(key, hand)

        key, bone_number = self._split_key(key)

        fingerlist = hand.fingers.finger_type(self._get_finger_type(key))
        bone = fingerlist[0].bone(self._get_bone_type(bone_number))

        return x_pos, y_pos, z_pos, 0.0, 0.0, 0.0

    def _get_finger_offsets(self, key, hand):
        key, bone_number = self._split_key(key)

        fingerlist = hand.fingers.finger_type(self._get_finger_type(key))

        if bone_number == 1 or ('Thumb' in key and bone_number == 2):
            bone = fingerlist[0].bone(self._get_bone_type(bone_number))
            x_pos, y_pos, z_pos, _, _, _ = self._get_wrist_values(hand)
            # print("1: key: {}, bone_number: {}, bone: {}, prev_joint: {}"
            #       .format(key, bone_number, bone, bone.prev_joint))
            return \
                bone.prev_joint.x - x_pos, \
                bone.prev_joint.y - y_pos, \
                bone.prev_joint.z - z_pos
        else:
            bone = fingerlist[0].bone(self._get_bone_type(bone_number - 1))
            # print("2: key: {}, bone_number: {}, bone: {}, prev_joint: {}, next_joint: {}"
            #       .format(key, bone_number, bone, bone.prev_joint, bone.next_joint))
            return \
                bone.next_joint.x - bone.prev_joint.x, \
                bone.next_joint.y - bone.prev_joint.y, \
                bone.next_joint.z - bone.prev_joint.z

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

    def _to_DataFrame(self):
        '''Returns all of the channels parsed from the file as a pandas DataFrame'''

        import pandas as pd
        time_index = pd.to_timedelta([f[0] for f in self._motions], unit='s')
        frames = [f[1] for f in self._motions]
        channels = np.asarray([[channel[2] for channel in frame] for frame in frames])
        column_names = ['%s_%s'%(c[0], c[1]) for c in self._motion_channels]

        return pd.DataFrame(data=channels, index=time_index, columns=column_names)
