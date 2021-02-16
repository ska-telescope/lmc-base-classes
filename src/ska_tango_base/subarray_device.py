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

from tango import DebugIt, DevState
from tango.server import run, attribute, command
from tango.server import device_property

# SKA specific imports
from ska_tango_base import SKAObsDevice, ObsDeviceStateModel
from ska_tango_base.commands import ActionCommand, ResultCode
from ska_tango_base.control_model import AdminMode, ObsState
from ska_tango_base.faults import CapabilityValidationError, StateModelError
from ska_tango_base.state_machine import ObservationStateMachine
from ska_tango_base.utils import for_testing_only

# PROTECTED REGION END #    //  SKASubarray.additionnal_imports

__all__ = ["SKASubarray", "SKASubarrayStateModel", "main"]


class SKASubarrayStateModel(ObsDeviceStateModel):
    """
    Implements the state model for the SKASubarray
    """

    def __init__(
        self,
        logger,
        op_state_callback=None,
        admin_mode_callback=None,
        obs_state_callback=None,
    ):
        """
        Initialises the model. Note that this does not imply moving to
        INIT state. The INIT state is managed by the model itself.

        :param logger: the logger to be used by this state model.
        :type logger: a logger that implements the standard library
            logger interface
        :param op_state_callback: A callback to be called when a
            transition implies a change to op state
        :type op_state_callback: callable
        :param admin_mode_callback: A callback to be called when a
            transition causes a change to device admin_mode
        :type admin_mode_callback: callable
        :param obs_state_callback: A callback to be called when a
            transition causes a change to device obs_state
        :type obs_state_callback: callable
        """
        action_breakdown = {
            # "action": ("action_on_obs_machine", "action_on_superclass"),
            "off_succeeded": ("to_EMPTY", "off_succeeded"),
            "off_failed": ("to_EMPTY", "off_failed"),
            "on_succeeded": (None, "on_succeeded"),
            "on_failed": ("to_EMPTY", "on_failed"),
            "assign_started": ("assign_started", None),
            "release_started": ("release_started", None),
            "resourcing_succeeded_some_resources": (
                "resourcing_succeeded_some_resources",
                None,
            ),
            "resourcing_succeeded_no_resources": (
                "resourcing_succeeded_no_resources",
                None,
            ),
            "resourcing_failed": ("resourcing_failed", None),
            "configure_started": ("configure_started", None),
            "configure_succeeded": ("configure_succeeded", None),
            "configure_failed": ("configure_failed", None),
            "scan_started": ("scan_started", None),
            "scan_succeeded": ("scan_succeeded", None),
            "scan_failed": ("scan_failed", None),
            "end_scan_succeeded": ("end_scan_succeeded", None),
            "end_scan_failed": ("end_scan_failed", None),
            "end_succeeded": ("end_succeeded", None),
            "end_failed": ("end_failed", None),
            "abort_started": ("abort_started", None),
            "abort_succeeded": ("abort_succeeded", None),
            "abort_failed": ("abort_failed", None),
            "obs_reset_started": ("reset_started", None),
            "obs_reset_succeeded": ("reset_succeeded", None),
            "obs_reset_failed": ("reset_failed", None),
            "restart_started": ("restart_started", None),
            "restart_succeeded": ("restart_succeeded", None),
            "restart_failed": ("restart_failed", None),
            "fatal_error": ("fatal_error", None),
        }

        super().__init__(
            action_breakdown,
            ObservationStateMachine,
            logger,
            op_state_callback=op_state_callback,
            admin_mode_callback=admin_mode_callback,
            obs_state_callback=obs_state_callback,
        )


class SKASubarrayResourceManager:
    """
    A simple class for managing subarray resources
    """

    def __init__(self):
        """
        Constructor for SKASubarrayResourceManager
        """
        self._resources = set()

    def __len__(self):
        """
        Returns the number of resources currently assigned. Note that
        this also functions as a boolean method for whether there are
        any assigned resources: ``if len()``.

        :return: number of resources assigned
        :rtype: int
        """
        return len(self._resources)

    def assign(self, resources):
        """
        Assign some resources

        :todo: Currently implemented for testing purposes to take a JSON
            string encoding a dictionary with key 'example'. In future this
            will take a collection of resources.

        :param resources: JSON-encoding of a dictionary, with resources to
            assign under key 'example'
        :type resources: JSON string
        """
        resources_dict = json.loads(resources)
        add_resources = resources_dict['example']
        self._resources |= set(add_resources)

    def release(self, resources):
        """
        Release some resources

        :todo: Currently implemented for testing purposes to take a JSON
            string encoding a dictionary with key 'example'. In future this
            will take a collection of resources.

        :param resources: JSON-encoding of a dictionary, with resources to
            assign under key 'example'
        :type resources: JSON string
        """
        resources_dict = json.loads(resources)
        drop_resources = resources_dict['example']
        self._resources -= set(drop_resources)

    def release_all(self):
        """
        Release all resources
        """
        self._resources.clear()

    def get(self):
        """
        Get current resources

        :return: a set of current resources.
        :rtype: set of string
        """
        return set(self._resources)


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
            device.resource_manager = SKASubarrayResourceManager()
            device._activation_time = 0.0

            # device._configured_capabilities is kept as a
            # dictionary internally. The keys and values will represent
            # the capability type name and the number of instances,
            # respectively.
            try:
                device._configured_capabilities = dict.fromkeys(
                    device.CapabilityTypes,
                    0
                )
            except TypeError:
                # Might need to have the device property be mandatory in the database.
                device._configured_capabilities = {}

            message = "SKASubarray Init command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class _ResourcingCommand(ActionCommand):
        """
        An abstract base class for SKASubarray's resourcing commands.
        """

        def __init__(self, target, state_model, action_hook, logger=None):
            """
            Constructor for _ResourcingCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param action_hook: a hook for the command, used to build
                actions that will be sent to the state model; for example,
                if the hook is "scan", then success of the command will
                result in action "scan_succeeded" being sent to the state
                model.
            :type action_hook: string
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, action_hook, start_action=True, logger=logger
            )

        def succeeded(self):
            """
            Action to take on successful completion of a resourcing
            command.
            """
            if len(self.target):
                action = "resourcing_succeeded_some_resources"
            else:
                action = "resourcing_succeeded_no_resources"
            self.state_model.perform_action(action)

        def failed(self):
            """
            Action to take on failed completion of a resourcing command.
            """
            self.state_model.perform_action("resourcing_failed")

    class AssignResourcesCommand(_ResourcingCommand):
        """
        A class for SKASubarray's AssignResources() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for AssignResourcesCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "assign", logger=logger)

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
            resource_manager = self.target
            resource_manager.assign(argin)

            message = "AssignResources command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ReleaseResourcesCommand(_ResourcingCommand):
        """
        A class for SKASubarray's ReleaseResources() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for OnCommand()

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "release", logger=logger)

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
            resource_manager = self.target
            resource_manager.release(argin)

            message = "ReleaseResources command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ReleaseAllResourcesCommand(ReleaseResourcesCommand):
        """
        A class for SKASubarray's ReleaseAllResources() command.
        """

        def do(self):
            """
            Stateless hook for ReleaseAllResources() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            resource_manager = self.target
            resource_manager.release_all()

            if len(resource_manager):
                message = "ReleaseAllResources command failed to release all."
                self.logger.info(message)
                return (ResultCode.FAILED, message)
            else:
                message = "ReleaseAllResources command completed OK"
                self.logger.info(message)
                return (ResultCode.OK, message)

    class ConfigureCommand(ActionCommand):
        """
        A class for SKASubarray's Configure() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ConfigureCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "configure", start_action=True, logger=logger
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
            device = self.target

            # In this example implementation, the keys of the dict
            # are the capability types, and the values are the
            # integer number of instances required.
            # E.g., config = {"BAND1": 5, "BAND2": 3}
            config = json.loads(argin)
            capability_types = list(config.keys())
            device._validate_capability_types(capability_types)

            # Perform the configuration.
            for capability_type, capability_instances in config.items():
                device._configured_capabilities[capability_type] += capability_instances

            message = "Configure command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ScanCommand(ActionCommand):
        """
        A class for SKASubarray's Scan() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ScanCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "scan", start_action=True, logger=logger
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
            # we do a json.loads just for basic string validation
            message = f"Scan command STARTED - config {json.loads(argin)}"
            self.logger.info(message)
            return (ResultCode.STARTED, message)

    class EndScanCommand(ActionCommand):
        """
        A class for SKASubarray's EndScan() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for EndScanCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "end_scan", logger=logger)

        def do(self):
            """
            Stateless hook for EndScan() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "EndScan command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class EndCommand(ActionCommand):
        """
        A class for SKASubarray's End() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for EndCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "end", logger=logger)

        def do(self):
            """
            Stateless hook for End() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target
            device._deconfigure()

            message = "End command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class AbortCommand(ActionCommand):
        """
        A class for SKASubarray's Abort() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for AbortCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "abort", start_action=True, logger=logger
            )

        def do(self):
            """
            Stateless hook for Abort() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "Abort command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class ObsResetCommand(ActionCommand):
        """
        A class for SKASubarray's ObsReset() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ObsResetCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "obs_reset", start_action=True, logger=logger
            )

        def do(self):
            """
            Stateless hook for ObsReset() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target

            # We might have interrupted a long-running command such as a Configure
            # or a Scan, so we need to clean up from that.

            # Now totally deconfigure
            device._deconfigure()

            message = "ObsReset command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class RestartCommand(ActionCommand):
        """
        A class for SKASubarray's Restart() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for RestartCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`SKASubarrayStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "restart", start_action=True, logger=logger
            )

        def do(self):
            """
            Stateless hook for Restart() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target

            # We might have interrupted a long-running command such as a Configure
            # or a Scan, so we need to clean up from that.

            # Now totally deconfigure
            device._deconfigure()

            # and release all resources
            device.resource_manager.release_all()

            message = "Restart command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    # PROTECTED REGION ID(SKASubarray.class_variable) ENABLED START #
    def _init_state_model(self):
        """
        Sets up the state model for the device
        """
        self.state_model = SKASubarrayStateModel(
            logger=self.logger,
            op_state_callback=self._update_state,
            admin_mode_callback=self._update_admin_mode,
            obs_state_callback=self._update_obs_state,
        )

    def init_command_objects(self):
        """
        Sets up the command objects
        """
        super().init_command_objects()

        device_args = (self, self.state_model, self.logger)
        resource_args = (self.resource_manager, self.state_model, self.logger)

        self.register_command_object(
            "AssignResources", self.AssignResourcesCommand(*resource_args)
        )
        self.register_command_object(
            "ReleaseResources", self.ReleaseResourcesCommand(*resource_args)
        )
        self.register_command_object(
            "ReleaseAllResources", self.ReleaseAllResourcesCommand(*resource_args)
        )
        self.register_command_object("Configure", self.ConfigureCommand(*device_args))
        self.register_command_object("Scan", self.ScanCommand(*device_args))
        self.register_command_object("EndScan", self.EndScanCommand(*device_args))
        self.register_command_object("End", self.EndCommand(*device_args))
        self.register_command_object("Abort", self.AbortCommand(*device_args))
        self.register_command_object("ObsReset", self.ObsResetCommand(*device_args))
        self.register_command_object("Restart", self.RestartCommand(*device_args))

    def _validate_capability_types(self, capability_types):
        """
        Check the validity of the input parameter passed to the
        Configure command.

        :param device: the device for which this class implements
            the configure command
        :type device: :py:class:`SKASubarray`
        :param capability_types: a list strings representing
            capability types.
        :type capability_types: list

        :raises CapabilityValidationError: If any of the capabilities
            requested are not valid.
        """
        invalid_capabilities = list(
            set(capability_types) - set(self._configured_capabilities))

        if invalid_capabilities:
            raise CapabilityValidationError(
                "Invalid capability types requested {}".format(
                    invalid_capabilities
                )
            )

    def _deconfigure(self):
        """
        Completely deconfigure the subarray
        """
        self._configured_capabilities = {k: 0 for k in self._configured_capabilities}

    # -----------------
    # Device Properties
    # -----------------
    CapabilityTypes = device_property(
        dtype=('str',),
    )

    SubID = device_property(
        dtype='str',
    )

    # ----------
    # Attributes
    # ----------
    activationTime = attribute(
        dtype='double',
        unit="s",
        standard_unit="s",
        display_unit="s",
        doc="Time of activation in seconds since Unix epoch.",
    )

    assignedResources = attribute(
        dtype=('str',),
        max_dim_x=100,
        doc="The list of resources assigned to the subarray.",
    )

    configuredCapabilities = attribute(
        dtype=('str',),
        max_dim_x=10,
        doc="A list of capability types with no. of instances "
            "in use on this subarray; "
            "e.g.\nCorrelators:512, PssBeams:4, "
            "PstBeams:4, VlbiBeams:0.",
    )

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
        return sorted(self.resource_manager.get())
        # PROTECTED REGION END #    //  SKASubarray.assignedResources_read

    def read_configuredCapabilities(self):
        # PROTECTED REGION ID(SKASubarray.configuredCapabilities_read) ENABLED START #
        """
        Reads capabilities configured in the Subarray.

        :return: A list of capability types with no. of instances used
            in the Subarray
        """
        configured_capabilities = []
        for capability_type, capability_instances in list(
            self._configured_capabilities.items()
        ):
            configured_capabilities.append(
                "{}:{}".format(capability_type, capability_instances))
        return sorted(configured_capabilities)
        # PROTECTED REGION END #    //  SKASubarray.configuredCapabilities_read

    # --------
    # Commands
    # --------

    def is_AssignResources_allowed(self):
        """
        Check if command `AssignResources` is allowed in the current
        device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("AssignResources")
        return command.check_allowed()

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to add to subarray",
        dtype_out='DevVarLongStringArray',
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
        (return_code, message) = command(argin)
        return [[return_code], [message]]

    def is_ReleaseResources_allowed(self):
        """
        Check if command `ReleaseResources` is allowed in the current
        device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ReleaseResources")
        return command.check_allowed()

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to remove from the subarray",
        dtype_out='DevVarLongStringArray',
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
        (return_code, message) = command(argin)
        return [[return_code], [message]]

    def is_ReleaseAllResources_allowed(self):
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ReleaseAllResources")
        return command.check_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
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

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Configure")
        return command.check_allowed()

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the scan configuration",
        dtype_out='DevVarLongStringArray',
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
        (return_code, message) = command(argin)
        return [[return_code], [message]]

    def is_Scan_allowed(self):
        """
        Check if command `Scan` is allowed in the current device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Scan")
        return command.check_allowed()

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
        (return_code, message) = command(argin)
        return [[return_code], [message]]

    def is_EndScan_allowed(self):
        """
        Check if command `EndScan` is allowed in the current device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("EndScan")
        return command.check_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
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

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("End")
        return command.check_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
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

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Abort")
        return command.check_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
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

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ObsReset")
        return command.check_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
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

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Restart")
        return command.check_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
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


if __name__ == '__main__':
    main()
