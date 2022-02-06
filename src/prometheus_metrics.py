'''Creates interface t osend metrics to prometheus'''
import os
import sys

from local_logger import create_logger
from prometheus_client import Gauge, start_http_server

# logger
loglevel = os.environ.get("LOGLEVEL", "DEBUG")
logger = create_logger(loglevel)



class Prom_metrics():
    '''creates http server and send metrics to promethus'''

    def __init__(self, port):
        self.http_server = start_http_server(port)
        self.gauge_hourly = Gauge('clear_profitline_hourly', 'farm profit',
                                  ['worker_name', 'coin'])
        self.gauge_hashrate = Gauge('worker_hashrate', 'actual worker hashrate',
                                    ['worker_name', 'algo'])
        self.gauge_coin_price = Gauge('coin_price', 'actual_coin_price',
                                      ['coin'])
        self.gauge_network_hashrate = Gauge('network_hashrate',
                                            'current network hasrate', ['coin', 'algo'])
        self.gauge_est_in_coin_profit = Gauge('worker_incoin_profit', 'profit in coin',
                                              ['coin', 'worker'])

    def set_mark(self, metric, labels, metric_name):
        '''set Gauge mark and add labels to metric'''
        try:
            if metric_name == 'clear_profitline_hourly':
                self.gauge_hourly.labels(
                    worker_name=labels[0], coin=labels[1]).set(metric)
            elif metric_name == 'worker_hashrate':
                self.gauge_hashrate.labels(
                    worker_name=labels[0], algo=labels[1]).set(metric)
            elif metric_name == 'coin_price':
                self.gauge_coin_price.labels(coin=labels).set(metric)
            elif metric_name == 'network_hashrate':
                self.gauge_network_hashrate.labels(
                    coin=labels[0], algo=labels[1]).set(metric)
            elif metric_name == 'worker_incoin_profit':
                self.gauge_est_in_coin_profit.labels(
                    coin=labels[0], worker=labels[1]).set(metric)
            logger.debug(
                f'created metric with type {metric_name} and value is: {metric}')
        except Exception as e:
            logger.error(f'error while setting metric {metric_name}, {e}')
