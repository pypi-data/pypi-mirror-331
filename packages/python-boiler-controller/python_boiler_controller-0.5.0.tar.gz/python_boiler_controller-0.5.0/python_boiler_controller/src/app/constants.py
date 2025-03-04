"""Store all necessary constants for the console application."""

CHOICES = [
    "Start Boiler Sequence",
    "Stop Boiler Sequence",
    "Simulate Boiler Error",
    "Toggle Run Interlock Switch",
    "Reset Lockout",
    "View Event Log",
]

PAGE_COUNT = 10


class Messages:
    """Store messages to be displayed to the user."""

    CHOICE_INPUT = "Select an action to perform: "
    EXIT = "Exiting the application..."
    WELCOME = "Boiler Controller initialized."
