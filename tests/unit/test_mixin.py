"""Tests for SkaMixin base class."""

import pytest
from tango.server import (
    BaseDevice,
    Device,
    attribute,
    class_property,
    command,
    device_property,
)
from tango.test_context import DeviceTestContext, MultiDeviceTestContext

from ska_tango_base.meta import SkaDeviceMeta
from ska_tango_base.mixin import SkaMixin


def test_command_from_mixin() -> None:
    """Test if we can create a command with SkaMixin."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=invalid-name,missing-function-docstring

    class MyMixin(SkaMixin):
        @command  # type: ignore[misc]
        def myCmd(self) -> int:
            return 0

    class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        pass

    with DeviceTestContext(MyDevice) as dp:
        assert dp.myCmd() == 0


def test_attribute_from_mixin() -> None:
    """Test if we can create an attribute with SkaMixin."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=invalid-name

    class MyMixin(SkaMixin):
        @attribute  # type: ignore[misc]
        def myAttr(self) -> int:
            """My attribute description."""
            return 0

    class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        pass

    with DeviceTestContext(MyDevice) as dp:
        assert dp.myAttr == 0


def test_device_property_from_mixin() -> None:
    """Test if we can create a device property with SkaMixin."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=invalid-name,missing-function-docstring

    class MyMixin(SkaMixin):
        my_prop: str = device_property(dtype=str)

        @command  # type: ignore[misc]
        def myCmd(self) -> str:
            return self.my_prop

    class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        pass

    with DeviceTestContext(MyDevice, properties={"my_prop": "foo"}) as dp:
        assert dp.myCmd() == "foo"


def test_class_property_from_mixin() -> None:
    """Test if we can create a device property with SkaMixin."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=invalid-name,missing-function-docstring

    class MyMixin(SkaMixin):
        my_prop: str = class_property(dtype=str, default_value="foo")

        @command  # type: ignore[misc]
        def myCmd(self) -> str:
            return self.my_prop

    class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        pass

    with DeviceTestContext(MyDevice) as dp:
        assert dp.myCmd() == "foo"


def test_attribute_override_with_mixin() -> None:
    """Test if we can override attribute read method with SkaMixin.

    We want to ensure that:
        - Subclasses of a mixin that use the ``read_<x>`` can use
          the default implementation provided by the mixin
        - Can override the implementation
        - That overriding the implementation does not break overrides
          for other subclasses of the mixin
    """
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=invalid-name

    class MyMixin(SkaMixin):
        myAttr = attribute()  # noqa: N815

        def read_myAttr(self) -> int:
            """Return default value."""
            return 0

    class MyDevice1(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        pass

    class MyDevice2(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        def read_myAttr(self) -> int:
            """First override."""
            return 2

    class MyDevice3(MyMixin, Device, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        def read_myAttr(self) -> int:
            """Second override."""
            return 3

    devices_info = (
        {
            "class": MyDevice1,
            "devices": [
                {"name": "test/device/1"},
            ],
        },
        {
            "class": MyDevice2,
            "devices": [
                {
                    "name": "test/device/2",
                },
            ],
        },
        {
            "class": MyDevice3,
            "devices": [
                {
                    "name": "test/device/3",
                },
            ],
        },
    )
    with MultiDeviceTestContext(devices_info) as context:
        proxy1 = context.get_device("test/device/1")
        assert proxy1.myAttr == 0

        proxy2 = context.get_device("test/device/2")
        assert proxy2.myAttr == 2

        proxy3 = context.get_device("test/device/3")
        assert proxy3.myAttr == 3


def test_composite_mixin() -> None:
    """Test that SkaMixin requires using SkaDeviceMeta."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=invalid-name,missing-function-docstring

    class MyMixin1(SkaMixin):
        @attribute  # type: ignore[misc]
        def myAttr(self) -> int:
            return 0

    class MyMixin2(SkaMixin):
        @command  # type: ignore[misc]
        def myCmd(self) -> int:
            return 0

    class MyCompositeMixin(MyMixin1, MyMixin2, SkaMixin):
        pass

    class MyDevice(
        MyCompositeMixin, Device, metaclass=SkaDeviceMeta  # type: ignore[misc]
    ):
        pass

    with DeviceTestContext(MyDevice) as dp:
        assert dp.myAttr == 0
        assert dp.myCmd() == 0


def test_just_base_device() -> None:
    """Test that SkaMixin only requires the BaseDevice."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=invalid-name,missing-function-docstring

    class MyMixin(SkaMixin):
        @attribute  # type: ignore[misc]
        def myAttr(self) -> int:
            return 0

    class MyDevice(MyMixin, BaseDevice, metaclass=SkaDeviceMeta):  # type: ignore[misc]
        pass

    with DeviceTestContext(MyDevice) as dp:
        assert dp.myAttr == 0


def test_no_meta_class() -> None:
    """Test that SkaMixin requires using SkaDeviceMeta."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=unused-variable

    class MyMixin(SkaMixin):
        pass

    with pytest.raises(TypeError):

        class MyDevice(MyMixin, Device):  # type: ignore[misc]
            pass


def test_no_base_device() -> None:
    """Test that SkaMixin requires using BaseDevice."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=unused-variable

    class MyMixin(SkaMixin):
        pass

    with pytest.raises(TypeError):

        class MyDevice(MyMixin):
            pass


def test_device_first() -> None:
    """Test that SkaMixin requires the mix-ins first."""
    # pylint: disable=too-few-public-methods,missing-class-docstring
    # pylint: disable=unused-variable

    class MyMixin(SkaMixin):
        pass

    with pytest.raises(TypeError):

        class MyDevice(Device, MyMixin):  # type: ignore[misc]
            pass
