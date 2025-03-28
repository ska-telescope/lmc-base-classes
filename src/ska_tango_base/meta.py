"""Improved Tango device metaclass."""

from __future__ import annotations

from typing import Any, Protocol

from tango.server import DeviceMeta

# Metaclass primer for dealing with this file.
#
# When you create a class, this is a python statement which runs some python
# code.  This python code is the metaclass's `__new__` method.  For example,
# the following class statement:
#
# class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):
#  MY_CLASS_VAR = 1
#  def init_device(self):
#    pass
#
# Will call `SkaDeviceMeta.__new__("MyDevcie", (MyMixin, Device),
#                                   {"MY_CLASS_VAR": 1,
#                                    "init_device": <function object>})
#
# We are adding a new magic method (`__new_tango_device_class__`) for base classes
# of a Tango device class so that they can modify the arguments passed to
# `tango.DeviceMeta.__new__`.  This is similar in spirit the python built-in
# `__init_subclass__` magic method, but occurs at a different point in the class
# construct process.
#
# We need to add this in order for our mix-in classes to be able to influence
# the creation of the Tango DeviceClass object (stored as `TangoClassClass`).
# This Tango DeviceClass is created during `tango.DeviceMeta.__new__` and
# `__init_subclass__` only runs after this point.


class NewTangoDeviceClassProcotol(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for base classes that can be used by SkaDeviceMeta."""

    @classmethod
    def __new_tango_device_class__(
        cls, name: str, bases: list[type], namespace: dict[str, Any], **kwargs: Any
    ) -> None:
        """Modify a subclass before construction.

        This method is free to modify bases and namespace as appropriate.  The
        intention here is to allow base classes to provide Tango objects to
        their subclasses.

        As a general rule, `namespace` should be updated with ``setdefault()``
        to allow either the derived class, or earlier base classes, to override
        the values your base class provides.

        .. warning ::

            Any additional bases added will not have their
            ``__new_tango_device_class__`` called automatically, so this must
            be done manually if it is required.

            Additionally, bases removed from this list will still have their
            ``__new_tango_device_class__`` class method called, regardless of
            when this removal happened.

        :param name: Name of Device class being constructed
        :param bases: Base classes from the class to inherit from
        :param namespace: Class namespace object
        :param kwargs: Additional arguments passed in class statement
        """


class SkaDeviceMeta(
    DeviceMeta  # type: ignore[misc]  # Cannot subclass DeviceMeta (has type Any)
):
    """Tango device metaclass that allows base classes to override.

    This metaclass provides a hook for base classes to be able to provide
    additional Tango attributes, properties or commands when creating the Tango
    device class.

    Direct base classes of the Tango device class being instantiated can provide a
    ``__new_tango_device_class__()`` class method, which is called before
    class construction.  See :py:class:`NewTangoDeviceClassProcotol` for details
    on this class method.

    The ``__new_tango_device_class__()`` class method is passed the
    ``bases`` and ``namespace`` that has already been modified by
    earlier base classes.  Modifications to the ``namespace`` and ``bases``
    arguments are passed on to ``tango.server.DeviceMeta.__new__()``.

    Example:
        .. code:: python

            class MyMixin:
                @classmethod
                def __new_tango_device_class__(cls, name, bases, namespace, **kwargs):
                    bases.append(MyNewBaseClass())
                    namespace.setdefault("foo", "bar")

            class MyDevice(MyMixin,
                           BaseDevice,
                           metaclass=SkaDeviceMeta,
                           my_kwarg="qux"):
                def foo(self):
                    return 1

        Here, ``MyMixin.__new_tango_device_class__()`` will be called with the
        following arguments:

        .. code :: python

            MyMixin.__new_tango_device_class__(
                "MyDevice",
                [MyMixin, BaseDevice],
                { "foo": <function object> },
                my_kwarg="qux"
            )

    :param name: Name of class being constructed
    :param bases: Base classes to inherit from
    :param namespace: Class namespace object
    :param kwargs: Additional arguments passed in class statement
    """

    def __new__(
        mcs: type[SkaDeviceMeta],  # noqa: N804
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        """Create high-level Tango device class."""
        # We want to allow the NewTangoDeviceClassProcotol objects to
        # be able to modify the bases of the derived class, so we change
        # bases to a list here.
        editable_bases = list(bases)
        for base in bases:
            ntdc = getattr(base, "__new_tango_device_class__", None)
            if ntdc is not None:
                ntdc(name, editable_bases, namespace, **kwargs)

        # We are actually constructing a Tango device here, so we don't want
        # anyone subclassing from this class to generate the tango objects again.  As
        # such, we override the "__new_tango_device_class__" method to do nothing
        # here.  We are using setdefault so that the class we are instantiating
        # could override us if they desired, or a base class could inject their
        # on into the namespace from their `__new_tango_device_class__` method.
        namespace.setdefault(
            "__new_tango_device_class__",
            classmethod(lambda cls, *args, **kwargs: None),
        )

        return super().__new__(mcs, name, tuple(editable_bases), namespace, **kwargs)
