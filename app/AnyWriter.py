import numpy as np


class AnyWriter:
    def __init__(self, template_directory='config/anybody_templates'):
        self._template_directory = template_directory
        self.mapping = {
            'Finger1': {'joint_leap': 'RightHandThumb',
                        'joint_any': ['CMCABDUCTION', 'CMCFLEXION', 'MCPFLEXION', 'MCPABDUCTION', 'DIPFLEXION'],
                        'template': 'Thumb.template'},
            'Finger2': {'joint_leap': 'RightHandIndex',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'PIPFLEXION', 'DIPFLEXION'],
                        'template': 'Finger.template'},
            'Finger3': {'joint_leap': 'RightHandMiddle',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'PIPFLEXION', 'DIPFLEXION'],
                        'template': 'Finger.template'},
            'Finger4': {'joint_leap': 'RightHandRing',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'PIPFLEXION', 'DIPFLEXION'],
                        'template': 'Finger.template'},
            'Finger5': {'joint_leap': 'RightHandPinky',
                        'joint_any': ['MCPFLEXION', 'MCPABDUCTION', 'PIPFLEXION', 'DIPFLEXION'],
                        'template': 'Finger.template'},
            'Wrist': {'joint_leap': 'RightHand',
                      'joint_any': ['WRISTFLEXION', 'WRISTABDUCTION'],
                      'template': 'Wrist.template'},
            'Elbow': {'joint_leap': 'RightElbow',
                      'joint_any': ['ELBOWPRONATION'],
                      'template': 'Elbow.template'}}
        pass

    def write(self, data):
        np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
        finger_values = {}

        for finger_name, joint_mapping in self.mapping.items():
            finger_values[finger_name] = {}
            for joint_name in joint_mapping['joint_any']:
                finger_values[finger_name][joint_name] = np.asarray(
                    data.values[joint_mapping['joint_leap']
                                + self._joint2channel(finger_name, joint_name)].values)

                entries = len(finger_values[finger_name][joint_name])

        # print(finger_values)
        # print(self._calctimeseries(data, entries))

        template_dict = {'TIMESERIES': self._joint2array(self._calctimeseries(data, entries))}
        template_string = open('TimeSeries.template', 'r').read().format(**template_dict)
        f = open('TimeSeries.any', 'w')
        f.write(template_string)
        f.close()

        #  finger_values = {'Finger2': {'MCPABDUCTION': [0, 1, 2], 'MCPFLEXION': [0, 1, 2]}, 'Finger3': ...}
        for finger_name, joint_mapping in self.mapping.items():
            template_dict = {'FINGERNAME': finger_name}

            for joint_name in joint_mapping['joint_any']:
                template_dict[joint_name] = self._joint2arrayneg(finger_values[finger_name][joint_name])

            template_filename = joint_mapping['template']
            template_string = open(self._template_directory + template_filename, 'r').read().format(**template_dict)
            f = open(finger_name + '.any', 'w')
            f.write(template_string)
            f.close()
            print('"{} written"'.format(f.name))

    @staticmethod
    def _floatformatter(x): "%.2f" % x

    @staticmethod
    def _joint2channel(finger_name, joint_name):
        thumb = 'Finger1' == finger_name

        if joint_name == 'CMCABDUCTION':
            # CMCABDUCTION is named CMCDEVIATION in Anybody unfortunately
            # Thumb only
            return '2_Yrotation'

        if joint_name == 'CMCFLEXION':
            # Thumb only
            return '2_Xrotation'

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

    def _calctimeseries(self, data, entries):
        timeseries = self._range(0.0, data.framerate, entries)
        return timeseries

    @staticmethod
    def _joint2array(joint_values):
        return np.array2string(joint_values.astype(float), separator=', ')[1:-1]

    @staticmethod
    def _joint2arrayneg(joint_values):
        return np.array2string(np.negative(joint_values.astype(float)), separator=', ')[1:-1]

    def write_bak(self, X, ofile):

        # Writing the skeleton info
        ofile.write('HIERARCHY\n')

        self.motions_ = []
        self._printJoint(X, X.root_name, 0, ofile)

        # Writing the motion header
        ofile.write('MOTION\n')
        ofile.write('Frames: %d\n' % X.values.shape[0])
        ofile.write('Frame Time: %f\n' % X.framerate)

        # Writing the data
        self.motions_ = np.asarray(self.motions_).T
        lines = [" ".join(item) for item in self.motions_.astype(str)]
        ofile.write("".join("%s\n" % l for l in lines))

    def _printJoint(self, X, joint, tab, ofile):

        if X.skeleton[joint]['parent'] == None:
            ofile.write('ROOT %s\n' % joint)
        elif len(X.skeleton[joint]['children']) > 0:
            ofile.write('%sJOINT %s\n' % ('\t' * (tab), joint))
        else:
            ofile.write('%sEnd site\n' % ('\t' * (tab)))

        ofile.write('%s{\n' % ('\t' * (tab)))

        ofile.write('%sOFFSET %3.5f %3.5f %3.5f\n' % ('\t' * (tab + 1),
                                                      X.skeleton[joint]['offsets'][0],
                                                      X.skeleton[joint]['offsets'][1],
                                                      X.skeleton[joint]['offsets'][2]))
        channels = X.skeleton[joint]['channels']
        n_channels = len(channels)

        if n_channels > 0:
            for ch in channels:
                self.motions_.append(np.asarray(X.values['%s_%s' % (joint, ch)].values))

        if len(X.skeleton[joint]['children']) > 0:
            ch_str = ''.join(' %s' * n_channels % tuple(channels))
            ofile.write('%sCHANNELS %d%s\n' % ('\t' * (tab + 1), n_channels, ch_str))

            for c in X.skeleton[joint]['children']:
                self._printJoint(X, c, tab + 1, ofile)

        ofile.write('%s}\n' % ('\t' * (tab)))
