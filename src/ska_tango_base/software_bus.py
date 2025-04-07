"""Internal software bus implementation."""

from __future__ import annotations

import functools
import inspect
import logging
import threading
import time
from collections import defaultdict
from copy import deepcopy
from queue import Full, Queue
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


# We are using a protocol here, rather than a function signature, to make it easier to
# avoid circular references.  If we just used a single function as an observer,
# then users would have to be careful to make sure closures only hold weak
# references to objects holding a reference to the bus.  By making the observer
# a class, we can manage this problem in the SignalBus ourselves.
class ObserverProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """An object which observers signals being emitted on a bus.

    The observer must be registered with the bus first with
    :py:func:`BusProtocol.register_observer`.
    """

    def notify_emission(self, signal: str, old_value: Any, new_value: Any) -> None:
        """Notify the observer of an emission asynchronously."""


NoValue = object()
"""Used to signal that there is no value stored.

Required as None is a valid value.
"""


class SignalBus:
    """A software bus that notifies observers listening to signals.

    The bus can :py:func:`emit()` values for a given signal.  In order to
    get notified when a value is emitted for any signals, a :py:class:`Observer`
    can be registered with :py:func:`register_observer()`.  Observers are stored
    in a class :py:class:`weakref.WeakSet` and so must be kept alive by the
    caller.

    Each signal is identified by a user-provided string.  The most recently
    emitted value for a signal is stored by the ``SignalBus`` and can be
    retrieved with :py:meth:`get_last_value()`.

    When a value is emitted for a given signal, the last value is immediately
    updated and an "emission" is added to an internal queue.  This queue is
    serviced by a separate background thread, which must be started with
    `start_thread()`.

    Once :py:func:`start_thread()` has been called, you can no longer call
    :py:func:`register_observer()` until the thread has been shutdown
    again with :py:func:`shutdown_thread()`.

    When background thread receives an emission from the internal queue it
    will notify all the registered :py:class:`Observer` objects that still exist by
    calling :py:func:`Observer.notify_emission`. This notification occurs in an
    unspecified order. Emissions are processed in the order they are received, however,
    additional emissions generated during a call :py:func:`Observer.notify_emission` are
    processed immediately.

    The internal queue has a maximum size and attempting to `emit()` while the
    queue is full will log a warning message before blocking until the queue has room.
    The expectation is that observers should return quickly compared to the rate
    that signals are emitted, so the internal queue filling up should be considered
    a misuse of ``SignalBus``. The limit is in place so that the failure mode is more
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
        self._logger = module_logger if logger is None else logger

        # We don't want to create circular references with this bus, so we only
        # ever hold on to observers with weak references.  If the observer goes
        # away, we don't care and will just stop notifying it.
        self._observers = WeakSet[ObserverProtocol]()

        # Held during emit to atomically update last_values and add to
        # _emission_queue
        self._value_lock = Lock()
        self._last_values: dict[str, Any] = {}

        self._last_emission_queue_full_log = 0.0
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

    def register_observer(self, observer: ObserverProtocol) -> None:
        """Register the observer to be notified is emitted for the signal.

        If the observer is destroyed it will automatically be unregistered.

        :param signal: name of the signal
        :param slot: callback to invoke

        :raises RuntimeError: if the background thread has already been started
        """
        if self._thread.is_alive():
            raise RuntimeError("Cannot connect new slots while the thread is running.")

        self._observers.add(observer)

    _LOG_QUEUE_FULL_PERIOD = 10.0

    def emit(self, signal: str, value: Any) -> None:
        """Emit a new value for the signal.

        The bus will hold a deep copy of value after this function returns.

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
        value = deepcopy(value)
        with self._value_lock:
            old_value = self._last_values.get(signal, NoValue)
            self._last_values[signal] = value

        # We have elected for the failure mode in the case of too many
        # emissions to be the bus slows down.  That is, we wait for
        # there to be room in the queue again.  This means we cannot
        # add things to the queue from the background thread, otherwise
        # we could potentially have a deadlock, as the background thread
        # is the only thing pulling things from the queue.
        #
        # This is fine in terms of having a consistent ordering for the
        # processing of emissions as, from the perspective of
        # a sequence of `emit()` calls from the other thread, it is as
        # if the background thread grabs the GIL and immediately processes
        # the emission after each call to `emit()`.  This is a valid execution
        # order for two threads which aren't synchronised and so should not
        # be surprising for users.
        if threading.current_thread() == self._thread:
            self._process_emission(signal, old_value, value)
        else:
            try:
                self._emission_queue.put((signal, old_value, value), block=False)
            except Full:
                now = time.time()
                if (
                    now - self._last_emission_queue_full_log
                    > self._LOG_QUEUE_FULL_PERIOD
                ):
                    self._logger.warning(
                        "Observers cannot keep up with rate signals are being emitted. "
                        "Siganl bus performance is degraded as the "
                        "internal queue is full. Blocking until there is room in "
                        "the queue."
                    )
                    self._last_emission_queue_full_log = now

                self._emission_queue.put((signal, old_value, value))

    def start_thread(self) -> None:
        """Start the background thread to notify observers about emissions."""
        self._thread.start()

    def shutdown_thread(self) -> None:
        """Shutdown the background thread.

        This waits for the thread to finish processing remaining emissions.
        """
        # TODO: Should we wait for processing to finish, or flush the queue
        # first?
        self._emission_queue.put(None)
        self._thread.join()

    def __del__(self) -> None:
        """Delete the object."""
        if self._thread.is_alive():
            self.shutdown_thread()

    def _process_emission(self, signal: str, old_value: Any, new_value: Any) -> None:
        for obs in self._observers:
            try:
                obs.notify_emission(signal, old_value, new_value)
            except Exception:  # pylint: disable=broad-exception-caught
                self._logger.exception(
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


class BusProtocol(Protocol):
    """A bus which emits signals and stores the most recently emitted value."""

    def get_last_value(self, signal: str) -> Any:
        """Return last value emitted for signal."""

    def register_observer(self, observer: ObserverProtocol) -> None:
        """Register the observer to be notified is emitted for any signal."""

    def emit(self, signal: str, value: Any) -> None:
        """Emit a new value for the signal."""


ListenerMethod: TypeAlias = Callable[[Any, Any, Any], None]
"""Method on an :py:class:`Observer` which can receive a signal."""


class Observer:
    """An observer that handles different signals with different methods.

    Sub-classes can be mark method as a :py:const:`ListenerMethod` using the
    :py:func:`listen_to_signal()` decorator.  :py:const:`ListenerMethod` will
    only be called for signals they are registered to.

    A subclass can override :py:attr:`observer_prefix` to provide a dynamic prefix
    to be applied to the signals passed to :py:func:`listen_to_signal`.
    """

    __listener_methods: ClassVar[dict[str, list[ListenerMethod]]] = {}

    def __init__(
        self, *args: Any, logger: logging.Logger | None = None, **kwargs: Any
    ) -> None:
        """Initialise object."""
        super().__init__(*args, **kwargs)
        self._logger = module_logger if logger is None else logger

    @property
    def observer_prefix(self) -> str:
        """Return prefix to for signals when looking up listener methods."""
        return ""

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Gather all the listener methods on subclasses."""
        super().__init_subclass__(**kwargs)
        listeners = defaultdict[str, list[ListenerMethod]](lambda: [])
        for key in dir(cls):
            obj = getattr(cls, key)
            if inspect.isroutine(obj) and hasattr(obj, "__listen_to_signal__"):
                listeners[obj.__listen_to_signal__].append(cast(ListenerMethod, obj))
        cls.__listener_methods = dict(listeners)

    def notify_emission(self, signal: str, old_value: Any, new_value: Any) -> None:
        """Call all the listener methods for the given signal."""
        if not signal.startswith(self.observer_prefix):
            return

        signal = signal.removeprefix(self.observer_prefix)

        for unbound_method in self.__listener_methods.get(signal, []):
            try:
                unbound_method(self, old_value, new_value)
            except Exception:  # pylint: disable=broad-exception-caught
                self._logger.exception(
                    (
                        "Listener method %r threw an unexpected exception for %r. "
                        + "Continuing with remaining listeners."
                    ),
                    unbound_method,
                    (old_value, new_value),
                )


_ListenerDecorator: TypeAlias = Callable[[ListenerMethod], ListenerMethod]


@overload
def listen_to_signal(signal: str) -> _ListenerDecorator:
    """Return a decorator."""


@overload
def listen_to_signal(signal: str, listener: ListenerMethod) -> ListenerMethod:
    """Decorate the listener."""


def listen_to_signal(
    signal: str, listener: ListenerMethod | None = None
) -> _ListenerDecorator | ListenerMethod:
    """Mark a method as listening to a signal.

    This function will be called asynchronously whenever a value is emitted
    for the signal.
    """
    if listener is None:
        return cast(_ListenerDecorator, functools.partial(listen_to_signal, signal))

    listener.__listen_to_signal__ = signal  # type: ignore[attr-defined]
    return listener


class SharingObserver(Observer):
    """An observer that shares its bus with sub-objects.

    When a :py:class:`BusProtocol` is assigned to :py:attr:`shared_bus` this will
    recursively set on all sub-objects which also inherit from
    :py:class:`SharingObserver`.

    Subclasses can be notified when a new `shared_bus` is available by overriding
    :py:meth:`on_new_shared_bus`.

    :py:class:`SharingObserver` updates the :py:attr:`observer_prefix` so that signals
    generated by sub-objects are prefixed with the path to that object.  That is, given
    the following:

    .. code :: python

        class SubObj(SharingObserver):
            @listen_to_signal("bar")
            def on_bar(self, old_value, new_value):
                if old_value == new_value:
                    print("No change")

        class MySharer(SharingObserver):
            def __init__(self):
                self.foo = SubObj()
                self.shared_bus = SignalBus()
                self.shared_bus.start_thread()

        sharer = MySharer

    The ``sharer.foo.on_bar`` listener method will receive values emitted
    on the bus for the signal "foo.bar".
    """

    _shared_bus: BusProtocol | None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise the device."""
        self._shared_bus = None
        self._path_from_root = ""
        super().__init__(*args, **kwargs)

    @property
    def observer_prefix(self) -> str:
        """Return the path from the root ``SharingObserver`` holding the bus."""
        return self._path_from_root

    @property
    def shared_bus(self) -> BusProtocol:
        """The shared bus used by this ``SharingObserver``."""
        if self._shared_bus is None:
            raise RuntimeError("The bus has not been shared!")

        return self._shared_bus

    @shared_bus.setter
    def shared_bus(self, bus: BusProtocol) -> None:
        self._shared_bus = bus

        for key, obj in vars(self).items():
            if isinstance(obj, SharingObserver):
                # pylint: disable=protected-access
                obj._path_from_root = f"{self._path_from_root}{key}."
                obj.shared_bus = self._shared_bus

        self._shared_bus.register_observer(self)
        self.on_new_shared_bus()

    def on_new_shared_bus(self) -> None:
        """Notify that a new bus is available."""


class HasSharedBusProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """An object with access to an shared bus."""

    shared_bus: BusProtocol
    """Bus to emit signals on."""

    _path_from_root: str
    """Path from the root of the bus to this object."""


T = TypeVar("T")


class Signal(Generic[T]):
    """Descriptor to provide access to signal on a shared bus.

    Can only be used on classes which model :py:class:`HasSharedBusProtocol`.

    Whenever a ``Signal`` is set, a signal is emitted with the value provided.

    The relative name of the signal is taken from the name of the ``Signal`` on
    the owner class, and can be overridden by providing ``name`` kwarg to the
    initialiser.

    The relative name is prefixed by the name of the owner object before being
    emitted on the bus.
    """

    def __init__(self: Signal[T], /, name: str | None = None) -> None:
        """Initialise the object."""
        self._basename = name

    def __set_name__(self: Signal[T], owner: Any, name: str) -> None:
        """Set the name of the descriptor."""
        if self._basename is None:
            self._basename = name

    def _get_name(self, obj: HasSharedBusProtocol) -> str:
        basename = cast(str, self._basename)
        # pylint: disable=protected-access
        return f"{obj._path_from_root}{basename}"

    @overload
    def __get__(self: Signal[T], obj: None, objtype: None) -> Signal[T]:
        """Return self."""

    @overload
    def __get__(self: Signal[T], obj: HasSharedBusProtocol, objtype: type) -> T:
        """Return the last emitted value."""

    def __get__(
        self: Signal[T],
        obj: HasSharedBusProtocol | None,
        objtype: type | None = None,
    ) -> T | Signal[T]:
        """Return the last emitted value or self.

        :raises KeyError: If the signal has never been emitted.
        """
        if obj is None:
            return self

        name = self._get_name(obj)
        value = obj.shared_bus.get_last_value(name)

        return cast(T, value)

    def __set__(self: Signal[T], obj: HasSharedBusProtocol, value: T) -> None:
        """Emit the signal."""
        name = self._get_name(obj)
        obj.shared_bus.emit(name, value)


class _BusOwnerMixedIn(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for a Tango device that also inherits from BusMixin."""

    shared_bus: SignalBus
    init_device: Callable[[], None]
    init_bus_sharers: Callable[[], None]
    delete_device: Callable[[], None]


class BusOwnerMixin(SharingObserver):
    """A base class for mix-ins to use the shared bus.

    This class is not intended to be inherited from directly by users.  Instead, it
    is intended to be used by mix-ins to utilities the bus.
    """

    shared_bus: SignalBus

    def init_bus_sharers(self: _BusOwnerMixedIn) -> None:
        """Initialise :py:func:`SharingObserver` objects.

        Sub-classes must override this to initialise their `SharingObserver` objects,
        before the `SignalBus` background thread is started.

        This is called during :py:func:`BusOwnerMixin.init_device()`.
        """

    def init_device(self: _BusOwnerMixedIn) -> None:
        """Initialise the shared bus."""
        super().init_device()
        self.init_bus_sharers()
        try:
            logger = self.logger  # type: ignore[attr-defined]
        except AttributeError:
            logger = None
        self.shared_bus = SignalBus(logger=logger)
        self.shared_bus.start_thread()

    def delete_device(self: _BusOwnerMixedIn) -> None:
        """Shutdown the bus background thread."""
        self.shared_bus.shutdown_thread()
        super().delete_device()
