import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
import pickle
from string import Template

import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from pymo.parsers import BVHParser
from pymo.preprocessing import *
from pymo.viz_tools import *
from pymo.writers import BVHWriter
from AnyBodyExport.AnyWriter import AnyWriter
from pymo.Leap2BVH_pos import Leap2BVH


parser = BVHParser()

parsed_data = parser.parse('test_output.bvh')
# print(parsed_data:)
#print_skel(parsed_data)
#parsed_data.values.head(10)
print("Test")


# leap = Leap2BVH()
# leapdata = leap.parse()

# writer = BVHWriter()
# f = open("test_output.bvh", 'w')
# writer.write(leapdata, f)
writer = AnyWriter()
writer.write(parsed_data)


# #open the file
# filein = open( 'Finger2.any' )
# #read it
# src = Template( filein.read() )
# test = result