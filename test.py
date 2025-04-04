"""A test."""

from __future__ import annotations

from typing import Any, Callable, Protocol

from tango.server import Device, attribute, command, run

from ska_tango_base._software_bus import (
    BusMixin,
    SharingObserver,
    Signal,
    listen_to_signal,
)
from ska_tango_base.meta import SkaDeviceMeta
from ska_tango_base.mixin import SkaMixin

if __name__ == "__main__":  # noqa: C901

    # pylint: disable=missing-function-docstring
    # pylint: disable=disallowed-name,invalid-name

    class _Widget(SharingObserver):
        foo = Signal[str](default_value="bar")

    class _MyProtocol(Protocol):
        init_device: Callable[[], None]

        def set_change_event(self, name: str, impl: bool, detect: bool) -> None:
            """Do something."""

        def push_change_event(self, name: str, value: Any) -> None:
            """Do something."""

    class _MyMixin(SharingObserver):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.widget = _Widget()
            super().__init__(*args, **kwargs)

        def init_device(self: _MyProtocol) -> None:
            super().init_device()
            self.set_change_event("myAttr", True, True)

        @attribute  # type: ignore[misc]
        def myAttr(self) -> str:
            return self.widget.foo

        @listen_to_signal("widget.foo")
        def update_my_attr(self: _MyProtocol, old_value: str, new_value: str) -> None:
            _ = old_value
            self.push_change_event("myAttr", new_value)

    class _CommandTracker(SharingObserver):
        lrc_event = Signal[int]()

        def _observe_bus(self) -> None:
            super()._observe_bus()
            self.lrc_event = 0

        def task_callback(self) -> None:
            self.lrc_event = 1

    class _LrcMixinProtocol(Protocol):
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

    class _LrcMixin(BusMixin, SkaMixin):
        lrcEvent = attribute(abs_change=1)  # noqa: N815

        def read_lrcEvent(self: _LrcMixinProtocol) -> int:
            return self.command_tracker.lrc_event

        @listen_to_signal("command_tracker.lrc_event")
        def update_lrc_event(
            self: _LrcMixinProtocol, old_value: int, new_value: int
        ) -> None:
            _ = old_value
            self.push_change_event("lrcEvent", new_value)

        def init_device(self: _LrcMixinProtocol) -> None:
            super().init_device()
            self.command_tracker = _CommandTracker()

            self.set_change_event("lrcEvent", True, True)

    # pylint: disable=too-many-ancestors
    class _MyDevice(
        _MyMixin,
        _LrcMixin,
        Device,  # type: ignore[misc]
        metaclass=SkaDeviceMeta,
    ):
        @command  # type: ignore[misc]
        def DoSomething(self) -> None:
            self.command_tracker.task_callback()

    run((_MyDevice,))
