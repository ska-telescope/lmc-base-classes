"""
This subpackage contains specifications of SKA state machines.
"""

__all__ = ("OperationStateMachine", "AdminModeStateMachine", "ObservationStateMachine")

from .operation_state_machine import OperationStateMachine
from .admin_mode_state_machine import AdminModeStateMachine
from .observation_state_machine import ObservationStateMachine

