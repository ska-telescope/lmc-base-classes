# -*- coding: utf-8 -*-
#
# This file is part of the RefCapCorrelator project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefCapCorrelator

Ref (Reference Element) device of Type RefCapCorrelator
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
from SKACapability import SKACapability
# Additional import
# PROTECTED REGION ID(RefCapCorrelator.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefCapCorrelator.additionnal_import

__all__ = ["RefCapCorrelator", "main"]


class RefCapCorrelator(SKACapability):
    """
    Ref (Reference Element) device of Type RefCapCorrelator
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefCapCorrelator.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefCapCorrelator.class_variable

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
        enum_labels=["IDLE", "IMG_CONTINUUM", "IMG_SPECTRAL_LINE", "IMG_ZOOM", "PULSAR_SEARCH", "TRANSIENT_SEARCH_FAST", "TRANSIENT_SEARCH_SLOW", "PULSAR_TIMING", "VLBI", ],
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
        SKACapability.init_device(self)
        # PROTECTED REGION ID(RefCapCorrelator.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefCapCorrelator.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefCapCorrelator.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefCapCorrelator.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefCapCorrelator.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefCapCorrelator.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(RefCapCorrelator.obsState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefCapCorrelator.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(RefCapCorrelator.obsMode_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefCapCorrelator.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(RefCapCorrelator.configurationProgress_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefCapCorrelator.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(RefCapCorrelator.configurationDelayExpected_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefCapCorrelator.configurationDelayExpected_read


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefCapCorrelator.main) ENABLED START #
    return run((RefCapCorrelator,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefCapCorrelator.main

if __name__ == '__main__':
    main()
