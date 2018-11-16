# import c3d
#
# reader = c3d.Reader(open('SeanR06_Take_001.c3d', 'rb'))
# for i, points, analog in reader.read_frames():
#     print('frame {}: point {}, analog {}'.format(
#         i, points.shape, analog.shape))

import c3d
import io
import numpy as np


r = c3d.Reader(open('TESTDPI.c3d', 'rb'))
w = c3d.Writer(
    point_rate=r.point_rate,
    analog_rate=r.analog_rate,
    point_scale=r.point_scale,
    gen_scale=r.get_float('ANALOG:GEN_SCALE'),
)
for f, p, a in r.read_frames(1):
    print("f: {}, p: {}, a: {}".format(f, p, a))
# w.add_frames((p, a) for _, p, a in r.read_frames())
# with open('random-points.c3d', 'wb') as h:
#     w.write(h)
# h = io.BytesIO()
# w.write(h)
