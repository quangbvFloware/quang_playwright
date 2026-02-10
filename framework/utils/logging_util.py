import logging
import math
import platform
from logging import Logger

from framework.consts.project import PYTHON_CONFIG_LOG

logger: Logger = logging.getLogger(PYTHON_CONFIG_LOG)


def cli_logging_format(debug_log=False):
    _loglevel = logging.DEBUG if debug_log else logging.INFO

    os_name = platform.system()
    logging.root.setLevel(logging.INFO)

    for _handler in logger.handlers[:]:
        logger.removeHandler(_handler)

    logger.propagate = False
    stream = logging.StreamHandler()
    stream.setLevel(_loglevel)

    if os_name == "Windows":
        LOG_FORMAT_WIN = "\t%(asctime)-6s %(levelname)7s | %(message)s"
        formatter = logging.Formatter(LOG_FORMAT_WIN, "%H:%M:%S")
    else:
        from colorlog import ColoredFormatter

        LOG_FORMAT = "\t%(asctime)-6s %(log_color)s%(levelname)7s | %(log_color)s%(message)s"
        formatter = ColoredFormatter(LOG_FORMAT, "%H:%M:%S")

    stream.setFormatter(formatter)
    logger.setLevel(_loglevel)
    logger.addHandler(stream)
    return logger