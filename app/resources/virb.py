#!/usr/bin/python3
# -*- coding: utf8 -*-
"""Python 3 Module to interact with Garmin Virb cameras over wifi / mass storage
This module also allows you to interact with the Garmin website and
fetch firmware updates when you don't feel like using the Garmin supplied
windows or Mac software.

I can't give you any warranty that any of these things will work,
especially the firmware upgrades could be dangerous.
"""
__author__ = 'Jan KLopper (jan@underdark.nl)'
__version__ = 0.2

import os
import simplejson
import requests

class Virb(object):
  """Class to interact with Garmin Virb cameras over wifi / http"""
  def __init__(self, host=('192.168.0.1', 80)):
    """Sets up the connection with the Virb device

    Accepts an ip and port which should be routable from the device running
    the code.

    host = ('192.168.0.1', 80)
    """
    self.host = host
    self.requestcount = 0

  def status(self):
    """Returns the current camera status"""
    command = 'status'
    data = {'command': command}
    return self._do_post(data=data)

  def features(self):
    """Returns the features"""
    command = 'features'
    data = {'command': command}
    return self._do_post(data=data)[command]

  def get_features(self):
    """Returns the features list as a dictionary"""
    features = self.features()
    results = {'enabled': {},
               'disabled': {}}
    for feature in features:
      name = str(feature['feature'])
      value = feature['value']
      try:
        value = int(value)
      except ValueError:
        value = str(value)
      if feature['enabled']:
        results['enabled'][name] = value
      else:
        results['disabled'][name] = value
    return results

  def set_features(self, feature, value):
    """Update a features"""
    command = 'updateFeature'
    data = {'command': command,
            'feature': feature,
            'value': value}
    return self._do_post(data=data)['features']

  def sensors(self):
    """Returns the current camera sensor readings"""
    command = 'sensors'
    data = {'command': command}
    sensors = self._do_post(data=data)
    if not sensors:
      raise VirbNoSensors('no Sensors are currently available')

  def device_info(self):
    """Returns the cameras device info"""
    command = 'deviceInfo'
    data = {'command': command}
    return self._do_post(data=data)[command]

  def locate(self):
    """Starts the camera emmiting its lost sound/flash"""
    command = 'locate'
    data = {'command':command}
    return bool(int(self._do_post(data=data)['result']))

  def found(self):
    """Stops the camera emmiting its lost sound/flash"""
    command = 'found'
    data = {'command':command}
    return bool(int(self._do_post(data=data)['result']))

  def media_dir_list(self):
    """Returns the list of media directories on the device"""
    command = 'mediaDirList'
    data = {'command':command}
    return self._do_post(data=data)#['mediaDirs']

  def media_list(self, path=None):
    """Returns the list of media directories on the device"""
    command = "mediaList"
    data = {'command':command}
    if path:
      data['path'] = path
    return self._do_post(data=data)['media']


  def live_preview(self, streamtype="rtp"):
    """Returns the cameras live preview url"""
    command = 'livePreview'
    data = {'command':command,
            'streamType':streamtype}
    return self._do_post(data=data)['url']

  def snap_picture(self, timer=0):
    """Take a picture"""
    command = 'snapPicture'
    data = {'command':command,
            'selfTimer':timer}
    return self._do_post(data=data)

  def start_recording(self):
    """Start recording"""
    command = "startRecording"
    data = {'command':command}
    return bool(int(self._do_post(data=data)['result']))

  def stop_recording(self):
    """Stop recording"""
    command = 'stopRecording'
    data = {'command':command}
    return bool(int(self._do_post(data=data)['result']))

  def stop_stil_tecording(self):
    """Stop recording still images"""
    command = 'stopStillRecording'
    data = {'command':command}
    return bool(int(self._do_post(data=data)['result']))

  def _do_post(self, url='virb', data=None):
    url = 'http://%s:%d/%s' % (self.host[0], self.host[1], url)
    request = requests.post(url, data=simplejson.dumps(data))
    self.requestcount += 1
    try:
      return request.json()
    except simplejson.scanner.JSONDecodeError:
      return request.text


class VirbUsb(object):
  """Class to interact with Garmin Virb devices over USB"""
  def __init__(self, device):
    """Sets the USB device path as seen on the filesystem

    For example:
    device = /media/garmin-virb"""
    self.device = device

  def get_log(self):
    """Yields a list of log entries on the device"""
    logfile = open('%s/Garmin/elog.txt' % self.device, 'r')
    logentry = []
    for line in logfile.readline():
      if line:
        logentry.append(line)
      if line == '-----------------------------------------':
        yield logentry
        logentry = []

  def clear_log(self):
    """Clears the log entries on the device"""
    logfile = open('%s/Garmin/elog.txt' % self.device, 'w')
    logfile.close()
    return True

  def get_tracks(self):
    """Lists all the gpx tracks on the devices"""
    trackpath = '%s/Garmin/GPX' % self.device
    fileslist = os.listdir(trackpath)
    return [filename for filename in fileslist
            if os.path.isfile(os.path.join(trackpath, filename))]

  def get_activity(self):
    """Lists all FIT activity files on the device

    Use https://github.com/dtcooper/python-fitparse to parse these files into
    something meaningfull. Or install fitparse using pip: `pip install fitparse`
    """
    activitypath = '%s/Garmin/Activity' % self.device
    fileslist = os.listdir(activitypath)
    return [filename for filename in fileslist
            if os.path.isfile(os.path.join(activitypath, filename))]

  def get_media(self, extensions=('jpg', 'mp4')):
    """Lists all pictures/videos on the devices

    Possibly filter on extensions (lowercase) using the extensions argument as
      a tuple
    """
    mediapath = '%s/DCIM/100_VIRB' % self.device
    fileslist = os.listdir(mediapath)
    return [filename for filename in fileslist
            if (os.path.isfile(os.path.join(mediapath, filename)) and
                filename[-3:].lower() in extensions)]

  def update_firmware(self, version=None):
    """This Upgrades the firmware on the Virb

    It follows the known update procedure but handles everything on its own.

    GCD Update Procedure

    Use the links in Firmware History to download the zipped file for the
    version you need.
    (https://www8.garmin.com/support/download_details.jsp?id=6565)
    Unzip the downloaded archive and extract the gcd file
    Rename the gcd file to gupdate.gcd
    Connect the VIRB to your computer via usb
    Copy the gupdate.gcd file to [µSD]/Garmin/gupdate.gcd
    Disconnect and reboot the VIRB
    Once the update is completed, the VIRB will delete the gupdate.gcd file"""
    if version:
      garmin = Garmin()
      firmware = garmin.get_firmware(version=version)
      targetpath = '%s/Garmin/gupdate-.gcd' % self.device
      print('Writing out data to device, do not reboot / power down')
      targetfile = open(targetpath, 'w')
      targetfile.write(firmware)
      print('Finishing writing out data to device, do not reboot / power down')
      os.fsync(targetfile)
      targetfile.close()
      print('All Done. Please reboot the Virb')
      return True
    return False


class Garmin(object):
  """Class to namespace any Garmin specific funtions and methods that have no
  direct use for any specific device information"""
  @staticmethod
  def get_firmware(device="VIRB", version=4.00):
    """Version as float"""
    return requests.get("https://download.garmin.com/software/%s_%d.gcd" % (
        device, int(version*100)))

class VirbError(Exception):
  """General exception class for Virb camera class"""


class VirbNoSensors(VirbError):
  """No sensors where located / enabled / connected to the Virb"""


if __name__ == '__main__':
  camera = Virb()
  print(repr(camera.status()))
  print(repr(camera.device_info()))
  print(repr(camera.features()))
  print(repr(camera.get_features()))
  try:
    print(repr(camera.sensors()))
  except VirbNoSensors:
    print('no sensors connected')
  print(repr(camera.media_dir_list()))
  #print(repr(camera.SnapPicture()))
