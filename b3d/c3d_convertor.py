import btk
import math3d

from bvh_reader import Joint, EndSite


class Convertor(object):


    def __init__(self):
        super(Convertor, self).__init__()


    def convert(self, bvh, output_file):
        acq = btk.btkAcquisition()
        acq.Init(0, bvh.frame_count)
        acq.SetPointFrequency(1 / bvh.frame_time)

        self.points_dict = {}
        marker_count = 0
        for key in bvh.channel_dict.keys():
            point = btk.btkPoint('Marker_' + key, bvh.frame_count)
            point.SetLabel('Marker_' + key)
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
        for i in range(bvh.frame_count):
            transformation_stack = []
            for root in bvh.root:
                # root position
                bone_length = root.offset
                if 'Xrotation' in bvh.channel_dict[root.name]:
                    rot = [bvh.channel_values[bvh.channel_dict[root.name]['Xrotation']][i], bvh.channel_values[bvh.channel_dict[root.name]['Yrotation']][i], bvh.channel_values[bvh.channel_dict[root.name]['Zrotation']][i]]

                # calculate transformation
                q_x = math3d.quaternion((1, 0, 0), rot[0])
                q_y = math3d.quaternion((0, 1, 0), rot[1])
                q_z = math3d.quaternion((0, 0, 1), rot[2])
                q_rot = math3d.multiply_quat(q_x, math3d.multiply_quat(q_y, q_z))
                mat_rot = math3d.matrix_from_quat(q_rot)
                # mat_trans = math3d.matrix_from_trans((bone_length[0] + pos[0], bone_length[1] + pos[1], bone_length[2] + pos[2]))
                mat_trans = math3d.matrix_from_trans((bone_length[0], bone_length[1], bone_length[2]))
                trans_matrix = math3d.multiply_matrix(mat_trans, mat_rot)
                pos_calc = [trans_matrix[3], trans_matrix[7], trans_matrix[11]]

                self.points_dict[root.name].SetValue(i, 0, pos_calc[0] * 10)
                self.points_dict[root.name].SetValue(i, 1, -pos_calc[2] * 10)
                self.points_dict[root.name].SetValue(i, 2, pos_calc[1] * 10)

                # push transformation onto stack
                transformation_stack.append(trans_matrix)

                # iterate through children joints
                for joint in root.children:
                    self.transform_joint(bvh, joint, i, transformation_stack)

                # pop transformation off stack
                transformation_stack.pop()


    def transform_joint(self, bvh, joint, frame, transformation_stack):
        if isinstance(joint, EndSite):
            return
        elif isinstance(joint, Joint):
            bone_length = joint.offset
            if 'Xrotation' in bvh.channel_dict[joint.name]:
                rot = [bvh.channel_values[bvh.channel_dict[joint.name]['Xrotation']][frame], bvh.channel_values[bvh.channel_dict[joint.name]['Yrotation']][frame], bvh.channel_values[bvh.channel_dict[joint.name]['Zrotation']][frame]]
            if 'Xposition' in bvh.channel_dict[joint.name]:
                pos = [bvh.channel_values[bvh.channel_dict[joint.name]['Xposition']][frame],
                       bvh.channel_values[bvh.channel_dict[joint.name]['Yposition']][frame],
                       bvh.channel_values[bvh.channel_dict[joint.name]['Zposition']][frame]]

            q_x = math3d.quaternion((1, 0, 0), rot[0])
            q_y = math3d.quaternion((0, 1, 0), rot[1])
            q_z = math3d.quaternion((0, 0, 1), rot[2])
            q_rot = math3d.multiply_quat(q_x, math3d.multiply_quat(q_y, q_z))
            mat_rot = math3d.matrix_from_quat(q_rot)
            mat_trans = math3d.matrix_from_trans(
                (bone_length[0] + pos[0], bone_length[1] + pos[1], bone_length[2] + pos[2]))
            # mat_trans = math3d.matrix_from_trans((bone_length[0], bone_length[1], bone_length[2]))
            trans_matrix = math3d.multiply_matrix(mat_trans, mat_rot)
            transformation_stack.append(trans_matrix)
            # apply transformations
            mat = math3d.identity_matrix()
            for transformation in reversed(transformation_stack):
                mat = math3d.multiply_matrix(transformation, mat)
            pos_calc = [mat[3], mat[7], mat[11]]

            self.points_dict[joint.name].SetValue(frame, 0, pos_calc[0])
            self.points_dict[joint.name].SetValue(frame, 1, pos_calc[1])
            self.points_dict[joint.name].SetValue(frame, 2, pos_calc[2])

            # iterate through children joints
            for child in joint.children:
                self.transform_joint(bvh, child, frame, transformation_stack)
            transformation_stack.pop()
        else:
            return