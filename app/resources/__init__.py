import os
import sys
import inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# AnyPyTools
arch_dir = 'AnyPyTools'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
# Gooey
arch_dir = 'Gooey'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
# LeapSDK
arch_dir = 'LeapSDK/v53_python39/lib/x64'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
# pymo
arch_dir = 'pymo/pymo'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
arch_dir = 'pymo'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
