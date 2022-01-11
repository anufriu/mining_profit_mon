import time
import os
import sys
from prometheus_client import start_http_server, Summary, Gauge, CollectorRegistry
from loguru import logger

#logger
logger.remove()
logger.level("INFO", color="<green>")
logger.level("DEBUG", color="<magenta>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.add(sink=sys.stdout,
format="[{time:YYYY-MM-DD at HH:mm:ss}] <level>[{level}] <bold>[{function}]</bold> {message}</level>",
level= os.environ.get("LOGLEVEL", "DEBUG"), backtrace=True, diagnose=True)

class Prom_metrics():
    def __init__(self):
        self.http_server = start_http_server(8910)
        self.gauge_daily = Gauge('clear_profitline_daily', 'farm profit', 
            ['worker_name', 'coin'])
        self.gauge_hourly = Gauge('clear_profitline_hourly', 'farm profit',
            ['worker_name', 'coin'])
        self.gauge_hashrate = Gauge('worker_hashrate', 'actual worker hashrate',
            ['worker_name', 'algo'])
        self.gauge_coin_price = Gauge('coin_price', 'actual_coin_price',
            ['coin'])

    def set_mark(self, metric, labels, metric_name):
        try:
            if metric_name == 'clear_profitline_daily':
                self.gauge_daily.labels(worker_name=labels[0], coin=labels[1]).set(metric)
            elif metric_name == 'clear_profitline_hourly':
                self.gauge_hourly.labels(worker_name=labels[0], coin=labels[1]).set(metric)
            elif metric_name == 'worker_hashrate':
                self.gauge_hashrate.labels(worker_name=labels[0], algo=labels[1]).set(metric)
            elif metric_name == 'coin_price':
                self.gauge_coin_price.labels(coin=labels[0]).set(metric)
        except Exception as e:
            logger.error(f'error while setting metric {metric_name}, {e}')

