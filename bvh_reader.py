import math3d


class BVH(object):
	

	def __init__(self):
		super(BVH, self).__init__()
		self.root = []
		self.channel_values = []
		self.channel_dict = {}

		self.display_frame = 2000


	def load_from_file(self, bvh_file_path):
		bvh_file = open(bvh_file_path, 'r')
		bvh_str = bvh_file.read()

		self.tokens = self.tokenize(bvh_str)
		self.token_index = 0

		self.parse_hierarchy()
		# for root in self.root:
		# 	print root
		self.parse_motion()
		# print self.channel_dict
		# print len(self.channel_values[self.channel_dict['RightArm']['Xrotation']])

		self.calculate_joint_position()

		bvh_file.close()


	def calculate_joint_position(self):
		for i in range(self.frame_count):
			transformation_stack = []
			for root in self.root:			
				# root position
				bone_length = root.offset
				if 'Xposition' in self.channel_dict[root.name]:
					pos = [self.channel_values[self.channel_dict[root.name]['Xposition']][i], self.channel_values[self.channel_dict[root.name]['Yposition']][i], self.channel_values[self.channel_dict[root.name]['Zposition']][i]]
				if 'Xrotation' in self.channel_dict[root.name]:
					rot = [self.channel_values[self.channel_dict[root.name]['Xrotation']][i], self.channel_values[self.channel_dict[root.name]['Yrotation']][i], self.channel_values[self.channel_dict[root.name]['Zrotation']][i]]
				# print 'frame', i, 'offset', bone_length, 'position', pos
				# calculate transformation
				q_x = math3d.quaternion((1, 0, 0), rot[0])
				q_y = math3d.quaternion((0, 1, 0), rot[1])
				q_z = math3d.quaternion((0, 0, 1), rot[2])
				q_rot = math3d.multiply_quat(q_x, math3d.multiply_quat(q_y, q_z))
				mat_rot = math3d.matrix_from_quat(q_rot)
				mat_trans = math3d.matrix_from_trans((bone_length[0] + pos[0], bone_length[1] + pos[1], bone_length[2] + pos[2]))
				trans_matrix = math3d.multiply_matrix(mat_trans, mat_rot)
				pos_calc = [trans_matrix[3], trans_matrix[7], trans_matrix[11]]
				if i == self.display_frame:
					print 'frame', i, 'joint', root.name, 'channel pos', pos, 'calc pos', pos_calc

				# push transformation onto stack
				transformation_stack.append(trans_matrix)

				# iterate through children joints
				for joint in root.children:
					self.transform_joint(joint, i, transformation_stack, pos_calc)

				# pop transformation off stack
				transformation_stack.pop()


	def transform_joint(self, joint, frame, transformation_stack, parent_pos):
		if isinstance(joint, EndSite):
			return
		elif isinstance(joint, Joint):
			bone_length = joint.offset
			if 'Xposition' in self.channel_dict[joint.name]:
				pos = [self.channel_values[self.channel_dict[joint.name]['Xposition']][frame], self.channel_values[self.channel_dict[joint.name]['Yposition']][frame], self.channel_values[self.channel_dict[joint.name]['Zposition']][frame]]
			if 'Xrotation' in self.channel_dict[joint.name]:
				rot = [self.channel_values[self.channel_dict[joint.name]['Xrotation']][frame], self.channel_values[self.channel_dict[joint.name]['Yrotation']][frame], self.channel_values[self.channel_dict[joint.name]['Zrotation']][frame]]
			q_x = math3d.quaternion((1, 0, 0), rot[0])
			q_y = math3d.quaternion((0, 1, 0), rot[1])
			q_z = math3d.quaternion((0, 0, 1), rot[2])
			q_rot = math3d.multiply_quat(q_x, math3d.multiply_quat(q_y, q_z))
			mat_rot = math3d.matrix_from_quat(q_rot)
			mat_trans = math3d.matrix_from_trans((bone_length[0], bone_length[1], bone_length[2]))
			trans_matrix = math3d.multiply_matrix(mat_trans, mat_rot)
			transformation_stack.append(trans_matrix)
			# apply transformations
			mat = math3d.identity_matrix()
			for transformation in reversed(transformation_stack):
				mat = math3d.multiply_matrix(transformation, mat)
			pos_calc = [mat[3], mat[7], mat[11]]
			if frame == self.display_frame:
				print 'frame', frame, 'joint', joint.name, 'channel pos', pos, 'calc pos', pos_calc, 'calc pos 2', pos_calc2
			# iterate through children joints
			for child in joint.children:
				self.transform_joint(child, frame, transformation_stack, pos_calc)
			transformation_stack.pop()
		else:
			return


	def tokenize(self, source):
		import re
		# split source string with either white spaces, line separators, or tabulations
		tokens = re.split(' |\n|\t', source)
		# filter the token list, remove all empty strings
		return filter(None, tokens)


	def parse_hierarchy(self):
		if self.tokens[self.token_index] != 'HIERARCHY':
			# print 'keyword HIERARCHY not found'
			return
		self.token_index += 1
		# parse all roots to support multiple hierarchy
		while self.tokens[self.token_index] == 'ROOT':
			joint = self.read_joint()
			if joint:
				self.root.append(joint)


	def parse_motion(self):
		if self.tokens[self.token_index] != 'MOTION':
			return
		self.token_index += 1
		if self.tokens[self.token_index] != 'Frames:':
			# print 'keyword Frames: not found'
			return
		self.token_index += 1
		try:
			self.frame_count = int(self.tokens[self.token_index])
		except ValueError:
			# print 'frame count invalid'
			return
		self.token_index += 1
		# Frame Time: is treated as two tokens
		if self.tokens[self.token_index] != 'Frame' or self.tokens[self.token_index + 1] != 'Time:':
			# print 'keyword Frame Time: not found'
			return
		self.token_index += 2
		try:
			self.frame_time = float(self.tokens[self.token_index])
		except ValueError:
			# print 'frame time invalid'
			return
		self.token_index += 1
		for i in range(self.frame_count):
			for j in range(len(self.channel_values)):
				try:
					self.channel_values[j].append(float(self.tokens[self.token_index]))
					self.token_index += 1
				except ValueError:
					# print 'frame data invalid', self.tokens[self.token_index]
					return
		

	# before reading a joint, the token index will be pointing to the keyword ROOT,
	# JOINT, or End
	#
	# after reading a joint, the token index will point to the token right after
	# the closing brace of the joint which has been read
	#
	# in case of invalid joint format, function will ignore this joint and return None
	# and the token index will point to the token that breaks joint format
	def read_joint(self):
		# print 'current token', self.tokens[self.token_index]
		# 0 for ROOT or JOINT, 1 for End Site
		joint_type = 0
		if self.tokens[self.token_index] == 'End':
			joint_type = 1
		self.token_index += 1
		# print 'current token', self.tokens[self.token_index]
		if joint_type == 0:
			joint_name = self.tokens[self.token_index]
		self.token_index += 1
		# print 'current token', self.tokens[self.token_index]
		if self.tokens[self.token_index] != '{':
			# print 'open brace not found'
			return None
		self.token_index += 1
		# print 'current token', self.tokens[self.token_index]
		if self.tokens[self.token_index] != 'OFFSET':
			# print 'keyword OFFSET not found'
			return None
		self.token_index += 1
		# print 'current token', self.tokens[self.token_index]		
		try:
			joint_offset = [float(self.tokens[self.token_index]), float(self.tokens[self.token_index + 1]), float(self.tokens[self.token_index + 2])]
		except ValueError:
			# print 'offset value error'
			return None
		self.token_index += 3
		if joint_type == 0:
			# print 'current token', self.tokens[self.token_index]
			if self.tokens[self.token_index] != 'CHANNELS':
				# print 'keyword CHANNELS not found'
				return None
			self.token_index += 1
			# print 'current token', self.tokens[self.token_index]
			try:
				joint_channel_count = int(self.tokens[self.token_index])
			except ValueError:
				# print 'channel count value error'
				return None
			self.token_index += 1
			# print 'current token', self.tokens[self.token_index]
			joint_channels = []
			self.channel_dict[joint_name] = {}
			for i in range(joint_channel_count):
				joint_channels.append(self.tokens[self.token_index])
				# channel data is stored in two data structures, a two-dimensional table which stores the channel values of each frame
				# and a dictionary which stores the links between the joints and the indices in the value table
				# in order to reference a channel value of a specifique joint at a specifique frame, one can do:
				#
				# self.channel_values[self.channel_dict[joint_name][channel_name]][frame]
				#
				# ==== NEED TO FIX LATER ====
				#
				# channel data structure is created when the channel part of a joint is parsed, it could happen that there is invalid
				# format in the rest of the joint definition
				# since a joint with invalid definition will be ignored, the created channel data structure also becomes invalid
				# to fix this later, we could perform a rollback when joint reading is failed
				self.channel_dict[joint_name][self.tokens[self.token_index]] = len(self.channel_values)
				self.channel_values.append([])
				self.token_index += 1
				# print 'current token', self.tokens[self.token_index]
			joint_children = []
			while self.tokens[self.token_index] == 'JOINT' or self.tokens[self.token_index] == 'End':
				child_joint = self.read_joint()
				# print 'current token', self.tokens[self.token_index]
				if child_joint:
					joint_children.append(child_joint)
		if self.tokens[self.token_index] != '}':
			# print 'close brace not found : ', self.tokens[self.token_index]
			return None
		if joint_type == 0:
			joint = Joint(joint_name, joint_offset, joint_channels, joint_children)
		else:
			joint = EndSite(joint_offset)
		self.token_index += 1
		return joint


class Node(object):
	

	def __init__(self, offset):
		super(Node, self).__init__()
		self.offset = offset


	def __str__(self):
		return ''


class Joint(Node):
	

	def __init__(self, node_name, offset, channels, children):
		super(Joint, self).__init__(offset)
		self.name = node_name
		self.channels = channels
		self.children = children


	def __str__(self):
		res = self.name
		res += ' ['
		for joint in self.children:
			res += str(joint)
		res += '] '
		return res


class EndSite(Node):
	

	def __init__(self, offset):
		super(EndSite, self).__init__(offset)


	def __str__(self):
		return 'EndSite : ' + str(self.offset)