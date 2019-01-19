import bvh_reader
import c3d_convertor

import sys, os


def main():
	if len(sys.argv) < 2:
		print 'error: input not specified'
		usage()
		return

	if len(sys.argv) > 2:
		output_folder = sys.argv[2]
	else:
		output_folder = '.'

	if not os.path.exists(output_folder):
		try:
			os.makedirs(output_folder)
		except OSError:
			print 'error: failed to create output folder', output_folder
			return

	if os.path.isfile(output_folder) or not os.path.isdir(output_folder):
		print 'error: output folder is not valid'
		usage()
		return

	if os.path.isfile(sys.argv[1]) and not os.path.isdir(sys.argv[1]):
		gen(os.path.abspath(sys.argv[1]), os.path.abspath(output_folder))
	elif not os.path.isfile(sys.argv[1]) and os.path.isdir(sys.argv[1]):
		batch(os.path.abspath(sys.argv[1]), os.path.abspath(output_folder))
	else:
		print 'error: input not valid'
		usage()


def gen(input_file, output_folder):
	print 'gen', '"' + input_file + '"'

	bvh = bvh_reader.BVH()
	if not bvh.load_from_file(input_file):
		print 'error: failed to load bvh file', input_file
		return
	
	output_name = os.path.splitext(os.path.basename(input_file))[0]
	output_file = os.path.join(output_folder, output_name + '.c3d')

	conv = c3d_convertor.Convertor()
	conv.convert(bvh, output_file)

	print '"' + output_file + '" generated'


def batch(input_folder, output_folder):
	print 'batch', '"' + input_folder + '"', '===>', output_folder
	for root, dirs, files in os.walk(input_folder):
		for f in files:
			gen(os.path.abspath(os.path.join(root, f)), output_folder)


def usage():
	print 'usage: python b3d.py input_file|input_folder [output_folder]'


if __name__ == '__main__':
	main()