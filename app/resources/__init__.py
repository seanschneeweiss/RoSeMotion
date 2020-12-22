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
arch_dir = 'LeapSDK/v41_python38/lib/x64' if sys.maxsize > 2 ** 32 \
    else 'LeapSDK/v41_python38/lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
# pymo
arch_dir = 'pymo/pymo'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
arch_dir = 'pymo'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
