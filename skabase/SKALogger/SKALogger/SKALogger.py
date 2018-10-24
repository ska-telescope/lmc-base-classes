# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#
# Distributed under the terms of the none license.
# See LICENSE.txt for more info.

""" SKALogger

A generic base device for Logging for SKA.
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import device_property
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(SKALogger.additionnal_import) ENABLED START #
import logging
import logging.handlers
import datetime

logger_dict = {}

# PROTECTED REGION END #    //  SKALogger.additionnal_import

__all__ = ["SKALogger", "main"]


class SKALogger(SKABaseDevice):
    """
    A generic base device for Logging for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKALogger.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.class_variable

    # -----------------
    # Device Properties
    # -----------------










    # ----------
    # Attributes
    # ----------











    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKALogger.init_device) ENABLED START #
        ####     log_path = device_property(dtype=str, default_value="/tmp")
        self.log_path = "/tmp" # Can be changed to a device property
        print self.log_path
        # PROTECTED REGION END #    //  SKALogger.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKALogger.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKALogger.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKALogger.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKALogger.delete_device

    # ------------------
    # Attributes methods
    # ------------------


    # --------
    # Commands
    # --------

    @command(
    dtype_in=('str',), 
    doc_in="none", 
    )
    @DebugIt()
    def Log(self, argin):
        # PROTECTED REGION ID(SKALogger.Log) ENABLED START #
        ###Log (timestamp,level,source,message)
        source_device =  argin[2]
        message = argin[3]
        timestamp = str(datetime.datetime.fromtimestamp(float(argin[0]) / 1000))
        logger = logger_dict.get(source_device)
        if not logger:
            logger = logging.getLogger(source_device)
            logger.setLevel(logging.INFO)

            # Add the log message handler to the logger
            handler = logging.handlers.RotatingFileHandler(
                self.log_path+ "/"+source_device.replace("/", "_"), maxBytes=3000000, backupCount=5)

            logger.addHandler(handler)
            logger_dict[source_device] = logger

        # This should log at the specified level
        logger.info("{}]\t{}".format(timestamp,message))
        # print argin
        # PROTECTED REGION END #    //  SKALogger.Log

    @command(
    dtype_in='DevVarLongStringArray', 
    doc_in="Central logging level for selected devices", 
    )
    @DebugIt()
    def SetCentralLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetCentralLoggingLevel) ENABLED START #
        CentralLoggingLevel = argin[0][:]
        CentralLoggingDevice = argin[1][:]
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
            dev_properties["logging_target"].append("device::central/logger/1")
            dev1.put_property(dev_properties)
            dev1.add_logging_target("device::central/logger/1")
            i += 1
        # PROTECTED REGION END #    //  SKALogger.SetCentralLoggingLevel

    @command(
    dtype_in='DevVarLongStringArray', 
    doc_in="Element logging level for selected devices", 
    )
    @DebugIt()
    def SetElementLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetElementLoggingLevel) ENABLED START #
        ElementLoggingLevel = argin[0][:]
        ElementLoggingDevice = argin[1][:]
        i = 0
        while i < len(ElementLoggingLevel[:]):
            self.info_stream("Element Logging level : %s, Device : %s", ElementLoggingLevel[i], ElementLoggingDevice[i])
            logger.debug("Element Logging level : %s, Device : %s", ElementLoggingLevel[i], ElementLoggingDevice[i])
            logger.info("Element Logging level : %s, Device : %s", ElementLoggingLevel[i], ElementLoggingDevice[i])
            logger.warning("Element Logging level : %s, Device : %s", ElementLoggingLevel[i], ElementLoggingDevice[i])
            logger.error("Element Logging level : %s, Device : %s", ElementLoggingLevel[i], ElementLoggingDevice[i])
            logger.fatal("Element Logging level : %s, Device : %s", ElementLoggingLevel[i], ElementLoggingDevice[i])
            dev1 = DeviceProxy(ElementLoggingDevice[i])
            dev1.elementLoggingLevel = ElementLoggingLevel[i]
            property_names = ["logging_level",
                              "logging_target",
                              "ElementLogger",
                              "ElementLoglevel",
                              "ServerHostName",
                              ]
            dev_properties = dev1.get_property(property_names)
            dev_properties["logging_level"] = ["INFO"]
            dev_properties["logging_target"] = ["device::localhost:10123/ref/elt/logger"]
            dev_properties["ElementLogger"] = ["device::localhost:10123/ref/elt/logger"]
            dev_properties["ElementLoglevel"] = [ElementLoggingLevel[i]]
            dev_properties["ServerHostName"] = ["localhost"]
            dev1.put_property(dev_properties)
            dev1.add_logging_target("device::localhost:10123/ref/elt/logger")
            i += 1
        # PROTECTED REGION END #    //  SKALogger.SetElementLoggingLevel

    @command(
    dtype_in='DevVarLongStringArray', 
    doc_in="Storage logging level for selected devices", 
    )
    @DebugIt()
    def SetStorageLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetStorageLoggingLevel) ENABLED START #
        StorageLoggingLevel = argin[0][:]
        StorageLoggingDevice = argin[1][:]
        i = 0
        while i < len(StorageLoggingLevel[:]):
            self.info_stream("Storage logging level : %s, Device : %s", StorageLoggingLevel[i], StorageLoggingDevice[i])
            logger.debug("Storage logging level : %s, Device : %s", StorageLoggingLevel[i], StorageLoggingDevice[i])
            logger.info("Storage logging level : %s, Device : %s", StorageLoggingLevel[i], StorageLoggingDevice[i])
            logger.warning("Storage logging level : %s, Device : %s", StorageLoggingLevel[i], StorageLoggingDevice[i])
            logger.error("Storage logging level : %s, Device : %s", StorageLoggingLevel[i], StorageLoggingDevice[i])
            logger.fatal("Storage logging level : %s, Device : %s", StorageLoggingLevel[i], StorageLoggingDevice[i])
            dev1 = DeviceProxy(StorageLoggingDevice[i])
            dev1.storageLoggingLevel = StorageLoggingLevel[i]
            i+=1
        # PROTECTED REGION END #    //  SKALogger.SetStorageLoggingLevel

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKALogger.main) ENABLED START #
    return run((SKALogger,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKALogger.main

if __name__ == '__main__':
    main()
