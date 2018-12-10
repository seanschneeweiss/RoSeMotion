import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

x = Leap.Vector(1, 0, 0)
y = Leap.Vector(0, 1, 0)
z = Leap.Vector(0, 1, 1)


matrix = Leap.Matrix(x, y, z)
point = Leap.Vector(1, 1, 1)
transformed = matrix.transform_direction(point)

# print(matrix.set_rotation(Leap.Vector.z_axis, .34))
# print(matrix)
# print(transformed)

import numpy as np
import math

eul1 = np.zeros(3)
eul2 = np.zeros(3)

#rotmat = Leap.Matrix()
rotmat = matrix
rotmat = rotmat.to_array_3x3()
rotmat = np.array(rotmat)
rotmat = rotmat.reshape(3, 3)
print(rotmat)

##############
#  i, j, k, n
#  n = parity of axis permutation (even=False, odd=True)
#  from https://github.com/dfelinto/blender/blob/master/source/blender/blenlib/intern/math_rotation.c
##############

# order = [0, 1, 2, False] # XYZ
# order = [0, 2, 1, True] # XZY
# order = [1, 0, 2, True] # YXZ
# order = [1, 2, 0, False] # YZX
order = [2, 0, 1, False]  # ZXY
# order = [2, 1, 0, True] # ZYX

i = int(order[0])
j = int(order[1])
k = int(order[2])
parity = order[3]

cy = np.hypot(rotmat[i, i], rotmat[i, j])

if cy > 16 * Leap.EPSILON:
    eul1[i] = math.atan2(rotmat[j, k], rotmat[k, k])
    eul1[j] = math.atan2(-rotmat[i, k], cy)
    eul1[k] = math.atan2(rotmat[i, j], rotmat[i, i])

    eul2[i] = math.atan2(-rotmat[j, k], -rotmat[k, k])
    eul2[j] = math.atan2(-rotmat[i, k], -cy)
    eul2[k] = math.atan2(-rotmat[i, j], -rotmat[i, i])

else:
    eul1[i] = math.atan2(-rotmat[k, j], rotmat[j, j])
    eul1[j] = math.atan2(-rotmat[i, k], cy)
    eul1[k] = 0.0

    eul2 = eul1

#  parity of axis permutation (even=False, odd=True)
if parity:
    eul1 = np.negative(eul1)
    eul2 = np.negative(eul2)

# return best, which is just the one with lowest values in it
if np.sum(np.absolute(eul1)) > np.sum(np.absolute(eul2)):
    print(eul2)
else:
    print(eul1)


def quat_to_mat(quat):
    q0 = math.sqrt(2) * quat[0]
    q1 = math.sqrt(2) * quat[1]
    q2 = math.sqrt(2) * quat[2]
    q3 = math.sqrt(2) * quat[3]

    qda = q0 * q1
    qdb = q0 * q2
    qdc = q0 * q3
    qaa = q1 * q1
    qab = q1 * q2
    qac = q1 * q3
    qbb = q2 * q2
    qbc = q2 * q3
    qcc = q3 * q3

    mat = np.zeros((3, 3))
    mat[0, 0] = 1.0 - qbb - qcc
    mat[0, 1] = qdc + qab
    mat[0, 2] = -qdb + qac

    mat[1, 0] = -qdc + qab
    mat[1, 1] = 1.0 - qaa - qcc
    mat[1, 2] = qda + qbc

    mat[2, 0] = qdb + qac
    mat[2, 1] = -qda + qbc
    mat[2, 2] = 1.0 - qaa - qbb
