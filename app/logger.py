import logging

import colorlog


def build_logger(logger_name: str, logging_level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with a specific logging level and format.

    Attributes:
        logger_name: str
            The name of the logger displayed in the message.
        logging_level: str
            The level of logging detail. Lower level are not displayed.
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    Returns:
        logging.Logger: The logger object.
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    handler = logging.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "white",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
