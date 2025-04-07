"""Tests for SignalBus class."""

from threading import Event
from typing import Any, Optional

from ska_tango_base.software_bus import NoValue, ObserverProtocol, SignalBus


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
