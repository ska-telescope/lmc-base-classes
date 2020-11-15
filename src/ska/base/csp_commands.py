"""
This module provides an abstract base class for a specialized command
derived from the ActionCommand.
This command class implements the validation of the input arguments of a command.
It also provides the possibility to recover the initial state, the one before the 
command was invoked, when wrong input parameters are specified.
"""
import logging
from ska.base.commands import ActionCommand, ResultCode
from ska.base.faults import CommandError, ResultCodeError, StateModelError

module_logger = logging.getLogger(__name__)

class InputValidatedCommand(ActionCommand):
    """
    Abstract base class for a tango command, which validates 
    the input args of a command and restores the original observing state
    when the validation fails throwing an exception.
    """
    def __init__(
        self, target, state_model, action_hook, start_action=False, logger=None
    ):
        """
        Create a new InputValidatedCommand for a device.

        :param target: the object that this base command acts upon. 
        :type target: object
        :param action_hook: a hook for the command, used to build
            actions that will be sent to the state model; for example,
            if the hook is "scan", then success of the command will
            result in action "scan_succeeded" being sent to the state
            model.
        :type action_hook: string
        :param start_action: whether the state model supports a start
            action (i.e. to put the state model into an transient state
            while the command is running); default False
        :type start_action: boolean
        :param logger: the logger to be used by this Command. If not
            provided, then a default module logger will be used.
        :type logger: a logger that implements the standard library
            logger interface
        """
        super().__init__(target, state_model, action_hook, start_action, logger=logger)
        # _validation_success: flag to signal if the input argument of a command are valid.
        self._validation_success = False
        self._rejected_hook = f"{action_hook}_rejected"
        # destination and source machine state: used to re-store the state before the
        # command execution, when this fails for bad input arguments.
        self._machine_dest = "IDLE"
        self._machine_source = "IDLE"

    def _call_do(self, argin=None):
        """
        Helper method that ensures the validation of command arguments,
        if specified, is performed before the ``do`` method call.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY
        """
        if argin is None:
            (return_code, message) = self.do()
        else:
            (return_code, message)= self.validate_input(argin)
            if return_code == ResultCode.FAILED:
                return (return_code, message)
            self._validation_success = True
            (return_code, message) = self.do(argin=argin)
        self.logger.info(
            f"Exiting command {self.name} with return_code {return_code!s}, "
            f"message: '{message}'"
        )
        return (return_code, message)

    def validate_input(self, argin):
        """
        Method implementing the validation of the command
        arguments.
        The class provides stub functionality; subclasses should subclass
        this method with their command functionality.

        :param argin: the command input parameters
        :type argin: ANY
        """
        raise NotImplementedError(
            "InputValidatedCommand is abstract; validate_input() must be subclassed not called."
        )

    def _get_rejected_hook(self):
        """
        Retrieve the trigger action that restores the observation state as it was
        before the command was started.

        :return: the trigger name if found, otherwise an empty string.
        :rtype: str
        """
        obs_state_machine = self.state_model._observation_state_machine
        triggers = obs_state_machine.get_triggers(self._machine_dest)
        for trigger in triggers:
            # get the list with states satisfying the conditions on trigger, dest and source
            # skip the trigger starting with 'to_' string.
            #if trigger.startswith('to_'):
            if self._rejected_hook in trigger:
                state = obs_state_machine.get_transitions(trigger=trigger, 
                                                          dest=self._machine_source,
                                                          source=self._machine_dest
                        )
                if state: 
                    msg ="Invoke {} action to restore state to {}".format(trigger, 
                                                                          self._machine_source
                                                                   )
                    self.logger.info(msg)
                    return trigger
        return ''

    def started(self):
        """
        Action to perform upon starting the comand.
        Store the source and destination machine states
        that can be used to restore the observing state
        before the command was invoked.
        """
        self._machine_source = self.state_model._observation_state_machine.state
        super().started()
        self._machine_dest = self.state_model._observation_state_machine.state
        self._validation_success = False

    def fatal_error(self):
        """
        Callback for the failed completion of the command.
        If the validation of the command argument fails, 
        the action to restore the original observing state is called.
        """
        action = "fatal_error"
        if not self._validation_success:
            _action = self._get_rejected_hook()
            if _action: 
                action = _action
        self._perform_action(action)
