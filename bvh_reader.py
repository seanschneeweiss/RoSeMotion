class BVH(object):
	

	def __init__(self):
		super(BVH, self).__init__()
		self.root = None


	def load_from_file(self, bvh_file_path):
		bvh_file = open(bvh_file_path, 'r')
		bvh_str = bvh_file.read()

		# bvh parser status:
		# 0 : no status
		# 1 : hierarchy
		# 2 : motion data
		status = 0
		buffer = ''
		i = 0
		while i < len(bvh_str):
			if status == 0:
				tokens = read_string(bvh_str[i:], 1)
				if tokens[0] == 'HIERARCHY':
					status = 1
					i += len(tokens[0])
				elif tokens[0] == 'MOTION':
					status = 2
					i += len(tokens[0])
			elif status == 1:
				tokens = read_string(bvh_str[i:], 1)
				if tokens[0] == 'ROOT':
					pass
				elif tokens[0] == 'JOINT'
		bvh_file.close()


	def read_int(self, source, count):
		buffer = ''
		int_ret = []
		for c in source:
			if c == ' ' or c == '\t' or c == '{' or c == '}':
				try:
					int_ret.append(int(buffer))
					buffer = ''
				except ValueError:
					return None
			else:
				buffer += c
			if len(int_ret) == count:
				return int_ret
		return None


	def read_float(self, source, count):
		buffer = ''
		float_ret = []
		for c in source:
			if c == ' ' or c == '\t' or c == '{' or c == '}':
				try:
					float_ret.append(float(buffer))
					buffer = ''
				except ValueError:
					return None
			else:
				buffer += c
			if len(float_ret) == count:
				return float_ret
		return None


	def read_string(self, source, count):
		buffer = ''
		str_ret = []
		for c in source:
			if c == ' ' or c == '\t' or c == '{' or c == '}':
				str_ret.append(buffer)
				buffer = ''
			else:
				buffer += c
			if len(str_ret) == count:
				return str_ret
		return None


class Node(object):
	

	def __init__(self, node_name, offset):
		super(Node, self).__init__()
		self.node_name = node_name
		self.offset = offset


class Joint(Node):
	

	def __init__(self, node_name, offset, channels, children):
		super(Joint, self).__init__(node_name, offset)
		self.channels = channels
		self.children = children


	def add_child(self, child):
		self.children.append(child)


class EndSite(Node):
	

	def __init__(self, node_name, offset):
		super(EndSite, self).__init__(node_name, offset)