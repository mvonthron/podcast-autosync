#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys, os
import time
from subprocess import Popen, PIPE
import re
import dbus
import gobject
import pynotify
from optparse import OptionParser

from autosync_rules import *

#
max_pause = 10

def notify(msg):
  """
  pynotify notifications
  """
  n = pynotify.Notification("Podcast Autosync", msg, "multimedia-player")
  n.show()


def sync(mount_point, rule):
  """
  call rsync to transfer files for each directory pair of the rule
  """
  total = 0
  
  for sync in rule["sync-dirs"]:
    p = Popen(["rsync", "--stats", "-tr", sync[0], os.path.join(mount_point, sync[1])], stdout=PIPE)
    for line in p.stdout.readlines():
      if line.startswith("Number of files transferred"):
        total += int(re.search("(\d*)$", line).group(0))

  if total == 0:
    submsg = "Nothing to be done"
  else:
    submsg = "%d files transferred" % total

  notify("%s synced\n%s" % (rule["name"], submsg))


class USBDaemon:
  """
  USB daemon class, waits for plug/unplug USB event from D-Bus
  """
  
  def __init__(self):
    self.bus = dbus.SystemBus()
    self.hal = self.bus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
    self.hal_manager = dbus.Interface(self.hal, "org.freedesktop.Hal.Manager")
    self.hal_manager.connect_to_signal("DeviceAdded", self.device_added)
    self.hal_manager.connect_to_signal("DeviceRemoved", self.device_removed)


  def device_added(self, uid):
    """
    catch "DeviceAdded" D-Bus events
    """
    
    dev_object = self.bus.get_object("org.freedesktop.Hal", uid)
    device = dbus.Interface(dev_object, 'org.freedesktop.Hal.Device')

    if not device.QueryCapability("volume"):
      return

    uuid = device.GetProperty("volume.uuid")
    
    if options.newdevicemode:
      self.manage_new_device(device)
    
    if not uuid in rules:
      print "Ignored device \"%s\" added" % uuid
      return 
    
    if rules[uuid]["name"] is None:
      rules[uuid]["name"] = device.GetProperty("volume.label")
    
    i=0
    while not device.GetProperty("volume.is_mounted") and i < max_pause:
      time.sleep(1)
      i += 1
    
    if not device.GetProperty("volume.is_mounted"):
      print "Device \"%s\" plugged without being mounted"
      return
    
    size = device.GetProperty("volume.size")
    msg = "Device added: %s (%.2fGb)\nTo be synced: %s" % (rules[uuid]["name"], float(size)/ 1024**3, ", ".join([os.path.basename(r[1]) for r in rules[uuid]["sync-dirs"]]))
    notify(msg)
    
    # perform actual sync check and transfers through rsync
    sync(device.GetProperty("volume.mount_point"), rules[uuid])


  def device_removed(self, uid):
    """
    catch "DeviceRemoved" D-Bus events
    nothing so far
    """
    
    #uuid = device.GetProperty("volume.uuid")
    #notify("Podcast Autosync", "%s has be removed" % rules[uuid]["name"])


  def manage_new_device(self, device):
    """
    sort of wizard to know uuid of the wanted device
    """

    uuid = device.GetProperty("volume.uuid")
    dev = device.GetProperty("block.device")
    name = device.GetProperty("volume.label")
    fs = device.GetProperty("volume.fsversion")
    size = device.GetProperty("volume.size")
    
    if device.GetProperty("volume.is_mounted"):
      mountmsg = "%s mounted on %s" % (dev, device.GetProperty("volume.mount_point"))
    else:
      mountmsg = "%s" % dev
      
    print "The following has been detected:"
    print "  %s\t(id: %s)\n  %s\n  %s, size: %.2fGb" % (name, uuid, mountmsg, fs, float(size)/ 1024**3)
    print "Is this the device you want to add?"
    
    if raw_input("[y/n] ") in ("y", "Y"):
      print
      print "Please edit file \"autosync_conf.py\" and add another rule with ID: \"%s\"" % uuid
      print "Help on format is provided inside the file"
    
    sys.exit()
    
    

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-n", "--new-device",
                    action="store_true", dest="newdevicemode",
                    help="helps registering a new device")
  parser.add_option("-c", "--conf",
                    dest="conffile", metavar="FILE",
                    help="use FILE as the configuration/rules file")
  parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose",
                    help="Verbose mode")
  (options, args) = parser.parse_args()
  
  if options.newdevicemode:
    print "Please plug the desired device", "(a few moments may be needed afterwards)"
    print
  
  from dbus.mainloop.glib import DBusGMainLoop
  DBusGMainLoop(set_as_default=True)
  pynotify.init("Podcast Autosync")
  
  daemon = USBDaemon()
  loop = gobject.MainLoop()
  
  try:
    loop.run()
  except KeyboardInterrupt, SystemExit:
    print "Exiting..."
    loop.quit()
