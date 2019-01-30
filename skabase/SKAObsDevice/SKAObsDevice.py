# -*- coding: utf-8 -*-
#
# This file is part of the SKAObsDevice project
#
#
#

""" SKAObsDevice

A generic base device for Observations for SKA. It inherits SKABaseDevice class. Any device implementing
an obsMode will inherit from SKAObsDevice instead of just SKABaseDevice.
"""
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
from future.utils import with_metaclass
file_path = os.path.dirname(os.path.abspath(__file__))
basedevice_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SKABaseDevice"
sys.path.insert(0, basedevice_path)

# tango imports
from tango.server import run, DeviceMeta, attribute
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(SKAObsDevice.additionnal_import) ENABLED START #
import release
# PROTECTED REGION END #    //  SKAObsDevice.additionnal_import

#__all__ = ["SKAObsDevice", "main"]


class SKAObsDevice(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    A generic base device for Observations for SKA.
    """
    # PROTECTED REGION ID(SKAObsDevice.class_variable) ENABLED START #
    def __init__(self, *args, **kwargs):
        super(SKAObsDevice, self).__init__(*args, **kwargs)

        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        # Initialize attribute values.
        self._obs_state = 0
        self._obs_mode = 0
        self._config_progress = 0
        self._config_delay_expected = 0

    # PROTECTED REGION END #    //  SKAObsDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    obsState = attribute(
        dtype='DevEnum',
        doc="Observing State",
        enum_labels=["IDLE", "CONFIGURING", "READY", "SCANNING", "PAUSED", "ABORTED", "FAULT", ],
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
        # PROTECTED REGION ID(SKAObsDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKAObsDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAObsDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAObsDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAObsDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAObsDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(SKAObsDevice.obsState_read) ENABLED START #
        """Reads Observation State of the device"""
        return self._obs_state
        # PROTECTED REGION END #    //  SKAObsDevice.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(SKAObsDevice.obsMode_read) ENABLED START #
        """Reads Observation Mode of the device"""
        return self._obs_mode
        # PROTECTED REGION END #    //  SKAObsDevice.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(SKAObsDevice.configurationProgress_read) ENABLED START #
        """Reads percentage configuration progress of the device"""
        return self._config_progress
        # PROTECTED REGION END #    //  SKAObsDevice.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(SKAObsDevice.configurationDelayExpected_read) ENABLED START #
        """Reads expected Configuration Delay in seconds"""
        return self._config_delay_expected
        # PROTECTED REGION END #    //  SKAObsDevice.configurationDelayExpected_read


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKAObsDevice.main) ENABLED START #
    return run((SKAObsDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAObsDevice.main

if __name__ == '__main__':
    main()
