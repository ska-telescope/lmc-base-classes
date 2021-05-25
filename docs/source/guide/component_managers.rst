Components and component managers
=================================

A fundamental assumption of this package is that each Tango device
exists to provide monitoring and control of some *component* of a SKA
telescope.

A *component* could be (for example):

* Hardware such as an antenna, dish, atomic clock, TPM, switch, etc

* An external service such as a database or cluster workload
  manager

* A software process or thread launched by the Tango device.

* In a hierarchical system, a group of subservient Tango devices.

By analogy, if the *component* is a television, the Tango device would
be the remote control for that television.

Tango devices and their components
----------------------------------
Note the distinction between a component and the Tango device that is
responsible for monitoring and controlling that component.

A component might be hardware equipment installed on site, such as a
dish or an antenna. The Tango device that monitors that component is a
software object, in a process running on a server, probably located in a
server room some distance away. Thus the Tango device and its component
are largely independent of each other:

* A Tango device may be running normally when its component is in a 
  fault state, or turned off, or even not fitted. Device states like
  ``OFF`` and ``FAULT`` represent the state of the monitored component.
  A Tango device that reports ``OFF`` state is running normally, and
  reporting that its component is turned off. A Tango device that
  reports ``FAULT`` state is running normally, and reporting that its
  component is in a fault state.

* When a Tango device itself experiences a fault (for example, its
  server crashes), this is not expected to affect the component. The
  component continues to run; the only impact is it can no longer be
  monitored or controlled.
  
  By analogy: when the batteries in your TV remote control go flat, the
  TV continues to run.

* We should not assume that a component's state is governed solely by
  its Tango device. On the contrary, components are influenced by a
  wide range of factors. For example, the following are ways in which a
  component might be switched off:

  * Its Tango device switches it off via its software interface;

  * Some other software entity switches it off via its software
    interface;

  * The hardware switches itself off, or its firmware switches it off,
    because it detected a critical fault.

  * The equipment's power button is pressed;

  * An upstream power supply device denies it power.

  A Tango device therefore must not treat its component as under its
  sole control. For example, having turned its component on, it must not
  assume that the component will remain on. Rather, it must continually
  *monitor* its component, and update its state to reflect changes in
  component state.
  
Component monitoring
--------------------
Component *monitoring* is the main mechanism by which a Tango device
maintains and updates its state:
  
* A Tango device should not make assumptions about component state after
  issuing a command. For example, after successfully telling its
  component to turn on, a Tango device should not assume that the
  component is on, and transition immediately to ON state. Rather, it
  should wait for its monitoring of the component to provide
  confirmation that the component is on; only then should it transition
  to ON state. It follows that a Tango device's ``On()`` command might
  complete successfully, yet the device's ``state()`` might not report
  ``ON`` state immediately, or for some seconds, or indeed at all.

* A Tango device also should not make assumptions about component state
  when the Tango device is *initialising*. For example, in a normal
  controlled startup of a telescope, an initialising Tango device might
  expect to find its component switched off, and to be itself
  responsible for switching the component on at the proper time.
  However, this is not the only circumstance in which a Tango device
  might initialise; the Tango device would also have to initialise
  following a reboot of the server on which it runs. In such a case, the
  component might already be switched on. Thus, at initialisation, a
  Tango device should merely launch the component monitoring that will
  allows the device to detect the state of the component.

Component managers
------------------
A Tango device's responsibility to monitor and control its component is
largely separate from its interface to the Tango subsystem. Therefore,
devices in this package implement component monitoring and control in a
separate *component manager*.

A component manager is responsible for:

  * establishing and maintaining communication with the component. For
    example:

    * If the component interface is via a connection-oriented protocol
      (such as TCP/IP), then the component manager must establish and
      maintain a *connection* to the component;

    * If the component is able to publish updates, then the component
      manager would need to subscribe to those updates;
  
    * If the component cannot publish updates, but can only respond to
      requests, then the component manager would need to initiate
      polling of the component.

  * implementing monitoring of the component so that changes in
    component state trigger callbacks that report those changes up to
    the Tango device;
    
  * implementing commands such as ``off()``, ``on()``, etc., so that
    they actually tell the component to turn off, turn on, etc.

.. note:: It is highly recommended to implement your component manager,
   and thoroughly test it, *before* embedding it in a Tango device.
