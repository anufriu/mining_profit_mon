import requests
import os
import sys
from loguru import logger



#logger
loglevel= os.environ.get("LOGLEVEL", "DEBUG")
logger.remove()
logger.level("INFO", color="<green>")
logger.level("DEBUG", color="<magenta>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.add(sink=sys.stdout,
format="[{time:YYYY-MM-DD at HH:mm:ss}] <level>[{level}] <bold>[{function}]</bold> {message}</level>",
level=loglevel, backtrace=True, diagnose=True)


class Wrapper:
    def __init__(self) -> None:
        self.main_url = 'https://api.minerstat.com/v2/coins'
        self.headers = {'accept': 'application/json','Content-Type': 'application/json' }

    def get_coin_info(self, ticker)->dict:
        try:
            req = requests.get(f'{self.main_url}?list={ticker}',headers=self.headers)
            if req.status_code in [200, 201]:
                logger.info('status code 200 all ok')
                res = req.json()[0]
            else:
                logger.error(f'status code is not ok got {req.status_code} with message: {req.text}')
                res = None
            logger.debug(f'request result: {res}')
        except requests.exceptions.RequestException as e:
            logger.error(f'problem with processing request to Minerstat got {e}')
            res = None
        return res

