import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation
from resources.pymo.pymo.parsers import BVHParser
from matplotlib.widgets import Slider
from resources.pymo.pymo.preprocessing import MocapParameterizer
import matplotlib.pyplot

# Set up formatting for the movie files
# Writer = animation.writers['ffmpeg']
# writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

# BVH-File
bvh = BVHParser()
bvh_data = bvh.parse('../../output/BVH/RightHand.bvh')
bvh_number_frames = np.size(bvh.data.values.RightHandIndex2_Xrotation.values)
bvh_frames = np.arange(0, bvh_number_frames)


mp = MocapParameterizer('position')
positions = mp.fit_transform([bvh_data])


fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='3d')

joints_to_draw = positions[0].skeleton.keys()
lines = []
points = []

df = positions[0].values
# frame = 10

for joint in joints_to_draw:
    parent_x = df['%s_Xposition' % joint][0]
    parent_y = df['%s_Yposition' % joint][0]
    parent_z = df['%s_Zposition' % joint][0]
    # ^ In mocaps, Y is the up-right axis

    points.append(ax.plot([parent_x],
                          [parent_y],
                          [parent_z],
                          linestyle="", c='b', marker='o'))

    children_to_draw = [c for c in positions[0].skeleton[joint]['children'] if c in joints_to_draw]

    for c in children_to_draw:
        child_x = df['%s_Xposition' % c][0]
        child_y = df['%s_Yposition' % c][0]
        child_z = df['%s_Zposition' % c][0]
        # ^ In mocaps, Y is the up-right axis

        lines.append(ax.plot([parent_x, child_x], [parent_y, child_y], [parent_z, child_z], 'k-', lw=2, c='black'))


def update(frame):
    index1 = 0
    index2 = 0

    for up_joint in joints_to_draw:
        up_parent_x = df['%s_Xposition' % up_joint][frame]
        up_parent_y = df['%s_Yposition' % up_joint][frame]
        up_parent_z = df['%s_Zposition' % up_joint][frame]
        # ^ In mocaps, Y is the up-right axis

        points[index1][0].set_data([up_parent_x], [up_parent_y])
        points[index1][0].set_3d_properties([up_parent_z])
        index1 += 1

        up_children_to_draw = [c for c in positions[0].skeleton[up_joint]['children'] if c in joints_to_draw]

        for c in up_children_to_draw:
            up_child_x = df['%s_Xposition' % c][frame]
            up_child_y = df['%s_Yposition' % c][frame]
            up_child_z = df['%s_Zposition' % c][frame]
            # ^ In mocaps, Y is the up-right axis

            lines[index2][0].set_data([[up_parent_x, up_child_x], [up_parent_y, up_child_y]])
            lines[index2][0].set_3d_properties([up_parent_z, up_child_z])
            index2 += 1


ax.set_xlim3d([-200.0, 200.0])
ax.set_xlabel('X')

ax.set_ylim3d([-200.0, 200.0])
ax.set_ylabel('Y')

ax.set_zlim3d([-200.0, 200.0])
ax.set_zlabel('Z')

ax.view_init(elev=135, azim=-90)

# Creating the Animation object
line_ani = animation.FuncAnimation(fig, update, bvh_number_frames-1,
                                   interval=5, blit=False)
line_ani.save('bvh_video.mp4')

plt.show()






