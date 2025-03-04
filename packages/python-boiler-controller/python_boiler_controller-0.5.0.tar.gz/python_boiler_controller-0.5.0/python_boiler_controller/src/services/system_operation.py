"""Handle all service related to boiler."""

import time

from python_boiler_controller.src.models.boiler import Boiler  # type: ignore
from python_boiler_controller.src.services.constants import (  # type: ignore
    EventData,
    EventName,
    SwitchStatus,
    SystemStatus,
)
from python_boiler_controller.src.services.logger import logger  # type: ignore


def start_boiler(boiler: Boiler):
    """Start the boiler if it is in ready state.

    Args:
        boiler (Boiler): Boiler object to start.
    """
    if (
        boiler.interlock_switch_status != SwitchStatus.CLOSED
        or boiler.status != SystemStatus.READY
    ):
        logger.warning(f"{EventName.START_BOILER}, {EventData.NOT_READY}")
        print(EventData.NOT_READY)
        return
    try:
        logger.info(f"{EventName.PRE_PURGE}, {EventData.PRE_PURGE_START}")
        print(EventData.PRE_PURGE_START)
        pre_purge(boiler=boiler)
    except KeyboardInterrupt:
        logger.error(f"{EventName.PRE_PURGE}, {EventData.PRE_PURGE_ERROR}")
        print(EventData.PRE_PURGE_ERROR)
        boiler.status = SystemStatus.READY
        return
    else:
        logger.info(f"{EventName.PRE_PURGE}, {EventData.PRE_PURGE_END}")
        print(EventData.PRE_PURGE_END)
    try:
        logger.info(f"{EventName.IGNITION}, {EventData.IGNITION_START}")
        ignite(boiler=boiler)
    except KeyboardInterrupt:
        logger.error(f"{EventName.IGNITION}, {EventData.IGNITION_ERROR}")
        boiler.status = SystemStatus.READY
        print(EventData.IGNITION_ERROR)
        return
    else:
        logger.info(f"{EventName.IGNITION}, {EventData.IGNITION_END}")
        print(EventData.IGNITION_END)
    boiler.status = SystemStatus.OPERATIONAL
    logger.info(f"{EventName.START_BOILER}, {EventData.OPERATIONAL}")
    print(EventData.OPERATIONAL)


def pre_purge(boiler: Boiler):
    """Pre-Purge the boiler before igniting.

    Args:
        boiler (Boiler): Boiler object to pre-purge.
    """
    for countdown in range(10, 0, -1):
        print(f"Pre-Purge Phase will complete in {countdown} seconds")
        time.sleep(1)
    boiler.status = SystemStatus.PRE_PURGE


def ignite(boiler: Boiler):
    """Ignite the boiler after pre purging.

    Args:
        boiler (Boiler): Boiler object to ignite.
    """
    for countdown in range(10, 0, -1):
        print(f"Ignition Phase will complete in {countdown} seconds")
        time.sleep(1)
    boiler.status = SystemStatus.IGNITION


def reset_lockout(boiler: Boiler):
    """Reset the boiler by closing the switch.

    Args:
        boiler (Boiler): Boiler object to reset.
    """
    if boiler.status == SystemStatus.OPERATIONAL:
        stop_boiler(boiler)
    if boiler.interlock_switch_status == SwitchStatus.OPEN:
        print("Closing the interlock switch")
        boiler.interlock_switch_status = SwitchStatus.CLOSED
    boiler.status = SystemStatus.READY
    message = f"{EventName.LOCKOUT_RESET}, {EventData.READY_MESSAGE}"
    logger.info(msg=message)
    print(EventData.READY_MESSAGE)


def stop_boiler(boiler: Boiler):
    """Stop the boiler if it is in operational state.

    Args:
        boiler (Boiler): Boiler object to stop.
    """
    if (
        boiler.status != SystemStatus.OPERATIONAL
        or boiler.interlock_switch_status != SwitchStatus.CLOSED
    ):
        print("No boiler is running.")
        return
    print("Stopping the boiler in 3 seconds...")
    time.sleep(3)
    logger.info(f"{EventName.STOP_BOILER}, {EventData.STOP_BOILER}")
    print(EventData.STOP_BOILER)
    boiler.status = SystemStatus.LOCKOUT
    boiler.interlock_switch_status = SwitchStatus.OPEN


def toggle_interlock_switch(boiler: Boiler):
    """Toggle the interlock switch in the boiler.

    Args:
        boiler (Boiler): Boiler object to toggle the switch.
    """
    if boiler.interlock_switch_status == SwitchStatus.OPEN:
        boiler.interlock_switch_status = SwitchStatus.CLOSED
        message = (
            f"{EventName.TOGGLE_INTERLOCK_SWITCH}, "
            f"{EventData.OPEN_TO_CLOSED}"
        )
        logger.info(msg=message)
        print(EventData.OPEN_TO_CLOSED)
        boiler.status = SystemStatus.READY
    elif boiler.interlock_switch_status == SwitchStatus.CLOSED:
        if boiler.status == SystemStatus.OPERATIONAL:
            stop_boiler(boiler)
        boiler.interlock_switch_status = SwitchStatus.OPEN
        message = (
            f"{EventName.TOGGLE_INTERLOCK_SWITCH}, "
            f"{EventData.CLOSED_TO_OPEN}"
        )
        logger.info(msg=message)
        print(EventData.CLOSED_TO_OPEN)


def simulate_error(boiler: Boiler):
    """Simulate error while the boiler is running.

    Args:
        boiler (Boiler): Boiler object to simulate error.
    """
    if boiler.status != SystemStatus.OPERATIONAL:
        print("Cannot simulate error when a boiler is not running.")
        return
    logger.error(f"{EventName.SIMULATE_ERROR}, {EventData.SIMULATE_ERROR}")
    print(EventData.SIMULATE_ERROR)
    stop_boiler(boiler)
