# Leap SDK

* Orion 4.0.0 + Python 3.7
* Orion 3.2.1 + Python 2.7

_Information from https://developer.leapmotion.com/documentation/_ \
Leap Motion technology tracks the movement of your hands and fingers.\
SDK features a C-style API called LeapC for accessing tracking data from the Leap Motion service
Older bindings for C++, C#, Java, JavaScript, Python, and Objective-C remain available, but are no longer actively 
supported.

## v4_python37 (Orion 4.0.0 + Python 3.7)
Using the newest version 4.0.0.52173 (as of 2019-02-11) from https://developer.leapmotion.com/releases

This is using the legacy API with the newest SDK. But the python wrapper has to be build by our selfs with CMAKE
and SWIG.\
We build this for x64 Windows system with Visual Studio 15 2017.
* CMAKE 3.10.3 (didn't work with 3.13)
* swig 3.0.12
* Python 3.7.2

## v3_python27 (Orion 3.2.1 + Python 2.7)
Python Wrapper is directly available by downloading.