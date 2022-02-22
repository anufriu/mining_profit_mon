'''creates logger object
to accept same setting in all files'''
import sys
from pathlib import Path

from loguru import logger


def create_or_attach_logfile():
    """create log file

    Returns:
        object: path to logfile
    """
    logfile = Path('log.log')
    logfile.touch(exist_ok=True)
    return logfile

def create_logger(loglevel):
    """creates logger object

    Args:
        loglevel (str): log level

    Returns:
        object: complete logger object
    """
    logger.remove()
    logger.level("INFO", color="<green>")
    logger.level("DEBUG", color="<magenta>")
    logger.level("WARNING", color="<yellow>")
    logger.level("ERROR", color="<red>")
    logfile = create_or_attach_logfile()
    logger.add(sink=sys.stdout,
        format="[{time:YYYY-MM-DD at HH:mm:ss}] <level>[{level}]<bold>[{function}] </bold>{message}</level>",
        level=loglevel, backtrace=True, diagnose=True)
    logger.add(sink=logfile,
        format="[{time:YYYY-MM-DD at HH:mm:ss}] <level>[{level}]<bold>[{function}] </bold>{message}</level>",
        level=loglevel, backtrace=True, diagnose=True)
    return logger
