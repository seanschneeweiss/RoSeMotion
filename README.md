# ROSE Motion

Zenodo Code Archive: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4344201.svg)](https://doi.org/10.5281/zenodo.4344201) MDPI Sensors Article: [![DOI](https://zenodo.org/badge/DOI/10.3390/s21041199.svg)](https://doi.org/10.3390/s21041199)

LeapMotion recording, export to BVH and Anybody
![ROSE Motion](https://snag.gy/T6kpqO.jpg)

## Structure / Actions

* **Record**
Plug in the Leap Motion Controller and make a recording of the right hand
    * **Settings**
        * Setting "Frames per second" defines the minimum time delta between to recorded frames
        * Checking "Animate" will open the bvh animation after recording, a slider can be used to iterate through the frames
        * Setting the basis
    * **BVH Export**
        * Setting "Write BVH-File" will export the recorded motion to a BVH file defined in the next setting
        * Choose the filepath and name in "BVH File"
        * Setting "BVH Channels" will export either the channels XRotation, YRotation, ZRotation or also XPosition, YPosition, ZPosition
    * **Interpolation Vector**
        * Setting "Write interpolation files for AnyBody" will export the files
            * Elbow.any (pronation angle)
            * Finger[1-5].any (angles for all finger joints)
            * FingerLength.any (scaling of the finger lengths based on Leap Motion recording)
            * TimeSeries.any (equally spaced time points between 0 and 1)
            * Wrist.any (abduction and flexion angles for wrist)
        * Choose the template directory, the AnyBody interpolation files are written based on those files
        * Choose the output directory, here the above mentioned files will be saved to
* **AnyBody** ([repository](https://github.com/seanschneeweiss/RoSeMotion-AnyBody))
    * **Source files**
        * Choose "exisiting vector files" if interpolation files are already in the project folder <AnyBodyFolder>/Model/InterpolVec
        * Choose ".bvh file" to convert it to the interpolation files based on the templates in config/anybody_templates/ and copy into the AnyBody project folder <AnyBodyFolder>/Model/InterpolVec
        * Choose "Source (.any)" to copy all .any files into the AnyBody project folder <AnyBodyFolder>/Model/InterpolVec
        * Setting "HAND.Main.any" defines the main model file of the AnyBody project, which should be loaded for the analysis
        * Setting "Start Frame" will define the first frame to start with (cut off the frames before that). Leaving this option empty will set the first frame to 1
        * Setting "End Frame" will define the last frame to end with (cut off the frames after that). Leaving this option empty will set the last frame to end
    * **Operations**
        * Select the operations which should be executed in AnyBody
        * Setting "Time steps" will rewrite alls lines which match ``nStep = xx;`` in the main model file. (e.g. ``nStep = 50;``)
    * **Results**
        * Selecting "plot after the analysis" will open an interactive plot for the results from the AnyBody analysis (joint angles)
        * Setting ".anydata.h5 file" will save the results from the AnyBody anaylsis to the specified file
        * Selecting "Open AnyBody" will open the AnyBody GUI after the analysis and will load the .anydata.h5 to make a replay available
* **Converter**
    * Convert a given bvh file to the interpolation files used for AnyBody based on the templates in config/anybody_templates
* **Animation**
    * Open a bvh file to animate it, a slider can be used to iterate through the frames

### Basis setting

* AnyBody initial basis -> select for correct movement within AnyBody
* Leap Motion first frame basis -> select for exporting to BVH and use in other applications

## Setup

**Windows**

* Install python (3.8.8) i.e. from

  https://www.python.org/downloads/
* Add python to system path during setup or follow the following instructions:

  https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation

* Install dependencies, by running the following in a command prompt:
```
pip install -r requirements.txt
```
You might have to use `pip3` instead, depending on your setup.

* Start RoSeMotion
```
python app/main.py
```

---
Following python packages and versions were tested:
 * _Gooey_ (1.0.8)
 * _AnyPyTools_ (1.4.6)
 * _Matplotlib_ (3.3.3) (only for AnyBody results)
 * _Numpy_ (1.19.5)
 * _Pandas_ (1.1.5)
 * _pywin32_ (300) (only for window size automation)
 * _pywinauto_ (0.6.6) (only for window size automation)
 * _Scikit-learn_ (0.23.2) (only for BVH animation)
 * _wxPython_ (4.1.0)

## Credits
* https://github.com/chriskiehl/Gooey
* https://github.com/YPZhou/b3d/
* https://github.com/AnyBody-Research-Group/AnyPyTools
* https://github.com/leapmotion/LeapCxx
* https://github.com/omimo/PyMO
