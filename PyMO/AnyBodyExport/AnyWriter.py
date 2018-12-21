import numpy as np
from string import Template
import re

class AnyWriter:
    def __init__(self):
        pass
    
    def write(self, data):
        maping = {'Finger2': {'joint_leap': 'RightHandIndex',
                              'joint_any': ['MCPFlexion', 'MCPAbduction', 'PIPFlexion', 'DIPFlexion']},
                  'Finger3': {'joint_leap': 'RightHandMiddle',
                              'joint_any': ['MCPFlexion', 'MCPAbduction', 'PIPFlexion', 'DIPFlexion']},
                  'Finger4': {'joint_leap': 'RightHandRing',
                              'joint_any': ['MCPFlexion', 'MCPAbduction', 'PIPFlexion', 'DIPFlexion']},
                  'Finger5': {'joint_leap': 'RightHandPinky',
                              'joint_any': ['MCPFlexion', 'MCPAbduction', 'PIPFlexion', 'DIPFlexion']}}

        result = {}

        for finger, value in maping.items():
            result[finger] = {}
            for joint in value['joint_any']:
                joint_values = np.asarray(data.values[value['joint_leap'] + self._joint2channel(joint)].values)
                result[finger][joint] = joint_values

        print(result)

        # #open the file
        # filein = open( 'Finger2.any' )
        # #read it
        # src = Template( filein.read() )
        # test = result['Finger2']['MCPFlexion']
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

        for finger, finger_joints in result.items():
            if finger == 'Thumb':
                print("Thumb")
                return

            # Finger2-5
            mcp_flexion = np.array2string(result[finger]['MCPFlexion'], separator=', ')[1:-1]
            mcp_abduction = np.array2string(result[finger]['MCPAbduction'], separator=', ')[1:-1]
            pip_flexion = np.array2string(result[finger]['PIPFlexion'], separator=', ')[1:-1]
            dip_flexion = np.array2string(result[finger]['DIPFlexion'], separator=', ')[1:-1]
            template = open('Finger.template', 'r').read().format(MCPFLEXION=mcp_flexion,
                                                                     MCPABDUCTION=mcp_abduction,
                                                                     PIPFLEXION=pip_flexion,
                                                                     DIPFLEXION=dip_flexion)
            open(finger + '.any', 'w').write(template)

    @staticmethod
    def _joint2channel(joint):
        if joint == 'MCPFlexion':
            return '2_Xrotation'
        if joint == 'MCPAbduction':
            return '2_Yrotation'
        if joint == 'PIPFlexion':
            return '3_Xrotation'
        if joint == 'DIPFlexion':
            return '4_Xrotation'


    def write_bak(self, X, ofile):
        
        # Writing the skeleton info
        ofile.write('HIERARCHY\n')
        
        self.motions_ = []
        self._printJoint(X, X.root_name, 0, ofile)

        # Writing the motion header
        ofile.write('MOTION\n')
        ofile.write('Frames: %d\n'%X.values.shape[0])
        ofile.write('Frame Time: %f\n'%X.framerate)

        # Writing the data
        self.motions_ = np.asarray(self.motions_).T
        lines = [" ".join(item) for item in self.motions_.astype(str)]
        ofile.write("".join("%s\n"%l for l in lines))

    def _printJoint(self, X, joint, tab, ofile):
        
        if X.skeleton[joint]['parent'] == None:
            ofile.write('ROOT %s\n'%joint)
        elif len(X.skeleton[joint]['children']) > 0:
            ofile.write('%sJOINT %s\n'%('\t'*(tab), joint))
        else:
            ofile.write('%sEnd site\n'%('\t'*(tab)))

        ofile.write('%s{\n'%('\t'*(tab)))
        
        ofile.write('%sOFFSET %3.5f %3.5f %3.5f\n'%('\t'*(tab+1),
                                                X.skeleton[joint]['offsets'][0],
                                                X.skeleton[joint]['offsets'][1],
                                                X.skeleton[joint]['offsets'][2]))
        channels = X.skeleton[joint]['channels']
        n_channels = len(channels)

        if n_channels > 0:
            for ch in channels:
                self.motions_.append(np.asarray(X.values['%s_%s'%(joint, ch)].values))

        if len(X.skeleton[joint]['children']) > 0:
            ch_str = ''.join(' %s'*n_channels%tuple(channels))
            ofile.write('%sCHANNELS %d%s\n' %('\t'*(tab+1), n_channels, ch_str)) 

            for c in X.skeleton[joint]['children']:
                self._printJoint(X, c, tab+1, ofile)

        ofile.write('%s}\n'%('\t'*(tab)))
