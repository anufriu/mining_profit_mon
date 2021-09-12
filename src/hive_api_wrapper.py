import requests
import sys
import traceback
from loguru import logger
#logger
logger.remove()
logger.add(sink= sys.stdout, format="[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>][{level}] [<bold>{function}</bold>] ->> <green>{message}</green>",
            level='INFO')

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
        self.headers = {'accept': 'application/json', 
            'Content-Type': 'application/json', 'Authorization': f'{token}'}
        self.main_url = 'https://api2.hiveos.farm/api/v2/'
 
    def h_req_preset(self, endpoint:str, req_type:str="get", payload:dict={}):
        '''готовим обьект requests'''
        logger.info(f'processing endpoint {endpoint} with request type: {req_type}')
        try:
            url_and_endpoint = str(self.main_url+endpoint)
            if req_type == "get":
                req = requests.get(url_and_endpoint, headers=self.headers)
            elif req_type == "post":
                print(payload)
                req = requests.post(url_and_endpoint, headers=self.headers, data=payload)
            if req.status_code in [200, 201]:
                logger.info('status code 200 all ok')
                return req
            else:
                logger.error(f'status code is not ok got {req.status_code} with message: {req.text}')
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f'problem with processing request to Hive got {e}')
            return None



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
                print({"command": command, "data": {}})
                logger.info(f'executed command: {command} with result: {req.json()}')
            else:
                logger.info('worker {worker_name} not found or not in list')

    def h_get_workers_info(self, farm_info):
        '''
        get all worker info
        '''
        logger.info(f'collecting info..')
        for farm in farm_info.keys():
            for worker in farm_info[farm]:
                try:
                    req = self.h_req_preset(endpoint=f'​farms​/{farm}​/workers​/{list(worker.values())[0]}')
                    if req and  req.status_code == 200:
                        return req.json
                    else:
                        return None
                except Exception as e:
                    logger.error(f'Exception occured while processing {list(worker.keys())[0]} --> {e}')
