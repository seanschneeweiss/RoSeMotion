# ROSE Motion
LeapMotion recording, export to BVH and Anybody

## Structure / Actions
* **Record**
Plug in the Leap Motion Controller and make a recording of the right hand
    * **Settings**
        * Setting "Frames per second" defines the minimum time delta between to recorded frames
        * Checking "Animate" will open the bvh animation after recording, a slider can be used to iterate through the frames
        * Setting the basis -> look at chapter ...
    * BVH Export
        * Setting "Write BVH-File" will export the recorded motion to a BVH file defined in the next setting
        * Choose the filepath and name in "BVH File"
        * Setting "BVH Channels" will export either the channels XRotation, YRotation, ZRotation or also XPosition, YPosition, ZPosition
    * Interpolation Vector
        * Setting "Write interpolation files for AnyBody" will export the files
            * Elbow.any (pronation angle)
            * Finger[1-5].any (angles for all finger joints)
            * FingerLength.any (scaling of the finger lengths based on Leap Motion recording)
            * TimeSeries.any (equally spaced time points between 0 and 1)
            * Wrist.any (abduction and flexion angles for wrist)
* AnyBody
    * Source files
    * Operations
    * Results
* Converter
* Animation

## 

## Setup
**Windows**

* Install python (3.7.2) i.e. from

  https://www.python.org/downloads/
* Add python to system path during setup or follow the following instructions:

  https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation

* Run in a command prompt:
```
  python -m pip install --upgrade pip
  pip install -U matplotlib
  pip install -U numpy
  pip install -U pandas
  pip install -U scikit-learn
  pip install -U pywin32
  pip install -U pywinauto
  pip install -U wxpython
  pip install -U scipy
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
 * _pywin32_ (224) (only for window size automation)
 * _pywinauto_ (0.6.6) (only for window size automation)
 * _Scipy_ (1.2.1) (only for AnyPyTools)
 * _Scikit-learn_ (0.20.3) (only for BVH animation)
 * _wxPython_ (4.0.4)

## Credits
https://github.com/chriskiehl/Gooey
https://github.com/YPZhou/b3d/
https://github.com/AnyBody-Research-Group/AnyPyTools
https://github.com/leapmotion/LeapCxx
https://github.com/omimo/PyMO