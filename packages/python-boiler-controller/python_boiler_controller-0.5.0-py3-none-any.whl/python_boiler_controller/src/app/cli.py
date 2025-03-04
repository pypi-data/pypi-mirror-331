"""Run the boiler starter code."""

from InquirerPy import inquirer  # type: ignore
from InquirerPy.base import Choice  # type: ignore
from python_boiler_controller.src.app.constants import (  # type: ignore
    CHOICES,
    Messages,
)
from python_boiler_controller.src.models.boiler import Boiler  # type: ignore
from python_boiler_controller.src.services.constants import (  # type: ignore
    EventData,
    EventName,
    SystemStatus,
)
from python_boiler_controller.src.services.logger import logger  # type: ignore
from python_boiler_controller.src.services.service_helpers import (
    view_log,
)  # type: ignore
from python_boiler_controller.src.services.system_operation import (
    reset_lockout,
    simulate_error,
    start_boiler,
    stop_boiler,
    toggle_interlock_switch,
)  # type: ignore


def handle_choice(choice: int):
    """Perform action based on the choice.

    Args:
        choice (int): choice to handle its equivalent action.
    """
    boiler = globals()["boiler"]
    if choice == 1:
        start_boiler(boiler=boiler)
    elif choice == 2:
        stop_boiler(boiler=boiler)
    elif choice == 3:
        simulate_error(boiler=boiler)
    elif choice == 4:
        toggle_interlock_switch(boiler=boiler)
    elif choice == 5:
        reset_lockout(boiler=boiler)
    elif choice == 6:
        view_log()


def get_choices() -> list[Choice]:
    """Get choices to be printed on the console."""
    choices = [
        Choice(value=index + 1, name=f"{index+1}.{name}")
        for index, name in enumerate(CHOICES)
    ]
    choices.append(Choice(value=None, name=f"{len(CHOICES)+1}.Exit"))
    return choices


def main():
    """Run the console application."""
    boiler = Boiler()
    globals()["boiler"] = boiler
    print(Messages.WELCOME)
    logger.info(f"{EventName.BOILER_INIT}, {EventData.BOILER_INIT}")
    while True:
        choice = inquirer.select(
            message=Messages.CHOICE_INPUT,
            choices=get_choices(),
        ).execute()
        if choice:
            handle_choice(choice=choice)
        else:
            if boiler.status == SystemStatus.OPERATIONAL:
                stop_boiler(boiler)
            break
    logger.info("Exit, Exited the application.")
    print(Messages.EXIT)


if __name__ == "__main__":
    main()
