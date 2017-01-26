import bvh_reader


def main():
	bvh = bvh_reader.BVH()
	bvh.load_from_file("data/N30_XYZ_Pos.bvh")


if __name__ == '__main__':
	main()