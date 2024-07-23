===============
Getting started
===============
This page will guide you through the steps to writing a SKA Tango device
based on the ``ska-tango-base`` package.

Prerequisites
-------------
It is assumed here that you have a subproject repository, and have `set
up your development environment`_. The ``ska-tango-base`` package can be
installed from the SKAO repository:

.. code-block:: shell-session

   me@local:~$ python3 -m pip --require-virtualenv install --extra-index-url https://artefact.skao.int/repository/pypi-all/simple ska-tango-base

Basic steps
-----------
The recommended basic steps to writing a SKA Tango device based on the
``ska-tango-base`` package are:

1. Write a component manager.

2. Implement command class objects.

3. Write your Tango device.

Detailed steps
--------------

Write a component manager
^^^^^^^^^^^^^^^^^^^^^^^^^
A fundamental assumption of this package is that each Tango device
exists to provide monitoring and control of some *component* of a SKA
telescope. That *component* could be some hardware, a software service
or process, or even a group of subservient Tango devices.

A *component manager* provides for monitoring and control of a
component. It is *highly recommended* to implement and thoroughly test
your component manager *before* embedding it in a Tango device.

For more information on components and component managers, see
:doc:`../concepts/component-managers`.

Writing a component manager involves the following steps.

1. **Choose a subclass for your component manager.** There are several
   component manager base classes, each associated with a device class.
   For example,
   
   * If your Tango device will inherit from ``SKABaseDevice``, then you
     will probably want to base your component manager on the
     ``BaseComponentManager`` class.

   * If your Tango device is a subarray, then you will want to base your
     component manager on ``SubarrayComponentManager``.

   .. inheritance-diagram::
      ska_tango_base
      ska_tango_base.subarray.subarray_component_manager
      :parts: 1
  

   These component managers are abstract. They specify an interface, but
   leave it up to you to implement the functionality. For example,
   ``BaseComponentManager``'s ``on()`` command looks like this:

   .. code-block:: py

     def on(self):
       raise NotImplementedError("BaseComponentManager is abstract.")
   
   Your component manager will inherit these methods, and override them
   with actual implementations.

   .. note:: In addition to these abstract classes, there are also
      reference implementations of concrete subclasses. For example, in
      addition to an abstract ``BaseComponentManager``, there is also a
      concrete ``ReferenceBaseComponentManager``. These reference
      implementations are provided for explanatory purposes: they
      illustrate how a concrete component manager might be implemented.
      You are encouraged to review the reference implementations, and
      adapt them to your own needs; but it is not recommended to
      subclass from them.

2. **Establish communication with your component.** How you do this will
   depend on the capabilities and interface of your component. for
   example:

   * If the component interface is via a connection-oriented protocol
     (such as TCP/IP), then the component manager must establish and
     maintain a *connection* to the component;

   * If the component is able to publish updates, then the component
     manager would need to subscribe to those updates;

   * If the component cannot publish updates, but can only respond to
     requests, then the component manager would need to initiate
     polling of the component.

3. **Implement component monitoring.** Whenever your component changes
   its state, your component manager needs to become reliably aware of
   that change within a reasonable time frame, so that it can pass this
   on to the Tango device.
   
   The abstract component managers provided already contain some helper
   methods to trigger device callbacks. For example,
   ``BaseComponentManager`` provides a ``component_fault`` method that
   lets the device know that the component has experienced a fault. You
   need to implement component monitoring so that, if the component
   experiences a fault, this is detected, and results in the
   ``component_fault`` helper method being called.

   For component-specific functionality, you will need to implement the
   corresponding helper methods. For example, if your component reports
   its temperature, then your component manager will need to

   1. Implement a mechanism by which it can let its Tango device know
      that the component temperature has changed, such as a callback;

   2. Implement monitoring so that this mechanism is triggered whenever
      a change in component temperature is detected.

4. **Implement component control.** Methods to control the component
   must be implemented; for example the component manager's ``on()``
   method must be implemented to actually tell the component to turn on.

   Note that component *control* and component *monitoring* are
   decoupled from each other. So, for example, a component manager's
   ``on()`` method should not directly call the callback that tells the
   device that the component is now on. Rather, the command should
   return without calling the callback, and leave it to the *monitoring*
   to detect when the component has changed states.
   
   Consider, for example, a component that takes ten seconds to power
   up:
   
   1. The ``on()`` command should be implemented to tell the component
      to power up. If the component accepts this command without
      complaint, then the ``on()`` command should return success. The
      component manager should not, however, assume that the component
      is now on.
   2. After ten seconds, the component has powered up, and the component
      manager's monitoring detects that the component is on. Only then
      should the callback be called to let the device know that the
      component has changed state, resulting in a change of device state
      to ``ON``.

.. note:: A component manager may maintain additional state, and support
   additional commands, that do not map to its component. That is, a
   call to a component manager needs not always result in a call to the
   underlying component. For example, a subarray's component manager may
   implement its ``assign_resources`` method simply to maintain a record
   (within the component manager itself) of what resources it has, so
   that it can validate arguments to other methods (for example, check
   that arguments to its ``configure`` method do not require access to
   resources that have not been assigned to it). In this case, the call
   to the component manager's ``assign_resources`` method would not
   result in interaction with the component; indeed, the component may
   not even possess the concepts of *resources* and *resource
   assignment*.

Implement command class objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Tango device command functionality is implemented in command *classes*
rather than methods. This allows for:
   
* functionality common to many classes to be abstracted out and
  implemented once for all. For example, there are many commands
  associated with transitional states (*e.g.* ``Configure()`` command
  and ``CONFIGURING`` state, ``Scan()`` command and ``SCANNING`` state,
  *etc.*). Command classes allow us to implement this association once
  for all, and to protect that implementation from accidental overriding
  by command subclasses.
* testing of commands independently of Tango. For example, a Tango
  device's ``On()`` command might only need to interact with the
  device's component manager and its operational state model. As such,
  in order to test the correct implementation of that command, we only
  need a component manager and an operational state model. Thus, we can
  test the command without actually instantiating the Tango device.

Writing a command class involves the following steps.

1. **Do you really need to implement the command?** If the command to be
   implemented is part of the Tango device you will inherit from,
   perhaps the current implementation is exactly what you need.

   For example, the ``SKABaseDevice`` class's implementation of the
   ``On()`` command simply calls its component manager's ``on()``
   method. Maybe you don't need to change that; you've implemented your
   component manager's ``on()`` method, and that's all there is to do.

2. **Choose a command class to subclass.**

   * If the command to be implemented is part of the device you will
     inherit from (but you still need to override it), then you would
     generally subclass the base device's command class. For example, if
     if you need to override ``SKABaseDevice``'s ``Standby`` command,
     then you would subclass ``SKABaseDevice.StandbyCommand``.

   * If the command is a new command, not present in the base device
     class, then you will want to inherit from one or more command
     classes in the :py:mod:`ska_tango_base.commands` module. 

     .. inheritance-diagram::
        ska_tango_base.commands.FastCommand
        ska_tango_base.commands.SlowCommand
        ska_tango_base.commands.DeviceInitCommand
        ska_tango_base.commands.SubmittedSlowCommand
        :parts: 1

3. **Implement class methods.**
   
   * In many cases, you only need to implement the ``do()`` method.


Write your Tango device
^^^^^^^^^^^^^^^^^^^^^^^

Writing the Tango device involves the following steps:

1. **Select a device class to subclass.**

   .. inheritance-diagram::
      ska_tango_base.SKAAlarmHandler
      ska_tango_base.SKACapability
      ska_tango_base.SKALogger
      ska_tango_base.SKAController
      ska_tango_base.SKATelState
      ska_tango_base.base.SKABaseDevice
      ska_tango_base.obs.SKAObsDevice
      ska_tango_base.subarray.SKASubarray
      :top-classes: ska_tango_base.base.SKABaseDevice
      :parts: 1

2. **Register your component manager.** This is done by overriding the
   ``create_component_manager`` class to return your component manager
   object:

   .. code-block:: py

     def create_component_manager(self):
         return AntennaComponentManager(
             self.op_state_model,
             logger=self.logger,
             communication_state_callback=self._communication_state_callback,
             component_state_callback=self._component_state_callback
         )
   
   When instantiating a component manager object that inherits directly
   or indirectly from BaseComponentManager, two callbacks should be
   provided by the Tango device, one for the communication state and the
   other for the component state. These callbacks allow the component
   manager to inform the Tango device of changes to the component while
   staying decoupled from the device itself.
   
   For instance, the derived
   component manager class will inherit *_update_communication_state*
   from BaseComponentManager, which internally calls the supplied
   *communication_state_callback*. The derived class will then use
   *_update_communication_state* when overriding *start_communicating* and
   *stop_communicating* to drive the op_state_model. Similarly when the
   component manager determines that the power or fault status of the
   component change it will use *_update_component_state* to drive the
   op_state_model.

   At a minimum, to ensure the actions are perfromed on the op_state_model,
   both callbacks should call the relevant *\<type\>_state_changed*
   SKABaseDevice method.
   
      **Communication state** - Perform actions based on the input
      communication_state
      (:obj:`CommunicationStatus <ska_control_model.CommunicationStatus>`
      type from ska_control_model).

      * SKABaseDevice method: *_communication_state_changed*
      * Op state actions: component_disconnected, component_unknown.
      * Minimum example:

      .. code-block:: py

        def _communication_state_callback(
         communication_state: CommunicationStatus
         ) -> None:
             super()._communication_state_changed(communication_state)

      **Component state** - Perform actions based on the input fault
      (boolean) and/or power (:obj:`PowerState <ska_control_model.PowerState>`
      type from ska_control_model).

      * SKABaseDevice method: *_component_state_changed*
      * Op state actions: component_fault, component_no_fault, component_on,
        component_standby, component_off.
      * Minimum example:

      .. code-block:: py

        def _component_state_callback(
            fault: Optional[bool] = None,
            power: Optional[PowerState] = None
         ) -> None:
             super()._component_state_changed(fault=fault, power=power)

   Information the component manager retrieves from the component needs to
   be made available to the wider control system in the form of attributes
   on the Tango device. This can be done with the use of additonal keyword
   arguments provided to the callbacks above that are used to update said
   attributes. However, a device with many different sensors could then end
   up with a long list of keyword arguments, and a cumbersome callback. It is
   recommended to split these additional arguments into their own callback(s)
   by adding methods to the Tango device with corresponding parameters in the
   derived component manager.

   Components may be software instead of hardware. In this case the
   *SKABaseDevice._component_state_changed* method should still be called with
   a power argument to drive the op_state_model, e.g. PowerState.ON to arrive
   in the ON operational state.
   Alternatively *SKABaseDevice._communication_state_changed* could be
   overridden so that a *communication_state* of
   CommunicationStatus.ESTABLISHED instead transitions the operational state
   to ON.
   

3. **Implement commands.** You've already written the command classes.
   There is some boilerplate to ensure that the Tango command methods
   invoke the command classes:

   1. Registration occurs in the ``init_command_objects`` method, using
      calls to the ``register_command_object`` helper method. Implement
      the ``init_command_objects`` method:

      .. code-block:: py

         def init_command_objects(self):
             super().init_command_objects()

             self.register_command_object(
                 "DoStuff", self.DoStuffCommand(self.component_manager, self.logger)
             )
             self.register_command_object(
                 "DoOtherStuff", self.DoOtherStuffCommand(
                     self.component_manager, self.logger
                 )
             )

   2. Any new commands need to be implemented as:

      .. code-block:: py

         @command(dtype_in=..., dtype_out=...)
         def DoStuff(self, argin):
             command = self.get_command_object("DoStuff")
             return command(argin)

      or, if the command does not take an argument:

      .. code-block:: py

         @command(dtype_out=...)
         def DoStuff(self):
             command = self.get_command_object("DoStuff")
             return command()

      Note that these two examples deliberately push all SKA business
      logic down to the command class (at least) or even the component
      manager. It is highly recommended not to include SKA business
      logic in Tango devices. However, Tango-specific functionality can
      and should be implemented directly into the command method. For
      example, many SKA commands accept a JSON string as argument, as a
      workaround for the fact that Tango commands cannot accept more
      than one argument. Since this use of JSON is closely associated
      with Tango, we might choose to unpack our JSON strings in the
      command method itself, thus leaving our command objects free of
      JSON:

      .. code-block:: py

         @command(dtype_in=..., dtype_out=...)
         def DoStuff(self, argin):
             args = json.loads(argin)
             command = self.get_command_object("DoStuff")
             return command(args)


.. _set up your development environment: https://developer.skatelescope.org/en/latest/tools/tango-devenv-setup.html
