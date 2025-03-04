"""Logger for the boiler application."""

import logging
import os

from python_boiler_controller.src.services.constants import LOG_FILEPATH  # type: ignore


def create_logger(filename: str = LOG_FILEPATH) -> logging.Logger:
    """Create a new logger with a file handler set to filename.

    Args:
        filename (str, optional): filename of the log file.
            Defaults to src/progress_review_2/Boiler Log.txt.

    Returns:
        logging.Logger: A logger with a file handler to log all messages above
            DEBUG level.
    """
    # Save the header in the log file.
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as fp:
            fp.write("Timestamp, Event, Event Data\n")
    logger = logging.getLogger(__name__)
    log_format = logging.Formatter("%(asctime)s, %(msg)s")
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    return logger


# Create a new logger.
logger = create_logger()
