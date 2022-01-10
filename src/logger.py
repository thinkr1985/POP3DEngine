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

    # formatter = ColoredFormatter()
    date_fmt = "%d-%m-%y %H:%M:%S"
    formatter = logging.Formatter(
        '%(levelname)s - %(asctime)s - %(filename)s - %(funcName)s - %(message)s',
        datefmt=date_fmt
    )

    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(formatter)
    log_stream_handler.setLevel(debug_level)

    log_file_handler = logging.FileHandler(LOG_FILE)
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(logging.DEBUG)

    logger_ = logging.getLogger(logger_name)
    logger_.addHandler(log_file_handler)
    logger_.addHandler(log_stream_handler)
    logger_.setLevel(debug_level)

    return logger_


class ColoredFormatter(logging.Formatter):
    """Custom logging Formatter for coloured stream logging."""

    BLUE = '\033[1;34m'
    GREEN = '\033[1;32m'
    ORANGE = '\033[0;33m'
    RED = '\033[1;31m'

    def __init__(self, *args, **kwargs):
        """Init.

        Args:
            message_only (bool): If True, show only the log message,
                otherwise show also logger name and log level. Defaults
                to False.
        """
        super(ColoredFormatter, self).__init__(*args, **kwargs)
        self.log_template = (
            '{color}%(levelname)s\t%(asctime)s-%(name)s-%(funcName)s-\t%(message)s'
        )
        self.datefmt = '%d-%b-%y-%H:%M:%S'

    def format(self, record):
        """Format the log record with a different colour for each log level.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record.
        """
        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._fmt = self.log_template.format(color=self.GREEN)
        elif record.levelno == logging.INFO:
            self._fmt = self.log_template.format(color=self.BLUE)
        elif record.levelno == logging.WARNING:
            self._fmt = self.log_template.format(color=self.ORANGE)
        elif record.levelno == logging.ERROR:
            self._fmt = self.log_template.format(color=self.RED)

        result = super(ColoredFormatter, self).format(record)

        return result
