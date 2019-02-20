# LeapMotion recording, export to BVH, C3D and Anybody

## Setup
**Windows**

* Install python (3.7.2) i.e. from

  https://www.python.org/downloads/
* Add python to system path during setup or follow the following instructions:

  https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation

* Run in a command prompt:
```
  python -m pip install --upgrade pip
  pip install numpy
  pip install pandas
  pip install wxpython
  pip install scipy
```
Alternative:
```
pip install -r requirements.txt
```

---
Following python packages are required:
 * _h5py_ (2.9.0) (only for AnyPyTools)
 * _Matplotlib_ (3.0.2) (only for AnyPyTools)
 * _Numpy_ (1.16.1)
 * _Pandas_ (0.24.1)
 * _Scipy_ (1.2.1) (only for AnyPyTools)
 * _wxPython_ (4.0.4)

## Credits
https://github.com/chriskiehl/Gooey
https://github.com/YPZhou/b3d/
https://github.com/AnyBody-Research-Group/AnyPyTools
https://github.com/leapmotion/LeapCxx
https://github.com/omimo/PyMO