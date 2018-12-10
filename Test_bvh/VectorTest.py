import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

x = Leap.Vector(1, 0, 0)
y = Leap.Vector(0, 1, 0)
z = Leap.Vector(0, 0, 1)


matrix = Leap.Matrix(x, y, z)
point = Leap.Vector(1, 1, 1)
transformed = matrix.transform_direction(point)

# print(matrix.set_rotation(Leap.Vector.z_axis, .34))



# print(matrix)
# print(transformed)

import numpy as np
import math

eul1 = Leap.Vector()
eul2 = Leap.Vector()

rotmat = Leap.Matrix()
rotmat = rotmat.to_array_3x3()
rotmat = np.array(rotmat)
rotmat = rotmat.reshape(3,3)

# i, j, k
# from https://github.com/dfelinto/blender/blob/master/source/blender/blenlib/intern/math_rotation.c
# order = [0, 1, 2] # XYZ
# order = [0, 2, 1] # XZY
# order = [1, 0, 2] # YXZ
# order = [1, 2, 0] # YZX
order = [2, 0, 1]  # ZXY
# order = [2, 1, 0] # ZYX

i = order[0]
j = order[1]
k = order[2]

cy = np.hypot(rotmat[0, 0], rotmat[0, 1])
# xyz order
if cy > 16 * Leap.EPSILON:
    eul1.x = math.atan2(rotmat[j, k], rotmat[k, k])
    eul1.y = math.atan2(-rotmat[i, k], cy)
    eul1.z = math.atan2(rotmat[i, j], rotmat[i, i])

    eul2.x = math.atan2(-rotmat[j, k], -rotmat[k, k])
    eul2.y = math.atan2(-rotmat[i, k], -cy)
    eul2.z = math.atan2(-rotmat[i, j], -rotmat[i, i])

else:
    eul1.x = math.atan2(-rotmat[k, j], rotmat[j, j])
    eul1.y = math.atan2(-rotmat[i, k], cy)
    eul1.z = 0.0

    eul2 = eul1

# TODO: check for parity  https://github.com/dfelinto/blender/blob/eb6fe5fa94b86a0a20742e06bf1e68b4cbaf6693/source/blender/blenlib/intern/math_rotation.c#L1607

# return best, which is just the one with lowest values in it
if eul1.magnitude > eul2.magnitude:
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
