#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CentralLogger device server receiving logs from SendingDS server"""
import sys
import time
import logging
from PyTango import server, DeviceProxy, Database, DbDevInfo, DevState, DebugIt, AttrQuality, AttrWriteType, DispLevel 
from PyTango.server import Device, DeviceMeta, attribute, command, run, device_property


"""CentralLogger device server class"""
class CentralLogger(Device):
    __metaclass__ = DeviceMeta

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.STANDBY)
        self.info_stream("Init CentralLogger Device.")

    @command(dtype_in='DevVarLongStringArray', dtype_out=None)
    def SetCentralLoggingLevel(self, element_devices_and_levels):
        CentralLoggingLevel = element_devices_and_levels[0][:]
        CentralLoggingDevice = element_devices_and_levels[1][:]
        i = 0
        while i < len(CentralLoggingLevel[:]):
            self.info_stream("%s,%s", CentralLoggingLevel[i], CentralLoggingDevice[i])
            dev1 = DeviceProxy(CentralLoggingDevice[i])
            dev1.centralLoggingLevel = CentralLoggingLevel[i]
            property_names = ["logging_level",
                              "logging_target",
                             ]
            dev_properties = dev1.get_property(property_names)
            dev_properties["logging_level"] = ["DEBUG"]
            dev_properties["logging_target"].append("device::central/cdev/cdev1")
            dev1.put_property(dev_properties)
            dev1.add_logging_target("device::central/cdev/cdev1")
            i+=1

    """Logs are received from all element devices at all levels.
       Filteration happens within the log function depending upon
       CentralLoggingLevel of each element device.
       NOTE : This fiteration logic is still under consideration."""
    @command(dtype_in='DevVarStringArray', dtype_out=None)
    def log(self, details):
	cmessage = details[3]
        clevel = details[1]
        tango_log_level = {"FATAL":1,"ERROR":2,"WARN":3,"INFO":4,"DEBUG":5}
        level_number = tango_log_level[clevel]
        clogsource = details[2]
        if clogsource == details[2]:
            device = DeviceProxy(clogsource)
            deviceLogLevel = device.centralLoggingLevel

            if clevel == "FATAL" and level_number <= deviceLogLevel:
                self.fatal_stream("%s : %s",clogsource, cmessage)
            elif clevel == "ERROR" and level_number <= deviceLogLevel:
                self.error_stream("%s : %s",clogsource, cmessage)
            elif clevel == "WARN" and level_number <= deviceLogLevel:
                self.warn_stream("%s : %s",clogsource, cmessage)
            elif clevel == "INFO" and level_number <= deviceLogLevel:
                self.info_stream("%s : %s",clogsource, cmessage)
            elif clevel == "DEBUG" and level_number <= deviceLogLevel:
                self.debug_stream("%s : %s",clogsource, cmessage)
            else:
                pass
        else:
            pass

run((CentralLogger,))
