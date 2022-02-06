import os
import sys

from local_logger import create_logger

# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
logger = create_logger(loglevel)


class Wrapper:
    def __init__(self, wallet) -> None:
        self.main_url = 'https://hiveon.net/api/v1/stats/miner/'
        self.wallet = wallet
        self.headers = {'accept': 'application/json',
                        'Content-Type': 'application/json'}

    def hon_get_billing_acc(self):
        '''get profitinfo for miner'''
        pass
