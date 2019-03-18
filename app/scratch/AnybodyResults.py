import os
import re
import numpy as np
import copy
from resources.AnyPyTools.anypytools import AnyPyProcess
from resources.AnyPyTools.anypytools.macro_commands import (MacroCommand, Load, SetValue, SetValue_random, Dump,
                                                            SaveDesign, LoadDesign, SaveValues, LoadValues,
                                                            UpdateValues, SaveData, OperationRun)
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib.lines import Line2D


LINE_STYLES = ['--', '-.', '--', ':']
COLORS = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
# 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan'


class AnybodyResults:
    def __init__(self):
        self.output = None
        self.fig = None
        self.ax = None

        data_dict = {'Interpolation': None}
        rotation_dict = {'Flexion': copy.deepcopy(data_dict),
                         'Abduction': copy.deepcopy(data_dict),
                         'Deviation': copy.deepcopy(data_dict)}
        self.joint_mapping = {
            'CMC1': copy.deepcopy(rotation_dict),
            'MCP1': copy.deepcopy(rotation_dict),
            'DIP1': copy.deepcopy(rotation_dict),
            'CMC2': copy.deepcopy(rotation_dict),
            'MCP2': copy.deepcopy(rotation_dict),
            'PIP2': copy.deepcopy(rotation_dict),
            'DIP2': copy.deepcopy(rotation_dict),
            'CMC3': copy.deepcopy(rotation_dict),
            'MCP3': copy.deepcopy(rotation_dict),
            'PIP3': copy.deepcopy(rotation_dict),
            'DIP3': copy.deepcopy(rotation_dict),
            'CMC4': copy.deepcopy(rotation_dict),
            'MCP4': copy.deepcopy(rotation_dict),
            'PIP4': copy.deepcopy(rotation_dict),
            'DIP4': copy.deepcopy(rotation_dict),
            'CMC5': copy.deepcopy(rotation_dict),
            'MCP5': copy.deepcopy(rotation_dict),
            'PIP5': copy.deepcopy(rotation_dict),
            'DIP5': copy.deepcopy(rotation_dict)}

        self.checkbuttons = {'check_finger': {'status': (False, True, False, False, False),
                                              'labels': ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky'),
                                              'buttons': None},
                             'check_joint': {'status': (False, True, False, False),
                                             'labels': ('CMC', 'MCP', 'PIP', 'DIP'),
                                             'buttons': None},
                             'check_rotation': {'status': (True, False, False),
                                                'labels': ('Flexion', 'Abduction', 'Deviation'),
                                                'buttons': None},
                             'check_data': {'status': (False, True),
                                            'labels': ('LM', 'Interpolation'),
                                            'buttons': None}}

        self.get_anybody_output()
        self.plot_setup()
        self.generate_lines_interpolation()
        self.update_plot()
        plt.show()

    def get_anybody_output(self):
        cwd = os.getcwd()
        os.chdir(
            'D:\\RobinSean\Sean\\5. Master\\Projekt CSE\\AnybodyModelle\\regensburg-ulm-hand-model\\AnyBody\\Application\\Examples\\FreeHandMove')

        app = AnyPyProcess(num_processes=1,
                           return_task_info=True,
                           anybodycon_path="C:/Program Files/AnyBody Technology/AnyBody.7.1/AnyBodyCon.exe")

        macrolist = [
            Load('FreeHand.Main.any'),
            OperationRun('Main.Study.Kinematics'),
            Dump('Main.Study.Output.JointAngleOutputs'),
            Dump('Main.Study.nStep')
        ]
        self.output = app.start_macro(macrolist)
        os.chdir(cwd)

    def plot_setup(self):
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.2)
        plt.grid()
        plt.title('comparison of angles')
        plt.xlabel('frame')
        plt.ylabel('angle in degree')
        custom_legend = [Line2D([0], [0], linestyle='None', color=COLORS[0], marker='$1$', lw=2, label='Thumb'),
                         Line2D([0], [0], linestyle='None', color=COLORS[1], marker='$2$', lw=2, label='Index'),
                         Line2D([0], [0], linestyle='None', color=COLORS[2], marker='$3$', lw=2, label='Middle'),
                         Line2D([0], [0], linestyle='None', color=COLORS[3], marker='$4$', lw=2, label='Ring'),
                         Line2D([0], [0], linestyle='None', color=COLORS[4], marker='$5$', lw=2, label='Pinky'),
                         Line2D([0], [0], linestyle=LINE_STYLES[0], color='k', lw=2, label='CMC'),
                         Line2D([0], [0], linestyle=LINE_STYLES[1], color='k', lw=2, label='MCP'),
                         Line2D([0], [0], linestyle=LINE_STYLES[2], color='k', lw=2, label='PIP'),
                         Line2D([0], [0], linestyle=LINE_STYLES[3], color='k', lw=2, label='DIP'),
                         Line2D([0], [0], linestyle='None', color='k', marker='$F$', lw=2, label='Flexion'),
                         Line2D([0], [0], linestyle='None', color='k', marker='$A$', lw=2, label='Abduction'),
                         Line2D([0], [0], linestyle='None', color='k', marker='$D$', lw=2, label='Deviation')]
        leg = self.ax.legend(handles=custom_legend)
        # change the font colors to match the line colors:
        for line, text in zip(leg.get_lines(), leg.get_texts()):
            text.set_color(line.get_color())

        """checkboxes"""
        rax_finger = plt.axes([0.05, 0.7, 0.1, 0.15])
        self.checkbuttons['check_finger']['buttons'] = CheckButtons(
            rax_finger, self.checkbuttons['check_finger']['labels'], self.checkbuttons['check_finger']['status'])

        rax_joint = plt.axes([0.05, 0.5, 0.1, 0.15])
        self.checkbuttons['check_joint']['buttons'] = CheckButtons(
            rax_joint, self.checkbuttons['check_joint']['labels'], self.checkbuttons['check_joint']['status'])

        rax_rotation = plt.axes([0.05, 0.3, 0.1, 0.15])
        self.checkbuttons['check_rotation']['buttons'] = CheckButtons(
            rax_rotation, self.checkbuttons['check_rotation']['labels'], self.checkbuttons['check_rotation']['status'])

        rax_data = plt.axes([0.05, 0.1, 0.1, 0.15])
        self.checkbuttons['check_data']['buttons'] = CheckButtons(
            rax_data, self.checkbuttons['check_data']['labels'], self.checkbuttons['check_data']['status'])

        # activate on_clicked function for all button groups
        for button_group, button_values in self.checkbuttons.items():
            button_values['buttons'].on_clicked(self.change_label)

    def save_status(self):
        for b_group, b_values in self.checkbuttons.items():
            self.checkbuttons[b_group]['status'] = b_values['buttons'].get_status()

    def change_label(self, label):
        self.save_status()
        self.update_plot()
        plt.draw()

    def generate_lines_interpolation(self):
        frames = self.output['Main.Study.nStep']
        t = np.arange(1, frames + 1, 1)

        output_path = 'Main.Study.Output.JointAngleOutputs.{}'
        rotation_index = {'Flexion': 0,
                          'Abduction': 1,
                          'Deviation': 2}
        markers_rotation = ['$F{}$', '$A{}$', '$D{}$']

        def joint_line_style(joint_name):
            if 'CMC' in joint_name:
                return LINE_STYLES[0]
            if 'MCP' in joint_name:
                return LINE_STYLES[1]
            if 'PIP' in joint_name:
                return LINE_STYLES[2]
            if 'DIP' in joint_name:
                return LINE_STYLES[3]

        # save plots into joint_mapping
        for joint_name, joint_values in self.joint_mapping.items():
            line_style = joint_line_style(joint_name)
            _, finger_number = AnybodyResults.split_joint(joint_name)
            line_color = COLORS[finger_number - 1]
            for rotation, rotation_data in joint_values.items():
                index = rotation_index[rotation]
                for data in rotation_data:
                    self.joint_mapping[joint_name][rotation][data] = self.ax.plot(
                        t, self.output[output_path.format(joint_name)][0][:, index],
                        visible=False,
                        lw=1.5,
                        marker=markers_rotation[index].format(finger_number),
                        markersize=11,
                        markevery=(0.02 * index + finger_number / 100, 0.1),
                        linestyle=line_style,
                        color=line_color
                    )[0]

    def update_plot(self):
        for joint_name, joint_values in self.joint_mapping.items():
            for rotation, rotation_data in joint_values.items():
                for data_name, line in rotation_data.items():
                    joint_type, finger_index = AnybodyResults.split_joint(joint_name)
                    plot_status = \
                        self.checkbuttons['check_finger']['status'][finger_index - 1] and \
                        self.checkbuttons['check_joint']['status'][
                            self.checkbuttons['check_joint']['labels'].index(joint_type)] and \
                        self.checkbuttons['check_rotation']['status'][
                            self.checkbuttons['check_rotation']['labels'].index(rotation)] and \
                        self.checkbuttons['check_data']['status'][
                            self.checkbuttons['check_data']['labels'].index(data_name)]
                    line.set_visible(plot_status)

    @staticmethod
    def split_joint(joint_name):
        joint_split = re.split('(\d)', joint_name)
        return joint_split[0], int(joint_split[1])


anybody_results = AnybodyResults()
