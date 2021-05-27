# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
""" SKASubarray

A SubArray handling device. It allows the assigning/releasing of resources
into/from Subarray, configuring capabilities, and exposes the related
information like assigned resources, configured capabilities, etc.
"""
# PROTECTED REGION ID(SKASubarray.additionnal_import) ENABLED START #
import json
import warnings

from tango import DebugIt
from tango.server import run, attribute, command
from tango.server import device_property

# SKA specific imports
from ska_tango_base import SKAObsDevice
from ska_tango_base.commands import (
    CompletionCommand,
    ObservationCommand,
    ResponseCommand,
    ResultCode,
)
from ska_tango_base.subarray import SubarrayComponentManager, SubarrayObsStateModel

# PROTECTED REGION END #    //  SKASubarray.additionnal_imports

__all__ = ["SKASubarray", "main"]


class SKASubarray(SKAObsDevice):
    """
    Implements the SKA SubArray device
    """

    class InitCommand(SKAObsDevice.InitCommand):
        """
        A class for the SKASubarray's init_device() "command".
        """

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            super().do()

            device = self.target
            device._activation_time = 0.0

            message = "SKASubarray Init command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class AssignResourcesCommand(
        ObservationCommand, ResponseCommand, CompletionCommand
    ):
        """
        A class for SKASubarray's AssignResources() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for AssignResourcesCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "assign", op_state_model, logger=logger
            )

        def do(self, argin):
            """
            Stateless hook for AssignResources() command functionality.

            :param argin: The resources to be assigned
            :type argin: list of str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.assign(argin)

            message = "AssignResources command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ReleaseResourcesCommand(
        ObservationCommand, ResponseCommand, CompletionCommand
    ):
        """
        A class for SKASubarray's ReleaseResources() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for ReleaseResourcesCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "release", op_state_model, logger=logger
            )

        def do(self, argin):
            """
            Stateless hook for ReleaseResources() command functionality.

            :param argin: The resources to be released
            :type argin: list of str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.release(argin)

            message = "ReleaseResources command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ReleaseAllResourcesCommand(
        ObservationCommand, ResponseCommand, CompletionCommand
    ):
        """
        A class for SKASubarray's ReleaseAllResources() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for ReleaseResourcesCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "release", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for ReleaseAllResources() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.release_all()

            message = "ReleaseAllResources command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ConfigureCommand(ObservationCommand, ResponseCommand, CompletionCommand):
        """
        A class for SKASubarray's Configure() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for ConfigureCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "configure", op_state_model, logger=logger
            )

        def do(self, argin):
            """
            Stateless hook for Configure() command functionality.

            :param argin: The configuration as JSON
            :type argin: str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.configure(argin)

            message = "Configure command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ScanCommand(ObservationCommand, ResponseCommand):
        """
        A class for SKASubarray's Scan() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for ScanCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "scan", op_state_model, logger=logger
            )

        def do(self, argin):
            """
            Stateless hook for Scan() command functionality.

            :param argin: Scan info
            :type argin: str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.scan(argin)

            message = f"Scan command started"
            self.logger.info(message)
            return (ResultCode.STARTED, message)

    class EndScanCommand(ObservationCommand, ResponseCommand):
        """
        A class for SKASubarray's EndScan() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for EndScanCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "end_scan", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for EndScan() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.end_scan()

            message = "EndScan command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class EndCommand(ObservationCommand, ResponseCommand):
        """
        A class for SKASubarray's End() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for EndCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "end", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for End() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.deconfigure()

            message = "End command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class AbortCommand(ObservationCommand, ResponseCommand, CompletionCommand):
        """
        A class for SKASubarray's Abort() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for AbortCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "abort", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for Abort() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.abort()

            message = "Abort command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ObsResetCommand(ObservationCommand, ResponseCommand, CompletionCommand):
        """
        A class for SKASubarray's ObsReset() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for ObsResetCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "obsreset", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for ObsReset() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.obsreset()

            message = "ObsReset command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class RestartCommand(ObservationCommand, ResponseCommand, CompletionCommand):
        """
        A class for SKASubarray's Restart() command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for RestartCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "restart", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for Restart() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.restart()

            message = "Restart command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    # PROTECTED REGION ID(SKASubarray.class_variable) ENABLED START #
    def _init_state_model(self):
        """
        Sets up the state model for the device
        """
        super()._init_state_model()
        self.obs_state_model = SubarrayObsStateModel(
            logger=self.logger, callback=self._update_obs_state
        )

    def create_component_manager(self):
        return SubarrayComponentManager(self.op_state_model, self.obs_state_model)

    def init_command_objects(self):
        """
        Sets up the command objects
        """
        super().init_command_objects()

        for (command_name, command_class) in [
            ("AssignResources", self.AssignResourcesCommand),
            ("ReleaseResources", self.ReleaseResourcesCommand),
            ("ReleaseAllResources", self.ReleaseAllResourcesCommand),
            ("Configure", self.ConfigureCommand),
            ("Scan", self.ScanCommand),
            ("EndScan", self.EndScanCommand),
            ("End", self.EndCommand),
            ("Abort", self.AbortCommand),
            ("ObsReset", self.ObsResetCommand),
            ("Restart", self.RestartCommand),
        ]:
            self.register_command_object(
                command_name,
                command_class(
                    self.component_manager,
                    self.op_state_model,
                    self.obs_state_model,
                    self.logger,
                ),
            )

    # -----------------
    # Device Properties
    # -----------------
    CapabilityTypes = device_property(
        dtype=("str",),
    )

    SubID = device_property(
        dtype="str",
    )

    # ----------
    # Attributes
    # ----------
    activationTime = attribute(
        dtype="double",
        unit="s",
        standard_unit="s",
        display_unit="s",
        doc="Time of activation in seconds since Unix epoch.",
    )
    """Device attribute."""

    assignedResources = attribute(
        dtype=("str",),
        max_dim_x=100,
        doc="The list of resources assigned to the subarray.",
    )
    """Device attribute."""

    configuredCapabilities = attribute(
        dtype=("str",),
        max_dim_x=10,
        doc="A list of capability types with no. of instances "
        "in use on this subarray; "
        "e.g.\nCorrelators:512, PssBeams:4, "
        "PstBeams:4, VlbiBeams:0.",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------
    def always_executed_hook(self):
        # PROTECTED REGION ID(SKASubarray.always_executed_hook) ENABLED START #
        """
        Method that is always executed before any device command gets executed.
        """
        pass
        # PROTECTED REGION END #    //  SKASubarray.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKASubarray.delete_device) ENABLED START #
        """
        Method to cleanup when device is stopped.
        """
        pass
        # PROTECTED REGION END #    //  SKASubarray.delete_device

    # ------------------
    # Attributes methods
    # ------------------
    def read_activationTime(self):
        # PROTECTED REGION ID(SKASubarray.activationTime_read) ENABLED START #
        """
        Reads the time since device is activated.

        :return: Time of activation in seconds since Unix epoch.
        """
        return self._activation_time
        # PROTECTED REGION END #    //  SKASubarray.activationTime_read

    def read_assignedResources(self):
        # PROTECTED REGION ID(SKASubarray.assignedResources_read) ENABLED START #
        """
        Reads the resources assigned to the device.

        :return: Resources assigned to the device.
        """
        return self.component_manager.assigned_resources  # pylint: disable=no-member
        # PROTECTED REGION END #    //  SKASubarray.assignedResources_read

    def read_configuredCapabilities(self):
        # PROTECTED REGION ID(SKASubarray.configuredCapabilities_read) ENABLED START #
        """
        Reads capabilities configured in the Subarray.

        :return: A list of capability types with no. of instances used
            in the Subarray
        """
        return (
            self.component_manager.configured_capabilities  # pylint: disable=no-member
        )
        # PROTECTED REGION END #    //  SKASubarray.configuredCapabilities_read

    # --------
    # Commands
    # --------

    def is_AssignResources_allowed(self):
        """
        Check if command `AssignResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("AssignResources")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to add to subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        Assign resources to this subarray

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: the resources to be assigned
        :type argin: list of str

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("AssignResources")
        args = json.loads(argin)
        (return_code, message) = command(args)
        return [[return_code], [message]]

    def is_ReleaseResources_allowed(self):
        """
        Check if command `ReleaseResources` is allowed in the current
        device state

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ReleaseResources")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to remove from the subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """
        Delta removal of assigned resources.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: the resources to be released
        :type argin: list of str

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("ReleaseResources")
        args = json.loads(argin)
        (return_code, message) = command(args)
        return [[return_code], [message]]

    def is_ReleaseAllResources_allowed(self):
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ReleaseAllResources")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def ReleaseAllResources(self):
        """
        Remove all resources to tear down to an empty subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("ReleaseAllResources")
        (return_code, message) = command()
        return [[return_code], [message]]

    def is_Configure_allowed(self):
        """
        Check if command `Configure` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Configure")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the scan configuration",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Configure(self, argin):
        """
        Configures the capabilities of this subarray

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: configuration specification
        :type argin: string

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Configure")
        args = json.loads(argin)
        (return_code, message) = command(args)
        return [[return_code], [message]]

    def is_Scan_allowed(self):
        """
        Check if command `Scan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Scan")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the per-scan configuration",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Scan(self, argin):
        """
        Start scanning

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Information about the scan
        :type argin: Array of str

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Scan")
        args = json.loads(argin)
        (return_code, message) = command(args)
        return [[return_code], [message]]

    def is_EndScan_allowed(self):
        """
        Check if command `EndScan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("EndScan")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def EndScan(self):
        """
        End the scan

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("EndScan")
        (return_code, message) = command()
        return [[return_code], [message]]

    def is_End_allowed(self):
        """
        Check if command `End` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("End")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def End(self):
        # PROTECTED REGION ID(SKASubarray.EndSB) ENABLED START #
        """
        End the scan block.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("End")
        (return_code, message) = command()
        return [[return_code], [message]]

    def is_Abort_allowed(self):
        """
        Check if command `Abort` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Abort")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Abort(self):
        """
        Abort any long-running command such as ``Configure()`` or
        ``Scan()``.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Abort")
        (return_code, message) = command()
        return [[return_code], [message]]

    def is_ObsReset_allowed(self):
        """
        Check if command `ObsReset` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ObsReset")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def ObsReset(self):
        """
        Reset the current observation process.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("ObsReset")
        (return_code, message) = command()
        return [[return_code], [message]]

    def is_Restart_allowed(self):
        """
        Check if command `Restart` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Restart")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Restart(self):
        """
        Restart the subarray. That is, deconfigure and release
        all resources.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Restart")
        (return_code, message) = command()
        return [[return_code], [message]]


# ----------
# Run server
# ----------
def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKASubarray.main) ENABLED START #
    """
    Main entry point of the module.

    :param args: positional args to tango.server.run
    :param kwargs: named args to tango.server.run

    :return: exit code
    """
    return run((SKASubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKASubarray.main


if __name__ == "__main__":
    main()
