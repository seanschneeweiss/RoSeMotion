import bvh_reader


def main():
	bvh = bvh_reader.BVH()
	bvh.load_from_file("data/test1Char00.bvh")


if __name__ == '__main__':
	main()