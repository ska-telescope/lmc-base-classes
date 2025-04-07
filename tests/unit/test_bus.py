"""Tests for SignalBus class."""

from threading import Event
from typing import Any, Callable, Optional, Protocol

import pytest
import tango
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango.server import Device, attribute, command
from tango.test_context import DeviceTestContext

from ska_tango_base.meta import SkaDeviceMeta
from ska_tango_base.mixin import SkaMixin
from ska_tango_base.software_bus import (
    BusOwnerMixin,
    NoValue,
    Observer,
    ObserverProtocol,
    SharingObserver,
    Signal,
    SignalBus,
    _BusOwnerMixedIn,
    listen_to_signal,
)


class _TestObsProtocol(ObserverProtocol):  # pylint: disable=too-few-public-methods
    def __init__(self) -> None:
        self.signal: Optional[str] = None
        self.old_value: Optional[Any] = None
        self.new_value: Optional[Any] = None
        self.event = Event()

    def notify_emission(self, signal: str, old_value: Any, new_value: Any) -> None:
        self.signal = signal
        self.old_value = old_value
        self.new_value = new_value
        self.event.set()


def test_emission() -> None:
    """Test that we can emit a value."""
    bus = SignalBus()
    obs = _TestObsProtocol()
    bus.register_observer(obs)
    bus.start_thread()

    try:
        bus.emit("foo", "old")

        assert bus.get_last_value("foo") == "old"

        obs.event.wait()

        assert obs.signal == "foo"
        assert obs.old_value is NoValue
        assert obs.new_value == "old"

        obs.event.clear()

        bus.emit("foo", "new")

        assert bus.get_last_value("foo") == "new"

        obs.event.wait()

        assert obs.signal == "foo"
        assert obs.old_value == "old"
        assert obs.new_value == "new"
    finally:
        bus.shutdown_thread()


class _TestObserver(Observer):
    def __init__(self) -> None:
        super().__init__()
        self.old_value: Optional[Any] = None
        self.new_value: Optional[Any] = None
        self.event = Event()

    @listen_to_signal("foo")
    def on_foo(self, old_value: Any, new_value: Any) -> None:
        """Record old_value and new_value."""
        self.old_value = old_value
        self.new_value = new_value
        self.event.set()


def test_listener() -> None:
    """Test using listen_to_signal with a shared bus."""
    listener = _TestObserver()
    bus = SignalBus()
    bus.register_observer(listener)
    bus.start_thread()

    try:
        bus.emit("foo", "old")
        listener.event.wait()

        assert listener.old_value is NoValue
        assert listener.new_value == "old"

        listener.event.clear()

        bus.emit("foo", "new")

        assert bus.get_last_value("foo") == "new"

        listener.event.wait()

        assert listener.old_value == "old"
        assert listener.new_value == "new"

    finally:
        bus.shutdown_thread()


class _TestSharingObserver(_TestObserver, SharingObserver):
    pass


class _TestParent(_TestSharingObserver):
    def __init__(self) -> None:
        super().__init__()
        self.sub_obj = _TestSharingObserver()


def test_sharing() -> None:
    """Test that buses are shared."""
    parent = _TestParent()
    with pytest.raises(RuntimeError, match="The bus has not been shared!"):
        parent.shared_bus.emit("foo", "bar")

    with pytest.raises(RuntimeError, match="The bus has not been shared!"):
        parent.sub_obj.shared_bus.emit("foo", "bar")

    bus = SignalBus()
    parent.shared_bus = bus
    assert parent.shared_bus is parent.sub_obj.shared_bus
    bus.start_thread()

    try:
        bus.emit("foo", "bar")
        parent.event.wait()

        assert parent.old_value is NoValue
        assert parent.new_value == "bar"

        bus.emit("sub_obj.foo", "bar")
        parent.sub_obj.event.wait()

        assert parent.sub_obj.old_value is NoValue
        assert parent.sub_obj.new_value == "bar"

    finally:
        parent.shared_bus.shutdown_thread()


def test_signal() -> None:
    """Test the Signal descriptor class."""
    # pylint: disable=disallowed-name

    class _Emitter(SharingObserver):
        foo = Signal[str]()

    obs = _TestObsProtocol()
    emitter = _Emitter()
    emitter.shared_bus = SignalBus()
    emitter.shared_bus.register_observer(obs)
    emitter.shared_bus.start_thread()

    try:
        emitter.foo = "old"
        obs.event.wait()

        assert obs.signal == "foo"
        assert obs.old_value is NoValue
        assert obs.new_value == "old"

        obs.event.clear()

        emitter.foo = "new"
        obs.event.wait()

        assert obs.signal == "foo"
        assert obs.old_value == "old"
        assert obs.new_value == "new"
    finally:
        emitter.shared_bus.shutdown_thread()


class _CommandTracker(SharingObserver):
    lrc_event = Signal[int]()

    def on_new_shared_bus(self) -> None:
        super().on_new_shared_bus()
        self.lrc_event = 0

    def task_callback(self) -> None:
        """Push an lrcEvent."""
        self.lrc_event = 1


class _LrcMixedIn(_BusOwnerMixedIn, Protocol):
    init_device: Callable[[], None]

    command_tracker: _CommandTracker

    def set_change_event(self, name: str, impl: bool, detect: bool = True) -> None:
        """Mark that this device manual pushes change events for an attribute."""

    def set_archive_event(self, name: str, impl: bool, detect: bool = True) -> None:
        """Mark that this device manual pushes archive events for an attribute."""

    def push_change_event(self, name: str, value: Any) -> None:
        """Push a change event for an attribute."""

    def push_archive_event(self, name: str, value: Any) -> None:
        """Push a change event for an attribute."""


class _LrcMixin(BusOwnerMixin, SkaMixin):
    lrcEvent = attribute(abs_change=1)  # noqa: N815

    # pylint: disable=invalid-name
    def read_lrcEvent(self: _LrcMixedIn) -> int:
        """Read the attribute."""
        return self.command_tracker.lrc_event

    @listen_to_signal("command_tracker.lrc_event")
    def update_lrc_event(self: _LrcMixedIn, old_value: int, new_value: int) -> None:
        """Update the attribute."""
        _ = old_value
        self.push_change_event("lrcEvent", new_value)

    def init_bus_sharers(self: _LrcMixedIn) -> None:
        """Initialise command tracker."""
        super().init_bus_sharers()

        self.command_tracker = _CommandTracker()

    def init_device(self: _LrcMixedIn) -> None:
        """Initialise device."""
        super().init_device()

        self.set_change_event("lrcEvent", True, True)


class _MyDevice(  # pylint: disable=too-many-ancestors
    _LrcMixin,
    Device,  # type: ignore[misc]
    metaclass=SkaDeviceMeta,
):
    @command  # type: ignore[misc]
    def do_something(self) -> None:
        """Call task callback."""
        self.command_tracker.task_callback()


def test_bus_owner_mixin() -> None:
    """Test for BusOwnerMixin."""
    callbacks = MockTangoEventCallbackGroup("lrcEvent")
    with DeviceTestContext(_MyDevice) as dp:
        dp.subscribe_event(
            "lrcEvent", tango.EventType.CHANGE_EVENT, callbacks["lrcEvent"]
        )
        callbacks.assert_change_event("lrcEvent", 0)
        dp.do_something()
        callbacks.assert_change_event("lrcEvent", 1)
        dp.init()
        callbacks.assert_change_event("lrcEvent", 0)
        dp.do_something()
        callbacks.assert_change_event("lrcEvent", 1)
