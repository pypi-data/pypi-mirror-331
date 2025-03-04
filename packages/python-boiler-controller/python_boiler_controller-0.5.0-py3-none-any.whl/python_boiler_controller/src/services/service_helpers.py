"""Help to organize the logs in a Pager format."""

from typing import Iterator

from python_boiler_controller.src.app.constants import PAGE_COUNT  # type: ignore
from python_boiler_controller.src.services.constants import LOG_FILEPATH  # type: ignore


def read_logs(filepath: str) -> Iterator[str]:
    """Read and return an iterator of logs.

    Args:
        filepath (str): filepath to read the logs from.

    Yields:
        Iterator[str]: An iterator which will give line by line log.
    """
    with open(filepath) as fp:
        fp.readline()  # Skips the header row.
        for line in fp.readlines():
            yield line


def view_log():
    """View the logs in a pager format. Default PAGE_COUNT is 10."""
    log_count = 0
    for log in read_logs(LOG_FILEPATH):
        # Waits for the user to continue or skip after
        # printing 10 logs.
        print(log)
        log_count += 1
        if log_count % PAGE_COUNT == 0:
            if input("Enter anything to continue, q to quit: ") == "q":
                return
