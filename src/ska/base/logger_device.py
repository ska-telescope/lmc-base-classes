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
# PROTECTED REGION ID(SKALogger.additionnal_import) ENABLED START #
# Standard imports
import os
import sys

# Tango imports
from tango import DebugIt, DeviceProxy, DevFailed
from tango.server import run, command

# SKA specific imports
from . import SKABaseDevice, release
from .control_model import LoggingLevel
# PROTECTED REGION END #    //  SKALogger.additionnal_import

__all__ = ["SKALogger", "main"]


class SKALogger(SKABaseDevice):
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

    @command(dtype_in='DevVarLongStringArray',
             doc_in="Logging level for selected devices:"
                    "(0=OFF, 1=FATAL, 2=ERROR, 3=WARNING, 4=INFO, 5=DEBUG)."
                    "Example: [[4, 5], ['my/dev/1', 'my/dev/2']].")
    @DebugIt()
    def SetLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetLoggingLevel) ENABLED START #
        """
        Sets logging level of the specified devices.

        :parameter: argin: DevVarLongStringArray
            Array consisting of

            argin[0]: list of DevLong. Desired logging level.

            argin[1]: list of DevString. Desired tango device.

        :returns: None.
        """
        logging_levels = argin[0][:]
        logging_devices = argin[1][:]
        for level, device in zip(logging_levels, logging_devices):
            try:
                new_level = LoggingLevel(level)
                self.info_stream("Setting logging level %s for %s", new_level, device)
                dev_proxy = DeviceProxy(device)
                dev_proxy.loggingLevel = new_level
            except DevFailed as dev_failed:
                self.error_stream("Failed to set logging level %s for %s", level, device)
                str_exception = "Exception: " + str(dev_failed)
                self.error_stream(str_exception)
        # PROTECTED REGION END #    //  SKALogger.SetLoggingLevel

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
