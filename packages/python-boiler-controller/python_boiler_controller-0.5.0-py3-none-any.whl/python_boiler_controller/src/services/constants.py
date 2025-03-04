"""Store all necessary constants for the services."""

from enum import Enum


LOG_FILEPATH = "Boiler Log.txt"


class SystemStatus(Enum):
    """Store the status of the boiler system."""

    LOCKOUT = "Lockout"
    READY = "READY"
    OPERATIONAL = "Operational"
    PRE_PURGE = "Pre-Purge"
    IGNITION = "Ignition"


class SwitchStatus(Enum):
    """Store the interlock switch status."""

    OPEN = "Open"
    CLOSED = "Closed"


class EventData:
    """Store the event data for logging purposes."""

    READY_MESSAGE = "Boiler Status changed to Ready."
    OPEN_TO_CLOSED = "Interlock Switch toggled to Closed."
    CLOSED_TO_OPEN = "Interlock Switch toggled to Open."
    OPERATIONAL = "Boiler is now operational."
    PRE_PURGE_START = "Starting Pre-Purge Phase."
    PRE_PURGE_ERROR = "An error occurred in Pre-Purge Phase."
    PRE_PURGE_END = "Pre-Purge Phase completed."
    IGNITION_START = "Starting Ignition Phase."
    IGNITION_END = "Ignition Phase completed."
    IGNITION_ERROR = "An error occurred in Ignition Phase."
    NOT_READY = "Cannot start the boiler while interlock switch is open."
    BOILER_INIT = "Boiler initialized"
    SIMULATE_ERROR = "An error occurred in the boiler."
    STOP_BOILER = "Boiler stopped."


class EventName:
    """Store the event name for logging purposes."""

    LOCKOUT_RESET = "Lockout Reset"
    TOGGLE_INTERLOCK_SWITCH = "Toggle Interlock Switch"
    START_BOILER = "Start Boiler"
    STOP_BOILER = "Stop Boiler"
    PRE_PURGE = "Pre-Purge Phase"
    IGNITION = "Ignition Phase"
    BOILER_INIT = "Boiler Init"
    SIMULATE_ERROR = "SIMULATE"
