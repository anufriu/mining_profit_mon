import hive_api_wrapper as api
import configparser
import traceback
import sys
from loguru import logger

#logger
logger.remove()
logger.add(sink= sys.stdout, format="[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>][{level}] [<bold>{function}</bold>] ->> <green>{message}</green>",
            level='INFO')

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
    worker_info = h_api.h_get_workers_info(workers_dict)
    print(worker_info)
    print(farms_list, workers_dict)



if __name__ == '__main__':
    h_api = api.Wrapper(hiveos_token)
    farms_list = h_api.h_get_farms_ids()
    workers_dict = h_api.h_get_workers_ids(farms_list)
    logic()