# pylint: disable=invalid-name,pointless-string-statement
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module implements Test Mode Overrides that can be added to an SKABaseDevice."""
import json
from typing import Any, Callable, Iterable, TypeAlias

from ska_control_model import HealthState, TestMode
from tango import AttReqType, AttributeProxy
from tango.server import attribute

from .base_device import SKABaseDevice


class TestModeOverrideMixin:
    """Add Test Mode Attribute Overrides to an TestModeOverrideMixin."""
    _test_mode: TestMode = None
    _test_mode_overrides: dict[str, Any] = None
    _test_mode_overrides_changed: Callable[[], None] | None = None
    _test_mode_enum_attrs = None
    push_change_event: Callable[[], None] | None = None
    push_archive_event: Callable[[], None] | None = None
    get_device_attr: Callable[[], None] | None = None

    def __init_subclass__(cls: SKABaseDevice, **kwargs):
        """Add our variables to the class we are extending.

        :param kwargs: keyword arguments (passed to superclass).
        """
        cls._test_mode: TestMode = TestMode.NONE  # just in case base device changes...
        cls._test_mode_overrides: dict[str, Any] = {}
        """Overrides used in TestMode - attribute name: override value"""
        cls._test_mode_overrides_changed: Callable[[], None] | None = None
        """Optional callback to trigger when test mode overrides change."""
        cls._test_mode_enum_attrs = {
            "healthState": HealthState,
        }
        """Tango attribute and enum class, for str conversion in TestMode overrides."""
        super().__init_subclass__(**kwargs)

    def _get_override_value(
        self,
        attr_name: str,
        default: Any = None,
    ) -> Any:
        """
        Read a value from our overrides, use a default value when not overridden.

        Used where we use possibly-overridden internal values within the device server
        (i.e. reading member variables, not via the Tango attribute read mechanism).

        e.g.
        ``my_thing = self._get_override_value("thing", self._my_thing_true_value)``

        :param attr_name: Tango Attribute name.
        :param default: Default value to return if no override in effect.
        :returns: Active override value or ``default``.
        """
        if (
            self._test_mode != TestMode.TEST
            or attr_name not in self._test_mode_overrides
        ):
            return default
        return self._override_value_convert(
            attr_name, self._test_mode_overrides[attr_name]
        )

    @attribute(dtype=TestMode, memorized=True, hw_memorized=True)
    def testMode(self) -> TestMode:
        """
        Read the Test Mode of the device.

        Either no test mode or an indication of the test mode.

        :return: Test Mode of the device
        """
        return self._test_mode

    @testMode.write  # type: ignore[no-redef]
    def testMode(self, value: TestMode) -> None:
        """
        Set the Test Mode of the device.

        Reset our test mode override values when leaving test mode.

        :param value: Test Mode
        """
        if value == TestMode.NONE:
            overrides_being_removed = list(self._test_mode_overrides.keys())
            self._test_mode_overrides = {}
            self._push_events_overrides_removed(overrides_being_removed)
            # call downstream callback function to deal with override changes
            if self._test_mode_overrides_changed is not None:
                self._test_mode_overrides_changed()

        self._test_mode = value

    @attribute(
        dtype=str,
        doc="Attribute value overrides (JSON dict)",
    )  # type: ignore[misc]
    def test_mode_overrides(self) -> str:
        """
        Read the current override configuration.

        :return: JSON-encoded dictionary (attribute name: value)
        """
        return json.dumps(self._test_mode_overrides)

    def is_test_mode_overrides_allowed(self, request_type: AttReqType) -> bool:
        """
        Control access to test_mode_overrides attribute.

        Writes to the attribute are allowed only if test mode is active.

        :param request_type: Attribute request type
        :returns: If in test mode
        """
        if request_type == AttReqType.READ_REQ:
            return True
        return self._test_mode == TestMode.TEST

    @test_mode_overrides.write  # type: ignore[no-redef, misc]
    def test_mode_overrides(self, value_str: str) -> None:
        """
        Write new override configuration.

        :param value_str: JSON-encoded dict of overrides (attribute name: value)
        """
        value_dict = json.loads(value_str)
        assert isinstance(value_dict, dict), "expected JSON-encoded dict"
        overrides_being_removed = self._test_mode_overrides.keys() - value_dict.keys()
        # we could call _override_value_convert on incoming values here, but I prefer to
        # leave as-is, so the user can read back the same thing they wrote in
        self._test_mode_overrides = value_dict
        self._push_events_overrides_removed(overrides_being_removed)

        # send events for all overrides
        # only *need* to send new or changed overrides but that's annoying to determine
        # i.e. premature optimisation
        for attr_name, value in value_dict.items():
            value = self._override_value_convert(attr_name, value)
            attr_cfg = self.get_device_attr().get_attr_by_name(attr_name)
            if attr_cfg.is_change_event():
                self.push_change_event(attr_name, value)
            if attr_cfg.is_archive_event():
                self.push_archive_event(attr_name, value)

        # call downstream callback function to deal with override changes
        if self._test_mode_overrides_changed is not None:
            self._test_mode_overrides_changed()

    def _push_events_overrides_removed(self, attrs_to_refresh: Iterable[str]) -> None:
        """
        Push true value events for attributes that were previously overridden.

        :param attrs_to_refresh: Names of our attributes that are no longer overridden
        """
        for attr_name in attrs_to_refresh:
            # Read configuration of attribute
            attr_cfg = self.get_device_attr().get_attr_by_name(attr_name)
            manual_event = attr_cfg.is_change_event() or attr_cfg.is_archive_event()

            if not manual_event:
                continue

            # Read current state of attribute
            attr = AttributeProxy(f"{self.get_name()}/{attr_name}").read()
            if attr_cfg.is_change_event():
                self.push_change_event(attr_name, attr.value, attr.time, attr.quality)
            if attr_cfg.is_archive_event():
                self.push_archive_event(attr_name, attr.value, attr.time, attr.quality)

    def _override_value_convert(self, attr_name: str, value: Any) -> Any:
        """
        Automatically convert types for attr overrides (e.g. enum label -> int).

        :param attr_name: Attribute name
        :param value: Value to convert
        :return: Converted value
        """
        if attr_name in self._test_mode_enum_attrs and isinstance(value, str):
            return self._test_mode_enum_attrs[attr_name][value]

        # default to no conversion
        return value


def overridable(
    func: Callable[[object, Any, Any], None]
) -> Callable[[object, Any, Any], None] | Any:
    """
    Decorate attribute with test mode overrides.

    :param func: Tango attribute
    :return: Overridden value or original function
    """
    attr_name = func.__name__

    def override_attr_in_test_mode(
        self: TestModeOverrideMixin, *args: Any, **kwargs: Any
    ) -> Callable[[object, Any, Any], None] | Any:
        """
        Override attribute when test mode is active and value specified.

        :param self: Tango device with TestModeOverrideMixin
        :param args: Any positional arguments
        :param kwargs: Any keyword arguments
        :return: Tango attribute
        """
        # pylint: disable=protected-access
        if self._test_mode == TestMode.TEST and attr_name in self._test_mode_overrides:
            return self._override_value_convert(
                attr_name, self._test_mode_overrides[attr_name]
            )

        # Test Mode not active, normal attribute behaviour
        return func(self, *args, **kwargs)

    return override_attr_in_test_mode
