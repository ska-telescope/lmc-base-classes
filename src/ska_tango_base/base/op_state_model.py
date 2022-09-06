# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module provides the op state model for SKA LMC Tango devices.

The model is now defined in the :py:mod:`ska_control_model` package, but
is imported here for backwards compatibility.
"""
from ska_control_model import OpStateModel

__all__ = ["OpStateModel"]
