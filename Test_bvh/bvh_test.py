import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
import pickle

import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from pymo.parsers import BVHParser
from pymo.preprocessing import *
from pymo.viz_tools import *
from pymo.writers import BVHWriter
from pymo.Leap2BVH import Leap2BVH


#parser = BVHParser()

#parsed_data = parser.parse('brekel01.bvh')
# print(parsed_data:)
#print_skel(parsed_data)
#parsed_data.values.head(10)

leap = Leap2BVH()
leapdata = leap.parse()

writer = BVHWriter()
f = open("test_output.bvh", 'w')
writer.write(leapdata, f)
