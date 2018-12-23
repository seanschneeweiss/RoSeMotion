import numpy as np
from string import Template
import re


class AnyWriter:
    def __init__(self):
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
                        'template': 'Finger.template'}}
        pass

    def write(self, data):
        finger_values = {}

        for finger_name, joint_mapping in self.mapping.items():
            finger_values[finger_name] = {}
            for joint_name in joint_mapping['joint_any']:
                finger_values[finger_name][joint_name] = np.asarray(
                    data.values[joint_mapping['joint_leap']
                                + self._joint2channel(finger_name, joint_name)].values)

        print(finger_values)

        # #open the file
        # filein = open( 'Finger2.any' )
        # #read it
        # src = Template( filein.read() )
        # test = finger_values['Finger2']['MCPFlexion']
        # # d = {'MCPFlexion': test.tolist()}
        # sarr = [str(a) for a in test]
        # d = {'MCPFlexion': ', '.join(sarr)}
        # res = src.substitute(d)
        # print(res)
        #
        # file = open('testfile.any', 'w')
        #
        # file.write(res)
        #
        # file.close()

        #  finger_values = {'Finger2': {'MCPABDUCTION': [0, 1, 2], 'MCPFLEXION': [0, 1, 2]}, 'Finger3': ...}
        for finger_name, joint_mapping in self.mapping.items():
            template_dict = {'FINGERNAME': finger_name}

            for joint_name in joint_mapping['joint_any']:
                template_dict[joint_name] = self._joint2array(finger_values[finger_name][joint_name])

            template_filename = joint_mapping['template']
            template_string = open(template_filename, 'r').read().format(**template_dict)
            f = open(finger_name + '.any', 'w')
            f.write(template_string)
            f.close()

    @staticmethod
    def _joint2channel(finger_name, joint_name):
        thumb = 'Thumb' in finger_name

        if joint_name == 'CMCABDUCTION':
            # CMCABDUCTION is named CMCDEVIATION in Anybody unfortunately
            # Thumb only
            return '2_Xrotation'

        if joint_name == 'CMCFLEXION':
            # Thumb only
            return '2_Zrotation'

        if joint_name == 'MCPFLEXION':
            return '3_Zrotation' if thumb else '2_Zrotation'

        if joint_name == 'MCPABDUCTION':
            # MCPABDUCTION is named MCPDEVIATION in Anybody unfortunately
            # for all fingers
            return '3_Xrotation' if thumb else '2_Xrotation'

        if joint_name == 'PIPFLEXION':
            # not used for Thumb
            return '3_Zrotation'

        if joint_name == 'DIPFLEXION':
            # for all fingers
            return '4_Zrotation'

    @staticmethod
    def _joint2array(joint_values):
        return np.array2string(joint_values, separator=', ')[1:-1]

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
