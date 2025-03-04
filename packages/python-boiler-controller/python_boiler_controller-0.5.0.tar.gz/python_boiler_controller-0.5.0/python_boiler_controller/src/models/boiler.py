"""Model object to store the state of the boiler."""

from dataclasses import dataclass

from python_boiler_controller.src.services.constants import (  # type: ignore
    SwitchStatus,
    SystemStatus,
)


@dataclass
class Boiler:
    """Maintain the state of the boiler and interlock switch."""

    status = SystemStatus.LOCKOUT
    interlock_switch_status = SwitchStatus.OPEN
