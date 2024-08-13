# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
Support for overriding Tango attributes when TestMode is TEST.
"""
from ska_control_model import TestMode, HealthState
from .base_device import SKABaseDevice

enum_attrs = { # TODO - confirm we can change this downstream, may need to refactor?
    "healthState": HealthState,
}
"""Tango attribute and enum class, for string conversion in TestMode overrides."""
def overridable(func):
    """Decorator to apply test mode overrides to attributes."""
    attr_name = func.__name__

    def override_attr_in_test_mode(self: SKABaseDevice, *args, **kwargs):
        """Override attribute when test mode is active and value specified."""
        if (
            self._test_mode == TestMode.TEST
            and attr_name in self._test_mode_overrides
        ):
            return _override_value_convert(
                attr_name, self._test_mode_overrides[attr_name]
            )

        # Test Mode not active, normal attribute behaviour
        return func(self, *args, **kwargs)

    return override_attr_in_test_mode


def _override_value_convert(attr_name: str, value: Any) -> Any:
    """Automatically convert types for attr overrides (e.g. enum label -> int)."""
    if attr_name in enum_attrs and type(value) is str:
        return enum_attrs[attr_name][value]

    # default to no conversion
    return value