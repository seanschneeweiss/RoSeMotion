import numpy as np
import matplotlib.pyplot as plt
from resources.pymo.pymo.parsers import BVHParser
from matplotlib2tikz import save as tikz_save

# BVH-File
bvh = BVHParser()
bvh_data = bvh.parse('../../output/BVH/20190213_validierung_1.bvh')
bvh_number_frames = np.size(bvh.data.values.RightHandIndex2_Xrotation.values)
bvh_frames = np.arange(0, bvh_number_frames)
print(bvh_number_frames, bvh_frames)

# Thumb
bvh_RightHandThumb2 = np.array([bvh_data.values.RightHandThumb2_Xrotation.values,
                                bvh_data.values.RightHandThumb2_Yrotation.values,
                                bvh_data.values.RightHandThumb2_Zrotation.values])
bvh_RightHandThumb3 = np.array([bvh_data.values.RightHandThumb3_Xrotation.values,
                                bvh_data.values.RightHandThumb3_Yrotation.values,
                                bvh_data.values.RightHandThumb3_Zrotation.values])
bvh_RightHandThumb4 = np.array([bvh_data.values.RightHandThumb4_Xrotation.values,
                                bvh_data.values.RightHandThumb4_Yrotation.values,
                                bvh_data.values.RightHandThumb4_Zrotation.values])
bvh_RightHandThumb5 = np.array([bvh_data.values.RightHandThumb5_Xrotation.values,
                                bvh_data.values.RightHandThumb5_Yrotation.values,
                                bvh_data.values.RightHandThumb5_Zrotation.values])

# Index
bvh_RightHandIndex1 = np.array([bvh_data.values.RightHandIndex1_Xrotation.values,
                                bvh_data.values.RightHandIndex1_Yrotation.values,
                                bvh_data.values.RightHandIndex1_Zrotation.values])
bvh_RightHandIndex2 = np.array([bvh_data.values.RightHandIndex2_Xrotation.values,
                                bvh_data.values.RightHandIndex2_Yrotation.values,
                                bvh_data.values.RightHandIndex2_Zrotation.values])
bvh_RightHandIndex3 = np.array([bvh_data.values.RightHandIndex3_Xrotation.values,
                                bvh_data.values.RightHandIndex3_Yrotation.values,
                                bvh_data.values.RightHandIndex3_Zrotation.values])
bvh_RightHandIndex4 = np.array([bvh_data.values.RightHandIndex4_Xrotation.values,
                                bvh_data.values.RightHandIndex4_Yrotation.values,
                                bvh_data.values.RightHandIndex4_Zrotation.values])
bvh_RightHandIndex5 = np.array([bvh_data.values.RightHandIndex5_Xrotation.values,
                                bvh_data.values.RightHandIndex5_Yrotation.values,
                                bvh_data.values.RightHandIndex5_Zrotation.values])

# Middle
bvh_RightHandMiddle1 = np.array([bvh_data.values.RightHandMiddle1_Xrotation.values,
                                 bvh_data.values.RightHandMiddle1_Yrotation.values,
                                 bvh_data.values.RightHandMiddle1_Zrotation.values])
bvh_RightHandMiddle2 = np.array([bvh_data.values.RightHandMiddle2_Xrotation.values,
                                 bvh_data.values.RightHandMiddle2_Yrotation.values,
                                 bvh_data.values.RightHandMiddle2_Zrotation.values])
bvh_RightHandMiddle3 = np.array([bvh_data.values.RightHandMiddle3_Xrotation.values,
                                 bvh_data.values.RightHandMiddle3_Yrotation.values,
                                 bvh_data.values.RightHandMiddle3_Zrotation.values])
bvh_RightHandMiddle4 = np.array([bvh_data.values.RightHandMiddle4_Xrotation.values,
                                 bvh_data.values.RightHandMiddle4_Yrotation.values,
                                 bvh_data.values.RightHandMiddle4_Zrotation.values])
bvh_RightHandMiddle5 = np.array([bvh_data.values.RightHandMiddle5_Xrotation.values,
                                 bvh_data.values.RightHandMiddle5_Yrotation.values,
                                 bvh_data.values.RightHandMiddle5_Zrotation.values])

# Ring
bvh_RightHandRing1 = np.array([bvh_data.values.RightHandRing1_Xrotation.values,
                               bvh_data.values.RightHandRing1_Yrotation.values,
                               bvh_data.values.RightHandRing1_Zrotation.values])
bvh_RightHandRing2 = np.array([bvh_data.values.RightHandRing2_Xrotation.values,
                               bvh_data.values.RightHandRing2_Yrotation.values,
                               bvh_data.values.RightHandRing2_Zrotation.values])
bvh_RightHandRing3 = np.array([bvh_data.values.RightHandRing3_Xrotation.values,
                               bvh_data.values.RightHandRing3_Yrotation.values,
                               bvh_data.values.RightHandRing3_Zrotation.values])
bvh_RightHandRing4 = np.array([bvh_data.values.RightHandRing4_Xrotation.values,
                               bvh_data.values.RightHandRing4_Yrotation.values,
                               bvh_data.values.RightHandRing4_Zrotation.values])
bvh_RightHandRing5 = np.array([bvh_data.values.RightHandRing5_Xrotation.values,
                               bvh_data.values.RightHandRing5_Yrotation.values,
                               bvh_data.values.RightHandRing5_Zrotation.values])

# Pinky
bvh_RightHandPinky1 = np.array([bvh_data.values.RightHandPinky1_Xrotation.values,
                                bvh_data.values.RightHandPinky1_Yrotation.values,
                                bvh_data.values.RightHandPinky1_Zrotation.values])
bvh_RightHandPinky2 = np.array([bvh_data.values.RightHandPinky2_Xrotation.values,
                                bvh_data.values.RightHandPinky2_Yrotation.values,
                                bvh_data.values.RightHandPinky2_Zrotation.values])
bvh_RightHandPinky3 = np.array([bvh_data.values.RightHandPinky3_Xrotation.values,
                                bvh_data.values.RightHandPinky3_Yrotation.values,
                                bvh_data.values.RightHandPinky3_Zrotation.values])
bvh_RightHandPinky4 = np.array([bvh_data.values.RightHandPinky4_Xrotation.values,
                                bvh_data.values.RightHandPinky4_Yrotation.values,
                                bvh_data.values.RightHandPinky4_Zrotation.values])
bvh_RightHandPinky5 = np.array([bvh_data.values.RightHandPinky5_Xrotation.values,
                                bvh_data.values.RightHandPinky5_Yrotation.values,
                                bvh_data.values.RightHandPinky5_Zrotation.values])

# Anybody
interpol_data = np.loadtxt("hand_interpolated_joint_angles_n047_2.txt", delimiter=",", skiprows=1, unpack=True)
any_number_frame = np.size(interpol_data[1])
any_frame = np.arange(0, bvh_number_frames, np.round(bvh_number_frames/any_number_frame))
print(any_number_frame, any_frame)

# Thumb
any_RightHandThumb2 = np.array([np.multiply(interpol_data[1], (180 / np.pi)),   # CMC1Flexion
                                np.multiply(interpol_data[2], (180 / np.pi)),   # CMC1Abduction
                                np.zeros(any_number_frame)])                    # CMC1Deviation = 0

any_RightHandThumb3 = np.array([np.multiply(interpol_data[3], (180 / np.pi)),   # MCP1Flexion
                                np.multiply(interpol_data[4], (180 / np.pi)),   # MCP1Abduction
                                np.zeros(any_number_frame)])                    # MCP1Deviation = 0

any_RightHandThumb4 = np.array([np.multiply(interpol_data[5], (180 / np.pi)),   # DIP1Flexion
                                np.zeros(any_number_frame),                     # DIP1Abduction = 0
                                np.zeros(any_number_frame)])                    # DIP1Deviation = 0

any_RightHandThumb5 = np.array([np.zeros(any_number_frame),                     # = 0
                                np.zeros(any_number_frame),                     # = 0
                                np.zeros(any_number_frame)])                    # = 0

# Index
any_RightHandIndex1 = np.array([np.zeros(any_number_frame),                     # CMC2Flexion = 0
                                np.zeros(any_number_frame),                     # CMC2Abduction = 0
                                np.zeros(any_number_frame)])                    # CMC2Deviation = 0

any_RightHandIndex2 = np.array([np.multiply(interpol_data[6], (180 / np.pi)),   # MCP2Flexion
                                np.multiply(interpol_data[7], (180 / np.pi)),   # MCP2Abduction
                                np.zeros(any_number_frame)])                    # MCP2Deviation = 0

any_RightHandIndex3 = np.array([np.multiply(interpol_data[8], (180 / np.pi)),   # PIP2Flexion
                                np.zeros(any_number_frame),                     # PIP2Abduction = 0
                                np.zeros(any_number_frame)])                    # PIP2Deviation = 0

any_RightHandIndex4 = np.array([np.multiply(interpol_data[9], (180 / np.pi)),   # DIP2Flexion
                                np.zeros(any_number_frame),                     # DIP2Abduction = 0
                                np.zeros(any_number_frame)])                    # DIP2Deviation = 0

any_RightHandIndex5 = np.array([np.zeros(any_number_frame),                     # = 0
                                np.zeros(any_number_frame),                     # = 0
                                np.zeros(any_number_frame)])                    # = 0

# Middle
any_RightHandMiddle1 = np.array([np.zeros(any_number_frame),                     # CMC3Flexion = 0
                                 np.zeros(any_number_frame),                     # CMC3Abduction = 0
                                 np.zeros(any_number_frame)])                    # CMC3Deviation = 0

any_RightHandMiddle2 = np.array([np.multiply(interpol_data[10], (180 / np.pi)),  # MCP3Flexion
                                 np.multiply(interpol_data[11], (180 / np.pi)),  # MCP3Abduction
                                 np.zeros(any_number_frame)])                    # MCP3Deviation = 0

any_RightHandMiddle3 = np.array([np.multiply(interpol_data[12], (180 / np.pi)),  # PIP3Flexion
                                 np.zeros(any_number_frame),                     # PIP3Abduction = 0
                                 np.zeros(any_number_frame)])                    # PIP3Deviation = 0

any_RightHandMiddle4 = np.array([np.multiply(interpol_data[13], (180 / np.pi)),  # DIP3Flexion
                                 np.zeros(any_number_frame),                     # DIP3Abduction = 0
                                 np.zeros(any_number_frame)])                    # DIP3Deviation = 0

any_RightHandMiddle5 = np.array([np.zeros(any_number_frame),                     # = 0
                                 np.zeros(any_number_frame),                     # = 0
                                 np.zeros(any_number_frame)])                    # = 0

# Ring
any_RightHandRing1 = np.array([np.zeros(any_number_frame),                     # CMC4Flexion = 0
                               np.zeros(any_number_frame),                     # CMC4Abduction = 0
                               np.zeros(any_number_frame)])                    # CMC4Deviation = 0

any_RightHandRing2 = np.array([np.multiply(interpol_data[14], (180 / np.pi)),  # MCP4Flexion
                               np.multiply(interpol_data[15], (180 / np.pi)),  # MCP4Abduction
                               np.zeros(any_number_frame)])                    # MCP4Deviation = 0

any_RightHandRing3 = np.array([np.multiply(interpol_data[16], (180 / np.pi)),  # PIP4Flexion
                               np.zeros(any_number_frame),                     # PIP4Abduction = 0
                               np.zeros(any_number_frame)])                    # PIP4Deviation = 0

any_RightHandRing4 = np.array([np.multiply(interpol_data[17], (180 / np.pi)),  # DIP4Flexion
                               np.zeros(any_number_frame),                     # DIP4Abduction = 0
                               np.zeros(any_number_frame)])                    # DIP4Deviation = 0

any_RightHandRing5 = np.array([np.zeros(any_number_frame),                     # = 0
                               np.zeros(any_number_frame),                     # = 0
                               np.zeros(any_number_frame)])                    # = 0

# Pinky
any_RightHandPinky1 = np.array([np.zeros(any_number_frame),                     # CMC5Flexion = 0
                                np.zeros(any_number_frame),                     # CMC5Abduction = 0
                                np.zeros(any_number_frame)])                    # CMC5Deviation = 0

any_RightHandPinky2 = np.array([np.multiply(interpol_data[18], (180 / np.pi)),  # MCP5Flexion
                                np.multiply(interpol_data[19], (180 / np.pi)),  # MCP5Abduction
                                np.zeros(any_number_frame)])                    # MCP5Deviation = 0

any_RightHandPinky3 = np.array([np.multiply(interpol_data[20], (180 / np.pi)),  # PIP5Flexion
                                np.zeros(any_number_frame),                     # PIP5Abduction = 0
                                np.zeros(any_number_frame)])                    # PIP5Deviation = 0

any_RightHandPinky4 = np.array([np.multiply(interpol_data[21], (180 / np.pi)),  # DIP5Flexion
                                np.zeros(any_number_frame),                     # DIP5Abduction = 0
                                np.zeros(any_number_frame)])                    # DIP5Deviation = 0

any_RightHandPinky5 = np.array([np.zeros(any_number_frame),                     # = 0
                                np.zeros(any_number_frame),                     # = 0
                                np.zeros(any_number_frame)])                    # = 0

# Plot
bvh_plot = bvh_RightHandIndex3
any_plot = any_RightHandIndex3

# use LaTeX fonts in the plot
# plt.rc('text', usetex=True)
plt.rc('font', family='serif')

fig, axs = plt.subplots(3, 1)
axs[0].plot(bvh_frames, bvh_plot[0], linestyle='-', linewidth=2)
axs[0].plot(any_frame, -any_plot[0], linestyle=':', linewidth=2, marker='x')
axs[0].set_xlim(0, bvh_number_frames)
axs[0].set_ylim(-90, 90)
axs[0].set_xlabel('frames')
axs[0].set_ylabel('angle in degree')
axs[0].set_title('flexion (x-axis)')
axs[0].legend(['bvh', 'any'], loc='center left', bbox_to_anchor=(1, 0.5))
axs[0].grid(True)

axs[1].plot(bvh_frames, bvh_plot[1], linestyle='-', linewidth=2)
axs[1].plot(any_frame, -any_plot[1], linestyle=':', linewidth=2, marker='x')
axs[1].set_xlim(0, bvh_number_frames)
axs[1].set_ylim(-90, 90)
axs[1].set_xlabel('frames')
axs[1].set_ylabel('angle in degree')
axs[1].set_title('abduction (y-axis)')
axs[1].legend(['bvh', 'any'], loc='center left', bbox_to_anchor=(1, 0.5))
axs[1].grid(True)


axs[2].plot(bvh_frames, bvh_plot[2], linestyle='-', linewidth=2)
axs[2].plot(any_frame, -any_plot[2], linestyle=':', linewidth=2, marker='x')
axs[2].set_xlim(0, bvh_number_frames)
axs[2].set_ylim(-90, 90)
axs[2].set_xlabel('frames')
axs[2].set_ylabel('angle in degree')
axs[2].set_title('deviation (z-axis)')
axs[2].legend(['bvh', 'any'], loc='center left', bbox_to_anchor=(1, 0.5))
axs[2].grid(True)
fig.tight_layout()
plt.savefig("pgf_texsystem.pdf")
plt.savefig("pgf_texsystem.png")
plt.show()
