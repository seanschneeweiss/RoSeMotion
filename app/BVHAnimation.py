import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib.widgets import Slider
from resources.pymo.pymo.preprocessing import MocapParameterizer
import numpy as np
from matplotlib import pyplot as plt


class BVHAnimation:
    @staticmethod
    def animate(bvh_data):
        BVHAnimation.init_plot(BVHAnimation.positions(bvh_data)[0])

    @staticmethod
    def positions(bvh_data):
        # convert rotations to positions for each joint
        mp = MocapParameterizer('position')
        return mp.fit_transform([bvh_data])

    @staticmethod
    def init_plot(positions):
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')

        axcolor = 'lightgoldenrodyellow'
        axframe = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)

        bvh_number_frames = positions.values.shape[0]
        sframe = Slider(axframe, 'Frame', 0, bvh_number_frames-1, valinit=0, valstep=1)

        joints_to_draw = positions.skeleton.keys()
        lines = []
        points = []

        df = positions.values

        for joint in joints_to_draw:
            parent_x = df['%s_Xposition' % joint][0]
            parent_y = df['%s_Yposition' % joint][0]
            parent_z = df['%s_Zposition' % joint][0]
            # ^ In mocaps, Y is the up-right axis

            points.append(ax.plot([parent_x],
                                       [parent_y],
                                       [parent_z],
                                       linestyle="", c='b', marker='o'))

            children_to_draw = [c for c in positions.skeleton[joint]['children'] if c in joints_to_draw]

            for c in children_to_draw:
                child_x = df['%s_Xposition' % c][0]
                child_y = df['%s_Yposition' % c][0]
                child_z = df['%s_Zposition' % c][0]
                # ^ In mocaps, Y is the up-right axis

                lines.append(ax.plot([parent_x, child_x], [parent_y, child_y], [parent_z, child_z], 'k-', lw=2, c='black'))

        def update(_):
            """Update function for the slider"""
            frame = int(sframe.val)
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

                up_children_to_draw = [c for c in positions.skeleton[up_joint]['children'] if c in joints_to_draw]

                for c in up_children_to_draw:
                    up_child_x = df['%s_Xposition' % c][frame]
                    up_child_y = df['%s_Yposition' % c][frame]
                    up_child_z = df['%s_Zposition' % c][frame]
                    # ^ In mocaps, Y is the up-right axis

                    lines[index2][0].set_data([[up_parent_x, up_child_x], [up_parent_y, up_child_y]])
                    lines[index2][0].set_3d_properties([up_parent_z, up_child_z])
                    index2 += 1

            fig.canvas.draw_idle()

        # update the plot when changing the slider value
        sframe.on_changed(update)

        # ax.set_xlim3d([-200.0, 200.0])
        ax.set_xlabel('X')

        # ax.set_ylim3d([-200.0, 200.0])
        ax.set_ylabel('Y')

        # ax.set_zlim3d([-200.0, 200.0])
        ax.set_zlabel('Z')

        ax.view_init(elev=135, azim=-90)

        plt.show()
