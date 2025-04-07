.. _mixin-guidelines:

=========================================================
Guidelines for building mix-in classes for ska-tango-base
=========================================================

.. warning::

   This page might contain bad advice and is probably incomplete.  Feel free to
   edit with your own suggestions.

This guide is aimed at providing developers of ska-tango-base recommendations
for how to build composable mix-in classes for Tango devices.

Prefer named methods for attribute callbacks
--------------------------------------------

pytango gives you two options when defining your Tango attributes with the high
level API:

1. Via decorators

  .. code:: python

    class MyDevice(Device):
        @attribute
        def myAttr(self) -> int:
          return 0

2. Via named functions

  .. code:: python

    class MyDevice(Device):
        myAttr = attribute()

        def read_myAttr(self) -> int:
          return 0

For mix-in classes, you should prefer the named function case as they can be
more easily overridden by devices inheriting from your mix-in class.  This is
especially important for mix-in classes as they are designed to be
overridden. Using the named functions, ``super()`` also works as you would
expect.  For example:

.. code:: python

   class MyMixin(SkaMixin):
     myAttr = attribute()

     def read_myAttr(self) -> int:
       return 0

   class MyDevice(MyMixin, Device, metaclass=SkaDeviceMeta):
     def read_myAttr(self) -> int:
       return super().read_myAttr() + 1

This is not a consideration for :py:class:`~tango.server.command` as Tango
commands are much simpler than attributes.  If a subclass wants to override a
:py:class`~tango.server.command` then it can simply define its own ``@command``
and call the original command function.

Always call super().init_device()
---------------------------------

To initialise your mix-in class at device init time, you can add a init_device()
method to your mix-in.  In order to be a good citizen, you should make sure to
call ``super().init_device()`` so that other mix-in classes can be initialised
and so that ``Device.init_device()`` is called.

The ``SkaMixin`` class will ensure that your mix-in class appears in the method
resolution order before :py:class:`~tango.server.Device` so that this
`init_device()` chain will definitely end.

Similarly, if using :py:class:`~ska_tango_base.software_bus.BusOwnerMixin`,
always call ``super().init_bus_sharers()``.

This is similar to the usual advice around always calling ``super().__init__()``
in your ``__init__()`` method.

Use Protocols for type checking
-------------------------------

Type checking a mix-in class can be a bit of a pain because we are expecting
the subclass to also inherit from :py:class:`~tango.server.Device`.  To get
around this, create a :py:class:`typing.Protocol` class to use as a type hint
for ``self``.

The protocol should provide methods for all the :py:class:`~tango.server.Device`
methods that the mix-in is required to use, as well as all the methods defined
by the mix-in itself.  This protocol should be marked private.  You could give
it a punny name like "_MyMixedIn" for the mix-in "MyMixin".
