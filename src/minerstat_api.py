import os
import sys

import requests

from local_logger import create_logger

# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
logger = create_logger(loglevel)


class Wrapper:
    '''Wrapper around https://minerstat.com/coin'''

    def __init__(self) -> None:
        self.main_url = 'https://api.minerstat.com/v2/coins'
        self.headers = {'accept': 'application/json',
                        'Content-Type': 'application/json'}

    def get_coin_info(self, ticker):
        '''Get hashrate or price or diff of requestet coin'''
        try:
            req = requests.get(
                f'{self.main_url}?list={ticker}', headers=self.headers)
            if req.status_code in [200, 201]:
                logger.info('status code 200 all ok')
                res = req.json()[0]
            else:
                logger.error(
                    f'status code is not ok: {req.status_code} with message: {req.text}')
                res = None
            logger.debug(f'request result: {res}')
        except requests.exceptions.RequestException as e:
            logger.error(
                f'problem with processing request to Minerstat got {e}')
            res = None
        return res
