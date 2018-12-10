from b3d import bvh_reader
from b3d import c3d_converter

bvh = bvh_reader.BVH()
if not bvh.load_from_file('../Test_c3d/test_output.bvh'):
    raise Exception('error: can not read bvh')

conv = c3d_converter.Converter()
conv.convert(bvh, 'test_output_old.c3d')
print('c3d generated')