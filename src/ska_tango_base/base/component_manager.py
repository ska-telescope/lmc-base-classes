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
from typing import Any, Optional, Tuple

from ska_tango_base.commands import BaseCommand, ResultCode

from ska_tango_base.control_model import PowerMode
from ska_tango_base.base.task_queue_manager import QueueManager, TaskState


class BaseComponentManager:
    """
    An abstract base class for a component manager for SKA Tango devices.

    It supports:

    * Maintaining a connection to its component

    * Controlling its component via commands like Off(), Standby(),
      On(), etc.

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    """

    def __init__(self, op_state_model, *args, **kwargs):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        """
        self.op_state_model = op_state_model
        self.queue_manager = self.create_queue_manager()

    def start_communicating(self):
        """
        Establish communication with the component, then start monitoring.

        This is the place to do things like:

        * Initiate a connection to the component (if your communication
          is connection-oriented)
        * Subscribe to component events (if using "pull" model)
        * Start a polling loop to monitor the component (if using a
          "push" model)
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    def stop_communicating(self):
        """
        Cease monitoring the component, and break off all communication with it.

        For example,

        * If you are communicating over a connection, disconnect.
        * If you have subscribed to events, unsubscribe.
        * If you are running a polling loop, stop it.
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @property
    def is_communicating(self):
        """
        Return whether communication with the component is established.

        For example:

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
        Power mode of the component.

        :return: the power mode of the component
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @property
    def faulty(self):
        """
        Whether the component is currently faulting.

        :return: whether the component is faulting
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @property
    def tasks_in_queue(self):
        """
        Read the long running commands in the queue.

        :return: tasks in the device queue
        """
        return self.queue_manager.tasks_in_queue

    @property
    def task_ids_in_queue(self):
        """
        Read the IDs of the long running commands in the queue.

        :return: unique ids for the enqueued commands
        """
        return self.queue_manager.task_ids_in_queue

    @property
    def task_status(self):
        """
        Read the status of the currently executing long running commands.

        :return: ID, status pairs of the currently executing commands
        """
        return self.queue_manager.task_status

    @property
    def task_progress(self):
        """
        Read the progress of the currently executing long running command.

        :return: ID, progress of the currently executing command.
        """
        return self.queue_manager.task_progress

    @property
    def task_result(self):
        """
        Read the result of the completed long running command.

        :return: ID, ResultCode, result.
        """
        return list(self.queue_manager.task_result)

    def off(self):
        """Turn the component off."""
        raise NotImplementedError("BaseComponentManager is abstract.")

    def standby(self):
        """Put the component into low-power standby mode."""
        raise NotImplementedError("BaseComponentManager is abstract.")

    def on(self):
        """Turn the component on."""
        raise NotImplementedError("BaseComponentManager is abstract.")

    def reset(self):
        """Reset the component (from fault state)."""
        raise NotImplementedError("BaseComponentManager is abstract.")

    action_map = {
        PowerMode.OFF: "component_off",
        PowerMode.STANDBY: "component_standby",
        PowerMode.ON: "component_on",
    }

    def component_power_mode_changed(self, power_mode):
        """
        Handle notification that the component's power mode has changed.

        This is a callback hook.

        :param power_mode: the new power mode of the component
        :type power_mode:
            :py:class:`ska_tango_base.control_model.PowerMode`
        """
        action = self.action_map[power_mode]
        self.op_state_model.perform_action(action)

    def component_fault(self):
        """
        Handle notification that the component has faulted.

        This is a callback hook.
        """
        self.op_state_model.perform_action("component_fault")

    def create_queue_manager(self) -> QueueManager:
        """Create a QueueManager.

        By default the QueueManager will not have a queue or workers. Thus
        tasks enqueued will block.

        :return: The queue manager.
        :rtype: QueueManager
        """
        return QueueManager(max_queue_size=0, num_workers=0)

    def enqueue(
        self,
        task: BaseCommand,
        argin: Optional[Any] = None,
    ) -> Tuple[str, ResultCode]:
        """Put `task` on the queue. The unique ID for it is returned.

        :param task: The task to execute in the thread
        :type task: BaseCommand
        :param argin: The parameter for the command
        :type argin: Any
        :return: The unique ID of the queued command and the ResultCode
        :rtype: tuple
        """
        return self.queue_manager.enqueue_task(task, argin=argin)

    def abort_tasks(self) -> None:
        """Start aborting tasks on the queue."""
        self.queue_manager.abort_tasks()

    def get_task_state(self, unique_id: str) -> TaskState:
        """Attempt to get state of QueueTask."""
        return self.queue_manager.get_task_state(unique_id)
