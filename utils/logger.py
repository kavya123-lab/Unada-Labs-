"""
utils/logger.py
----------------
Centralized logging configuration for the project.

Why use the `logging` module instead of print()?
- print() statements are hard to turn off, can't be filtered by
  severity (info vs. warning vs. error), and don't automatically
  include timestamps or which module produced them.
- Python's built-in `logging` module solves all of that and is what
  every production-grade Python project uses instead of print().
- Having ONE function that configures logging consistently means every
  module's log messages look the same and are easy to scan in your
  terminal while the Streamlit app is running — useful for watching
  each agent start and finish as the pipeline executes.
"""

import logging
import sys

# This format includes: timestamp, log level, the module name that
# logged the message, and the message itself — everything needed to
# trace exactly what each agent is doing as the pipeline runs.
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Create (or retrieve) a configured logger for the given module name.

    Parameters
    ----------
    name : str
        Usually passed as __name__ from the calling module, so log
        messages clearly show which file produced them, e.g.
        "agents.research_agent" or "services.gemini_service".

    Returns
    -------
    logging.Logger
        A logger instance that writes INFO-level and above messages
        to the terminal (stdout) using a consistent, readable format.
    """
    logger = logging.getLogger(name)

    # Guard against attaching duplicate handlers if get_logger() is
    # called more than once for the same module name. This matters
    # specifically for Streamlit, which re-runs the whole script on
    # every user interaction — without this check, log lines would
    # start appearing two, three, or more times per message.
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # Prevent messages from also being passed up to the root
        # logger, which would otherwise print every message twice.
        logger.propagate = False

    return logger
