"""Base class for mix-in classes which provide Tango objects."""

from __future__ import annotations

from copy import copy
from typing import Any

from tango.server import BaseDevice, DeviceMeta, is_tango_object

from .meta import SkaDeviceMeta


class SkaMixin:  # pylint: disable=too-few-public-methods
    """Base classes for mix-in classes which provide Tango objects.

    .. note::

        For the purposes of this documentation, classes directly inheriting
        from SkaMixin are known as mix-ins.  This means that SkaMixin is itself not
        a mix-in.

    Tango objects (:py:class:`~tango.server.attribute`,
    :py:func:`~tango.server.command`, :py:class:`~tango.server.device_property`
    and :py:class:`~tango.server.class_property`) defined on mix-ins (i.e. subclasses
    of ``SkaMixin``) will be copied to device classes inheriting from those mix-ins.
    Importantly, the Tango objects are *copied* to the device class, meaning multiple
    device classes that inherit from the same ``SkaMixin`` will have different
    Tango objects.

    ``SkaMixin`` requires the device class to use the
    :py:class:`~ska_tango_base.meta.SkaDeviceMeta` metaclass and will raise
    :py:class:`TypeError` at class construction time if a mix-in is used without the
    metaclass when constructing a device class.

    Furthermore, a device class inheriting from mix-ins must inherit from all the
    mix-ins before inheriting from :py:class:`tango.server.Device` (or one of
    its subclasses).  A :py:class:`TypeError` is raised if this is not the case.

    In order to inherit from a mix-in, a non-device class must also directly
    inherit from ``SkaMixin`` itself (i.e. also be a mix-in), otherwise a
    :py:class:`TypeError` is raised.

    ``SkaMixin`` models the
    :py:class:`~ska_tango_base.meta.NewTangoDeviceClassProcotol`.

    Example:
        .. code:: python

            class MyMixin(SkaMixin):
                @attribute
                def myAttr(self) -> int:
                    return 1

            class MyDevice(MyMixin, Device, metaclass=SkaMetaDevice):
                pass

            # MyDevice will provide a Tango attribute called myAttr
    """

    @classmethod
    def __new_tango_device_class__(
        cls: type,
        name: str,
        bases: list[type],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Copy all Tango objects defined in by the mix-in into the namespace."""
        _ = name
        _ = bases
        _ = kwargs
        for key in dir(cls):
            obj = getattr(cls, key)
            if is_tango_object(obj):
                # We use setdefault here so that earlier bases or the derived
                # class can override the obj we provide.  This makes it appear
                # like the tango object belongs to this mix-in as a normal
                # python attribute and we respect method resolution order
                # properly.
                #
                # We are using copy() here so that multiple devices inheriting
                # from the same mix-in get different copies of these tango
                # objects.  This allows them to override their behaviour
                # differently.
                namespace.setdefault(key, copy(obj))

    @classmethod
    def __init_subclass__(cls, **kwargs: dict[str, Any]):
        """Check if subclasses of the mix-in are allowed.

        A subclass of a mix-in is allowed if either:
            1. The subclass inherits from :py:class:`tango.server.BaseDevice` and
               uses the :py:class:`SkaDeviceMeta` metaclass and is not itself a mix-in.
            2. All the mix-ins must be earlier in the method resolution order than
               :py:class:`tango.server.BaseDevice`.
            3. The subclass is itself a mix-in (i.e. inherits directly from SkaMixin).

        Rule 1 ensures that :py:func:`SkaMixin.__new_tango_device_class__` will be
        called at the correct time.

        Rule 2 ensures that `init_device()` can be used by mix-ins to initialise
        themselves and call `super().init_device()`.  By having ``BaseDevice`` last
        in the MRO, we always have a base-case `init_device()` call which does not
        call `super().init_device()`.

        Rule 3 ensures that users of a mix-in understand that this is a mix-in and not
        a normal class to inherit from and makes error reporting the other rules more
        straight forward.

        :raises TypeError: If the subclass of the mix-in is not valid.
        """

        def to_names(classes: list[type]) -> str:
            names = [c.__name__ for c in classes]

            if len(names) == 0:
                return ""

            if len(names) == 1:
                return names[0]

            head = ", ".join(names[:-1])
            return " and ".join([head, names[-1]])

        if SkaMixin in cls.__bases__:
            # Forbid constructing a device class from a mix-in, e.g:
            #
            # class MyDevice(SkaMixin, Device):
            #     pass
            #
            # We check against `DeviceMeta` here and not `SkaDeviceMeta`
            # as it is `DeviceMeta` which actually creates the Tango
            # DeviceClass and that is what we have issue with.
            if isinstance(cls, DeviceMeta):
                raise TypeError(
                    f"{cls.__name__} must not directly inheirt from SkaMixin"
                    " while using the tango.DeviceMeta metaclass"
                )
        else:
            mixins = [c for c in cls.__bases__ if SkaMixin in c.__bases__]

            # Forbid using metaclasses to make something other than a mix-in
            # or a Device, e.g:
            #
            # class MyClass(Mixin1, Mixin2):
            #     pass
            #
            # You would need to also inherit from `SkaMixin` for the above
            # to work.
            if not isinstance(cls, SkaDeviceMeta):
                raise TypeError(
                    f"{cls.__name__} must use the SkaMetaDevice metaclass, "
                    "or directly inheirt from SkaMixin, "
                    f"in order to inherit from {to_names(mixins)}."
                )

            # Forbid inherit from a mix-in _after_ Device, e.g:
            #
            # class MyDevice(Device, MyMixin):
            #     pass
            mro = cls.mro()
            device_index = mro.index(BaseDevice)
            bad_mixins = [m for m in mixins if mro.index(m) > device_index]
            device_bases = [c for c in cls.__bases__ if issubclass(c, BaseDevice)]

            if len(bad_mixins) > 0:
                raise TypeError(
                    f"{cls.__name__} must inherit from"
                    f" {to_names(bad_mixins)} before {to_names(device_bases)}"
                )

        super().__init_subclass__(**kwargs)
