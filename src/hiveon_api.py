import os
import sys
from loguru import logger

# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
logger.remove()
logger.level("INFO", color="<green>")
logger.level("DEBUG", color="<magenta>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.add(sink=sys.stdout,
           format="[{time:YYYY-MM-DD at HH:mm:ss}] <level>[{level}]<bold>[{function}]</bold>{message}</level>",
           level=loglevel, backtrace=True, diagnose=True)


class Wrapper:
    def __init__(self, wallet) -> None:
        self.main_url = 'https://hiveon.net/api/v1/stats/miner/'
        self.wallet = wallet
        self.headers = {'accept': 'application/json',
                        'Content-Type': 'application/json'}

    def hon_get_billing_acc(self):
        '''get profitinfo for miner'''
        pass
