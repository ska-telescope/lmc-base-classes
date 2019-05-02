# -*- coding: utf-8 -*-
#
# This file is part of the SKATestDevice project
#
#
#

""" SKATestDevice

A generic Test device for testing SKA base class functionalities.
"""
# PROTECTED REGION ID(SKATestDevice.additionnal_import) ENABLED START #
# standard imports
import os
import sys
import json
from future.utils import with_metaclass


# Tango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import DeviceMeta, attribute, command

# SKA specific imports
from skabase import release
from skabase.auxiliary.utils import (exception_manager, convert_api_value, coerce_value)
from SKABaseDevice import SKABaseDevice


file_path = os.path.dirname(os.path.abspath(__file__))
basedevice_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SKABaseDevice"
sys.path.insert(0, basedevice_path)

# PROTECTED REGION END #    //  SKATestDevice.additionnal_import

__all__ = ["SKATestDevice", "main"]


class SKATestDevice(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    A generic Test device for testing SKA base class functionalities.
    """
    # PROTECTED REGION ID(SKATestDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    obsState = attribute(
        dtype='DevEnum',
        doc="Observing State",
        enum_labels=["IDLE", "CONFIGURING", "READY", "SCANNING",
                     "PAUSED", "ABORTED", "FAULT", ],
    )

    obsMode = attribute(
        dtype='DevEnum',
        doc="Observing Mode",
        enum_labels=["IDLE", "IMAGING", "PULSAR-SEARCH", "PULSAR-TIMING", "DYNAMIC-SPECTRUM",
                     "TRANSIENT-SEARCH", "VLBI", "CALIBRATION", ],
    )

    configurationProgress = attribute(
        dtype='uint16',
        unit="%",
        max_value=100,
        min_value=0,
        doc="Percentage configuration progress",
    )

    configurationDelayExpected = attribute(
        dtype='uint16',
        unit="seconds",
        doc="Configuration delay expected in seconds",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKATestDevice.init_device) ENABLED START #
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        self._storage_logging_level = int(tango.LogLevel.LOG_DEBUG)
        self._element_logging_level = int(tango.LogLevel.LOG_DEBUG)
        self._central_logging_level = int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SKATestDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKATestDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATestDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKATestDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATestDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(SKATestDevice.obsState_read) ENABLED START #
        """Reads Observing State of the device"""
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(SKATestDevice.obsMode_read) ENABLED START #
        """Reads Observing Mode of the device"""
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(SKATestDevice.configurationProgress_read) ENABLED START #
        """Reads percentage configuration progress"""
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(SKATestDevice.configurationDelayExpected_read) ENABLED START #
        """Reads configuration delay expected in seconds"""
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.configurationDelayExpected_read

    # --------
    # Commands
    # --------

    @command(
        dtype_in='str',
        doc_in="JSON encoded dict with this format\n{``group``: str,  # name of existing group\n"
               "  ``command``: str, # name of command to run\n"
               "  ``arg_type``: str,  # data type of command input argument\n"
               "  ``arg_value``: str, # value for command input argument\n"
               "  ``forward``: bool  # True if command should be forwarded to "
               "all subgroups (default)\n}",
        dtype_out='str',
        doc_out="Return value from command on the group, as a JSON encoded string.\n"
                "This will be a list of dicts of the form \n[ \n{``device_name``: str,  "
                "# TANGO device name\n  ``argout``: <value>,  # return value from "
                "command (type depends on command)\n  ``failed``: bool  # True if command failed\n},"
                "\n{ ... },\n ... ]",
    )
    @DebugIt()
    def RunGroupCommand(self, argin):
        # PROTECTED REGION ID(SKATestDevice.RunGroupCommand) ENABLED START #
        with exception_manager(self):
            defaults = {'arg_type': None, 'arg_value': None, 'forward': True}
            required = ('group', 'command', 'arg_type', 'arg_value', 'forward')
            args = self._parse_argin(argin, defaults=defaults, required=required)
            group_name = args['group']
            group = self.groups.get(group_name)
            if group:
                group_command = args['command']
                forward = args['forward']
                if args['arg_type']:
                    _, param = convert_api_value({'type': args['arg_type'],
                                                  'value': args['arg_value']})
                    replies = group.command_inout(group_command, param, forward=forward)
                else:
                    replies = group.command_inout(group_command, forward=forward)
                results = []
                for reply in replies:
                    result = {
                        'device_name': reply.dev_name(),
                        'argout': coerce_value(reply.get_data()),
                        'failed': reply.has_failed(),
                    }
                    results.append(result)
                argout = json.dumps(results, sort_keys=True)
            else:
                raise RuntimeError("Invalid group requested. '{}' not in '{}'"
                                   .format(group_name, sorted(self.groups.keys())))
        return argout
        # PROTECTED REGION END #    //  SKATestDevice.RunGroupCommand

    @command(
    )
    @DebugIt()
    def On(self):
        # PROTECTED REGION ID(SKATestDevice.On) ENABLED START #
        """Starts the device"""
        self.dev_logging("TurnOn Sending DEBUG", int(tango.LogLevel.LOG_DEBUG))
        self.dev_logging("TurnOn Sending INFO", int(tango.LogLevel.LOG_INFO))
        self.dev_logging("TurnOn Sending WARNING", int(tango.LogLevel.LOG_WARN))
        self.dev_logging("TurnOn Sending ERROR", int(tango.LogLevel.LOG_ERROR))
        self.dev_logging("TurnOn Sending FATAL", int(tango.LogLevel.LOG_FATAL))
        #TODO: Set state to ON
        # PROTECTED REGION END #    //  SKATestDevice.On

    @command(
    )
    @DebugIt()
    def Stop(self):
        # PROTECTED REGION ID(SKATestDevice.Stop) ENABLED START #
        """Stops the device"""
        self.dev_logging("TurnOFF Sending DEBUG", int(tango.LogLevel.LOG_DEBUG))
        self.dev_logging("TurnOFF Sending INFO", int(tango.LogLevel.LOG_INFO))
        self.dev_logging("TurnOFF Sending WARNING", int(tango.LogLevel.LOG_WARN))
        self.dev_logging("TurnOFF Sending ERROR", int(tango.LogLevel.LOG_ERROR))
        self.dev_logging("TurnOFF Sending FATAL", int(tango.LogLevel.LOG_FATAL))
        # TODO: Set state to OFF
        # PROTECTED REGION END #    //  SKATestDevice.Stop

# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKATestDevice.main) ENABLED START #
    """
    Main entry point of the module.
    """
    return run((SKATestDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKATestDevice.main

if __name__ == '__main__':
    main()
