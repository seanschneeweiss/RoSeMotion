import math


# Converts angle from degree to radian	
def to_radian(angle):
	return angle / 180.0 * math.pi


# Constructs a quaternion from a rotation of degree 'angle' around vector 'axis'
def quaternion(axis, angle):
	angle *= 0.5
	sinAngle = math.sin(to_radian(angle))
	return normalize((axis[0] * sinAngle, axis[1] * sinAngle, axis[2] * sinAngle, math.cos(to_radian(angle))))


# Normalizes quaternion 'q'
def normalize(q):
	length = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])
	return (q[0] / length, q[1] / length, q[2] / length, q[3] / length)


# Multiplies 2 quaternions : 'q1' * 'q2'	
def multiply_quat(q1, q2):
	return (q1[3] * q2[0] + q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1],
			q1[3] * q2[1] + q1[1] * q2[3] + q1[2] * q2[0] - q1[0] * q2[2],
			q1[3] * q2[2] + q1[2] * q2[3] + q1[0] * q2[1] - q1[1] * q2[0],
			q1[3] * q2[3] - q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2])


# Converts quaternion 'q' to a rotation matrix
def matrix_from_quat(q):
	x2 = q[0] * q[0]
	y2 = q[1] * q[1]
	z2 = q[2] * q[2]
	xy = q[0] * q[1]
	xz = q[0] * q[2]
	yz = q[1] * q[2]
	wx = q[3] * q[0]
	wy = q[3] * q[1]
	wz = q[3] * q[2]
	return (1.0 - 2.0 * (y2 + z2), 2.0 * (xy - wz), 2.0 * (xz + wy), 0.0,
			2.0 * (xy + wz), 1.0 - 2.0 * (x2 + z2), 2.0 * (yz - wx), 0.0,
			2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (x2 + y2), 0.0,
			0.0, 0.0, 0.0, 1.0)


# Constructs a translation matrix
def matrixFromTrans(trans):
	return (1, 0, 0, trans[0],
			0, 1, 0, trans[1],
			0, 0, 1, trans[2],
			0, 0, 0, 1)


# Multiplies 2 Mat4 : 'm1' * 'm2'			
def multiplyMatrix(m1, m2):
	res = []
	for i in range(0, 4):
		for j in range(0, 4):
			res.append(m1[i * 4] * m2[j] + m1[i * 4 + 1] * m2[j + 4] + m1[i * 4 + 2] * m2[j + 8] + m1[i * 4 + 3] * m2[j + 12])
	return res


# Multiplies matrix 'm' by vector 'v'
def multiplyMatByVec(m, v):
	w = 1.0
	if len(v) == 4:
		w = v[3]
	return (m[0] * v[0] + m[1] * v[1] + m[2] * v[2] + m[3] * w,
			m[4] * v[0] + m[5] * v[1] + m[6] * v[2] + m[7] * w,
			m[8] * v[0] + m[9] * v[1] + m[10] * v[2] + m[11] * w,
			m[12] * v[0] + m[13] * v[1] + m[14] * v[2] + m[15] * w)


# Transposes matrix 'm'
def transpose(m):
	return (m[0], m[4], m[8], m[12],
			m[1], m[5], m[9], m[13],
			m[2], m[6], m[10], m[14],
			m[3], m[7], m[11], m[15])


# Calculates inverse of matrix m
# Reimplement of gluInvertMatrix
def invertMatrix(m):
	inv = []
	inv.append(m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] + m[9] * m[7] * m[14] + m[13] * m[6] * m[11] - m[13] * m[7] * m[10])
	inv.append(-m[1] * m[10] * m[15] + m[1] * m[11] * m[14] + m[9] * m[2] * m[15] - m[9] * m[3] * m[14] - m[13] * m[2] * m[11] + m[13] * m[3] * m[10])
	inv.append(m[1] * m[6] * m[15] - m[1] * m[7] * m[14] - m[5] * m[2] * m[15] + m[5] * m[3] * m[14] + m[13] * m[2] * m[7] - m[13] * m[3] * m[6])
	inv.append(-m[1] * m[6] * m[11] + m[1] * m[7] * m[10] + m[5] * m[2] * m[11] - m[5] * m[3] * m[10] - m[9] * m[2] * m[7] + m[9] * m[3] * m[6])
	inv.append(-m[4] * m[10] * m[15] + m[4] * m[11] * m[14] + m[8] * m[6] * m[15] - m[8] * m[7] * m[14] - m[12] * m[6] * m[11] + m[12] * m[7] * m[10])
	inv.append(m[0] * m[10] * m[15] - m[0] * m[11] * m[14] - m[8] * m[2] * m[15] + m[8] * m[3] * m[14] + m[12] * m[2] * m[11] - m[12] * m[3] * m[10])
	inv.append(-m[0] * m[6] * m[15] + m[0] * m[7] * m[14] + m[4] * m[2] * m[15] - m[4] * m[3] * m[14] - m[12] * m[2] * m[7] + m[12] * m[3] * m[6])
	inv.append(m[0] * m[6] * m[11] - m[0] * m[7] * m[10] - m[4] * m[2] * m[11] + m[4] * m[3] * m[10] + m[8] * m[2] * m[7] - m[8] * m[3] * m[6])
	inv.append(m[4] * m[9] * m[15] - m[4] * m[11] * m[13] - m[8] * m[5] * m[15] + m[8] * m[7] * m[13] + m[12] * m[5] * m[11] - m[12] * m[7] * m[9])
	inv.append(-m[0] * m[9] * m[15] + m[0] * m[11] * m[13] + m[8] * m[1] * m[15] - m[8] * m[3] * m[13] - m[12] * m[1] * m[11] + m[12] * m[3] * m[9])
	inv.append(m[0] * m[5] * m[15] - m[0] * m[7] * m[13] - m[4] * m[1] * m[15] + m[4] * m[3] * m[13] + m[12] * m[1] * m[7] - m[12] * m[3] * m[5])
	inv.append(-m[0] * m[5] * m[11] + m[0] * m[7] * m[9] + m[4] * m[1] * m[11] - m[4] * m[3] * m[9] - m[8] * m[1] * m[7] + m[8] * m[3] * m[5])
	inv.append(-m[4] * m[9] * m[14] + m[4] * m[10] * m[13] + m[8] * m[5] * m[14] - m[8] * m[6] * m[13] - m[12] * m[5] * m[10] + m[12] * m[6] * m[9])
	inv.append(m[0] * m[9] * m[14] - m[0] * m[10] * m[13] - m[8] * m[1] * m[14] + m[8] * m[2] * m[13] + m[12] * m[1] * m[10] - m[12] * m[2] * m[9])
	inv.append(-m[0] * m[5] * m[14] + m[0] * m[6] * m[13] + m[4] * m[1] * m[14] - m[4] * m[2] * m[13] - m[12] * m[1] * m[6] + m[12] * m[2] * m[5])
	inv.append(m[0] * m[5] * m[10] - m[0] * m[6] * m[9] - m[4] * m[1] * m[10] + m[4] * m[2] * m[9] + m[8] * m[1] * m[6] - m[8] * m[2] * m[5])
	
	det = m[0] * inv[0] + m[1] * inv[4] + m[2] * inv[8] + m[3] * inv[12]
	if det == 0:
		return None
	
	det = 1.0 / det
	mOut = []
	for i in range(16):
		mOut.append(inv[i] * det)
	return mOut


# Calculates length^2 of vector 'v'	
def length2(v):
	return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]

	
# Calculates vector dot product : 'v1' * 'v2'	
def dot(v1, v2):
	return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

	
# Calculates vector cross product : 'v1' x 'v2'
def cross(v1, v2):
	return (v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0])

	
# Normalizes vector 'v'
def normalizeVec(v):
	l2 = length2(v)
	if l2 == 0:
		return (0, 0, 0)
	l = math.sqrt(l2)
	return (v[0] / l, v[1] / l, v[2] / l)