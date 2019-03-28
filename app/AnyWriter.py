import os
import re

import numpy as np


class AnyWriter:
    def __init__(self, template_directory='config/anybody_templates/', output_directory='../output/Anybody/'):
        self._template_directory = template_directory
        self._output_directory = output_directory
        self.mapping = {
            'Finger1': {'joint_leap': 'RightHandThumb',
                        'joint_any': ['CMCFLEXION', 'CMCABDUCTION', 'CMCDEVIATION', 'MCPFLEXION', 'MCPABDUCTION',
                                      'MCPDEVIATION', 'DIPFLEXION', 'DIPABDUCTION', 'DIPDEVIATION'],
                        'template': 'Thumb.template',
                        'function': ['negative']},
            'Finger2': {'joint_leap': 'RightHandIndex',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'MCPDEVIATION', 'PIPFLEXION', 'PIPABDUCTION',
                                      'PIPDEVIATION', 'DIPFLEXION', 'DIPABDUCTION', 'DIPDEVIATION'],
                        'template': 'Finger.template',
                        'function': ['negative']},
            'Finger3': {'joint_leap': 'RightHandMiddle',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'MCPDEVIATION', 'PIPFLEXION', 'PIPABDUCTION',
                                      'PIPDEVIATION', 'DIPFLEXION', 'DIPABDUCTION', 'DIPDEVIATION'],
                        'template': 'Finger.template',
                        'function': ['negative']},
            'Finger4': {'joint_leap': 'RightHandRing',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'MCPDEVIATION', 'PIPFLEXION', 'PIPABDUCTION',
                                      'PIPDEVIATION', 'DIPFLEXION', 'DIPABDUCTION', 'DIPDEVIATION'],
                        'template': 'Finger.template',
                        'function': ['negative']},
            'Finger5': {'joint_leap': 'RightHandPinky',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'MCPDEVIATION', 'PIPFLEXION', 'PIPABDUCTION',
                                      'PIPDEVIATION', 'DIPFLEXION', 'DIPABDUCTION', 'DIPDEVIATION'],
                        'template': 'Finger.template',
                        'function': ['negative']},
            'Wrist': {'joint_leap': 'RightHand',
                      'joint_any': ['WRISTFLEXION', 'WRISTABDUCTION', 'WRISTDEVIATION'],
                      'template': 'Wrist.template',
                      'function': ['negative']},
            'Elbow': {'joint_leap': 'RightElbow',
                      'joint_any': ['ELBOWFLEXION','ELBOWABDUCTION', 'ELBOWPRONATION'],
                      'template': 'Elbow.template',
                      'function': ['correct_pronation']}}

        self.regex_find = re.compile(r'{(((\s*-?\d+\.\d+),?)+)};')
        self.regex_replace = re.compile(r'(((\s*-?\d+\.\d+),?)+)')

    def write(self, data):
        self.write_joints(data)
        self.write_timeseries(data)
        self.write_finger_length(data)

    def write_joints(self, data):
        finger_values = {}

        for finger_name, joint_mapping in self.mapping.items():
            finger_values[finger_name] = {}
            for joint_name in joint_mapping['joint_any']:
                finger_values[finger_name][joint_name] = np.asarray(
                    data.values[joint_mapping['joint_leap']
                                + self._joint2channel(finger_name, joint_name)].values)

        np.set_printoptions(formatter={'float': '{: 0.2f}'.format}, threshold=np.inf)

        #  finger_values = {'Finger2': {'MCPABDUCTION': [0, 1, 2], 'MCPFLEXION': [0, 1, 2]}, 'Finger3': ...}
        for finger_name, joint_mapping in self.mapping.items():
            _, finger_number = AnyWriter.split_finger(finger_name)
            template_dict = {'FINGERNAME': finger_name,
                             'FINGERNUMBER': finger_number}

            for joint_name in joint_mapping['joint_any']:
                # Apply functions for correcting data, if set in mapping (see __init__ method)
                joint_values = AnyWriter._apply_function(joint_name, joint_mapping['function'],
                                                         finger_values[finger_name][joint_name])
                template_dict[joint_name] = self._format2outputarray(joint_values)

            template_filename = joint_mapping['template']
            with open(self._template_directory + template_filename, 'r') as f:
                template_string = f.read().format(**template_dict)
            with open(self._output_directory + finger_name + '.any', 'w') as f:
                f.write(template_string)
                print('"{} written"'.format(f.name))

    def write_timeseries(self, data):
        # threshold: workaround for printing more than 1000 values
        np.set_printoptions(formatter={'float': '{: 0.5f}'.format}, threshold=np.inf)

        entries = data.values.shape[0]
        template_dict = {'TIMESERIES': self._format2outputarray(np.linspace(0, 1, num=entries))}
        template_string = open(self._template_directory + 'TimeSeries.template', 'r').read().format(**template_dict)

        with open(self._output_directory + 'TimeSeries.any', 'w') as f:
            f.write(template_string)
            print('"{} written"'.format(os.path.normpath(f.name)))

    def write_finger_length(self, data):
        template_dict = {}
        # use offsets value from bvh to scale finger lengths in AnyBody
        for joint_name, joint_value in data.skeleton.items():
            finger_length = np.linalg.norm(np.array(joint_value['offsets'])) / 1000
            template_dict[joint_name] = finger_length

        # hand length, hand breadth
        hand_length = np.linalg.norm(
            np.array(data.skeleton['RightHandMiddle1']['offsets']) +
            np.array(data.skeleton['RightHandMiddle2']['offsets']) +
            np.array(data.skeleton['RightHandMiddle3']['offsets']) +
            np.array(data.skeleton['RightHandMiddle4']['offsets']) +
            np.array(data.skeleton['RightHandMiddle4_Nub']['offsets'])
        ) / 1000
        template_dict['HANDLENGTH'] = hand_length

        # hand breadth from leap motion is too small
        # template_dict['HANDBREADTH'] = np.linalg.norm(
        #     np.array(data.skeleton['RightHandPinky1']['offsets'] + data.skeleton['RightHandPinky2']['offsets']) -
        #     np.array(data.skeleton['RightHandIndex1']['offsets'] + data.skeleton['RightHandIndex2']['offsets'])
        # ) / 1000

        # use scaling factor (hand breadth to hand length) from UZWR standard hand
        template_dict['HANDBREADTH'] = hand_length * (0.098 / 0.2)

        template_string = open(self._template_directory + 'FingerLength.template', 'r').read().format(**template_dict)
        with open(self._output_directory + 'FingerLength.any', 'w') as f:
            f.write(template_string)
            print('"{} written"'.format(os.path.normpath(f.name)))

    @staticmethod
    def _joint2channel(finger_name, joint_name):
        thumb = 'Finger1' == finger_name
        if joint_name == 'CMCFLEXION':
            # Thumb only
            return '2_Xrotation'

        if joint_name == 'CMCABDUCTION':
            # CMCABDUCTION is named CMCDEVIATION in Anybody unfortunately
            # Thumb only
            return '2_Yrotation'

        if joint_name == 'CMCDEVIATION':
            # CMCABDUCTION is named CMCDEVIATION in Anybody unfortunately
            # Thumb only
            return '2_Zrotation'

        if joint_name == 'MCPFLEXION':
            return '3_Xrotation' if thumb else '2_Xrotation'

        if joint_name == 'MCPABDUCTION':
            # MCPABDUCTION is named MCPDEVIATION in Anybody unfortunately
            # for all fingers
            return '3_Yrotation' if thumb else '2_Yrotation'

        if joint_name == 'MCPDEVIATION':
            # MCPABDUCTION is named MCPDEVIATION in Anybody unfortunately
            # for all fingers
            return '3_Zrotation' if thumb else '2_Zrotation'

        if joint_name == 'PIPFLEXION':
            # not used for Thumb
            return '3_Xrotation'

        if joint_name == 'PIPABDUCTION':
            # not used for Thumb
            return '3_Yrotation'

        if joint_name == 'PIPDEVIATION':
            # not used for Thumb
            return '3_Zrotation'

        if joint_name == 'DIPFLEXION':
            # for all fingers
            return '4_Xrotation'

        if joint_name == 'DIPABDUCTION':
            # for all fingers
            return '4_Yrotation'

        if joint_name == 'DIPDEVIATION':
            # for all fingers
            return '4_Zrotation'

        if joint_name == 'WRISTFLEXION':
            # only for wrist
            return '_Xrotation'

        if joint_name == 'WRISTABDUCTION':
            # only for wrist
            return '_Yrotation'

        if joint_name == 'WRISTDEVIATION':
            # only for wrist
            return '_Zrotation'

        if joint_name == 'ELBOWFLEXION':
            # only for elbow
            return '_Xrotation'

        if joint_name == 'ELBOWABDUCTION':
            # only for elbow
            return '_Yrotation'

        if joint_name == 'ELBOWPRONATION':
            # only for elbow
            return '_Zrotation'

    @staticmethod
    def _format2outputarray(joint_values):
        return np.array2string(joint_values.astype(float), separator=', ')[1:-1]

    @staticmethod
    def split_finger(finger_name):
        finger_split = re.split(r'(\d)', finger_name)
        if len(finger_split) == 1:
            return finger_name, None
        return finger_split[0], int(finger_split[1])

    @staticmethod
    def _apply_function(joint_name, operations, joint_values):
        for op in operations:
            if op == 'negative':
                joint_values = np.negative(joint_values)

            if op == 'correct_pronation' and joint_name == 'ELBOWPRONATION':
                joint_values = 95.0 + joint_values

        return joint_values

    def extract_frames(self, start, end):
        def prepare_result(x):
            np.set_printoptions(formatter={'float': '{: 0.2f}'.format}, threshold=np.inf)
            return np.array2string(np.fromstring(x[0], sep=',').astype(float)[start:end], separator=', ')[1:-1]

        for finger_name in self.mapping:
            selected_filepath = self._output_directory + finger_name + '.any'
            with open(selected_filepath) as file:
                old_file = file.read()
                matches = list(map(prepare_result, self.regex_find.findall(old_file)))

            new_file = re.sub(self.regex_replace, '{{}}', old_file)
            # replace single brackets with two, so that they don't get replaced by str.format
            new_file = re.sub(r'{\w', r'{\g<0>', new_file)
            new_file = re.sub(r'\w}', r'\g<0>}', new_file)

            with open(selected_filepath, 'w') as file:
                file.write(new_file.format(*matches))
                if not end:
                    end = len(np.fromstring(matches[0], sep=','))
                print("Extracted values between frame {} and {} from {}"
                      .format(start+1, start+end, os.path.normpath(file.name)))

    def extract_frame_timeseries(self, start, end):
        selected_filepath =self._output_directory + 'TimeSeries.any'
        with open(selected_filepath) as file:
            old_file = file.read()
            match = self.regex_find.findall(old_file)

        if not end:
            end = len(np.fromstring(match[0][0], sep=','))

        new_file = re.sub(self.regex_replace, '{{}}', old_file)

        np.set_printoptions(formatter={'float': '{: 0.5f}'.format}, threshold=np.inf)
        with open(selected_filepath, 'w') as file:
            file.write(new_file.format(np.array2string(
                np.linspace(0, 1, num=end-start).astype(float), separator=', ')[1:-1]))
            print("Extracted values between frame {} and {} from {}"
                  .format(start+1, end, os.path.normpath(file.name)))
