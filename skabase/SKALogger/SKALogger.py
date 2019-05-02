# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#


""" SKALogger

A generic base device for Logging for SKA. It enables to view on-line logs through the TANGO Logging Services
and to store logs using Python logging. It configures the log levels of remote logging for selected devices.
"""
# tango imports
import tango
from tango import DebugIt, DeviceProxy, DevFailed
from tango.server import run, DeviceMeta, command

# Additional import
# PROTECTED REGION ID(SKALogger.additionnal_import) ENABLED START #
from future.utils import with_metaclass
# standard imports
import os
import sys

# SKA specific imports
from skabase import release
file_path = os.path.dirname(os.path.abspath(__file__))
basedevice_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SKABaseDevice"
sys.path.insert(0, basedevice_path)
from SKABaseDevice import SKABaseDevice
# PROTECTED REGION END #    //  SKALogger.additionnal_import

__all__ = ["SKALogger", "main"]


class SKALogger(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    A generic base device for Logging for SKA.
    """
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
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        self._storage_logging_level = int(tango.LogLevel.LOG_DEBUG)
        self._element_logging_level = int(tango.LogLevel.LOG_DEBUG)
        self._central_logging_level = int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SKALogger.init_device

    def write_storageLoggingLevel(self, value):
        # PROTECTED REGION ID(SKALogger.write_storageLoggingLevel) ENABLED START #
        self._storage_logging_level = value
        # PROTECTED REGION END #    //  SKALogger.write_storageLoggingLevel

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
        A method of LogConsumer Interface, to enable log messages appear in Tango log viewer.
        :parameter: argin: DevVarStringArray
            Consists a list of strings. The individual items in the list are as follows:
            argin[0] : the timestamp in millisecond since epoch (01.01.1970)
            argin[1] : the log level
            argin[2] : the log source (i.e. device name)
            argin[3] : the log message
            argin[4] : the log NDC (contextual info) - Not used but reserved
            argin[5] : the thread identifier (i.e. the thread from which the log request comes from)

        :returns: DevString.
            Returns the log message when successful. None if fail.
        """
        log_level = argin[1]
        log_source = argin[2]
        log_message = argin[3]
        tango_log_level = {"FATAL": int(tango.LogLevel.LOG_FATAL),
                           "ERROR": int(tango.LogLevel.LOG_ERROR),
                           "WARN": int(tango.LogLevel.LOG_WARN),
                           "INFO": int(tango.LogLevel.LOG_INFO),
                           "DEBUG": int(tango.LogLevel.LOG_DEBUG)}
        level_number = tango_log_level[log_level]

        # Check source devices Central and Element logging levellogging
        try:
            device = DeviceProxy(log_source)
        except DevFailed:
            self.error_stream("%s : Failed to create device proxy.", __name__)
            return ""

        device_log_level = -1
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
        Sets Central logging level of the source device.

        :parameter: argin: DevVarLogStringArray
            Array consisting of
            argin[0]: DevLong. Desired logging level
            argin[1]: DevString. Desired tango device

        :returns: None.
        """
        central_logging_level = argin[0][:]
        #To convert the type of log level from numpy.ndarray to list. Needs to fix in PyTango.
        central_logging_level = central_logging_level.tolist()
        central_logging_device = argin[1][:]
        i = 0
        while i < len(central_logging_level[:]):
            self.info_stream("Central Logging level : %s, Device : %s",
                             central_logging_level[i],
                             central_logging_level[i])
            dev_proxy = DeviceProxy(central_logging_device[i])
            dev_proxy.centralLoggingLevel = central_logging_level[i]
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
        Set Element logging level of source device.

        :parameter: argin: DevVarLogStringArray
            Array consisting of
            argin[0]: DevLong. Desired logging level
            argin[1]: DevString. Desired tango device

        :returns: None.
        """
        element_logging_level = argin[0][:]
        #To convert the type of log level from numpy.ndarray to list. Needs to fix in PyTango.
        element_logging_level = element_logging_level.tolist()
        element_logging_device = argin[1][:]
        i = 0
        while i < len(element_logging_level[:]):
            self.info_stream("Element Logging level : %s, Device : %s",
                             element_logging_level[i],
                             element_logging_device[i])
            dev_proxy = DeviceProxy(element_logging_device[i])
            dev_proxy.elementLoggingLevel = element_logging_level[i]
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
        Sets Storage logging level of source device.

        :parameter: argin: DevVarLogStringArray
            Array consisting of
            argin[0]: DevLong. Desired logging level
            argin[1]: DevString. Desired tango device

        :returns: None.
        """
        storage_logging_level = argin[0][:]
        #To convert the type of log level from numpy.ndarray to list. Needs to fix in PyTango.
        storage_logging_level = storage_logging_level.tolist()
        storage_logging_device = argin[1][:]
        i = 0
        while i < len(storage_logging_level[:]):
            self.info_stream("Storage logging level : %s, Device : %s",
                             storage_logging_level[i],
                             storage_logging_device[i])
            dev_proxy = DeviceProxy(storage_logging_device[i])
            dev_proxy.storageLoggingLevel = storage_logging_level[i]
            i += 1
        # PROTECTED REGION END #    //  SKALogger.SetStorageLoggingLevel

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKALogger.main) ENABLED START #
    """
    Main entry point of the module.
    """
    return run((SKALogger,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKALogger.main

if __name__ == '__main__':
    main()
