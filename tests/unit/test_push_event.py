# pylint: disable=invalid-name
"""
Tests for SKABaseDevice.push_<X>_event.

This is testing all the available overloads.
"""

from __future__ import annotations

import logging
from typing import Any, Sequence, Tuple

import pytest
import tango
from ska_control_model import ResultCode
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango import AttrQuality, DevFailed, DevState
from tango.server import attribute, command

from ska_tango_base import SKABaseDevice
from ska_tango_base.base import BaseComponentManager


# pylint: disable-next=abstract-method
class ComponentManagerT(BaseComponentManager):
    """Dummy component manager."""


class SimpleDevice(SKABaseDevice[ComponentManagerT]):
    """A device with attributes for testing push_change_event."""

    def __init__(self: SimpleDevice, *args: Any, **kwargs: Any) -> None:
        """Initialise SimpleDevice.

        :param args: positional arguments to pass to the parent class.
        :param kwargs: keyword arguments to pass to the parent class.
        """
        super().__init__(*args, **kwargs)
        self._scalar = 0
        self._spectrum = [0, 0, 0]
        self._image = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self._encoded = ("uint8_le", b"\x00\x00")

    class InitCommand(SKABaseDevice.InitCommand):
        """InitCommand for SimpleDevice."""

        def do(
            self: SimpleDevice.InitCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """Stateless hook for device initialisation.

            :param args: positional arguments to this do method
            :param kwargs: keyword arguments to this do method

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            self._device.set_change_event("scalar", True, False)
            self._device.set_archive_event("scalar", True, False)
            self._device.set_change_event("spectrum", True, False)
            self._device.set_archive_event("spectrum", True, False)
            self._device.set_change_event("image", True, False)
            self._device.set_archive_event("image", True, False)
            self._device.set_change_event("encoded", True, False)
            self._device.set_archive_event("encoded", True, False)

            message = "SimpleDevice Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=int
    )
    def scalar(self: SimpleDevice) -> int:
        """Read the scalar attribute.

        :return: the scalar
        """
        return self._scalar

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=(int,), max_dim_x=3
    )
    def spectrum(self: SimpleDevice) -> Sequence[int]:
        """Read the spectrum attribute.

        :return: the spectrum
        """
        return self._spectrum

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=((int,),),
        max_dim_x=3,
        max_dim_y=3,
    )
    def image(self: SimpleDevice) -> Sequence[Sequence[int]]:
        """Read the image attribute.

        :return: the image
        """
        return self._image

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=tango.DevEncoded
    )
    def encoded(self: SimpleDevice) -> Tuple[str, bytes]:
        """Read the encoded attribute.

        :return: the encoded data
        """
        return self._encoded

    def create_component_manager(self: SimpleDevice) -> ComponentManagerT:
        """Create the component manager.

        :return: the created component manager
        """
        return ComponentManagerT(logging.getLogger(__name__))

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=(str,), dtype_out=None
    )
    def PushChangeEvent(self: SimpleDevice, args: Sequence[str]) -> None:
        """Push an event to an attribute.

        :param args: (attr, event_type) pair, where
            attr: attribute to test
            event_type: which event type to push, either "archive" or "change"
        """
        attr = args[0]
        event_type = args[1]
        push_event = "push_" + event_type + "_event"

        if attr == "scalar":
            self._scalar += 1
            getattr(self, push_event)(attr, self._scalar)
        elif attr == "state":
            getattr(self, push_event)(attr)
        elif attr == "spectrum":
            self._spectrum = [x + 1 for x in self._spectrum]
            getattr(self, push_event)(attr, self._spectrum)
        elif attr == "image":
            self._image = [[x + 1 for x in y] for y in self._image]
            getattr(self, push_event)(attr, self._image)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventExcept(self: SimpleDevice, event_type: str) -> None:
        """Push an exception event to the scalar attribute.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        try:
            tango.Except.throw_exception(
                "Test_Reason", "a description", "PushChangeEventEx"
            )
        except DevFailed as ex:
            getattr(self, push_event)("scalar", ex)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventNoValue(self: SimpleDevice, event_type: str) -> None:
        """Push an event with no data the scalar attribute.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        # We can only omit `value` for"state" and "status" so this should raise
        # an exception
        getattr(self, push_event)("scalar")

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventDimx(self: SimpleDevice, event_type: str) -> None:
        """Push an event to the spectrum attribute with `dim_x` set.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        self._spectrum = [x + 1 for x in self._spectrum]
        getattr(self, push_event)("spectrum", self._spectrum, 2)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventDimy(self: SimpleDevice, event_type: str) -> None:
        """Push an event to the image attribute with `dim_y` set.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        image = [1, 1, 1, 1, 1, 1]
        getattr(self, push_event)("image", image, 3, 2)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventQuality(self: SimpleDevice, event_type: str) -> None:
        """Push an event to the scalar attribute with a quality.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        self._scalar += 1
        getattr(self, push_event)("scalar", self._scalar, 0.0, AttrQuality.ATTR_INVALID)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventEncoded(self: SimpleDevice, event_type: str) -> None:
        """Push an event to the encoded attribute.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        val = int.from_bytes(self._encoded[1], byteorder="little") + 1
        self._encoded = ("uint8_le", val.to_bytes(2, byteorder="little"))
        getattr(self, push_event)("encoded", self._encoded[0], self._encoded[1])

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventDimxQuality(self: SimpleDevice, event_type: str) -> None:
        """Push an event to the spectrum attribute with a `dim_x` and quality.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        self._spectrum = [x + 1 for x in self._spectrum]
        getattr(self, push_event)(
            "spectrum", self._spectrum, 0.0, AttrQuality.ATTR_INVALID, 2
        )

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventDimyQuality(self: SimpleDevice, event_type: str) -> None:
        """Push an event to the spectrum attribute with a `dim_y` and quality.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        image = [1, 1, 1, 1, 1, 1]
        getattr(self, push_event)("image", image, 0.0, AttrQuality.ATTR_INVALID, 3, 2)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=None
    )
    def PushChangeEventEncodedQuality(self: SimpleDevice, event_type: str) -> None:
        """Push an event to the encoded attribute.

        :param event_type: which event type to push, either "archive" or "change"
        """
        push_event = "push_" + event_type + "_event"

        val = int.from_bytes(self._encoded[1], byteorder="little") + 1
        self._encoded = ("uint8_le", val.to_bytes(2, byteorder="little"))
        getattr(self, push_event)(
            "encoded", self._encoded[0], self._encoded[1], 0.0, AttrQuality.ATTR_INVALID
        )


@pytest.fixture(scope="module")
def device_test_config() -> dict[str, Any]:
    """
    Specify device configuration for testing push_change_event.

    :return: specification of how the device under test should be
        configured
    """
    return {"device": SimpleDevice}


@pytest.fixture(scope="module", name="change_event_callbacks")
def make_change_event_callbacks() -> MockTangoEventCallbackGroup:
    """
    Return a dictionary of Tango device change event callbacks.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "scalar",
        "state",
        "spectrum",
        "image",
        "encoded",
        assert_no_error=False,
    )


def subscribe_to_event_type(
    dut: tango.DeviceProxy,
    callbacks: MockTangoEventCallbackGroup,
    attr: str,
    event_type: str,
) -> None:
    """Subscribe to an event of a particular type.

    :param dut: a proxy to the device under test
    :param callbacks: dictionary of mock change event
        callbacks with asynchrony support
    :param attr: attribute to subscript to with PushChangeEvent command
    :param event_type: which event type to push, either "archive" or "change"
    """
    if event_type == "change":
        ev = tango.EventType.CHANGE_EVENT
    else:
        assert event_type == "archive"
        ev = tango.EventType.ARCHIVE_EVENT

    dut.subscribe_event(attr, ev, callbacks[attr])


class TestPushEventBasic:
    """Basic SKABaseDevice.push_<X>_event tests."""

    @pytest.mark.parametrize(
        "attr,event_type",
        [
            ("scalar", "change"),
            ("spectrum", "change"),
            ("image", "change"),
            ("state", "change"),
            ("scalar", "archive"),
            ("spectrum", "archive"),
            ("image", "archive"),
            ("state", "archive"),
        ],
    )
    def test_push_event(
        self: TestPushEventBasic,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        attr: str,
        event_type: str,
    ) -> None:
        """Test push_<x>_event.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param attr: attribute to test with PushChangeEvent command
        :param event_type: which event type to push, either "archive" or "change"
        """
        initial_values = {
            "scalar": 0,
            "spectrum": [0, 0, 0],
            "image": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            "state": DevState.DISABLE,
        }

        final_values = {
            "scalar": 1,
            "spectrum": [1, 1, 1],
            "image": [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
            "state": DevState.DISABLE,
        }

        subscribe_to_event_type(
            device_under_test, change_event_callbacks, attr, event_type
        )
        change_event_callbacks[attr].assert_change_event(initial_values[attr])
        device_under_test.PushChangeEvent((attr, event_type))
        change_event_callbacks[attr].assert_change_event(final_values[attr])

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_except(
        self: TestPushEventBasic,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that an exception can be push with push_<x>_event.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "scalar", event_type
        )

        change_event_callbacks["scalar"].assert_change_event(0)
        device_under_test.PushChangeEventExcept(event_type)
        change_event_callbacks["scalar"].assert_against_call(event_error=True)

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_no_value(
        self: TestPushEventBasic,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that push_<x>_event cannot be called without a value argument.

        An absent value argument is when attr is one of the built-in
        "state" or "status" attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "scalar", event_type
        )

        change_event_callbacks["scalar"].assert_change_event(0)
        with pytest.raises(DevFailed):
            device_under_test.PushChangeEventNoValue(event_type)


class TestPushEventAdvanced:
    """Advanced SKABaseDevice.push_<x>_event tests."""

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_dimx(
        self: TestPushEventAdvanced,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that push_<x>_event can be called with dim_x set.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "spectrum", event_type
        )
        change_event_callbacks["spectrum"].assert_change_event([0, 0, 0])
        device_under_test.PushChangeEventDimx(event_type)
        change_event_callbacks["spectrum"].assert_change_event([1, 1])

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_dimy(
        self: TestPushEventAdvanced,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that push_<x>_event can be called with dim_y set.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "image", event_type
        )
        change_event_callbacks["image"].assert_change_event(
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        )
        device_under_test.PushChangeEventDimy(event_type)
        change_event_callbacks["image"].assert_change_event([[1, 1, 1], [1, 1, 1]])

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_encoded(
        self: TestPushEventAdvanced,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that push_<x>_event can be called with encoded data.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "encoded", event_type
        )
        change_event_callbacks["encoded"].assert_change_event(("uint8_le", b"\x00\x00"))
        device_under_test.PushChangeEventEncoded(event_type)
        change_event_callbacks["encoded"].assert_change_event(("uint8_le", b"\x01\x00"))

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_quality(
        self: TestPushEventAdvanced,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that push_<x>_event can be called with a quality provided.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "scalar", event_type
        )
        change_event_callbacks["scalar"].assert_change_event(0)
        device_under_test.PushChangeEventQuality(event_type)
        change_event_callbacks["scalar"].assert_against_call(
            attribute_value=None, attribute_quality=AttrQuality.ATTR_INVALID
        )

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_dimx_quality(
        self: TestPushEventAdvanced,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that push_<x>_event can set quality with the `dim_x` argument.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "spectrum", event_type
        )
        change_event_callbacks["spectrum"].assert_change_event([0, 0, 0])
        device_under_test.PushChangeEventDimxQuality(event_type)
        change_event_callbacks["spectrum"].assert_against_call(
            attribute_value=None, attribute_quality=AttrQuality.ATTR_INVALID
        )

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_dimy_quality(
        self: TestPushEventAdvanced,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that push_<x>_event can set quality with the `dim_y` argument.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "image", event_type
        )
        change_event_callbacks["image"].assert_change_event(
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        )
        device_under_test.PushChangeEventDimyQuality(event_type)
        change_event_callbacks["image"].assert_against_call(
            attribute_value=None, attribute_quality=AttrQuality.ATTR_INVALID
        )

    @pytest.mark.parametrize(
        "event_type",
        ["change", "archive"],
    )
    def test_push_event_encoded_quality(
        self: TestPushEventAdvanced,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        event_type: str,
    ) -> None:
        """Test that push_<x>_event can set quality with encoded data.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param event_type: which event type to push, either "archive" or "change"
        """
        subscribe_to_event_type(
            device_under_test, change_event_callbacks, "encoded", event_type
        )
        change_event_callbacks["encoded"].assert_change_event(("uint8_le", b"\x00\x00"))
        device_under_test.PushChangeEventEncodedQuality(event_type)
        change_event_callbacks["encoded"].assert_against_call(
            attribute_value=None, attribute_quality=AttrQuality.ATTR_INVALID
        )
