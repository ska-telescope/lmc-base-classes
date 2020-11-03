# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementObsDevice project
#

""" CspSubElementObsDevice

General observing device for SKA CSP Subelement.
"""

# PROTECTED REGION ID(CspSubElementObsDevice.additionnal_import) ENABLED START #
import json
import warnings

# Tango imports 
import tango
from tango import DebugIt, DevState, AttrWriteType
from tango.server import run, attribute, command, device_property

# SKA specific imports
from ska.base import SKAObsDevice, DeviceStateModel
from ska.base.commands import ResultCode, ResponseCommand, ActionCommand
from ska.base.control_model import ObsState
from ska.base.csp_subelement_state_machine import CspObservationStateMachine
from ska.base.faults import StateModelError
from ska.base.utils import for_testing_only
# PROTECTED REGION END #    //  CspSubElementObsDevice.additionnal_import

__all__ = ["CspSubElementObsDevice", "CspSubElementObsDeviceStateModel", "main"]

class CspSubElementObsDeviceStateModel(DeviceStateModel):
    """
    Implements the state model for the CspSubElementObsDevice
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
        super().__init__(
            logger,
            op_state_callback=op_state_callback,
            admin_mode_callback=admin_mode_callback,
        )

        self._obs_state = None
        self._obs_state_callback = obs_state_callback

        self._observation_state_machine = CspObservationStateMachine(
            self._update_obs_state
        )

    @property
    def obs_state(self):
        """
        Returns the obs_state

        :returns: obs_state of this state model
        :rtype: ObsState
        """
    def _update_obs_state(self, machine_state):
        """
        Helper method that updates obs_state whenever the observation
        state machine reports a change of state, ensuring that the
        callback is called if one exists.

        :param machine_state: the new state of the observation state
            machine
        :type machine_state: str
        """
        obs_state = ObsState[machine_state]
        if self._obs_state != obs_state:
            self._obs_state = obs_state
            if self._obs_state_callback is not None:
                self._obs_state_callback(obs_state)

    __action_breakdown = {
        # "action": ("action_on_obs_machine", "action_on_superclass"),
        "off_succeeded": ("to_IDLE", "off_succeeded"),
        "off_failed": ("to_IDLE", "off_failed"),
        "on_succeeded": (None, "on_succeeded"),
        "on_failed": ("to_IDLE", "on_failed"),
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
        "obs_reset_succeeded": ("reset_succeeded", None),
        "obs_reset_failed": ("reset_failed", None),
    }

    def _is_obs_action_allowed(self, action):
        if action not in self.__action_breakdown:
            return None

        if self.op_state != DevState.ON:
            return False

        (obs_action, super_action) = self.__action_breakdown[action]

        if obs_action not in self._observation_state_machine.get_triggers(
            self._observation_state_machine.state
        ):
            return False
        return super_action is None or super().is_action_allowed(super_action)

    def is_action_allowed(self, action):
        """
        Whether a given action is allowed in the current state.

        :param action: an action, as given in the transitions table
        :type action: ANY

        :returns: where the action is allowed in the current state:
        :rtype: bool: True if the action is allowed, False if it is
            not allowed
        :raises StateModelError: for an unrecognised action
        """
        obs_allowed = self._is_obs_action_allowed(action)
        if obs_allowed is None:
            return super().is_action_allowed(action)
        if obs_allowed:
            return True
        try:
            return super().is_action_allowed(action)
        except StateModelError:
            return False

    def try_action(self, action):
        """
        Checks whether a given action is allowed in the current state,
        and raises a StateModelError if it is not.

        :param action: an action, as given in the transitions table
        :type action: str

        :raises StateModelError: if the action is not allowed in the
            current state

        :returns: True if the action is allowed
        :rtype: boolean
        """
        if not self.is_action_allowed(action):
            raise StateModelError(
                f"Action {action} is not allowed in operational state "
                f"{self.op_state}, admin mode {self.admin_mode}, "
                f"observation state {self.obs_state}."
            )
        return True

    def perform_action(self, action):
        """
        Performs an action on the state model

        :param action: an action, as given in the transitions table
        :type action: ANY

        :raises StateModelError: if the action is not allowed in the
            current state

        """
        self.try_action(action)

        if self._is_obs_action_allowed(action):
            (obs_action, super_action) = self.__action_breakdown[action]

            if obs_action == "to_IDLE":
                message = (
                    "Changing device state of a non-IDLE observing device "
                    "should only be done as an emergency measure and may be "
                    "disallowed in future."
                )
                self.logger.warning(message)
                warnings.warn(message, PendingDeprecationWarning)

            self._observation_state_machine.trigger(obs_action)
            if super_action is not None:
                super().perform_action(super_action)
        else:
            super().perform_action(action)

    @for_testing_only
    def _straight_to_state(self, op_state=None, admin_mode=None, obs_state=None):
        """
        Takes the SKASubarrayStateModel straight to the specified states.
        This method exists to simplify testing; for example, if testing
        that a command may be run in a given state, one can push the
        state model straight to that state, rather than having to drive
        it to that state through a sequence of actions. It is not
        intended that this method would be called outside of test
        setups. A warning will be raised if it is.

        Note that this method will allow you to put the device into an
        incoherent combination of states and modes (e.g. adminMode
        OFFLINE, opState STANDBY, and obsState SCANNING).

        :param op_state: the target operational state (optional)
        :type op_state: :py:class:`tango.DevState`
        :param admin_mode: the target admin mode (optional)
        :type admin_mode: :py:class:`~ska.base.control_model.AdminMode`
        :param obs_state: the target observation state (optional)
        :type obs_state: :py:class:`~ska.base.control_model.ObsState`
        """
        if obs_state is not None:
            getattr(self._observation_state_machine, f"to_{obs_state.name}")()
        super()._straight_to_state(op_state=op_state, admin_mode=admin_mode)


class CspSubElementObsDevice(SKAObsDevice):
    """
    General observing device for SKA CSP Subelement.

    **Properties:**

    - Device Property
        DeviceID
            - Identification number of the observing device.
            - Type:'DevUShort'
    """
    # PROTECTED REGION ID(CspSubElementObsDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubElementObsDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    DeviceID = device_property(
        dtype='DevUShort',
    )

    # ----------
    # Attributes
    # ----------

    subarrayMembership = attribute(
        dtype=('DevUShort',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=16,
        label="subarrayMembership",
        doc="Identification number of the affilaited subarray.\nImplemented an array because"
            " some  devices can be shared among several subarrays.\n",
    )

    scanID = attribute(
        dtype='DevULong64',
        label="scanID",
        doc="The scan identification number to be inserted in the output\nproducts.",
    )

    configurationID = attribute(
        dtype='DevString',
        label="configurationID",
        doc="The configuration ID specified into the JSON configuration.",
    )

    lastScanConfiguration = attribute(
        dtype='DevString',
        label="lastScanConfiguration",
        doc="The last valid scan configuration.",
    )

    sdpDestinationAddresses = attribute(
        dtype='DevString',
        label="sdpDestinationAddresses",
        doc="JSON formatted string\nReport the list of all the SDP addresses provided by SDP"
            " to receive the output products.\nSpecifies the Mac, IP, Port for each resource:\nCBF:"
            " visibility channels\nPSS ? Pss pipelines\nPST ? PSTBeam\nNot used by al CSP Sub-element"
            " observing device (for ex. Mid CBF VCCs)",
    )

    sdpLinkCapacity = attribute(
        dtype='DevFloat',
        label="sdpLinkCapacity",
        doc="The SDP link capavity in GB/s.",
    )

    sdpLinkActive = attribute(
        dtype=('DevBoolean',),
        max_dim_x=100,
        label="sdpLinkActive",
        doc="Flag reporting if the SDP link is active.\nTrue: active\nFalse:down",
    )

    # ---------------
    # General methods
    # ---------------

    def _init_state_model(self):
        """
        Sets up the state model for the device
        """
        self.state_model = CspSubElementObsDeviceStateModel(
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
        self.register_command_object(
            "ConfigureScan", self.ConfigureScanCommand(*device_args)
        )
        self.register_command_object(
            "Scan", self.ScanCommand(*device_args)
        )
        self.register_command_object(
            "EndScan", self.EndScanCommand(*device_args)
        )
        self.register_command_object(
            "GoToIdle", self.GoToIdleCommand(*device_args)
        )
        self.register_command_object(
            "Abort", self.AbortCommand(*device_args)
        )
        self.register_command_object(
            "ObsReset", self.ObsResetCommand(*device_args)
        )
    
    class InitCommand(SKAObsDevice.InitCommand):
        """
        A class for the CspSubElementObsDevice's init_device() "command".
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
            device._obs_state = ObsState.IDLE
            device._scan_id = 0
            device._subarray_id = [0,]

            device._sdp_addresses = {"outputHost":[], "outputMac": [], "outputPort":[]}
            device._sdp_links_active = [False,]
            device._sdp_link_capacity = 0.

            device._config_id = ''
            device._last_scan_configuration = ''

            message = "CspSubElementObsDevice Init command completed OK"
            device.logger.info(message)
            return (ResultCode.OK, message)

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(CspSubElementObsDevice.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementObsDevice.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(CspSubElementObsDevice.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementObsDevice.delete_device
    # ------------------
    # Attributes methods
    # ------------------

    def read_subarrayMembership(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.subarrayMembership_read) ENABLED START #
        """Return the subarrayMembership attribute."""
        return self._subarray_id
        # PROTECTED REGION END #    //  CspSubElementObsDevice.subarrayMembership_read
        
    def write_subarrayMembership(self, value):
        # PROTECTED REGION ID(CspSubElementObsDevice.subarrayMembership_write) ENABLED START #
        """Set the subarrayMembership attribute."""
        self._subarray_id = value
        # PROTECTED REGION END #    //  CspSubElementObsDevice.subarrayMembership_write

    def read_scanID(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.scanID_read) ENABLED START #
        """Return the scanID attribute."""
        return self._scan_id 
        # PROTECTED REGION END #    //  CspSubElementObsDevice.scanID_read

    def read_configurationID(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.configurationID_read) ENABLED START #
        """Return the configurationID attribute."""
        return self._config_id
        # PROTECTED REGION END #    //  CspSubElementObsDevice.configurationID_read

    def read_lastScanConfiguration(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.lastScanConfiguration_read) ENABLED START #
        """Return the lastScanConfiguration attribute."""
        return self._last_scan_configuration
        # PROTECTED REGION END #    //  CspSubElementObsDevice.lastScanConfiguration_read

    def read_sdpDestinationAddresses(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.sdpDestinationAddresses_read) ENABLED START #
        """Return the sdpDestinationAddresses attribute."""
        return json.dumps(self._sdp_addresses)
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpDestinationAddresses_read

    def read_sdpLinkCapacity(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.sdpLinkCapacity_read) ENABLED START #
        """Return the sdpLinkCapacity attribute."""
        return self._sdp_link_capacity
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpLinkCapacity_read

    def read_sdpLinkActive(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.sdpLinkActive_read) ENABLED START #
        """Return the sdpLinkActive attribute."""
        return self._sdp_link_active
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpLinkActive_read

    # --------
    # Commands
    # --------

    class ConfigureScanCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's ConfigureScan command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ConfigureScanCommand

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
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
            Stateless hook for ConfigureScan() command functionality.

            :param argin: The configuration as JSON formatted string
            :type argin: str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target
            result_code, msg = self.validate_configuration_data(argin)
            if result_code == ResultCode.FAILED:
                return (result_code, msg)
            # store the configuration on command success
            device._last_valid_configuration = argin
            return (ResultCode.OK, "Configure command completed OK")

        def validate_configuration_data(self, argin):
            """
            Validate the configuration parameters against allowed values, as needed.
            :param argin:
                The JSON formatted string with configuration for the device.
            : type argin: 'DevString'
            :return: A tuple containing a return code and a string message.
            :rtype: (ResultCode, str)
            """
            device = self.target
            try: 
                configuration_dict = json.loads(argin)
                device._config_id = configuration_dict['id']
            except Exception:
                return (ResultCode.FAILED, "No configuration ID specified")
            return (ResultCode.OK, "Configuration validated with success")

    class ScanCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's Scan command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ScanCommand

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
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

            :param argin: The scan ID.
            :type argin: str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target
            if not argin.isdigit():
                return (ResultCode.FAILED, "Scan argument is not an integer")
            device._scan_id = int(argin)
            return (ResultCode.STARTED, "Scan command started")
        
    class EndScanCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's EndScan command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for EndScanCommand

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "end_scan", logger=logger
            )

        def do(self):
            """
            Stateless hook for EndScan() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            return (ResultCode.OK, "EndScan command completed OK")
        
    class GoToIdleCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's GoToIdle command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for GoToIdle Command.

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "end", logger=logger
            )

        def do(self):
            """
            Stateless hook for GoToIdle() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target
            # reset to default values the configurationID and scanID
            device._config_id = ''
            device._scan_id = 0
            return (ResultCode.OK, "GoToIdle command completed OK")
        

    class ObsResetCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's ObsReset command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ObsReset Command.

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "obs_reset", logger=logger
            )

        def do(self):
            """
            Stateless hook for ObsReset() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "ObsReset command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)
        

    class AbortCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's Abort command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for Abort Command.

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
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
            return (ResultCode.OK, "Abort command completed OK")
        
    @command(
        dtype_in='DevString',
        doc_in="JSON formatted string with the scan configuration.",
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status. "
                "The message is for information purpose only.",
    )
    @DebugIt()
    def ConfigureScan(self, argin):
        # PROTECTED REGION ID(CspSubElementObsDevice.ConfigureScan) ENABLED START #
        """
        Configure the observing device parameters for the current scan.

        :param argin: JSON formatted string with the scan configuration.
        :type argin: 'DevString'

        :return:
            A tuple containing a return code and a string message indicating status. 
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("ConfigureScan")
        (return_code, message) = command(argin)
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.ConfigureScan

    @command(
        dtype_in='DevString',
        doc_in="A string with the scan ID",
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(CspSubElementObsDevice.Scan) ENABLED START #
        """
        Start an observing scan.

        :param argin: A string with the scan ID
        :type argin: 'DevString'

        :return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Scan")
        (return_code, message) = command(argin)
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.Scan

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.EndScan) ENABLED START #
        """
        End a running scan.

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("EndScan")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.EndScan

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string  message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def GoToIdle(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.GoToIdle) ENABLED START #
        """
        Transit the device from READY to IDLE obsState.

        :return:
            A tuple containing a return code and a string  message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("GoToIdle")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.GoToIdle

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def ObsReset(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.ObsReset) ENABLED START #
        """
        Reset the observing device from a FAULT/ABORTED obsState to IDLE.

        :return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("ObsReset")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.ObsReset

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.Abort) ENABLED START #
        """
        Abort the current observing process and move the device
        to ABORTED obsState.

        :return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Abort")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.Abort

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the CspSubElementObsDevice module."""
    # PROTECTED REGION ID(CspSubElementObsDevice.main) ENABLED START #
    return run((CspSubElementObsDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubElementObsDevice.main


if __name__ == '__main__':
    main()
