import os

import requests

from local_logger import create_logger

# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
logger = create_logger(loglevel)


class Wrapper:
    '''
    contains a functions to get 
    data from 2miners.com
    return dict liker {"Last 24 hours":reward, "Last 60 minutes":reward}
    '''

    def __init__(self, ticker: str, wallet: str) -> None:
        self.pool_ticker = ticker
        self.main_url = f'https://{ticker}.2miners.com/api'
        self.wallet = wallet
        self.headers = {'Content-Type': 'application/json'}
        # ask 2miners about it cos eth in json is int
        self.reward_multy_map = {"eth": 0.000000001, "rvn": 0.00000001}

    def get_sumreward_by_account(self) -> dict:
        """
        process request to api and 
        """
        reward_by_interval = {}
        try:
            req = requests.get(self.main_url+'/accounts/'+self.wallet,
                               headers=self.headers)
            if req.status_code == requests.codes.ok:
                for reward in req.json()['sumrewards']:
                    reward_by_interval[reward['name']] = reward['reward'] * \
                        self.reward_multy_map[self.pool_ticker]
                logger.debug(
                    f'got rewards for {self.pool_ticker}: {reward_by_interval}')
            else:
                logger.error(
                    f'Status code of request to {req.url} is not ok, got {req}')
        except requests.exceptions.RequestException as e:
            logger.error(
                f'problem with processing request to 2 miners got {e}')
        return reward_by_interval
