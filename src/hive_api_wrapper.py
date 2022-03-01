'''hiveos api wrapper with most useful methods'''
import os

import requests

from local_logger import create_logger

# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
logger = create_logger(loglevel)


class Wrapper():
    ''' класс реализующий обертку над requests
    содержит методы для работы с HIVE API
    https://app.swaggerhub.com/apis/HiveOS/public/2.1-beta
    init args:
        - token: $token токен из https://the.hiveos.farm/account
        - headers: {'accept': 'application/json',  'Authorization': 'Bearer $accessToken'}
    '''

    def __init__(self, token: str):
        self.token = token
        self.headers = {'accept': 'application/json',
                        'Content-Type': 'application/json', 'Authorization': f'{token}'}
        self.main_url = 'https://api2.hiveos.farm/api/v2/'

    def h_req_preset(self, endpoint: str, req_type: str = "get", payload: dict={}):
        '''готовим обьект requests'''
        logger.info(
            f'processing endpoint {endpoint} with request type: {req_type}')
        status_code = 500
        text = str()
        req = None
        try:
            url_and_endpoint = str(self.main_url+endpoint)
            logger.debug(
                f'URL: {url_and_endpoint}, request type: {req_type}, payload: {payload}')
            if req_type not in ["get", "post"]:
                logger.error(f'usupported request type got {req_type}')
            if req_type == "get":
                req = requests.get(url_and_endpoint, headers=self.headers)
                status_code= req.status_code
                text = req.text
            elif req_type == "post":
                req = requests.post(
                    url_and_endpoint, headers=self.headers, json=payload)
                status_code= req.status_code
                text = req.text
            if status_code == 200:
                logger.info('status code 200 all ok')
            else:
                logger.error(
                    f'status code is not ok: {status_code} with message: {text}')
        except requests.exceptions.RequestException as error:
            logger.error(f'problem with processing request to Hive got {error}')
        return req

    @staticmethod
    def _get_info_from_worker_dct(target_list:list, target_keys:list)->list:
        '''
        get list of dicts to get values by keys
        returns list
        '''
        resulting_list = []
        try:
            for target in target_list:
                for key in target_keys:
                    if target.get(key):
                        resulting_list.append(target.get(key))
            return resulting_list
        except KeyError:
            logger.error('No such keys in json')
        except TypeError:
            logger.error('invalid worker info type recieved!')
        return resulting_list

    def h_get_farms_ids(self) -> list:
        '''get worker list'''
        farms_info = self.h_req_preset(endpoint='farms', req_type='get')
        farms_ids = []
        if farms_info:
            farms_ids = [farm['id'] for farm in farms_info.json().get('data')]
            logger.info(f'got farms ids list {farms_ids}')
        else:
            logger.error('cant get farm ids!')
        return farms_ids

    def h_get_workers_ids(self, farms) -> dict:
        '''get farm or worker dict
        {farm_id: [{worker_name: worker_id}]}
        '''
        worker_ids = {}
        if not farms:
            logger.error('Cant get info about farms!')
        for farm_id in farms:
            data = self.h_req_preset(
                endpoint=f'farms/{farm_id}/workers2', req_type='get')
            if data:
                worker_ids = {farm_id: [{worker['name']:worker['id']}
                                        for worker in data.json().get('data')]}
                logger.info(f'got farm ids list {worker_ids}')
            else:
                logger.error('got empty Data... returning empty dct')
        return worker_ids

    def h_post_command_execute(self, command, worker_name, farms):
        '''execute command in hiveos'''
        logger.info(f'trying to execute command: {command}..')
        farms_and_workers = self.h_get_workers_ids(farms)
        for farm, worker in farms_and_workers.items():
            worker = worker[0]
            if worker_name in worker.keys():
                req = None
                try:
                    req = self.h_req_preset(endpoint=f'farms/{farm}/workers/{worker[worker_name]}/command',
                                            req_type="post", payload={"command": "exec", "data": {"cmd": f"{command}"}})
                except AttributeError:
                    logger.error(
                        f'got invalid answer from h_req_preset func recieved {req}')
                    return
                if req:
                    logger.info(
                        f'executed command: {command} with result: {req.json()}')
            else:
                logger.info('worker {worker_name} not found or not in list')

    def h_get_workers_info(self, farm_info):
        '''
        get all worker info
        '''
        logger.info('collecting info..')
        worker_info = None
        for farm in farm_info.keys():
            try:
                req = self.h_req_preset(
                    endpoint=f'farms/{farm}/workers2', req_type='get')
                if req and req.status_code == 200:
                    worker_info =  req.json()
            except Exception as error:
                logger.error(f'Exception occured while processing: {error}')
        return worker_info

    def h_get_workers_gpus(self, farm_id, worker_ids: list):
        '''
        get worker gpu info
        '''
        logger.info('processing')
        ids = []
        res = None
        for i in worker_ids:
            for k, value in i.items():
                ids.append(str(value))
        worker_ids_formatted = '%2C'.join(ids)
        endpoint = f'farms/{farm_id}/workers/gpus?worker_ids={worker_ids_formatted}'
        try:
            req = self.h_req_preset(endpoint=endpoint, req_type='get')
            if req and req.status_code == 200:
                res = req.json()
            else:
                res = None
        except Exception as error:
            logger.error(f'Exception occured {error}')
        return res

    def h_get_benchmark_jobs(self, farm_id):
        """currently not working

        Args:
            farm_id (int): farm id in hiveos

        Returns:
            json: list of benchmarks
        """
        logger.info('processing')
        endpoint = f'farms/{farm_id}/benchmarks/jobs'
        res = None
        try:
            req = self.h_req_preset(endpoint=endpoint, req_type='get')
            if req and req.status_code == 200:
                res = req.json()
            else:
                res = None
        except Exception as error:
            logger.error(f'Exception occured {error}')
        return res

    def h_post_benchmark(self, farm_id, worker_id=None):
        """start benchmark job

        Args:
            farm_id (int): farm id from hiveos
            worker_id (int, optional): farm id from hiveos. Defaults to None.

        Returns:
            json: result of post request
        """
        logger.info('processing')
        endpoint = f'farms/{farm_id}/benchmarks'
        data = {'worker_id': worker_id,
                'algos': ['ethash']}
        try:
            req = self.h_req_preset(
                endpoint=endpoint, req_type='post', payload=data)
            if req and req.status_code == 201:
                res = req.json()
                logger.info(f'sucsesfully processed with response {res}')
            else:
                res = None
                logger.error('non 200 recieved')
        except Exception as error:
            logger.error(f'Exception occured {error}')
            res = None
        logger.info('processed')
        return res

    def h_get_worker_hashrate(self, worker):
        '''returns worker hashrate in hash (not mega hash or etc) by coin'''
        dict_with_hasrates = {}
        try:
            target_lst = worker['miners_summary']['hashrates']
            if not target_lst:
                logger.error('cant get miner summary')
                return dict_with_hasrates
            for miner in target_lst:
                miner_l = []
                miner_l.append(miner)
                # solomine
                coin = self._get_info_from_worker_dct(miner_l, ['coin'])
                hashrate = self._get_info_from_worker_dct(miner_l, ['hash'])
                dict_with_hasrates[coin[0]] = hashrate[0]
                # for dualmine
                dcoin = self._get_info_from_worker_dct(miner_l, ['dcoin'])
                dhash = self._get_info_from_worker_dct(miner_l, ['dhash'])
                if dcoin:
                    dict_with_hasrates[dcoin[0]] = dhash[0]
            logger.debug(f'got reult {dict_with_hasrates}')
            return dict_with_hasrates
        except IndexError as error:
            logger.error(f'got index error while processing {error}')
        except KeyError:
            logger.error('No such keys in json')
        except TypeError:
            logger.error('invalid worker info type recieved!')
        return dict_with_hasrates

    def h_get_worker_algo(self, worker):
        """get current worker algoritm

        Args:
            worker (int): id

        Returns:
            list: list of algos
        """
        algolist = []
        try:
            target_lst = worker['miners_summary']['hashrates']
            algolist = self._get_info_from_worker_dct(target_lst, ['algo', 'dalgo'])
        except KeyError:
            logger.error('No such keys in json')
        except TypeError:
            logger.error('invalid worker info type recieved!')
        return algolist

    def h_get_worker_coin(self, worker):
        """get current mining coins

        Args:
            worker (int): id

        Returns:
            list: list of coins
        """
        coinlist = []
        try:
            target_lst = worker['miners_summary']['hashrates']
            coinlist = self._get_info_from_worker_dct(target_lst, ['coin', 'dcoin'])
        except KeyError:
            logger.error('No such keys in json')
        except TypeError:
            logger.error('invalid worker info type recieved!')
        return coinlist

    @staticmethod
    def h_get_worker_power_cons(worker):
        """get worker power consumption in watts

        Args:
            worker (int): id

        Returns:
            int: power consumption
        """
        powerdraw = str()
        try:
            powerdraw =  worker['stats']['power_draw']
        except KeyError:
            logger.error('No such keys in json')
        except TypeError:
            logger.error('invalid worker info type recieved!')
        return powerdraw

    @staticmethod
    def h_get_worker_name(worker):
        """get worker name

        Args:
            worker (id): id

        Returns:
            str: worker name
        """
        worker_name = str()
        try:
            worker_name = worker['name']
        except KeyError:
            logger.error('No such keys in json')
        except TypeError:
            logger.error('invalid worker info type recieved!')
        return worker_name
