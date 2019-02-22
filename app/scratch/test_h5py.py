import numpy as np
import h5py
import matplotlib.pyplot as plt

h5file = h5py.File('output.anydata.h5')
data = np.array(h5file['Output/JointAngleOutputs/CMC1Flexion'])
h5file.close()
print(data)

number_frames = np.size(data)
frames = np.arange(0, number_frames)

# use LaTeX fonts in the plot
# plt.rc('text', usetex=True)
plt.rc('font', family='serif')

plt.plot(frames, np.multiply(data, 180/np.pi))
plt.xlim(0, number_frames)
plt.ylim(-90, 90)
plt.xlabel('frames')
plt.ylabel('angle in degree')
plt.title('flexion (x-axis)')
plt.legend(['bvh', 'any'], loc=2)
plt.grid(True)
plt.show()
