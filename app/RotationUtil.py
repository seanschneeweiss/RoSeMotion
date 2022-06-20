import numpy as np
import math

from resources.LeapSDK.v53_python39 import Leap


def get_order():
    ##############
    #  i, j, k, n
    #  n = parity of axis permutation (even=False, odd=True)
    #  from https://github.com/dfelinto/blender/blob/master/source/blender/blenlib/intern/math_rotation.c
    ##############

    return [0, 1, 2, False]  # XYZ
    # return [0, 2, 1, True]   # XZY
    # return [1, 0, 2, True]   # YXZ
    # return [1, 2, 0, False]  # YZX
    # return [2, 0, 1, False]  # ZXY
    # return [2, 1, 0, True]   # ZYX


def _rot2eulsimple(rotmat):
    eul = np.zeros(3)
    if -1 < rotmat[1, 1] < 1:
        eul[1] = math.acos(rotmat[1, 1])
    if rotmat[1, 1] >= 1.0:
        eul[1] = 0
    if rotmat[1, 1] <= -1.0:
        eul[1] = np.pi

    if rotmat[0, 0] < 1 and rotmat[1, 1] > -1:
        eul[0] = math.acos(rotmat[0, 0])
    if rotmat[1, 1] >= 1.0:
        eul[0] = 0
    if rotmat[1, 1] <= -1.0:
        eul[0] = np.pi

    eul[2] = 0
    return eul


def _rot2eul(rotmat):
    ##############
    #  i, j, k, n
    #  n = parity of axis permutation (even=False, odd=True)
    #  from https://github.com/dfelinto/blender/blob/master/source/blender/blenlib/intern/math_rotation.c
    ##############

    # order = [0, 1, 2, False] # XYZ
    # order = [0, 2, 1, True] # XZY
    # order = [1, 0, 2, True] # YXZ
    # order = [1, 2, 0, False] # YZX
    # order = [2, 0, 1, False]  # ZXY
    # order = [2, 1, 0, True] # ZYX

    order = get_order()

    i = int(order[2])
    j = int(order[1])
    k = int(order[0])
    parity = order[3]

    eul1 = np.zeros(3)
    eul2 = np.zeros(3)

    cy = np.hypot(rotmat[i, i], rotmat[i, j])

    if cy > Leap.EPSILON:
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
    if not parity:
        eul1 = np.negative(eul1)
        eul2 = np.negative(eul2)

    # return best, which is just the one with lowest values in it
    if np.sum(np.absolute(eul1)) > np.sum(np.absolute(eul2)):
        return eul2
    return eul1


def quat2mat(quat):
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
    mat[1, 0] = qdc + qab
    mat[2, 0] = -qdb + qac

    mat[0, 1] = -qdc + qab
    mat[1, 1] = 1.0 - qaa - qcc
    mat[2, 1] = qda + qbc

    mat[0, 2] = qdb + qac
    mat[1, 2] = -qda + qbc
    mat[2, 2] = 1.0 - qaa - qbb

    return mat


def vec2quat(v1, v2):
    a = np.divide(v1, np.linalg.norm(v1))
    b = np.divide(v2, np.linalg.norm(v2))

    xUnitVec = np.array([1, 0, 0])
    yUnitVec = np.array([0, 1, 0])

    dot_p = np.dot(a, b)

    if dot_p < -1 + Leap.EPSILON:
        tmpvec3 = np.cross(xUnitVec, a)
        if np.linalg.norm(tmpvec3) < Leap.EPSILON:
            tmpvec3 = np.cross(yUnitVec, a)
        tmpvec3 = np.divide(tmpvec3, np.linalg.norm(tmpvec3))

        t = np.pi * 0.5
        s = np.sin(t)
        q = np.zeros(4)
        q[0] = np.cos(t)
        q[1] = tmpvec3[0]*s
        q[2] = tmpvec3[1]*s
        q[3] = tmpvec3[2]*s
        return q

    if dot_p > 1 - Leap.EPSILON:
        return np.array([0, 0, 0, 1])

    tmpvec3 = np.cross(a, b)
    q = np.append(1 + dot_p, tmpvec3)
    return np.divide(q, np.linalg.norm(q))


def rot2quat(rotmat):
    q = np.zeros(4)

    tr = 0.25 * (1 + np.trace(rotmat))
    if tr > Leap.EPSILON:
        s = np.sqrt(tr)
        q[0] = s
        s = 1.0 / (4.0 * s)
        q[1] = (rotmat[1, 2] - rotmat[2, 1]) * s
        q[2] = (rotmat[2, 0] - rotmat[0, 2]) * s
        q[3] = (rotmat[0, 1] - rotmat[1, 0]) * s
        return normalize_quat(q)

    if rotmat[0, 0] > rotmat[1, 1] and rotmat[0, 0] > rotmat[2, 2]:
        s = 2.0 * np.sqrt(1.0 + rotmat[0, 0] - rotmat[1, 1] - rotmat[2, 2])
        q[1] = 0.25 * s
        s = 1.0 / s
        q[0] = (rotmat[1, 2] - rotmat[2, 1]) * s
        q[2] = (rotmat[1, 0] - rotmat[0, 1]) * s
        q[3] = (rotmat[2, 0] - rotmat[0, 2]) * s
        return normalize_quat(q)

    if rotmat[1, 1] > rotmat[2, 2]:
        s = 2.0 * np.sqrt(1.0 + rotmat[1, 1] - rotmat[0, 0] - rotmat[2, 2])
        q[2] = 0.25 * s
        s = 1.0 / s
        q[0] = (rotmat[2, 0] - rotmat[0, 2]) * s
        q[1] = (rotmat[1, 0] - rotmat[0, 1]) * s
        q[3] = (rotmat[2, 1] - rotmat[1, 2]) * s
        return normalize_quat(q)

    s = 2.0 * np.sqrt(1.0 + rotmat[2, 2] - rotmat[0, 0] - rotmat[1, 1])
    q[3] = 0.25 * s
    s = 1.0 / s
    q[0] = (rotmat[0, 1] - rotmat[1, 0]) * s
    q[1] = (rotmat[2, 0] - rotmat[0, 2]) * s
    q[2] = (rotmat[2, 1] - rotmat[1, 2]) * s
    return normalize_quat(q)


def normalize_quat(q):
    scal = np.sqrt(np.dot(q, q))
    if scal != 0.0:
        return np.kron(q, 1.0 / scal)

    q[1] = 1.0
    q[0] = q[2] = q[3] = 0.0
    return q


def conjugate_quat(q):
    q[1] = -q[1]
    q[2] = -q[2]
    q[3] = -q[4]
    return q


def multiply_quat(q1, q2):
    q = np.zeros(4)
    t0 = q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3]
    t1 = q1[0] * q2[1] + q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2]
    t2 = q1[0] * q2[2] + q1[2] * q2[0] + q1[3] * q2[1] - q1[1] * q2[3]
    q[3] = q1[0] * q2[3] + q1[3] * q2[0] + q1[1] * q2[2] - q1[2] * q2[1]
    q[0] = t0
    q[1] = t1
    q[2] = t2
    return q


def vec2eul(v1, v2):
    quaternions = vec2quat(v1, v2)
    rotmat = quat2mat(quaternions)
    euler = _rot2eul(rotmat)
    return euler[0], euler[1], euler[2]


def rot2eul(rotmat):
    euler = _rot2eul(rotmat)
    return euler[0], euler[1], euler[2]


def quat_diff(q_prev, q_next):
    q_prev = conjugate_quat(q_prev)
    q_prev = np.kron(q_prev, 1.0 / np.dot(q_prev, q_prev))
    return multiply_quat(q_prev, q_next)


def quat_between_rot(rotmat_prev, rotmat_next):
    # TODO: normalize rotation matrix
    return quat_diff(rot2quat(rotmat_prev), rot2quat(rotmat_next))
