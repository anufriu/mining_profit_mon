'''get data from minerstat and hiveos, compares it and creates
prometheus metrics
'''
import argparse
import configparser
import os
import sys
import time
import traceback

import hive_api_wrapper as api
import minerstat_api as m_api
import prometheus_metrics as prom_exporter
from local_logger import create_logger
from two_miners_api import Wrapper as t_miners_api

#from loguru import logger


def argparser():
    """[pars args from stdin]

    Returns:
        [object]: [with arguments]
    """
    parser = argparse.ArgumentParser(description='sukablyat')
    parser.add_argument('-l', '--loglevel',
                        help='loglevel',
                        choices=["INFO", "ERROR", "DEBUG"],
                        action='store',
                        dest='loglevel',
                        default="INFO")
    parser.add_argument('-c', '--config',
                        help='config path',
                        action='store',
                        dest='configpath',
                        default='src/config.ini')
    args = parser.parse_args()
    return args


# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
logger = create_logger(loglevel)


# getconfig
try:
    ar = argparser()
    config = configparser.ConfigParser()
    config.read(ar.configpath)
    hiveos_token = config['hiveos'].get('token')
    power_price = float(config['constants'].get('powercost'))/1000
    hiveon_eth_wallet = config['hiveon_stat'].get('miner_wallet')
    try:
        prometheus_port = int(config['prometheus'].get('port'))
    except KeyError:
        logger.info(
            ' Prometheus port did not set in config using default port 8910')
        prometheus_port = 8910
    if not power_price:
        logger.warning('power price is not set using 0.1$')
        power_price = 0.0001
    if not hiveos_token:
        logger.error('cant find token field check the config. exiting...')
        sys.exit(1)
except configparser.Error as e:
    logger.error(
        f'problem with config parsing: {e} exiting...')
    sys.exit(1)


class Coin():
    """contains info about coin
    """
    def __init__(self, coin):
        self.coin = coin

    def get_coin_info(self):
        """get netrwork hashrate, price, diff from minerstat

        Returns:
            dict: info
        """
        data = m_api.Wrapper().get_coin_info(self.coin)
        logger.debug(f'got answer from minerstat: {data}')
        return data


class Worker():
    """contains needful info about workers
    """
    def __init__(self, data) -> None:
        self.w_name = h_api.h_get_worker_name(data)
        self.w_hashrate = h_api.h_get_worker_hashrate(data)
        self.worker_online = True
        if not self.w_hashrate:
            self.worker_online = False
        if not data['stats']['online']:
            self.worker_online = False
            logger.warning(f'{self.w_name} is OFFLINE, skipping')
            return
        self.w_algo = h_api.h_get_worker_algo(data)
        self.w_get_coin = h_api.h_get_worker_coin(data)
        self.w_power_cons = h_api.h_get_worker_power_cons(data)


class Calculations():
    """class for calculations
    """

    def __init__(self) -> None:
        pass

    def calculate_coin_profit(self, coin, hashrate):
        ''' calculate profit in reward unit for 1 hour mining'''
        profit = {}
        try:
            coinstat = Coin(coin).get_coin_info()
            if not coinstat:
                logger.error(f'can get info from coinstat for {coin}')
                return profit
            try:
                reward = coinstat['reward']*1000
                reward_unit = coinstat['reward_unit']
                usd_price = coinstat['price']
                logger.info(f'reward for 1 hour mining {coin} for 1 h/s '
                            f'is: {reward} {reward_unit}')
                hashrate_reward = self.calculate_hashrate_reward(hashrate,
                                                                 reward, reward_unit, coin)
                hour_reward = hashrate_reward.get(coin)
                if hour_reward:
                    hour_usd_reward = hour_reward.get('reward')*usd_price
                    logger.info(f'Dirty hour USD profit: {hour_usd_reward} $')
                    profit[coin] = {'hour_reward': hour_reward.get('reward'),
                                    'hour_usd_reward': hour_usd_reward, 'coin': coin}
            except KeyError:
                logger.error('cant get reward from minerstat!')
        except TypeError:
            logger.warning('cant get coin attr, probably custom miner is set')
        return profit

    @staticmethod
    def calculate_hashrate_reward(hashrate, reward, reward_unit, coin) -> dict:
        """calculating reward for hashrate

        Args:
            hashrate (int): hashrate
            reward (int): calculated reward
            reward_unit (int): reward currency
            coin (str): coint name (ticker)

        Returns:
            dict: {coin:{reward:hahrate_reward, unit:reward_unit}}
        """
        h_rew = hashrate*reward
        logger.info(f'reward for 1 hour mining {coin} for {hashrate} h/s '
                    f'is: {h_rew} {reward_unit}')
        hashrate_reward_dict = {
            coin: {"reward": hashrate*reward, "unit": reward_unit}}
        return hashrate_reward_dict

    @staticmethod
    def calculate_powerdraw( powercons, hours=1):
        """calculate powerdrow by hours

        Args:
            powercons (int): powerdraw metric from hiveos
            hours (int, optional): hours number. Defaults to 1.

        Returns:
            int: powerdraw cost
        """
        powerdraw1h = powercons*hours   # watts per 1h
        logger.debug(f'powerdraw 1h = {powerdraw1h}, price = {power_price}')
        powerdraw1h_cost = int(powerdraw1h)*float(power_price)
        logger.info(
            f'worker electricity price per {hours}h: {powerdraw1h_cost}$')
        return powerdraw1h_cost

    def calculate_clean_profit(self, coin, powercons, dirty_profit, w_name) -> dict:
        '''calculate profit with power consumption'''
        e_cost = self.calculate_powerdraw(powercons)
        clean_profit_dct = {}
        hour_clean_profit = dirty_profit[coin]['hour_usd_reward'] - e_cost
        logger.info(f'Hour clean profit for worker '
                    f'{w_name}: {hour_clean_profit}'
                    f'$ for coin: {dirty_profit[coin]["coin"]}')
        clean_profit_dct[coin] = {'hourly': hour_clean_profit}
        return clean_profit_dct


def generate_network_hrate_metric(coin_name: str, coin_hash: int, coin_algo: str):
    """generate prometheus metric of network hashrate

    Args:
        coin_name (str): _description_
        coin_hash (int): _description_
        coin_algo (str): _description_
    """
    try:
        labels = [coin_name, coin_algo]
        write_to_prom.set_mark(coin_hash, labels, 'network_hashrate')
    except Exception as error:
        logger.error(f'Error while writing to prometheus: {error}')


def generate_hour_reward_metric(coin_name: str, worker_name: str,
                                coin_reward: float, metric_name: str):
    """generate per hour reward metric

    Args:
        coin_name (str): _description_
        worker_name (str): _description_
        coin_reward (float): _description_
        metric_name (str): _description_
    """
    try:
        write_to_prom.set_mark(
            coin_reward, [coin_name, worker_name], metric_name)
    except Exception as error:
        logger.error(f'Error while writing to prometheus: {error}')

def skipper(name, status, coin)-> bool:
    """check the nessesary attr of worker

    Args:
        name (str): _description_
        status (bool): _description_
        coin (str): _description_

    Returns:
        bool: _description_
    """
    is_skip = False
    if not name:
        is_skip = True
        logger.error('cant get worker name, skipping')
    if not status:
        logger.warning('worker offline or have a bad status')
        is_skip = True
    if not coin:
        logger.error('No info about current mining coin, skipping')
        is_skip = True
    return is_skip

def generate_2miners_reward_metric(coin_ticker: str):
    """create reward metric based on 2miners api

    Args:
        coin_ticker (str): _description_
    """
    if coin_ticker in config['2miners_stat']:
        two_miners_coin_reward = t_miners_api(coin_ticker,
                                              config['2miners_stat'][coin_ticker]).get_sumreward_by_account()
        coin_reward_24h = two_miners_coin_reward['Last 24 hours']
        try:
            write_to_prom.set_mark(
                coin_reward_24h, [coin_ticker], 'two_miners_actual_profitline_24h')
        except Exception as error:
            logger.error(f'Error while writing to prometheus: {error}')

    else:
        logger.warning(f'ticker {coin_ticker} is not presented in 2Miners config section'
                       f'its probably being mined on other pool')

def logic():
    """main function contains all logic in it
    """
    try:
        workers_info = h_api.h_get_workers_info(workers_dict)
        coinlist = []
        coindata = []
        if not workers_info:
            logger.error('cant get info from hiveos api! sleeping')
            return
        for worker in workers_info['data']: 
            worker_attr = Worker(dict(worker))
            worker_calc = Calculations()
            counter = 0
            worker_consumption = worker_calc.calculate_powerdraw(worker_attr.w_power_cons)
            attr_check = skipper(worker_attr.w_name,
                worker_attr.worker_online, worker_attr.w_get_coin)
            if attr_check:
                continue
            logger.info(f'processing {worker_attr.w_name}')
            for c in worker_attr.w_get_coin:
                if not worker_attr.w_hashrate:
                    logger.error('No info about worker hashrate, skipping')
                    continue
                worker_profit = worker_calc.calculate_coin_profit(c,
                                                                  worker_attr.w_hashrate[c])
                worker_profit_clean = worker_calc.calculate_clean_profit(c,
                                                                         worker_attr.w_power_cons, worker_profit,
                                                                         worker_attr.w_name)
                if not worker_profit_clean:
                    logger.error(f'cant get clean profit for worker'
                                 f'{worker_attr.w_name}, skipping')
                    continue
                worker_reward_by_hr = worker_profit.get(c)['hour_reward']
                generate_hour_reward_metric(c, worker_attr.w_name,
                                            worker_reward_by_hr, 'worker_incoin_profit')
                if c not in coinlist:
                    coin_data = Coin(c).get_coin_info()
                    if not coin_data:
                        logger.error(
                            f'cant get coin info by ticker {c}, skipping')
                        continue
                    coinlist.append(c)
                    coindata.append(coin_data)
                    write_to_prom.set_mark(coin_data['price'], c, 'coin_price')
                labels = [worker_attr.w_name, c]
                logger.debug(f'created labels {labels}')
                worker_profit = worker_profit_clean.get(c)
                if not worker_profit:
                    continue
                write_to_prom.set_mark(
                    worker_profit['hourly'], labels, 'clear_profitline_hourly')
                if not worker_attr.w_algo:
                    logger.error(
                        f'cant get algo for worker {worker_attr.w_name}')
                    continue
                write_to_prom.set_mark(worker_attr.w_hashrate[c], [labels[0],
                                                                   worker_attr.w_algo[counter]], 'worker_hashrate')
                counter += 1
        for coin in coindata:
            coin_name = coin.get('name')
            coin_ticker = coin.get('coin').lower()
            generate_network_hrate_metric(coin_name,
                                          coin.get('network_hashrate'), coin.get('algorithm'))
            if  config.has_section('2miners_stat'):
                if config['2miners_stat']['enabled'] == 'True':
                    logger.debug(
                        '2 miners scrape was set to true in config, processing')
                generate_2miners_reward_metric(coin_ticker)
    except Exception:
        logger.error(
            f'some shit happened! sleeping and hope its gone: {traceback.format_exc()}')


def mainloop():
    """mainloop
    """
    while True:
        try:
            logic()
            logger.info('sleeping')
            time.sleep(600)
        except KeyboardInterrupt:
            logger.info('keyboard interrupt...')
            sys.exit(0)


if __name__ == '__main__':
    h_api = api.Wrapper(hiveos_token)
    farms_list = h_api.h_get_farms_ids()
    workers_dict = h_api.h_get_workers_ids(farms_list)
    write_to_prom = prom_exporter.Prom_metrics(prometheus_port)
    mainloop()
