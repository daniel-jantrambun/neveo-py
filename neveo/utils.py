import logging
import os


def get_logger(name: str = None):
    """get a logger"""
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    root_logger.handlers = []
    root_logger.addHandler(handler)

    logger = logging.getLogger(name)
    if os.getenv("LOG_LEVEL"):
        try:
            log_level = getattr(logging, os.environ["LOG_LEVEL"].upper())
        except Exception:
            print("Environment variable not understood -" "setting log level as INFO.")
            log_level = logging.INFO
    else:
        log_level = logging.INFO

    logger.setLevel(log_level)

    return logger
