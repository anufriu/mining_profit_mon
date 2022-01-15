import hive_api_wrapper as api
import minerstat_api as m_api
import configparser
import traceback
import sys
import argparse
import os
import time
import prometheus_metrics as prom_exporter
from loguru import logger

def argparser():
    parser = argparse.ArgumentParser(description='sukablyat')
    parser.add_argument('-l', '--loglevel', 
                        help='loglevel', 
                        choices=["INFO", "ERROR", "DEBUG"],
                        action='store',
                        dest='loglevel',
                        default="INFO")
    args = parser.parse_args()
    os.environ["LOGLEVEL"] = str(args.loglevel)
    return args

#logger
logger.remove()
logger.level("INFO", color="<green>")
logger.level("DEBUG", color="<magenta>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.add(sink=sys.stdout,
format="[{time:YYYY-MM-DD at HH:mm:ss}] <level>[{level}] <bold>[{function}]</bold> {message}</level>",
level= os.environ.get("LOGLEVEL", "DEBUG"), backtrace=True, diagnose=True)

#getconfig
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    hiveos_token = config['hiveos'].get('token')
    power_price = config['constants'].get('powercost')
    hiveon_eth_wallet = config['hiveon_stat'].get('miner_wallet')
    if not power_price:
        logger.warning('power proce is not set using 0.1$')
        power_price = 0.1
    if hiveos_token:
        pass
    else:
        logger.error(f'cant find token field check the config. exiting...')
        sys.exit(1)
except configparser.Error:
    logger.error(f'problem with config parsing: {traceback.print_exception()}\n exiting...')
    sys.exit(1)

class Coin():
    def get_coin_info(coin)-> list:
        data = m_api.Wrapper().get_coin_info(coin)
        logger.debug(f'got answer from minerstat: {data}')
        return data

class Worker_profit():
    def __init__(self, data) -> None:
        self.data = data
        self.w_name = h_api.h_get_worker_name(data)
        self.w_hashrate = h_api.h_get_worker_hashrate(data)
        self.w_algo = h_api.h_get_worker_algo(data)
        self.w_power_cons = h_api.h_get_worker_power_cons(data)
        self.w_get_coin = h_api.h_get_worker_coin(data)
        self.dirty_profit = self.calculate_coin_profit()
        self.clean_profit = self.calculate_clean_profit()



    def calculate_coin_profit(self):
        ''' calculate profit in reward unit for 1 hour mining'''
        profit = []
        for c in self.w_get_coin:
            coinstat = Coin.get_coin_info(c)
            if not coinstat:
                logger.error(f'can calculate profit for {c}')
                return
            try:
                reward = coinstat['reward']*1000
                reward_unit = coinstat['reward_unit']
                usd_price = coinstat['price']
                logger.info(f'reward for 1 hour mining {c} for 1 h/s '\
                    f'is: {reward} {reward_unit}')
                hour_reward = self.w_hashrate.get(c)*reward
                hour_usd_reward = hour_reward*usd_price
                logger.info(f'reward for 1 hour mining {c} for {self.w_hashrate.get(c)} h/s '\
                    f'is: {hour_reward} {reward_unit}')
                logger.info(f'Dirty hour USD profit: {hour_usd_reward} $')
            except KeyError:
                logger.error(f'cant get reward drom minerstat!')
            profit.append({'coin':c, 'hour_reward': hour_reward,
             'hour_usd_reward':hour_usd_reward})
        return profit
            
    def calculate_powerdraw(self, hours=1):
        powerdraw1h = self.w_power_cons*hours   # watts per 1h
        logger.debug(f'powerdraw 1h = {powerdraw1h}, price = {power_price}')
        powerdraw1h_cost = int(powerdraw1h)*float(power_price)
        logger.info(f'worker electricity price per {hours}h: {powerdraw1h_cost}$')
        return powerdraw1h_cost

    def calculate_clean_profit(self)->dict:
        '''calculate profit with power consumption'''
        e_cost = self.calculate_powerdraw()
        clean_profit_dct = {}
        for i in self.dirty_profit:
            hour_clean_profit = i['hour_usd_reward'] - e_cost
            logger.info(f'Hour clean profit for worker '\
                f'{self.w_name}: {hour_clean_profit} $ for coin: {i["coin"]}')
            daily_clean_profit = (i['hour_usd_reward']*24) - self.calculate_powerdraw(24)
            logger.info('Daily clean profit for worker '\
                f'{self.w_name}: {daily_clean_profit} $ for coin: {i["coin"]}')
            clean_profit_dct[i['coin']] = {'daily': daily_clean_profit, 'hourly': hour_clean_profit}
        return clean_profit_dct

def calculate_actual_profit_hiveon(hiveon_eth_wallet):

    pass

def logic():
    workers_info = h_api.h_get_workers_info(workers_dict)
    coinlist = []
    for worker in workers_info['data']:
        worker_data = dict(worker)
        worker_attr = Worker_profit(worker_data)
        counter = 0
        for c in worker_attr.w_get_coin:
            if c not in coinlist:
                coinlist.append(c)
                price = Coin.get_coin_info(c)
                write_to_prom.set_mark(price['price'], c, 'coin_price')
            labels = [worker_attr.w_name, c]
            logger.debug(f'created labels {labels}')
            hour_metric = worker_attr.clean_profit[c]['hourly']
            write_to_prom.set_mark(hour_metric, labels, 'clear_profitline_hourly')
            write_to_prom.set_mark(worker_attr.w_hashrate.get(c), [labels[0], 
                worker_attr.w_algo[counter]],'worker_hashrate')
            counter += 1

    try:
        workers_info = h_api.h_get_workers_info(workers_dict)
        for worker in workers_info['data']:
            worker_data = dict(worker)
            worker_attr = Worker_profit(worker_data)
            counter = 0
            for c in worker_attr.w_get_coin:
                if c not in coinlist:
                    coinlist.append(c)
                    price = Coin.get_coin_info(c)
                    write_to_prom.set_mark(price['price'], c, 'coin_price')
                labels = [worker_attr.w_name, c]
                logger.debug(f'created labels {labels}')
                daily_metric, hour_metric = worker_attr.clean_profit[c]['daily'], worker_attr.clean_profit[c]['hourly']
                #write_to_prom.set_mark(daily_metric, labels, 'clear_profitline_daily') # could be done in prometheus
                write_to_prom.set_mark(hour_metric, labels, 'clear_profitline_hourly')
                write_to_prom.set_mark(worker_attr.w_hashrate.get(c), [labels[0], 
                    worker_attr.w_algo[counter]],'worker_hashrate')
                counter += 1
    except Exception as e:
        logger.error(f'some shit happened! sleeping anf hope inst gone')
    

def mainloop():
    while True:
        try:
            logic()
            logger.info('sleeping')
            time.sleep(600)
        except KeyboardInterrupt:
            logger.info('keyboard interrupt...')
            sys.exit(0)



if __name__ == '__main__':
    ar = argparser()
    h_api = api.Wrapper(hiveos_token)
    farms_list = h_api.h_get_farms_ids()
    workers_dict = h_api.h_get_workers_ids(farms_list)
    write_to_prom = prom_exporter.Prom_metrics()
    mainloop()
