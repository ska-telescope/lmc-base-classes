"""Internal software bus implementation."""

from __future__ import annotations

import functools
import inspect
import logging
from collections import defaultdict
from queue import Queue
from threading import Lock, Thread
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Protocol,
    TypeAlias,
    TypeVar,
    cast,
    overload,
)
from weakref import WeakSet

from tango import EnsureOmniThread

module_logger = logging.getLogger(__name__)


class Observer(Protocol):  # pylint: disable=too-few-public-methods
    """Notified whenever a value is emitted for a signal.

    The Observer must be registered with the bus first with
    :py:func:`BusProtocol.register_observer`.
    """

    def notify_emission(self, signal: str, old_value: Any, new_value: Any) -> None:
        """Notify the observer of an emission asynchronously."""


class BusProtocol(Protocol):
    """Protocol for a bus-like object."""

    @property
    def logger(self) -> logging.Logger:
        """Return the logger for the bus."""

    def get_last_value(self, signal: str) -> Any:
        """Return last value emitted for signal."""

    def register_observer(self, signal: str, observer: Observer) -> None:
        """Register the observer to be notified is emitted for the signal."""

    def emit(self, signal: str, value: Any) -> None:
        """Emit a new value for the signal."""


class HasSharedBusProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """An object with access to an InternalBus, for type checking of this file."""

    shared_bus: BusProtocol
    _signal_prefix: str


NoValue = object()
"""Used to signal that there is no value stored.

Required as None is a valid value.
"""


class ThreadedBus:
    """A software bus that propagates signals to slots in a separate thread.

    The bus can :py:func:`emit()` values for a given signal.  In order to
    get notified when a value is emitted for a signal, a :py:class:`Observer`
    can be registered with :py:func:`register_observer()`.

    Each signal is identified by a user-provided string.  The most recently
    emitted value for a signal is stored by the ``ThreadedBus`` and can be
    retrieved with `get_last_value()`.

    When a value is emitted for a given signal, the last_value is immediately
    updated and an "emission" is added to an internal queue.  This queue is
    serviced by a separate background thread, which must be started with
    `start_thread()`.

    Once `start_thread()` has been called, you can no longer call
    `register_observer()` until the thread has been shutdown again with
    `shutdown_thread()`.

    When background thread receives an emission from the internal queue it
    will notify all the :py:class:`Observer`'s registered for the signal in
    an unspecified order.  For a given signal, emissions are processed in
    the order they are received, but there is no guarantee on the order
    that emissions for different signals are processed.

    The internal queue has a maximum size and attempting to `emit()` while the
    queue is full will raise a :py:class:`queue.Full` exception. The expectation
    is that observers should return quickly compared to the rate that signals are
    emitted, so the internal queue filling up should be considered a misuse of
    ``ThreadedBus``. The limit is in place so that the failure mode is more
    explicit than some queue growing and eating up all the memory on the system.
    """

    def __init__(
        self,
        logger: logging.Logger | None = None,
        max_queue_size: int = 256,
    ) -> None:
        """Initialise the object.

        :param logger: to use to for logging
        :param max_queue_size: maximum number of emissions that can be stored
                               in the internal queue
        """
        self.logger = module_logger if logger is None else logger

        self._observers: dict[str, WeakSet[Observer]] = {}

        # Held during emit to atomically update last_values and add to
        # _emission_queue
        self._value_lock = Lock()
        self._last_values: dict[str, Any] = {}

        self._emission_queue = Queue[tuple[str, Any, Any] | None](
            maxsize=max_queue_size
        )
        self._thread = Thread(target=self._run_bus_thread)

    def get_last_value(self, signal: str) -> Any:
        """Return the last value emitted for a signal.

        :param signal: name of the signal
        :raises KeyError: if no value has been emitted for the signal
        :returns: last value emitted
        """
        # We don't need to synchronise read access to the `_last_values` as
        # the GIL will ensure that the python dictionary is always in a coherent
        # state.  If some other thread is in the middle of calling `emit()` we
        # either get the value before the emission or the value after, however,
        # both these are valid answers if this read wasn't synchronised with the
        # `emit()`.
        return self._last_values[signal]

    def register_observer(self, signal: str, observer: Observer) -> None:
        """Register the observer to be notified is emitted for the signal.

        :param signal: name of the signal
        :param slot: callback to invoke

        :raises RuntimeError: if the background thread has already been started
        """
        if self._thread.is_alive():
            raise RuntimeError("Cannot connect new slots while the thread is running.")

        # We don't want to create circular references with this bus, so we only
        # ever hold on to observers with weak references.  If the observer goes
        # away, we don't care and will just stop notifying it.
        observers = self._observers.setdefault(signal, WeakSet())
        observers.add(observer)

    def emit(self, signal: str, value: Any) -> None:
        """Emit a new value for the signal.

        When this function returns the last value will be updated with ``value``.  That
        is, provided no other thread is emitting values for this signal, the following
        assert will never fire for any ``value`` and ``signal``:

        .. code:: python

            bus.emit(signal, value)
            assert bus.get_last_value(signal) == value

        Any observes registered for this signal are notified asynchronously in by the
        background thread which is started by :py:func:`start_thread()`.

        :param signal: name of the signal
        :param value: new value to emit
        """
        with self._value_lock:
            try:
                old_value = self.get_last_value(signal)
            except KeyError:
                old_value = NoValue
            self._emission_queue.put((signal, old_value, value), block=False)
            self._last_values[signal] = value

    def start_thread(self) -> None:
        """Start the background thread to notify observers about emissions."""
        self._thread.start()

    def shutdown_thread(self) -> None:
        """Shutdown the background thread.

        This waits for the thread to finish processing remaining emissions.
        """
        self._emission_queue.put(None)
        self._thread.join()

    def __del__(self) -> None:
        """Delete the object."""
        self.shutdown_thread()

    def _process_emission(self, signal: str, old_value: Any, new_value: Any) -> None:
        for obs in self._observers[signal]:
            try:
                obs.notify_emission(signal, old_value, new_value)
            except Exception:  # pylint: disable=broad-exception-caught
                self.logger.exception(
                    (
                        "Observer %r threw an unexpected exception while "
                        + "processing emission %r. Continuing with remaining observers."
                    ),
                    obs,
                    (signal, old_value, new_value),
                )

    def _run_bus_thread(self) -> None:
        with EnsureOmniThread():
            while True:
                emission = self._emission_queue.get()
                if emission is None:
                    break
                self._process_emission(*emission)


class SharingObserver:
    """An observer that shares its bus with sub-objects."""

    ListenerMethod: TypeAlias = Callable[[Any, Any, Any], None]

    _shared_bus: BusProtocol | None
    _signal_prefix: str
    __listener_methods: ClassVar[dict[str, list[ListenerMethod]]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise the device."""
        self._shared_bus = None
        self._signal_prefix = ""
        super().__init__(*args, **kwargs)

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Gather all the listener methods on subclasses."""
        super().__init_subclass__(**kwargs)
        listeners = defaultdict[str, list[SharingObserver.ListenerMethod]](lambda: [])
        for key in dir(cls):
            obj = getattr(cls, key)
            if inspect.isroutine(obj) and hasattr(obj, "__listen_to_signal__"):
                listeners[obj.__listen_to_signal__].append(
                    cast(SharingObserver.ListenerMethod, obj)
                )
        cls.__listener_methods = dict(listeners)

    @property
    def shared_bus(self) -> BusProtocol:
        """The shared bus used by this SharingObserver."""
        if self._shared_bus is None:
            raise RuntimeError("The bus has not been shared!")

        return self._shared_bus

    @shared_bus.setter
    def shared_bus(self, bus: BusProtocol) -> None:
        self._shared_bus = bus

        for key, obj in vars(self).items():
            if isinstance(obj, SharingObserver):
                # pylint: disable=protected-access
                obj._signal_prefix = f"{self._signal_prefix}{key}."
                obj.shared_bus = self._shared_bus

        self._observe_bus()

    def _observe_bus(self) -> None:
        """Register self with the bus for all signals we are listening to."""
        for signal_suffix in self.__listener_methods.keys():
            # TODO: Check if this signal exists and raise an error if not
            signal = f"{self._signal_prefix}{signal_suffix}"
            self.shared_bus.register_observer(signal, self)

    def notify_emission(self, signal: str, old_value: Any, new_value: Any) -> None:
        """Notify the observer of an emission asynchronously.

        For SharingObserver, this calls all the listener methods for the given signal.
        """
        signal_suffix = signal.removeprefix(self._signal_prefix)
        for unbound_method in self.__listener_methods[signal_suffix]:
            try:
                unbound_method(self, old_value, new_value)
            except Exception:  # pylint: disable=broad-exception-caught
                self.shared_bus.logger.exception(
                    (
                        "Listener method %r threw an unexpected exception for %r. "
                        + "Continuing with remaining listeners."
                    ),
                    unbound_method,
                    (old_value, new_value),
                )


_ListenerDecorator: TypeAlias = Callable[
    [SharingObserver.ListenerMethod], SharingObserver.ListenerMethod
]


@overload
def listen_to_signal(signal: str) -> _ListenerDecorator:
    """Return a decorator."""


@overload
def listen_to_signal(
    signal: str, listener: SharingObserver.ListenerMethod
) -> SharingObserver.ListenerMethod:
    """Decorate the listener."""


def listen_to_signal(
    signal: str, listener: SharingObserver.ListenerMethod | None = None
) -> _ListenerDecorator | SharingObserver.ListenerMethod:
    """Mark a method as listening to a signal.

    This function will be called asynchronously whenever a value is emitted
    for the signal.
    """
    if listener is None:
        return cast(_ListenerDecorator, functools.partial(listen_to_signal, signal))

    listener.__listen_to_signal__ = signal  # type: ignore[attr-defined]
    return listener


T = TypeVar("T")


class Signal(Generic[T]):
    """Descriptor to provide access to signal on a bus."""

    def __init__(
        self: Signal[T], /, name: str | None = None, default_value: T | None = None
    ) -> None:
        """Initialise the object."""
        self._basename = name
        self.default_value = default_value

    def __set_name__(self: Signal[T], owner: Any, name: str) -> None:
        """Set the name of the descriptor."""
        if self._basename is None:
            self._basename = name

    def _get_name(self, obj: HasSharedBusProtocol) -> str:
        basename = cast(str, self._basename)
        # pylint: disable=protected-access
        return f"{obj._signal_prefix}{basename}"

    @overload
    def __get__(self: Signal[T], obj: None, objtype: None) -> Signal[T]:
        """Return self."""

    @overload
    def __get__(self: Signal[T], obj: HasSharedBusProtocol, objtype: type) -> T:
        """Return stored value."""

    def __get__(
        self: Signal[T],
        obj: HasSharedBusProtocol | None,
        objtype: type | None = None,
    ) -> T | Signal[T]:
        """Return stored value."""
        if obj is None:
            return self

        name = self._get_name(obj)
        value = obj.shared_bus.get_last_value(name)

        return cast(T, value)

    def __set__(self: Signal[T], obj: HasSharedBusProtocol, value: T) -> None:
        """Set stored value and push events."""
        name = self._get_name(obj)
        obj.shared_bus.emit(name, value)


class _BusMixinProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for a Tango device that also inherits from BusMixin."""

    shared_bus: ThreadedBus
    init_device: Callable[[Any], None]
    delete_device: Callable[[], None]


class BusOwnerMixin(SharingObserver):
    """A base class for mix-ins to use the shared bus.

    This class is not intended to be inherited from directly by users.  Instead, it
    is intended to be used by mix-ins to utilities the bus.

    All SharingObserver sub-objects must be initialised either before
    :py:func:`BusOwnerMixin.__init__()` is called or during ``init_device()``.
    """

    shared_bus: ThreadedBus

    def __init__(self: _BusMixinProtocol, *args: Any, **kwargs: Any) -> None:
        """Initialize the object."""
        # `init_device` will be called during `super().__init__`, and
        # after `init_device` is called all the SharingObserver sub-objects
        # should have been initialised. We only want setup the bus once these
        # sub-objects have been initialised.
        #
        # We patch `init_device` as we want the bus to be re-created with
        # every call to the `Init` command.
        old_init_device = type(self).init_device

        @functools.wraps(old_init_device)
        def init_device(self: Any) -> None:
            old_init_device(self)
            self.shared_bus = ThreadedBus()
            self.shared_bus.start_thread()

        type(self).init_device = init_device

        super().__init__(*args, **kwargs)

    def delete_device(self: _BusMixinProtocol) -> None:
        """Shutdown the bus background thread as we delete the device."""
        super().delete_device()
        self.shared_bus.shutdown_thread()
