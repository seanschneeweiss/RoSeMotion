import btk

from bvh_reader import Joint, EndSite


class Converter(object):


    def __init__(self):
        super(Converter, self).__init__()


    def convert(self, bvh, output_file):
        acq = btk.btkAcquisition()
        acq.Init(0, bvh.frame_count)
        acq.SetPointFrequency(1 / bvh.frame_time)

        self.points_dict = {}
        marker_count = 0
        for key in bvh.channel_dict.keys():
            point = btk.btkPoint(key, bvh.frame_count)
            point.SetLabel(key)
            self.points_dict[key] = point
            marker_count += 1

        self.calculate_joint_position(bvh)
        for key in self.points_dict.keys():
            acq.AppendPoint(self.points_dict[key])

        writer = btk.btkAcquisitionFileWriter()
        writer.SetInput(acq)
        writer.SetFilename(output_file)
        writer.Update()


    def calculate_joint_position(self, bvh):
        for frame in range(bvh.frame_count):
            for root in bvh.root:
                # root position
                self.points_dict[root.name].SetValue(frame, 0, 0.0)
                self.points_dict[root.name].SetValue(frame, 1, 0.0)
                self.points_dict[root.name].SetValue(frame, 2, 0.0)

                # iterate through children joints
                for joint in root.children:
                    self.transform_joint(bvh, joint, frame, [0.0, 0.0, 0.0])


    def transform_joint(self, bvh, joint, frame, parent_offset):
        if isinstance(joint, EndSite):
            return
        elif isinstance(joint, Joint):
            if 'Xposition' in bvh.channel_dict[joint.name]:
                pos = [bvh.channel_values[bvh.channel_dict[joint.name]['Xposition']][frame],
                       bvh.channel_values[bvh.channel_dict[joint.name]['Yposition']][frame],
                       bvh.channel_values[bvh.channel_dict[joint.name]['Zposition']][frame]]

            self.points_dict[joint.name].SetValue(frame, 0, parent_offset[0] + pos[0])
            self.points_dict[joint.name].SetValue(frame, 1, parent_offset[1] + pos[1])
            self.points_dict[joint.name].SetValue(frame, 2, parent_offset[2] + pos[2])

            bone_length = joint.offset

            offset = [0, 0, 0]
            offset[0] = parent_offset[0] + bone_length[0]
            offset[1] = parent_offset[1] + bone_length[1]
            offset[2] = parent_offset[2] + bone_length[2]

            # iterate through children joints
            for child in joint.children:
                self.transform_joint(bvh, child, frame, offset)
        else:
            return