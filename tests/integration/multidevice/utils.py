"""Multi device test utils."""
import logging
import uuid
from ast import List
from dataclasses import dataclass
from typing import Any, Callable, Dict

import tango
from tango import EventData, EventType


@dataclass
class StoredCommand:
    """
    Used to keep track of commands scheduled across devices.

    command_name: The Tango command to execute across devices.
    command_id: Every Tango device will return the command ID for the
    long running command submitted to it.
    is_completed: Whether the command is done or not
    """

    command_name: str
    command_id: str
    is_completed: bool


class LongRunningDeviceInterface:
    """
    This class is a convenience class for long running command devices.

    The intent of this class is that clients should not have to keep
    track of command IDs or the various attributes
    to determine long running command progress/results.

    This class is also useful when you want to run a long running
    command across various devices. Once they all complete a callback
    supplied by the user is fired.

    Using this class, a client would need to:
    - Supply the Tango devices to connect to that implements long
    running commands
    - The Long running commands to run (including parameter)
    - Optional callback that should be executed when the command
    completes

    The callback will be executed once the command completes across all
    devices. Thus there's no need to watch attribute changes or keep
    track of commands IDs. They are handled here.
    """

    def __init__(self, tango_devices: List, logger: logging.Logger):
        """Init LRC device interface."""
        self._logger = logger
        self._tango_devices = tango_devices
        self._long_running_device_proxies = []
        self._result_subscriptions = []
        self._stored_commands: Dict[str, List[StoredCommand]] = {}
        self._stored_callbacks: Dict[str, Callable] = {}

    def setup(self):
        """Only create the device proxy and subscribe when a command is invoked."""
        if not self._long_running_device_proxies:
            for device in self._tango_devices:
                self._long_running_device_proxies.append(tango.DeviceProxy(device))

        if not self._result_subscriptions:
            for device_proxy in self._long_running_device_proxies:
                self._result_subscriptions.append(
                    device_proxy.subscribe_event(
                        "longRunningCommandResult",
                        EventType.CHANGE_EVENT,
                        self,
                        wait=True,
                    )
                )

    def push_event(self, ev: EventData):
        """
        Handle the attribute change events.

        For every event that comes in:

        - Update command state:
            - Make sure that it's a longRunningCommandResult
            - Check to see if the command ID we get from the event
                is one we are keeping track of.
            - If so, set that command to completed

        - Check if we should fire the callback:
            Once the command across all devices have completed
            (for that command)
            - Check whether all have completed
            - If so, fire the callback
            - Clean up
        """
        if ev.err:
            self._logger.error("Event system DevError(s) occured: %s", str(ev.errors))
            return

        if ev.attr_value and ev.attr_value.name == "longrunningcommandresult":
            if ev.attr_value.value:
                # push change event to new attribute for all tango devices
                # for tango_dev in self._tango_devices:
                #     tango_dev.push_change_event("lastResultCommandIDs", ev.attr_value.value[0])
                #     tango_dev.push_change_event("lastResultCommandName", ev.attr_value.value[1])

                event_command_id = ev.attr_value.value[0]
                for stored_commands in self._stored_commands.values():
                    for stored_command in stored_commands:
                        if stored_command.command_id == event_command_id:
                            stored_command.is_completed = True

        completed_group_keys = []
        for key, stored_command_group in self._stored_commands.items():
            if stored_command_group:
                # Determine if all the commands in this group have completed
                commands_are_completed = [
                    stored_command.is_completed
                    for stored_command in stored_command_group
                ]
                if all(commands_are_completed):
                    completed_group_keys.append(key)

                    # Get the command IDs
                    command_ids = [
                        stored_command.command_id
                        for stored_command in stored_command_group
                    ]
                    command_name = stored_command_group[0].command_name

                    # Trigger the callback, send command_name and command_ids
                    # as paramater
                    self._stored_callbacks[key](command_name, command_ids)
                    # Remove callback as the group completed

        # Clean up
        # Remove callback and commands no longer needed
        for key in completed_group_keys:
            del self._stored_callbacks[key]
            del self._stored_commands[key]

    def execute_long_running_command(
        self,
        command_name: str,
        command_arg: Any = None,
        on_completion_callback: Callable = None,
    ):
        """
        Execute the long running command with an argument if any.

        Once the commmand completes, then the `on_completion_callback`
        will be executed with the EventData as parameter.
        This class keeps track of the command ID and events
        used to determine when this commmand has completed.

        :param command_name: A long running command that exists on the
            target Tango device.
        :type command_name: str
        :param command_arg: The argument to be used in the long running
            command method.
        :type command_arg: Any, optional
        :param on_completion_callback: The method to execute when the
            long running command has completed.
        :type on_completion_callback: callable, optional
        """
        self.setup()
        unique_id = uuid.uuid4()
        self._stored_callbacks[unique_id] = on_completion_callback
        self._stored_commands[unique_id] = []
        for device_proxy in self._long_running_device_proxies:
            _, command_id = device_proxy.command_inout(command_name, command_arg)
            self._stored_commands[unique_id].append(
                StoredCommand(
                    command_name,
                    command_id,
                    False,
                )
            )
