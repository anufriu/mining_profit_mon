import hive_api_wrapper as api
import configparser
import traceback
import sys
import argparse
import os
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
    print(args.loglevel)
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
    if hiveos_token:
        pass
    else:
        logger.error(f'cant find token field check the config. exiting...')
        sys.exit(1)
except configparser.Error:
    logger.error(f'problem with config parsing: {traceback.print_exception()}\n exiting...')
    sys.exit(1)


def logic():
    workers_info = h_api.h_get_workers_info(workers_dict)
    for worker in workers_info['data']:
        print(worker['stats'].keys())
        print(worker['miners_summary'])
        worker_data = dict(worker)
        w_name = h_api.h_get_worker_name(worker_data)
        w_hashrate = h_api.h_get_worker_hashrate(worker_data)
        w_algo = h_api.h_get_worker_algo(worker_data)
        w_power_cons = h_api.h_get_worker_power_cons(worker_data)
        w_get_coin = h_api.h_get_worker_coin(worker_data)
        logger.debug(f'worker name: {w_name}, algo: {w_algo}, '\
             f'hashrate: {w_hashrate} power_consumption: {w_power_cons}, coin: {w_get_coin}')
    

if __name__ == '__main__':
    ar = argparser()
    h_api = api.Wrapper(hiveos_token)
    farms_list = h_api.h_get_farms_ids()
    workers_dict = h_api.h_get_workers_ids(farms_list)
    logic()