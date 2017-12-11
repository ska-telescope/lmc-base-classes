#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dummy Device server as sending device to CentralLoggerDS"""

import time
import sys
from PyTango import server 
from PyTango import Database, DbDevInfo, DevState
from PyTango.server import Device, DeviceMeta, command, run

"""Created Device Class"""
class Sending(Device):
    __metaclass__ = DeviceMeta

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.STANDBY)
        self.debug_stream("Init Sending device.")

    @command
    def TurnOn(self):
        # turn on the sending device.
        self.debug_stream("TurnOn Sending device")
        self.set_state(DevState.ON)

    @command
    def TurnOff(self):
        # turn off the sending device
        self.debug_stream("TurnOff Sending device.")
        self.set_state(DevState.OFF)

"""This part is needed to start device server from command line"""
if '--register' in sys.argv:
    reg_ind = sys.argv.index('--register')
    sys.argv.pop(reg_ind)
    name = sys.argv.pop(reg_ind)
    db = Database()
    dev_info = DbDevInfo()
    dev_info._class = 'Sending'
    dev_info.server = 'SendingDS/dummy'
    dev_info.name = name
    db.add_device(dev_info)
else:
    run([Sending])
