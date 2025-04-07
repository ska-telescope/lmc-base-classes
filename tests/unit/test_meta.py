"""Test for SkaDeviceMeta metaclass."""

from __future__ import annotations

import inspect
from typing import Any, Callable, ClassVar, Protocol

import tango
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango.server import Device, attribute, command
from tango.test_context import DeviceTestContext

from ska_tango_base.meta import SkaDeviceMeta


def test_adding_a_base() -> None:
    """Test if we can add a base with SkaDeviceMeta."""
    # pylint: disable=too-few-public-methods,missing-class-docstring

    class NewBase:
        pass

    class MyMixin:
        @classmethod
        def __new_tango_device_class__(
            cls: type,
            name: str,
            bases: list[type],
            namespace: dict[str, Any],
        ) -> None:
            _ = cls
            _ = name
            _ = namespace
            bases.append(NewBase)

    class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        pass

    assert NewBase in MyDevice.__bases__


def test_removing_a_base() -> None:
    """Test if we can remove a base with SkaDeviceMeta."""
    # pylint: disable=too-few-public-methods,missing-class-docstring

    class NewBase:
        pass

    class MyMixin:
        @classmethod
        def __new_tango_device_class__(
            cls: type,
            name: str,
            bases: list[type],
            namespace: dict[str, Any],
        ) -> None:
            _ = cls
            _ = name
            _ = namespace
            bases.remove(NewBase)

    class MyDevice(
        MyMixin, NewBase, Device, metaclass=SkaDeviceMeta  # type: ignore[misc]
    ):
        pass

    assert NewBase not in MyDevice.__bases__


def test_adding_a_method() -> None:
    """Test if we can add a method with SkaDeviceMeta."""
    # pylint: disable=too-few-public-methods,missing-class-docstring

    class MyMixin:
        @classmethod
        def __new_tango_device_class__(
            cls: type,
            name: str,
            bases: list[type],
            namespace: dict[str, Any],
        ) -> None:
            _ = cls
            _ = name
            _ = bases
            namespace["foo"] = lambda self: None

    class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        pass

    assert inspect.isroutine(MyDevice.foo)


def test_update_class_variable() -> None:
    """Test if we can add a class variable with SkaDeviceMeta."""
    # pylint: disable=too-few-public-methods,missing-class-docstring

    class MyMixin:
        @classmethod
        def __new_tango_device_class__(
            cls: type,
            name: str,
            bases: list[type],
            namespace: dict[str, Any],
        ) -> None:
            _ = cls
            _ = name
            _ = bases
            namespace["MY_VAR"] = 1

    class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        MY_VAR = 0

    assert MyDevice.MY_VAR == 1


def test_attribute_storage_mixin() -> None:  # noqa: C901
    """Test that AttributeStorageMixin is possible with SkaDeviceMeta."""

    class _AttributeStorageProtocol(Protocol):
        init_device: Callable[[], None]

        def set_change_event(self, name: str, impl: bool, detect: bool = True) -> None:
            """Mark that this device manual pushes change events for an attribute."""

        def set_archive_event(self, name: str, impl: bool, detect: bool = True) -> None:
            """Mark that this device manual pushes archive events for an attribute."""

        def push_change_event(self, name: str, value: Any) -> None:
            """Push a change event for an attribute."""

        def push_archive_event(self, name: str, value: Any) -> None:
            """Push a change event for an attribute."""

        _attribute_storage: dict[str, Any]
        # pylint: disable=unused-private-member
        __all_stored_attributes: ClassVar[dict[str, StoredAttribute]]

    class StoredAttribute:
        """Dummy implementation of a python descriptor coupled to a Tango attribute."""

        def __init__(
            self: StoredAttribute,
            attr_name: str,
            default_value: Any,
            **kwargs: Any,
        ):
            """Initialise the object."""
            self.attr_name = attr_name
            self.default_value = default_value
            self.attr_kwargs = kwargs

        def on_init_device(
            self: StoredAttribute, device: _AttributeStorageProtocol
        ) -> None:
            """Initialise device for stored attribute."""
            device.set_change_event(self.attr_name, True, True)
            device.set_archive_event(self.attr_name, True, True)
            # pylint: disable=protected-access
            device._attribute_storage[self.attr_name] = self.default_value

        def __get__(
            self: StoredAttribute,
            obj: _AttributeStorageProtocol | None,
            objtype: type | None = None,
        ) -> Any:
            """Return stored value."""
            if obj is None:
                return self

            return obj._attribute_storage[self.attr_name]

        def __set__(
            self: StoredAttribute, obj: _AttributeStorageProtocol, value: Any
        ) -> None:
            """Set stored value and push events."""
            obj._attribute_storage[self.attr_name] = value
            obj.push_change_event(self.attr_name, value)
            obj.push_archive_event(self.attr_name, value)

        def generate_tango_objects(self: StoredAttribute) -> dict[str, attribute]:
            """Create a Tango attribute object for this stored attribute."""

            def fget(device: _AttributeStorageProtocol) -> Any:
                return self.__get__(device)  # pylint: disable=unnecessary-dunder-call

            def fset(device: _AttributeStorageProtocol, value: Any) -> None:
                self.__set__(device, value)  # pylint: disable=unnecessary-dunder-call

            return {self.attr_name: attribute(fget=fget, fset=fset, **self.attr_kwargs)}

    class AttributeStorageMixin:  # pylint: disable=too-few-public-methods
        """Dummy attribute storage mixin.

        This is something we want the metaclass to be able to support.
        """

        _attribute_storage: dict[str, Any]

        @classmethod
        def __new_tango_device_class__(
            cls: type[AttributeStorageMixin],
            name: str,
            bases: list[type],
            namespace: dict[str, Any],
        ) -> None:
            """Create new tango objects for stored attributes."""
            _ = cls
            _ = name
            stored_attributes = {}
            for base in reversed(bases):
                for key in dir(base):
                    obj = getattr(base, key)
                    if isinstance(obj, StoredAttribute):
                        stored_attributes[key] = obj

            for key, obj in namespace.items():
                if isinstance(obj, StoredAttribute):
                    stored_attributes[key] = obj

            for key, obj in stored_attributes.items():
                namespace.update(obj.generate_tango_objects())

            namespace["_AttributeStorageMixin__all_stored_attributes"] = (
                stored_attributes
            )

        def init_device(self: _AttributeStorageProtocol) -> None:
            """Initialise Tango device."""
            super().init_device()

            self._attribute_storage = {}

            for attr in self.__all_stored_attributes.values():
                attr.on_init_device(self)

    class MyDevice(
        AttributeStorageMixin, Device, metaclass=SkaDeviceMeta  # type: ignore[misc]
    ):
        """Dummy class using StoredAttributes."""

        my_value = StoredAttribute("myAttr", 0, dtype=int, abs_change=1)

        @command  # type: ignore[misc]
        def do_something(self) -> None:
            """Set myAttr to 7."""
            self.my_value = 7

    callbacks = MockTangoEventCallbackGroup("myAttr")
    with DeviceTestContext(MyDevice) as dp:
        dp.subscribe_event("myAttr", tango.EventType.CHANGE_EVENT, callbacks["myAttr"])
        callbacks.assert_change_event("myAttr", 0)
        dp.myAttr = 1
        callbacks.assert_change_event("myAttr", 1)
        dp.do_something()
        callbacks.assert_change_event("myAttr", 7)
