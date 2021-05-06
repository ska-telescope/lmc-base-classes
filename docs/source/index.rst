Welcome to SKA Tango Base documentation!
========================================

Introduction
------------

This package provides base devices and functionality for the Tango
devices that provide local monitoring and control (LMC) of SKA telescope
components

Device model
^^^^^^^^^^^^

A fundamental assumption of this package is that each Tango device
exists to provide monitoring and control of some *component* of a SKA
telescope.

A *component* could be (for example):

* Hardware such as an antenna, dish, atomic clock, TPM, switch, etc

* An external software system such as a database or cluster workload
  manager

* A process or thread launched by the TANGO device.

By analogy, if the *component* is a television, the Tango device would
be the remote control for that television.

This assumption has the following implications for our device model:

* A TANGO device is largely decoupled from its component.

  * If the component is shut down, the TANGO device continues to run
    (and reports that its component has been shut down).

  * If the TANGO device is shut down, the component itself continues to
    run (though it can no longer be controlled).

* A component is assumed to be highly exposed: it is influenced by many
  factors. For example, a hardware component might lose power because:

  * its TANGO device turned it off via its software interface;
  * some other entity turned it off via its software interface;
  * someone pressed the power button on its front panel;
  * its power supply failed, or it blew a fuse;
  * it was denied power by an upstream device (or there was a total
    power failure)

  A TANGO device therefore must not treat its component as under its
  sole control. For example, having turned its component on, it must not
  assume that component will remain on until it turns it off again.
  Instead, a TANGO device must continually monitor its component for
  change.

  Similarly, a TANGO device should not make assumptions about component
  state after issuing a command. For example, after telling its
  component to turn on, a TANGO device should not assume that it is on;
  rather, it should monitor the component and detect that it is on. by
  the same token, a TANGO device also should not make assumptions about
  component state when it is initialising. 

* TANGO device states mostly reflect the state of the *component*, not
  the device itself. For example, a FAULT state means that the component
  has faulted. It does not imply that the TANGO device has faulted, nor
  should it be used for that purpose.

Implementation guidance
^^^^^^^^^^^^^^^^^^^^^^^
Devices in this package contain a *component_manager*, which they use to
monitor and control their component. For example, the device On()
command is implemented simply to call the component manager's on()
method.  Devices that are built on this package need to implement their
own component manager.

For example, to write a TANGO device to monitor 
and control a SKA-Mid dish, you will need to write a component manager
that:

* establishes and maintains a connection to a dish;
* implements monitoring so that changes in dish state trigger callbacks
  that report those changes up to the device;
* implements the off(), on(), etc. control methods so that they actually
  tell the dish to turn off, turn on, etc.

The component manager provided in this package is an example; it exists
to explain and illustrate how a component manager should work, and to
allow testing of this package.

API
---
.. toctree::
  :caption: Standard Devices
  :maxdepth: 2

   Base Device<SKABaseDevice>
   Alarm Handler<SKAAlarmHandler>
   Logger<SKALogger>
   Master<SKAMaster>
   Tel State<SKATelState>

   Obs Device<SKAObsDevice>
   Capability<SKACapability>
   Subarray<SKASubarray>

.. toctree::
  :caption: CSP Devices
  :maxdepth: 2

   CSP Sub-element Master<CspSubElementMaster>
   CSP Sub-element Obs Device<CspSubElementObsDevice>
   CSP Sub-element Subarray<CspSubElementSubarray>

.. toctree::
  :caption: Component Managers
  :maxdepth: 2

   Component Manager<component_manager>
   Subarray Component Manager<subarray_component_manager>
   CSP Subelement Obs Component Manager<csp_subelement_obs_component_manager>
   CSP Subelement Subarray Component Manager<csp_subelement_subarray_component_manager>

.. toctree::
   :caption: State
   :maxdepth: 2
 
   Operation State Model<state/op_state_model>
   Admin Mode Model<state/admin_mode_model>
   Observation State Model<state/obs_state_model>
   Subarray Observation State Model<state/subarray_obs_state_model>
   CSP Subelement Obs State Mode<state/csp_subelement_obs_state_model>

.. toctree::
  :caption: Other modules
  :maxdepth: 2

   Control Model<Control_Model>
   Commands<Commands>
   Utils<utils>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
