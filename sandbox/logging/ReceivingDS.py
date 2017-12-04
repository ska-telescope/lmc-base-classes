#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dummy tango receiving logging device server as CentralLogger"""
import time
import sys
from PyTango import server, DeviceProxy, Database, DbDevInfo, DevState, DebugIt
from PyTango.server import  Device, DeviceMeta,  command, run


"""Created Receiving device server class"""
class Receiving(Device):
    __metaclass__ = DeviceMeta

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.STANDBY)
        self.debug_stream("Init Receiving Device.")

    @command(dtype_in='DevVarStringArray', dtype_out=None)
    def log(self, details):
	message = details[3]
#        print(message)
        self.debug_stream(message)

"""This part is needed to start device server from command line"""
if '--register' in sys.argv:
    reg_ind = sys.argv.index('--register')
    sys.argv.pop(reg_ind)
    name = sys.argv.pop(reg_ind)
    db = Database()
    dev_info = DbDevInfo()
    dev_info._class = 'Receiving'
    dev_info.server = 'ReceivingDS/logdev'
    dev_info.name = name
    db.add_device(dev_info)
    print("In registration....")
else:
    print("Runing DS....")
    run([Receiving])
