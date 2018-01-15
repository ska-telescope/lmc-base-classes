#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ElementLogger device server receiving logs from another device server"""
import sys
import time
import logging
from PyTango import server, DeviceProxy, Database, DbDevInfo, DevState, DebugIt, AttrQuality, AttrWriteType, DispLevel 
from PyTango.server import Device, DeviceMeta, attribute, command, run, device_property


"""ElementLogger device server class"""
class ElementLogger(Device):
    __metaclass__ = DeviceMeta

    def init_device(self):
        Device.init_device(self)
        self.__StorageLoggingLevel = 5 #Storage logging level for ElementLogger(Unused currently)
        self.__ElementLoggingLevel = 5 #Element logging level for all Element devices(Unused currently)
        self.set_state(DevState.STANDBY)
        self.info_stream("Init ElementLogger Device.")

    @command(dtype_in='DevVarLongStringArray', dtype_out=None)
    def SetStorageLoggingLevel(self, storages):
        StorageLoggingLevel = storages[0][:]
        StorageLoggingDevice = storages[1][:]
        i = 0
        while i < len(StorageLoggingLevel[:]):
            self.info_stream("%s,%s", StorageLoggingLevel[i], StorageLoggingDevice[i])
            dev1 = DeviceProxy(StorageLoggingDevice[i])
            dev1.storageLoggingLevel = StorageLoggingLevel[i]
            i+=1

    @command(dtype_in='DevVarLongStringArray', dtype_out=None)
    def SetElementLoggingLevel(self, element_devices_and_levels):
        ElementLoggingLevel = element_devices_and_levels[0][:]
        ElementLoggingDevice = element_devices_and_levels[1][:]
        i = 0
        while i < len(ElementLoggingLevel[:]):
            self.info_stream("%s,%s", ElementLoggingLevel[i], ElementLoggingDevice[i])
            dev1 = DeviceProxy(ElementLoggingDevice[i])
            dev1.elementLoggingLevel = ElementLoggingLevel[i]
            property_names = ["logging_level",
                              "logging_target",
                             ]
            dev_properties = dev1.get_property(property_names)
            dev_properties["logging_level"] = ["DEBUG"]
            dev_properties["logging_target"].append("device::ellogger/elem/elem1")
            dev1.put_property(dev_properties)
            dev1.add_logging_target("device::ellogger/elem/elem1")
            i+=1
        
    """Logs are received from all element devices at all levels.
       Filteration happens within the log function depending upon
       ElementLoggingLevel of each element device.
       NOTE : This fiteration logic is still under consideration."""
    @command(dtype_in='DevVarStringArray', dtype_out=None)
    def log(self, details):
	message = details[3]
        level = details[1]
        tango_log_level = {"FATAL":1,"ERROR":2,"WARN":3,"INFO":4,"DEBUG":5}
        level_number = tango_log_level[level]
        logsource = details[2]
        if logsource == details[2]:
            device = DeviceProxy(logsource)
            deviceLogLevel = device.elementLoggingLevel
            if level == "FATAL" and level_number <= deviceLogLevel:
                self.fatal_stream("%s : %s",logsource, message)
            elif level == "ERROR" and level_number <= deviceLogLevel:
                self.error_stream("%s : %s",logsource, message)
            elif level == "WARN" and level_number <= deviceLogLevel:
                self.warn_stream("%s : %s",logsource, message)
            elif level == "INFO" and level_number <= deviceLogLevel:
                self.info_stream("%s : %s",logsource, message)
            elif level == "DEBUG" and level_number <= deviceLogLevel: 
                self.debug_stream("%s : %s",logsource, message)
            else:
                pass
        else:
            pass

run((ElementLogger,))
