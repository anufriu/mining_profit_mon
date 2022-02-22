'''wrapper for hiveon api'''
import os

from local_logger import create_logger

# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
logger = create_logger(loglevel)


class Wrapper:
    """
    maker requests to hiveon
    """
    def __init__(self, wallet) -> None:
        self.main_url = 'https://hiveon.net/api/v1/stats/miner/'
        self.wallet = wallet
        self.headers = {'accept': 'application/json',
                        'Content-Type': 'application/json'}
