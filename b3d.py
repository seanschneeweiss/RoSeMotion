import bvh_reader
import c3d_convertor


def main():
	bvh = bvh_reader.BVH()
	bvh.load_from_file("data/test1Char00.bvh")
	
	conv = c3d_convertor.Convertor()
	conv.convert(bvh)


if __name__ == '__main__':
	main()