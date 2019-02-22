"""
============
3D animation
============

A simple example of an animated plot... In 3D!
"""
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from resources.pymo.pymo.parsers import BVHParser

# BVH-File
bvh = BVHParser()
bvh_data = bvh.parse('../../output/BVH/20190213_validierung_1.bvh')
bvh_number_frames = np.size(bvh.data.values.RightHandIndex2_Xrotation.values)
bvh_frames = np.arange(0, bvh_number_frames)



print(bvh_data.skeleton["Leap_Root"]['offsets'][0])
# Attaching 3D axis to the figure
fig = plt.figure()
ax = p3.Axes3D(fig)

# Fifty lines of random 3-D lines
# data = [Gen_RandLine(25, 3) for index in range(1)]

# Creating fifty line objects.
# NOTE: Can't pass empty arrays into 3d version of plot()
# lines = [ax.plot(dat[0, 0:1], dat[1, 0:1], dat[2, 0:1])[0] for dat in data]
for finger in bvh_data.skeleton:
    for finger_child in bvh_data.skeleton[finger]['children']:
        ax.plot([bvh_data.skeleton[finger]['offsets'][0], bvh_data.skeleton[finger_child]['offsets'][0]],
                [bvh_data.skeleton[finger]['offsets'][1], bvh_data.skeleton[finger_child]['offsets'][1]],
                [bvh_data.skeleton[finger]['offsets'][2], bvh_data.skeleton[finger_child]['offsets'][2]])
# Setting the axes properties
ax.set_xlim3d([-100.0, 100.0])
ax.set_xlabel('X')

ax.set_ylim3d([-100.0, 100.0])
ax.set_ylabel('Y')

ax.set_zlim3d([-100.0, 100.0])
ax.set_zlabel('Z')

ax.set_title('3D Test')

plt.show()