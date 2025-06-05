"""logging setup"""

import sys

from loguru import logger

LOG_FOLDER = "logs/"
LOG_ROTATION = "1 day"

logger.remove(0)

# all logger.info('message') goes strictly to info.log
logger.add(
    LOG_FOLDER + "info.log",
    filter=lambda record: record["level"].name == "INFO",
    serialize=True,
    rotation=LOG_ROTATION,
)

# all logger.error('message') goes strictly to error.log,
logger.add(
    LOG_FOLDER + "error.log",
    filter=lambda record: record["level"].name == "ERROR"
    and "traceback" not in record["extra"],
    serialize=True,
    rotation=LOG_ROTATION,
    backtrace=True,
    diagnose=True,
)

logger.add(
    sys.stderr,
    level="DEBUG",
    colorize=True,
)
__all__ = ["logger"]
