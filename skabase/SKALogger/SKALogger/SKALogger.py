# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#

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
    dtype_in='str', 
    doc_in="Central logging level for selected devices", 
    )
    @DebugIt()
    def SetCentralLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetCentralLoggingLevel) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKALogger.SetCentralLoggingLevel

    @command(
    dtype_in='str', 
    doc_in="Element logging level for selected devices", 
    )
    @DebugIt()
    def SetElementLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetElementLoggingLevel) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKALogger.SetElementLoggingLevel

    @command(
    dtype_in='str', 
    doc_in="Storage logging level for selected devices", 
    )
    @DebugIt()
    def SetStorageLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetStorageLoggingLevel) ENABLED START #
        pass
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
