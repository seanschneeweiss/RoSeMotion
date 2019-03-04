"""
============
3D animation
============

A simple example of an animated plot... In 3D!
"""
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation
from resources.pymo.pymo.parsers import BVHParser


def calc_offset_pos(name):
    name_parent = bvh_data.skeleton[name]['parent']

    # root
    if name_parent:
        bvh_data.skeleton[name]['offset_position'] = np.add(bvh_data.skeleton[name]['offsets'],
                                                     bvh_data.skeleton[name_parent]['offset_position'])
    else:
        bvh_data.skeleton[name]['offset_position'] = bvh_data.skeleton[name]['offsets']

    for child in bvh_data.skeleton[name]['children']:
        calc_offset_pos(child)


def calc_frame_pos(name):
    name_parent = bvh_data.skeleton[name]['parent']
    if 'Nub' not in name:
        # root
        if name_parent and 'Nub' not in name:
            for index in bvh_frames:
                pos_x = np.add(bvh_data.skeleton[name]['frame_offset_x'][index],
                               bvh_data.skeleton[name_parent]['frame_position_x'][index])
                pos_y = np.add(bvh_data.skeleton[name]['frame_offset_y'][index],
                               bvh_data.skeleton[name_parent]['frame_position_y'][index])
                pos_z = np.add(bvh_data.skeleton[name]['frame_offset_z'][index],
                               bvh_data.skeleton[name_parent]['frame_position_z'][index])
                bvh_data.skeleton[name]['frame_position_x'].append(pos_x)
                bvh_data.skeleton[name]['frame_position_y'].append(pos_y)
                bvh_data.skeleton[name]['frame_position_z'].append(pos_z)
        else:
            for index in bvh_frames:
                pos_x = bvh_data.skeleton[name]['frame_offset_x'][index]
                pos_y = bvh_data.skeleton[name]['frame_offset_y'][index]
                pos_z = bvh_data.skeleton[name]['frame_offset_z'][index]

                bvh_data.skeleton[name]['frame_position_x'].append(pos_x)
                bvh_data.skeleton[name]['frame_position_y'].append(pos_y)
                bvh_data.skeleton[name]['frame_position_z'].append(pos_z)

        for child in bvh_data.skeleton[name]['children']:
            calc_frame_pos(child)


def rot_matrix(name, frame):
    # name = "RightHandThumb2"
    # frame = 5
    channel = np.array([name + "_Yrotation",
                        name + "_Yrotation",
                        name + "_Zrotation"])

    offset = bvh_data.skeleton[name]['offsets']
    angle_x = np.deg2rad(bvh_data.values[channel[0]][frame])
    angle_y = np.deg2rad(bvh_data.values[channel[1]][frame])
    angle_z = np.deg2rad(bvh_data.values[channel[2]][frame])

    rotation_x = np.array([[1,               0,                0],
                          [0, np.cos(angle_x), -np.sin(angle_x)],
                          [0, np.sin(angle_x),  np.cos(angle_x)]])

    rotation_y = np.array([[np.cos(angle_y),  0, np.sin(angle_y)],
                          [0,                1,               0],
                          [-np.sin(angle_y), 0, np.cos(angle_y)]])

    rotation_z = np.array([[np.cos(angle_z), -np.sin(angle_z), 0],
                           [np.sin(angle_z),  np.cos(angle_z), 0],
                           [0,                              0, 1]])

    # print(rotation_x)
    # print(np.matmul(np.matmul(rotation_z, np.matmul(rotation_y, rotation_x)), offset))
    pos = np.matmul(np.matmul(rotation_z, np.matmul(rotation_y, rotation_x)), offset)
    bvh_data.skeleton[name]['frame_offset_x'].append(pos[0])
    bvh_data.skeleton[name]['frame_offset_y'].append(pos[1])
    bvh_data.skeleton[name]['frame_offset_z'].append(pos[2])

    # print(channel)
    # print(offset)
    # print(angle_x, angle_y, angle_z)


# BVH-File
bvh = BVHParser()
bvh_data = bvh.parse('../../output/BVH/RightHand.bvh')
bvh_number_frames = np.size(bvh.data.values.RightHandIndex2_Xrotation.values)
bvh_frames = np.arange(0, bvh_number_frames)

# print(bvh_data.skeleton["Leap_Root"]['offsets'][0])

# Get Root
root = bvh_data.root_name
# print(np.add(bvh_data.skeleton[root]['offsets'], bvh_data.skeleton["RightElbow"]['offsets']))
# bvh_data.skeleton[root]['position'] = bvh_data.skeleton[root]['offsets']
calc_offset_pos(root)
# print(root)
# print(bvh_data.values["Leap_Root_Xrotation"][0])

for finger in bvh_data.skeleton:
    if 'Nub' not in finger:
        bvh_data.skeleton[finger]['frame_offset_x'] = []
        bvh_data.skeleton[finger]['frame_offset_y'] = []
        bvh_data.skeleton[finger]['frame_offset_z'] = []
        for i in bvh_frames:
            rot_matrix(finger, i)

        bvh_data.skeleton[finger]['frame_position_x'] = []
        bvh_data.skeleton[finger]['frame_position_y'] = []
        bvh_data.skeleton[finger]['frame_position_z'] = []


print(bvh_data.skeleton['RightHandThumb2']['frame_offset_x'][369])
print(bvh_data.skeleton['RightHandThumb2']['frame_offset_x'][0])
print(bvh_data.skeleton['RightHand']['frame_offset_x'][0])
print(np.add(bvh_data.skeleton['RightHandThumb2']['frame_offset_x'][0],
                               bvh_data.skeleton['RightHand']['frame_offset_x'][0]))
calc_frame_pos(root)

# Attaching 3D axis to the figure
fig = plt.figure()
ax = p3.Axes3D(fig)
# Fifty lines of random 3-D lines
# data = [Gen_RandLine(25, 3) for index in range(1)]

# Creating fifty line objects.
# NOTE: Can't pass empty arrays into 3d version of plot()
# lines = [ax.plot(dat[0, 0:1], dat[1, 0:1], dat[2, 0:1])[0] for dat in data]
for finger in bvh_data.skeleton:
    finger_parent = bvh_data.skeleton[finger]['parent']
    if finger_parent and 'Nub' not in finger:
        # print(finger, finger_parent)
        # ax.plot([bvh_data.skeleton[finger]['offset_position'][0],
        #          bvh_data.skeleton[finger_parent]['offset_position'][0]],
        #         [bvh_data.skeleton[finger]['offset_position'][1],
        #          bvh_data.skeleton[finger_parent]['offset_position'][1]],
        #         [bvh_data.skeleton[finger]['offset_position'][2],
        #          bvh_data.skeleton[finger_parent]['offset_position'][2]])
        ax.plot([bvh_data.skeleton[finger]['frame_position_x'][0],
                 bvh_data.skeleton[finger_parent]['frame_position_x'][0]],
                [bvh_data.skeleton[finger]['frame_position_y'][0],
                 bvh_data.skeleton[finger_parent]['frame_position_y'][0]],
                [bvh_data.skeleton[finger]['frame_position_z'][0],
                 bvh_data.skeleton[finger_parent]['frame_position_z'][0]])
# Setting the axes properties
ax.set_xlim3d([-200.0, 200.0])
ax.set_xlabel('X')

ax.set_ylim3d([-200.0, 200.0])
ax.set_ylabel('Y')

ax.set_zlim3d([-200.0, 200.0])
ax.set_zlabel('Z')

ax.set_title('3D Test')

plt.show()