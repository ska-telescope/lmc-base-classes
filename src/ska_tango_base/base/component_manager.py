"""
This module provides an abstract component manager for SKA Tango base devices.

The basic model is:

* Every Tango device has a *component* that it monitors and/or
  controls. That component could be, for example:

  * Hardware such as an antenna, APIU, TPM, switch, subrack, etc.

  * An external software system such as a cluster manager

  * A software routine, possibly implemented within the Tango device
    itself
    
  * In a hierarchical system, a pool of lower-level Tango devices.

* A Tango device will usually need to establish and maintain a
  *connection* to its component. This connection may be deliberately
  broken by the device, or it may fail.

* A Tango device *controls* its component by issuing commands that cause
  the component to change behaviour and/or state; and it *monitors* its
  component by keeping track of its state.
"""
from ska_tango_base.control_model import PowerMode


class BaseComponentManager:
    """
    An abstract base class for a component manager for SKA Tango
    devices, supporting:

    * Maintaining a connection to its component

    * Controlling its component via commands like Off(), Standby(),
      On(), etc.

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    """

    def __init__(self, op_state_model, *args, **kwargs):
        """
        Initialise a new ComponentManager instance

        :param op_state_model: the op state model used by this component
            manager
        """
        self.op_state_model = op_state_model

    def start_communicating(self):
        """
        Establish communication with the component, then start
        monitoring. This is the place to do things like:

        * Initiate a connection to the component (if your communication
          is connection-oriented)
        * Subscribe to component events (if using "pull" model)
        * Start a polling loop to monitor the component (if using a
          "push" model)
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    def stop_communicating(self):
        """
        Cease monitoring the component, and break off all communication
        with it. For example,

        * If you are communicating over a connection, disconnect.
        * If you have subscribed to events, unsubscribe.
        * If you are running a polling loop, stop it.
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @property
    def is_communicating(self):
        """
        Whether communication with the component is established and
        active, allowing monitoring and control of the component. For
        example:

        * If communication is over a connection, are you connected?
        * If communication is via event subscription, are you
          subscribed, and is the event subsystem healthy?
        * If you are polling the component, is the polling loop running,
          and is the component responsive?

        :return: whether there is currently a connection to the
            component
        :rtype: bool
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @property
    def power_mode(self):
        """
        Power mode of the component

        :return: the power mode of the component
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @property
    def faulty(self):
        """
        Whether the component is currently faulting

        :return: whether the component is faulting
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    def off(self):
        """
        Turn the component off
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    def standby(self):
        """
        Put the component into low-power standby mode
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    def on(self):
        """
        Turn the component on
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    def reset(self):
        """
        Reset the component (from fault state)
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    action_map = {
        PowerMode.OFF: "component_off",
        PowerMode.STANDBY: "component_standby",
        PowerMode.ON: "component_on",
    }

    def component_power_mode_changed(self, power_mode):
        """
        Callback hook, called when whether the component power mode
        changes

        :param power_mode: the new power mode of the component
        :type power_mode:
            :py:class:`ska_tango_base.control_model.PowerMode`
        """
        action = self.action_map[power_mode]
        self.op_state_model.perform_action(action)

    def component_fault(self):
        """
        Callback hook, called when the component faults
        """
        self.op_state_model.perform_action("component_fault")
