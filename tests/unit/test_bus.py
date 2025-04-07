"""Tests for SignalBus class."""

from threading import Event
from typing import Any, Optional

import pytest

from ska_tango_base.software_bus import (
    NoValue,
    Observer,
    ObserverProtocol,
    SharingObserver,
    SignalBus,
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
