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
from PyTango import DebugIt, DeviceProxy
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
from logging.handlers import SysLogHandler

logger_dict = {}
logging.basicConfig()
logger = logging.getLogger("SKALogger")
logger.setLevel(logging.DEBUG)
syslog = SysLogHandler(address='/dev/log', facility= 'syslog')
formatter = logging.Formatter('%(name)s: %(levelname)s %(module)s %(message)r')
syslog.setFormatter(formatter)
logger.addHandler(syslog)


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
        self._storage_logging_level = 5
        self._element_logging_level = 5
        self._central_logging_level = 5

    def write_storageLoggingLevel(self, value):
        self._storage_logging_level = value
        if self._storage_logging_level == int(tango.LogLevel.LOG_FATAL):
            logger.setLevel(logging.FATAL)
        elif self._storage_logging_level == int(tango.LogLevel.LOG_ERROR):
            logger.setLevel(logging.ERROR)
        elif self._storage_logging_level == int(tango.LogLevel.LOG_WARNING):
            logger.setLevel(logging.WARNING)
        elif self._storage_logging_level == int(tango.LogLevel.LOG_INFO):
            logger.setLevel(logging.INFO)
        elif self._storage_logging_level == int(tango.LogLevel.LOG_DEBUG):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.DEBUG)

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
    doc_in="Details of timestamp, logging level, source device and message.",
    dtype_out='str',
    doc_out="Returns the logging message."
    )
    @DebugIt()
    def Log(self, argin):
        # PROTECTED REGION ID(SKALogger.Log) ENABLED START #
        """
        A method of LogConsumer Interface, to enable log viewer.
        """
        log_time = argin[0]
        log_level = argin[1]
        log_source = argin[2]
        log_message = argin[3]
        tango_log_level = {"FATAL": 1, "ERROR": 2, "WARN": 3, "INFO": 4, "DEBUG": 5}
        level_number = tango_log_level[log_level]
        device = DeviceProxy(log_source)

        if self.SkaLevel == 1:
            device_log_level = device.centralLoggingLevel

        elif self.SkaLevel == 2:
            device_log_level = device.elementLoggingLevel

        if log_level == "FATAL" and level_number <= device_log_level:
            self.fatal_stream("%s : %s", log_source, log_message)
        elif log_level == "ERROR" and level_number <= device_log_level:
            self.error_stream("%s : %s", log_source, log_message)
        elif log_level == "WARN" and level_number <= device_log_level:
            self.warn_stream("%s : %s", log_source, log_message)
        elif log_level == "INFO" and level_number <= device_log_level:
            self.info_stream("%s : %s", log_source, log_message)
        elif log_level == "DEBUG" and level_number <= device_log_level:
            self.debug_stream("%s : %s", log_source, log_message)

        return str(log_message)

        # TODO Add dictionary for log sources
        # logger = logger_dict.get(logSource)
        # if not logger:
            # logger = logging.getLogger(logSource)
            # logger.setLevel(logging.INFO)
            # # Add the log message handler to the logger
            # syslog = SysLogHandler(address='/dev/log')
            # logger.addHandler(syslog)
            # logger.debug('this is debug')
            # logger.critical('this is critical')
            #logger_dict[logSource] = logger
        # This should log at the specified level
        #logger.info("{}]\t{}".format(timestamp, logMessage))

        # PROTECTED REGION END #    //  SKALogger.Log

    @command(
    dtype_in='DevVarLongStringArray',
    doc_in="Central logging level for selected devices",
    )
    @DebugIt()
    def SetCentralLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetCentralLoggingLevel) ENABLED START #
        """
        A method to set Central logging level of source device.
        """
        central_logging_level = argin[0][:]
        central_logging_device = argin[1][:]
        i = 0
        while i < len(central_logging_level[:]):
            self.info_stream("Central Logging level : %s, Device : %s", central_logging_level[i],
                             central_logging_level[i])
            dev_proxy = DeviceProxy(central_logging_device[i])
            dev_proxy.centralLoggingLevel = central_logging_level[i]
            property_names = ["logging_level",
                              "logging_target",
                              "CentralLogger"
                              ]
            dev_properties = dev_proxy.get_property(property_names)
            dev_properties["logging_level"] = ["DEBUG"]
            dev_properties["logging_target"].append("device::central/logger/1")
            dev_properties["CentralLogger"] = ["device::central/logger/1"]
            dev_proxy.put_property(dev_properties)
            dev_proxy.add_logging_target("device::central/logger/1")
            i += 1
        # PROTECTED REGION END #    //  SKALogger.SetCentralLoggingLevel

    @command(
    dtype_in='DevVarLongStringArray',
    doc_in="Element logging level for selected devices",
    )
    @DebugIt()
    def SetElementLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetElementLoggingLevel) ENABLED START #
        """
        A method to set Element logging level of source device.
        """
        element_logging_level = argin[0][:]
        element_logging_device = argin[1][:]
        i = 0
        while i < len(element_logging_level[:]):
            self.info_stream("Element Logging level : %s, Device : %s", element_logging_level[i],
                             element_logging_device[i])
            dev_proxy = DeviceProxy(element_logging_device[i])
            dev_proxy.elementLoggingLevel = element_logging_level[i]
            property_names = ["logging_level",
                              "logging_target",
                              "ElementLogger",
                              "ElementLoglevel",
                              "ServerHostName",
                              ]
            dev_properties = dev_proxy.get_property(property_names)
            dev_properties["logging_level"] = ["INFO"]
            dev_properties["logging_target"].append("device::ref/elt/logger")
            dev_properties["ElementLogger"] = ["device::ref/elt/logger"]
            dev_properties["ElementLoglevel"] = [element_logging_level[i]]
            dev_properties["ServerHostName"] = ["localhost"]
            dev_proxy.put_property(dev_properties)
            dev_proxy.add_logging_target("device::ref/elt/logger")
            i += 1
        # PROTECTED REGION END #    //  SKALogger.SetElementLoggingLevel

    @command(
    dtype_in='DevVarLongStringArray',
    doc_in="Storage logging level for selected devices",
    )
    @DebugIt()
    def SetStorageLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetStorageLoggingLevel) ENABLED START #
        """
        A method to set Storage logging level of source device.
        """
        storage_logging_level = argin[0][:]
        storage_logging_device = argin[1][:]
        i = 0
        while i < len(storage_logging_level[:]):
            self.info_stream("Storage logging level : %s, Device : %s", storage_logging_level[i],
                             storage_logging_device[i])
            dev_proxy = DeviceProxy(storage_logging_device[i])
            dev_proxy.storageLoggingLevel = storage_logging_level[i]
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
