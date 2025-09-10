import logging
import sys


def get_logger(name: str = "app"):
    """Returns a logger with the given name, configured once."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        # If set to True, loggers in other files will also be handled by this root logger (which may cause duplicates).
        logger.propagate = False

    return logger
