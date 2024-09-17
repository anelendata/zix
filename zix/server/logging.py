import logging
import os
import sys
import typing
from logging.config import dictConfig
from pathlib import Path


LOGGING_FORMAT = "%(asctime)s -- %(name)s -- %(levelname)s :: %(funcName)s -- %(lineno)d -- %(message)s"
FORMATTER = logging.Formatter(
    LOGGING_FORMAT
)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            # "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            "format": LOGGING_FORMAT
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "my.packg": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "__main__": {  # if __name__ == "__main__"
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False
        },
    }
}
dictConfig(LOGGING_CONFIG)


def get_console_handler():
    """Get formatted console handler.

    Returns:
        A formatted STDOUT log handler.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_logger(*, logger_name: typing.Union[str, Path]):
    """Get logger with prepared handlers.

    Args:
        logger_name (typing.Union[str, Path]): The name of the logger to get.
    Returns:
        A logger formatted to handle STDOUT logs.
    """
    logger = logging.getLogger(logger_name)

    console_handler = get_console_handler()

    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
