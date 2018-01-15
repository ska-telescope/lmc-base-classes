#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Sending Device server which is logged by ElementLogger and CentralLogger"""
import sys
import time
import logging
import logging.handlers
import syslog
from logging.handlers import SysLogHandler
from PyTango import AttrQuality, AttrWriteType, DispLevel, DevState, DebugIt, Database, DbDevInfo, DeviceProxy
from PyTango.server import Device, DeviceMeta, attribute, command, run, device_property

logger = logging.getLogger("Sending")
syslog = SysLogHandler(address='/dev/log', facility='user')
formatter = logging.Formatter('%(name)s: %(levelname)s %(module)s %(message)r')
syslog.setFormatter(formatter)
logger.addHandler(syslog)

"""Sending Device server class"""
class Sending(Device):
    __metaclass__ = DeviceMeta

    """Attributes for setting logging levels for element storage and central"""
    elementLoggingLevel = attribute(label="ElementLogginglevel", dtype=int,
                         fget="get_elementLoggingLevel",
                         fset="set_elementLoggingLevel",
                         doc="Sets element logging level")

    storageLoggingLevel = attribute(label="StorgeLoggingLevel", dtype=int,
                         fget="get_storageLoggingLevel",
                         fset="set_storageLoggingLevel",
                         doc="Sets syslog logging level")

    centralLoggingLevel = attribute(label="CentralLoggingLevel", dtype=int,
                         fget="get_centralLoggingLevel",
                         fset="set_centralLoggingLevel",
                         doc="Sets Central logging level")

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.STANDBY)
        self.__elementLoggingLevel = 5        
        self.__storageLoggingLevel = 5        
        self.__centralLoggingLevel = 5        
        logger.setLevel(logging.DEBUG)

    def get_elementLoggingLevel(self):
        return self.__elementLoggingLevel

    def set_elementLoggingLevel(self, elementLoggingLevel):
        self.__elementLoggingLevel = elementLoggingLevel
        return elementLoggingLevel

    def get_centralLoggingLevel(self):
        return self.__centralLoggingLevel

    def set_centralLoggingLevel(self, centralLoggingLevel):
        self.__centralLoggingLevel = centralLoggingLevel
        return centralLoggingLevel

    def get_storageLoggingLevel(self):
        return self.__storageLoggingLevel

    def set_storageLoggingLevel(self, storageLoggingLevel):
        self.debug_stream("In set_StorageLogginglevel")
        self.__storageLoggingLevel = storageLoggingLevel

        if self.__storageLoggingLevel == 1:
            logger.setLevel(logging.FATAL)
        elif self.__storageLoggingLevel == 2:
            logger.setLevel(logging.ERROR)
        elif self.__storageLoggingLevel == 3:
            logger.setLevel(logging.WARNING)
        elif self.__storageLoggingLevel == 4:
            logger.setLevel(logging.INFO)
        elif self.__storageLoggingLevel == 5:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.DEBUG)
        return storageLoggingLevel

    @command
    def TurnOn(self):
        # turn on the sending device.
        self.set_state(DevState.ON)
        self.debug_stream("TurnOn Sending DEBUG")
        self.info_stream("TurnOn Sending INFO")
        self.warn_stream("TurnOn Sending WARNING")
        self.error_stream("TurnOn Sending ERROR")
        self.fatal_stream("TurnOn Sending FATAL")

        logger.debug("TurnOn Sending debug")
        logger.info("TurnOn Sending info")
        logger.warning("TurnOn Sending warn")
        logger.error("TurnOn Sending error")
        logger.fatal("TurnOn Sending fatal")

    @command
    def TurnOff(self):
        # turn off the sending device
        self.set_state(DevState.OFF)
        self.debug_stream("TurnOff Sending DEBUG")
        self.info_stream("TurnOff Sending INFO")
        self.warn_stream("TurnOff Sending WARNING")
        self.error_stream("TurnOff Sending ERROR")
        self.fatal_stream("TurnOff Sending FATAL")

        logger.debug("TurnOff Sending debug")
        logger.info("TurnOff Sending info")
        logger.warning("TurnOff Sending warn")
        logger.error("TurnOff Sending error")
        logger.fatal("TurnOff Sending fatal")

run([Sending])
