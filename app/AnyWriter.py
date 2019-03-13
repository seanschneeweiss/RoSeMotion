import numpy as np
from config.Configuration import env


class AnyWriter:
    def __init__(self, template_directory='config/anybody_templates/', output_directory='../output/Anybody/'):
        self._template_directory = template_directory
        self._output_directory = output_directory
        self.mapping = {
            'Finger1': {'joint_leap': 'RightHandThumb',
                        'joint_any': ['CMCABDUCTION', 'CMCFLEXION', 'MCPFLEXION', 'MCPABDUCTION', 'DIPFLEXION'],
                        'template': 'Thumb.template',
                        'function': []},
            'Finger2': {'joint_leap': 'RightHandIndex',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'PIPFLEXION', 'DIPFLEXION'],
                        'template': 'Finger.template',
                        'function': []},
            'Finger3': {'joint_leap': 'RightHandMiddle',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'PIPFLEXION', 'DIPFLEXION'],
                        'template': 'Finger.template',
                        'function': []},
            'Finger4': {'joint_leap': 'RightHandRing',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'PIPFLEXION', 'DIPFLEXION'],
                        'template': 'Finger.template',
                        'function': []},
            'Finger5': {'joint_leap': 'RightHandPinky',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'PIPFLEXION', 'DIPFLEXION'],
                        'template': 'Finger.template',
                        'function': []},
            'Wrist': {'joint_leap': 'RightHand',
                      'joint_any': ['WRISTFLEXION', 'WRISTABDUCTION'],
                      'template': 'Wrist.template',
                      'function': []},
            'Elbow': {'joint_leap': 'RightElbow',
                      'joint_any': ['ELBOWPRONATION'],
                      'template': 'Elbow.template',
                      'function': []}}
        pass

    def write(self, data):
        self.write_fingers(data)
        self.write_timeseries(data)

    def write_fingers(self, data):
        finger_values = {}

        for finger_name, joint_mapping in self.mapping.items():
            finger_values[finger_name] = {}
            for joint_name in joint_mapping['joint_any']:
                finger_values[finger_name][joint_name] = np.asarray(
                    data.values[joint_mapping['joint_leap']
                                + self._joint2channel(finger_name, joint_name)].values)

        np.set_printoptions(formatter={'float': '{: 0.2f}'.format})

        #  finger_values = {'Finger2': {'MCPABDUCTION': [0, 1, 2], 'MCPFLEXION': [0, 1, 2]}, 'Finger3': ...}
        for finger_name, joint_mapping in self.mapping.items():
            template_dict = {'FINGERNAME': finger_name}

            for joint_name in joint_mapping['joint_any']:
                # Apply functions for correcting data, if set in mapping (see __init__ method)
                joint_values = AnyWriter._apply_function(joint_mapping['function'],
                                                         finger_values[finger_name][joint_name])
                template_dict[joint_name] = self._joint2array(joint_values)

            template_filename = joint_mapping['template']
            with open(self._template_directory + template_filename, 'r') as f:
                template_string = f.read().format(**template_dict)
            with open(self._output_directory + finger_name + '.any', 'w') as f:
                f.write(template_string)
                print('"{} written"'.format(f.name))

    def write_timeseries(self, data):
        # threshold: workaround for printing more than 1000 values
        np.set_printoptions(formatter={'float': '{: 0.4f}'.format}, threshold=np.inf)

        # TODO: add TIMESERIES to the dictionary in the __init__ method
        entries = data.values.shape[0]
        template_dict = {'TIMESERIES': self._joint2array(self._calctimeseries(data, entries))}
        template_string = open(self._template_directory + 'TimeSeries.template', 'r').read().format(**template_dict)

        with open(self._output_directory + 'TimeSeries.any', 'w') as f:
            f.write(template_string)
            print('"{} written"'.format(f.name))

    @staticmethod
    def _joint2channel(finger_name, joint_name):
        thumb = 'Finger1' == finger_name

        if joint_name == 'CMCABDUCTION':
            # CMCABDUCTION is named CMCDEVIATION in Anybody unfortunately
            # Thumb only
            return '2_Xrotation'

        if joint_name == 'CMCFLEXION':
            # Thumb only
            return '2_Yrotation'

        if joint_name == 'MCPFLEXION':
            return '3_Xrotation' if thumb else '2_Xrotation'

        if joint_name == 'MCPABDUCTION':
            # MCPABDUCTION is named MCPDEVIATION in Anybody unfortunately
            # for all fingers
            return '3_Yrotation' if thumb else '2_Yrotation'

        if joint_name == 'PIPFLEXION':
            # not used for Thumb
            return '3_Xrotation'

        if joint_name == 'DIPFLEXION':
            # for all fingers
            return '4_Xrotation'

        if joint_name == 'WRISTFLEXION':
            # only for wrist
            return '_Xrotation'

        if joint_name == 'WRISTABDUCTION':
            # only for wrist
            return '_Yrotation'

        if joint_name == 'ELBOWPRONATION':
            # only for wrist
            return '_Zrotation'

    @staticmethod
    def _range(start, step, num, dtype=np.float):
        # return np.fromiter(itertools.count(start, step), dtype, num)
        return np.linspace(0, 1, num=num)

    @staticmethod
    def _calctimeseries(data, entries):
        timeseries = AnyWriter._range(0.0, data.framerate, entries)
        return timeseries

    @staticmethod
    def _joint2array(joint_values):
        return np.array2string(joint_values.astype(float), separator=', ')[1:-1]

    @staticmethod
    def _apply_function(operations, joint_values):
        for op in operations:
            if op == 'negative':
                joint_values = np.negative(joint_values)

            if op == 'correct_pronation':
                joint_values = 90.0 + joint_values

        return joint_values
