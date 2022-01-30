"""Creating a Logger module"""
import os
import logging
import datetime
import tempfile

APP_NAME = "PyEngine"
DEBUG_LEVEL = logging.DEBUG
TEMP_DIR = os.path.join(tempfile.gettempdir(), APP_NAME)

DATESTAMP = datetime.datetime.now().strftime("%d-%b-%Y")
LOG_FILE = os.path.join(TEMP_DIR, f"{DATESTAMP}.log")


def get_logger(module=__file__, debug_level=logging.DEBUG):
    """
    This function creates a logger with given arguments.
    Args:
        module (str): string to use as name of logger.
        debug_level (logging.DEBUG): Debug Level of the logger.

    Returns:
        logging.getLogger: Returns the logger object.
    """
    if not debug_level:
        debug_level = DEBUG_LEVEL

    if not module:
        module = __file__

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    logger_name = os.path.split(module)[-1].split(".")[0]
    format_ = '%(levelname)7s - %(asctime)s - %(filename)s - %(funcName)s - %(message)s'
    date_fmt = "%d-%m-%y %H:%M:%S"

    log_file_formatter = logging.Formatter(format_, datefmt=date_fmt)
    text_stream_formatter = CustomFormatter(fmt=format_)

    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(text_stream_formatter)
    log_stream_handler.setLevel(debug_level)

    log_file_handler = logging.FileHandler(LOG_FILE)
    log_file_handler.setFormatter(log_file_formatter)
    log_file_handler.setLevel(logging.DEBUG)

    logger_ = logging.getLogger(logger_name)
    logger_.addHandler(log_file_handler)
    logger_.addHandler(log_stream_handler)
    logger_.setLevel(debug_level)

    return logger_


class CustomFormatter(logging.Formatter):
    """Logging colored formatter,
     adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
