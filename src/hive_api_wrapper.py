import requests
import sys
import traceback
import json
import os
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

class Wrapper():
    ''' класс реализующий обертку над requests
    содержит методы для работы с HIVE API
    https://app.swaggerhub.com/apis/HiveOS/public/2.1-beta
    init args:
        - token: $token токен из https://the.hiveos.farm/account
        - headers: {'accept': 'application/json',  'Authorization': 'Bearer $accessToken'}
    '''


    def __init__(self, token:str):
        self.token = token
        self.headers = {'accept': 'application/json', 'accept': 'application/pdf',
            'Content-Type': 'application/json', 'Authorization': f'{token}' }
        self.main_url = 'https://api2.hiveos.farm/api/v2/'
 
    def h_req_preset(self, endpoint:str, req_type:str="get", payload:dict={}):
        '''готовим обьект requests'''
        logger.info(f'processing endpoint {endpoint} with request type: {req_type}')
        try:
            url_and_endpoint = str(self.main_url+endpoint)
            logger.debug(f'URL: {url_and_endpoint}, request type: {req_type}, payload: {payload}')
            if req_type == "get":
                req = requests.get(url_and_endpoint, headers=self.headers)
                res = req
            elif req_type == "post":
                req = requests.post(url_and_endpoint, headers=self.headers, json=payload)
                res = req
            if req.status_code in [200, 201]:
                logger.info('status code 200 all ok')
                res = req
            else:
                logger.error(f'status code is not ok got {req.status_code} with message: {req.text}')
                res = None
            logger.debug(f'request result: {res}')
        except requests.exceptions.RequestException as e:
            logger.error(f'problem with processing request to Hive got {e}')
            res = None
        return res



    def h_get_farms_ids(self) ->list:
        '''get worker list'''
        data = self.h_req_preset(endpoint='farms', req_type='get')
        if data:
            ids = [farm['id'] for farm in data.json().get('data')]
            logger.info(f'got farms ids list {ids}')
            return ids
        else:
            logger.error(f'got empty Data... returning None')
            return None

    def h_get_workers_ids(self, farms) ->dict:
        '''get farm\worker dict {farm_id: [{worker_name: worker_id}]} '''
        farm_ids = farms
        for farm_id in farm_ids:
            data = self.h_req_preset(endpoint=f'farms/{farm_id}/workers', req_type='get')
            if data:
                worker_ids = { farm_id:[{worker['name']:worker['id']} for worker in data.json().get('data')]}
                logger.info(f'got farm ids list {worker_ids}')
            else:
                logger.error(f'got empty Data... returning None')
                return None
        return worker_ids
    
    def h_post_command_execute(self, command, worker_name):
        '''execute command in hiveos'''
        logger.info(f'trying to execute command: {command}..')
        farms_and_workers= self.h_get_workers_ids()
        for farm, worker in farms_and_workers.items():
            worker = worker[0]
            if worker_name in worker.keys():
                try:
                    req = self.h_req_preset(endpoint=f'farms/{farm}/workers/{worker[worker_name]}/command',
                        req_type="post", payload={"command": "exec", "data": {"cmd":f"{command}"}})
                except AttributeError:
                    logger.error(f'got invalid answer from h_req_preset func recieved {req}')
                    return
                logger.info(f'executed command: {command} with result: {req.json()}')
            else:
                logger.info('worker {worker_name} not found or not in list')

    def h_get_power_report(self, farm_ids)-> dict:
        '''
        get power report
        '''
        res = {}
        for f in farm_ids:
            try:
                req = self.h_req_preset(endpoint=f'farms/{f}/power_report?start_date=2021-12-01&period=3d&action=download&worker_ids=3859467%2C203704769', req_type='get')
                if req and req.status_code == 200:
                    res[f] = req.json()
                else:
                    res[f] = None
            except Exception as e:
                logger.error(f'Exception occured {e}')
        return res

    def h_get_workers_info(self, farm_info):
        '''
        get all worker info
        '''
        logger.info(f'collecting info..')
        for farm in farm_info.keys():
            for worker in farm_info[farm]:
                try:
                    req = self.h_req_preset(endpoint=f'farms/{37347}/workers', req_type='get')
                    if req and req.status_code == 200:
                        return req.json()
                    else:
                        return None
                except Exception as e:
                    logger.error(f'Exception occured while processing {list(worker.keys())[0]} --> {e}')

    def h_get_workers_gpus(self, farm_id, worker_ids:list):
        '''
        get worker gpu info
        '''
        logger.info('processing')
        ids = []
        for i in worker_ids:
            for k, v in i.items():
                ids.append(str(v))
        worker_ids_formatted = '%2C'.join(ids)
        endpoint = f'farms/{farm_id}/workers/gpus?worker_ids={worker_ids_formatted}'
        try:
            req = self.h_req_preset(endpoint=endpoint, req_type='get')
            if req and req.status_code == 200:
                res = req.json()
            else:
                res = None
        except Exception as e:
            logger.error(f'Exception occured {e}')
        return res

    def h_get_benchmark_jobs(self, farm_id, worker_id=None):
        logger.info('processing')
        endpoint = f'farms/{farm_id}/benchmarks/jobs'
        try:
            req = self.h_req_preset(endpoint=endpoint, req_type='get')
            if req and req.status_code == 200:
                res = req.json()
            else:
                res = None
        except Exception as e:
            logger.error(f'Exception occured {e}')
        return res

    def h_post_benchmark(self, farm_id, worker_id=None):
        logger.info('processing')
        endpoint = f'farms/{farm_id}/benchmarks'
        data = {'worker_id': worker_id,
                'algos': ['ethash']}
        try:
            req = self.h_req_preset(endpoint=endpoint, req_type='post', payload=data)
            print(req.json())
            if req and req.status_code == 201:
                res = req.json()
                logger.info(f'sucsesfully processed with response {res}')
            else:
                res = None
                logger.error(f'non 200 recieved')
        except Exception as e:
            logger.error(f'Exception occured {e}')
            res = None
        logger.info('processed')
        return res





