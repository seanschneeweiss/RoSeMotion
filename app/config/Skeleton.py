class Skeleton:
    def __init__(self, channel_setting):
        if channel_setting not in ('rotation', 'position'):
            raise ValueError('Choose a correct channel setting:\n'
                             '-> "rotation" for using only Xrotation, Yrotation and Zrotation\n'
                             '-> "position" for using Xposition, Yposition, Zposition'
                             ' and Xrotation, Yrotation, Zrotation for all joints')
        self.channel_setting = channel_setting

        self.root_name = 'Leap_Root'
        self.framerate = 0.033333
        self.skeleton = \
            {self.root_name: {'channels': [], 'children': ['RightElbow'], 'parent': None},
             'RightElbow': {'channels': [], 'children': ['RightHand'], 'parent': self.root_name},
             'RightHand': {'channels': [], 'children': ['RightHandThumb2', 'RightHandIndex1', 'RightHandMiddle1', 'RightHandRing1', 'RightHandPinky1'], 'parent': 'RightElbow'},
             'RightHandIndex1': {'channels': [], 'children': ['RightHandIndex2'], 'parent': 'RightHand'},
             'RightHandIndex2': {'channels': [], 'children': ['RightHandIndex3'], 'parent': 'RightHandIndex1'},
             'RightHandIndex3': {'channels': [], 'children': ['RightHandIndex4'], 'parent': 'RightHandIndex2'},
             'RightHandIndex4': {'channels': [], 'children': ['RightHandIndex5'], 'parent': 'RightHandIndex3'},
             'RightHandIndex5': {'channels': [], 'children': ['RightHandIndex5_End'], 'parent': 'RightHandIndex4'},
             'RightHandIndex5_End': {'channels': [], 'children': [], 'parent': 'RightHandIndex5'},
             'RightHandMiddle1': {'channels': [], 'children': ['RightHandMiddle2'], 'parent': 'RightHand'},
             'RightHandMiddle2': {'channels': [], 'children': ['RightHandMiddle3'], 'parent': 'RightHandMiddle1'},
             'RightHandMiddle3': {'channels': [], 'children': ['RightHandMiddle4'], 'parent': 'RightHandMiddle2'},
             'RightHandMiddle4': {'channels': [], 'children': ['RightHandMiddle5'], 'parent': 'RightHandMiddle3'},
             'RightHandMiddle5': {'channels': [], 'children': ['RightHandMiddle5_End'], 'parent': 'RightHandMiddle4'},
             'RightHandMiddle5_End': {'channels': [], 'children': [], 'parent': 'RightHandMiddle5'},
             'RightHandPinky1': {'channels': [], 'children': ['RightHandPinky2'], 'parent': 'RightHand'},
             'RightHandPinky2': {'channels': [], 'children': ['RightHandPinky3'], 'parent': 'RightHandPinky1'},
             'RightHandPinky3': {'channels': [], 'children': ['RightHandPinky4'], 'parent': 'RightHandPinky2'},
             'RightHandPinky4': {'channels': [], 'children': ['RightHandPinky5'], 'parent': 'RightHandPinky3'},
             'RightHandPinky5': {'channels': [], 'children': ['RightHandPinky5_End'], 'parent': 'RightHandPinky4'},
             'RightHandPinky5_End': {'channels': [], 'children': [], 'parent': 'RightHandPinky5'},
             'RightHandRing1': {'channels': [], 'children': ['RightHandRing2'], 'parent': 'RightHand'},
             'RightHandRing2': {'channels': [], 'children': ['RightHandRing3'], 'parent': 'RightHandRing1'},
             'RightHandRing3': {'channels': [], 'children': ['RightHandRing4'], 'parent': 'RightHandRing2'},
             'RightHandRing4': {'channels': [], 'children': ['RightHandRing5'], 'parent': 'RightHandRing3'},
             'RightHandRing5': {'channels': [], 'children': ['RightHandRing5_End'], 'parent': 'RightHandRing4'},
             'RightHandRing5_End': {'channels': [], 'children': [], 'parent': 'RightHandRing5'},
             'RightHandThumb2': {'channels': [], 'children': ['RightHandThumb3'], 'parent': 'RightHand'},
             'RightHandThumb3': {'channels': [], 'children': ['RightHandThumb4'], 'parent': 'RightHandThumb2'},
             'RightHandThumb4': {'channels': [], 'children': ['RightHandThumb5'], 'parent': 'RightHandThumb3'},
             'RightHandThumb5': {'channels': [], 'children': ['RightHandThumb5_End'], 'parent': 'RightHandThumb4'},
             'RightHandThumb5_End': {'channels': [], 'children': [], 'parent': 'RightHandThumb5'}}
