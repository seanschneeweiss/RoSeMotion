import re
import numpy as np

from config.Skeleton import Skeleton
from resources.pymo.pymo.data import MocapData
from RotationUtil import rot2eul, vec2eul, get_order
from resources.LeapSDK.v4_python37 import Leap


class LeapData:
    """
    A class to convert LeapMotion frames to PyMO data structure (MocapData)

    Calculates translations (offsets) and rotation data for the joints
    """

    def __init__(self, channel_setting='rotation'):
        self._skeleton = {}
        self._setting = Skeleton(channel_setting)
        self._motion_channels = []
        self._motions = []
        self._framerate = 0.0
        self._root_name = ''
        self.data = MocapData()

        self.do()

    def parse(self):
        self.data.skeleton = self._skeleton
        self.data.channel_names = self._motion_channels
        self.data.values = self._motion2DataFrame()
        self.data.root_name = self._root_name
        self.data.framerate = self._framerate

        return self.data

    def do(self):
        self._skeleton = self._setting.skeleton
        self._skeleton_apply_channels(self._setting.channel_setting)  # fill channels into skeleton in selected order (i.e. xyz)

        # self._motion_channels = motion_channels
        self._root_name = self._setting.root_name
        self._framerate = self._setting.framerate  # TODO: framerate

        for key, value in self._skeleton.items():
            value['offsets'] = [0, 0, 0]
            for channel in value['channels']:
                self._motion_channels.append((key, channel))

    def add_frame(self, frame_id, hand):
        channel_values = []
        for joint_name, joint_value in self._skeleton.items():
            if frame_id == 0:
                # offsets
                if joint_name == 'Leap_Root':
                    x_offset, y_offset, z_offset, _, _, _ = LeapData._get_root_values()
                elif joint_name == 'RightElbow':
                    x_offset, y_offset, z_offset, _, _, _ = LeapData._get_elbow_values(hand)
                elif joint_name == 'RightHand':
                    x_offset, y_offset, z_offset, _, _, _ = LeapData._get_wrist_values(hand)
                elif 'End' in joint_name:
                    # Workaround for getting motion data also from finger tip by adding a not used end
                    x_offset = y_offset = z_offset = 0.0
                else:
                    x_offset, y_offset, z_offset, _, _, _ = LeapData._get_finger_values(joint_name, hand)
                joint_value['offsets'] = [x_offset, y_offset, z_offset]  # y, z, x

            for channel in joint_value['channels']:
                # motion data with rotations
                if joint_name == 'Leap_Root':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = LeapData._get_root_values()
                elif joint_name == 'RightElbow':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = LeapData._get_elbow_values(hand)
                elif joint_name == 'RightHand':
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = LeapData._get_wrist_values(hand)
                else:
                    x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = LeapData._get_finger_values(joint_name, hand)

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

        self._motions.append((frame_id, channel_values))

    @staticmethod
    def _get_root_values():
        return 0, 0, 0, 0, 0, 0

    @staticmethod
    def _get_elbow_values(hand):
        arm = hand.arm

        x_elbow = arm.elbow_position.x
        y_elbow = arm.elbow_position.y
        z_elbow = arm.elbow_position.z

        # rotation matrix from basis vectors
        rotmat = LeapData._basis2rot(arm.basis)
        eul_x, eul_y, eul_z = rot2eul(rotmat)

        return \
            x_elbow, \
            y_elbow, \
            z_elbow, \
            eul_x * Leap.RAD_TO_DEG, \
            eul_y * Leap.RAD_TO_DEG, \
            eul_z * Leap.RAD_TO_DEG

    @staticmethod
    def _get_wrist_values(hand):
        arm = hand.arm

        x_wrist = hand.wrist_position.x - arm.elbow_position.x
        y_wrist = hand.wrist_position.y - arm.elbow_position.y
        z_wrist = hand.wrist_position.z - arm.elbow_position.z

        # rotation matrix from basis vectors

        rotmat_prev = LeapData._basis2rot(arm.basis)
        rotmat_next = LeapData._basis2rot(hand.basis)
        eul_x, eul_y, eul_z = rot2eul(np.matmul(rotmat_next, np.transpose(rotmat_prev)))

        return \
            x_wrist, \
            y_wrist, \
            z_wrist, \
            eul_x * Leap.RAD_TO_DEG, \
            eul_y * Leap.RAD_TO_DEG, \
            eul_z * Leap.RAD_TO_DEG

    @staticmethod
    def _get_finger_values(key, hand):
        key, bone_number = LeapData._split_key(key)

        fingerlist = hand.fingers.finger_type(LeapData._get_finger_type(key))

        # vector between wrist and metacarpal proximal (carpals), thumb is excluded
        if bone_number == 1:
            bone = fingerlist[0].bone(LeapData._get_bone_type(bone_number))

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
        
        # thumb carpometacarpal joint
        if 'Thumb' in key and bone_number == 2:
            bone = fingerlist[0].bone(LeapData._get_bone_type(bone_number))
            
            # rotmat_prev = LeapData._basis2rot(hand.basis)

            # basis = bone.basis
            # rotmat_next = np.array([[basis.z_basis.x, basis.y_basis.x, basis.x_basis.x],
            #                         [basis.z_basis.y, basis.y_basis.y, basis.x_basis.y],
            #                         [basis.z_basis.z, basis.y_basis.z, basis.x_basis.z]])

            # rotmat_next = LeapData._basis2rot(bone.basis)

            # eul_x, eul_y, eul_z = rot2eul(np.matmul(rotmat_next, np.transpose(rotmat_prev)))
            vec_prev = np.array([bone.prev_joint.x - hand.wrist_position.x,
                                 bone.prev_joint.y - hand.wrist_position.y,
                                 bone.prev_joint.z - hand.wrist_position.z])

            vec_next = np.array([bone.next_joint.x - bone.prev_joint.x,
                                 bone.next_joint.y - bone.prev_joint.y,
                                 bone.next_joint.z - bone.prev_joint.z])

            eul_x, eul_y, eul_z = vec2eul(vec_prev, vec_next)
            
            return \
                bone.prev_joint.x - hand.wrist_position.x, \
                bone.prev_joint.y - hand.wrist_position.y, \
                bone.prev_joint.z - hand.wrist_position.z, \
                eul_x * Leap.RAD_TO_DEG, \
                eul_y * Leap.RAD_TO_DEG, \
                eul_z * Leap.RAD_TO_DEG

        # vector for bones metacarpal, proximal, intermediate, distal
        bone_prev = fingerlist[0].bone(LeapData._get_bone_type(bone_number - 1))

        if not bone_number == 5:
            bone_next = fingerlist[0].bone(LeapData._get_bone_type(bone_number))

            # rotation matrix from basis vectors
            rotmat_prev = LeapData._basis2rot(bone_prev.basis)
            rotmat_next = LeapData._basis2rot(bone_next.basis)

            # rotation matrix between rotmat_prev and rotmat_next by multiplying
            eul_x, eul_y, eul_z = rot2eul(np.matmul(rotmat_next, np.transpose(rotmat_prev)))
         
            return \
                bone_prev.next_joint.x - bone_prev.prev_joint.x, \
                bone_prev.next_joint.y - bone_prev.prev_joint.y, \
                bone_prev.next_joint.z - bone_prev.prev_joint.z, \
                eul_x * Leap.RAD_TO_DEG, \
                eul_y * Leap.RAD_TO_DEG, \
                eul_z * Leap.RAD_TO_DEG

        #  no rotation, only offset for finger tip
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
    def _get_channels(joint_name, channel_setting):
        if '_End' in joint_name:
            return []

        channels_position = ['Xposition', 'Yposition', 'Zposition']
        channels_rotation = ['Xrotation', 'Yrotation', 'Zrotation']

        order = get_order()  # rotation order, i.e. xyz
        channels_rotation = \
            [channels_rotation[order[0]]] + [channels_rotation[order[1]]] + [channels_rotation[order[2]]]

        # TODO: make position joints generic (Leap_root, RightElbow), parent==None or parent==self.root_name
        if channel_setting == 'position' or joint_name in ('Leap_Root', 'RightElbow'):
            return channels_position + channels_rotation

        return channels_rotation

    def _skeleton_apply_channels(self, channel_setting):
        for joint_name, joint_dict in self._skeleton.items():
            joint_dict['channels'] = self._get_channels(joint_name, channel_setting)

    def _motion2DataFrame(self):
        """Returns all of the channels parsed from the LeapMotion sensor as a pandas DataFrame"""

        import pandas as pd
        time_index = pd.to_timedelta([f[0] for f in self._motions], unit='s')
        frames = [f[1] for f in self._motions]
        channels = np.asarray([[channel[2] for channel in frame] for frame in frames])
        column_names = ['%s_%s' % (c[0], c[1]) for c in self._motion_channels]

        return pd.DataFrame(data=channels, index=time_index, columns=column_names)
