class BVH(object):
	

	def __init__(self):
		super(BVH, self).__init__()
		self.root = []
		self.channel_values = []
		self.channel_dict = {}
		self.position_values = []
		self.position_dict = {}

		self.display_frame = 2000


	def load_from_file(self, bvh_file_path):
		bvh_file = open(bvh_file_path, 'r')
		bvh_str = bvh_file.read()

		self.tokens = self.tokenize(bvh_str)
		if len(self.tokens) == 0:
			return False
		self.token_index = 0

		if not self.parse_hierarchy():
			return False
		if not self.parse_motion():
			return False

		bvh_file.close()
		return True


	def tokenize(self, source):
		import re, os
		# split source string with either white spaces, line separators, or tabulations
		if (os.name == "posix"):
			tokens = re.split(' |\n|\r\n|\t', source) #linux
		else:
			tokens = re.split(' |\n|\t', source) # windows
		# filter the token list, remove all empty strings
		return filter(None, tokens)


	def parse_hierarchy(self):
		if self.tokens[self.token_index] != 'HIERARCHY':
			print('keyword HIERARCHY not found')
			return False
		self.token_index += 1
		self.joint_count = 0
		# parse all roots to support multiple hierarchy
		while self.tokens[self.token_index] == 'ROOT':
			joint = self.read_joint()
			if joint:
				self.root.append(joint)
		return True


	def parse_motion(self):
		if self.tokens[self.token_index] != 'MOTION':
			return False
		self.token_index += 1
		if self.tokens[self.token_index] != 'Frames:':
			print('keyword Frames: not found')
			return False
		self.token_index += 1
		try:
			self.frame_count = int(self.tokens[self.token_index])
		except ValueError:
			print('frame count invalid')
			return False
		self.token_index += 1
		# Frame Time: is treated as two tokens
		if self.tokens[self.token_index] != 'Frame' or self.tokens[self.token_index + 1] != 'Time:':
			print('keyword Frame Time: not found')
			return False
		self.token_index += 2
		try:
			self.frame_time = float(self.tokens[self.token_index])
		except ValueError:
			print('frame time invalid')
			return False
		self.token_index += 1
		for i in range(self.frame_count):
			for j in range(len(self.channel_values)):
				try:
					self.channel_values[j].append(float(self.tokens[self.token_index]))
					self.token_index += 1
				except ValueError:
					print('frame data invalid', self.tokens[self.token_index])
					return False
		return True
		

	# before reading a joint, the token index will be pointing to the keyword ROOT,
	# JOINT, or End
	#
	# after reading a joint, the token index will point to the token right after
	# the closing brace of the joint which has been read
	#
	# in case of invalid joint format, function will ignore this joint and return None
	# and the token index will point to the token that breaks joint format
	def read_joint(self):
		# 0 for ROOT or JOINT, 1 for End Site
		joint_type = 0
		if self.tokens[self.token_index] == 'End':
			joint_type = 1
		self.token_index += 1
		if joint_type == 0:
			joint_name = self.tokens[self.token_index]
		self.token_index += 1
		if self.tokens[self.token_index] != '{':
			print('open brace not found')
			return None
		self.token_index += 1
		if self.tokens[self.token_index] != 'OFFSET':
			print('keyword OFFSET not found')
			return None
		self.token_index += 1	
		try:
			joint_offset = [float(self.tokens[self.token_index]), float(self.tokens[self.token_index + 1]), float(self.tokens[self.token_index + 2])]
		except ValueError:
			print('offset value error')
			return None
		self.token_index += 3
		if joint_type == 0:
			if self.tokens[self.token_index] != 'CHANNELS':
				print('keyword CHANNELS not found')
				return None
			self.token_index += 1
			try:
				joint_channel_count = int(self.tokens[self.token_index])
			except ValueError:
				print('channel count value error')
				return None
			self.token_index += 1
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
			joint_children = []
			while self.tokens[self.token_index] == 'JOINT' or self.tokens[self.token_index] == 'End':
				child_joint = self.read_joint()
				if child_joint:
					joint_children.append(child_joint)
		if self.tokens[self.token_index] != '}':
			print('close brace not found : ', self.tokens[self.token_index])
			return None
		if joint_type == 0:
			joint = Joint(joint_name, joint_offset, joint_channels, joint_children)
			self.joint_count += 1
		else:
			joint = EndSite(joint_offset)
		self.token_index += 1		
		return joint


class Node(object):
	

	def __init__(self, offset):
		super(Node, self).__init__()
		self.offset = offset


	# def __str__(self):
	# 	return ''


class Joint(Node):
	

	def __init__(self, node_name, offset, channels, children):
		super(Joint, self).__init__(offset)
		self.name = node_name
		self.channels = channels
		self.children = children


	# def __str__(self):
	# 	res = self.name
	# 	res += ' ['
	# 	for joint in self.children:
	# 		res += str(joint)
	# 	res += '] '
	# 	return res


class EndSite(Node):
	

	def __init__(self, offset):
		super(EndSite, self).__init__(offset)


	# def __str__(self):
	# 	return 'EndSite : ' + str(self.offset)
