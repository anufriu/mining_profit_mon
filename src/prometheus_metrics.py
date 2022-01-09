import time
from prometheus_client import start_http_server, Summary, Gauge, CollectorRegistry


class Prom_metrics():
    def __init__(self):
        self.http_server = start_http_server(8910)
        self.gauge_daily = Gauge('clear_profitline_daily', 'farm profit', 
            ['worker_name', 'coin'])
        self.gauge_hourly = Gauge('clear_profitline_hourly', 'farm profit',
             ['worker_name', 'coin'])

    def set_mark(self, metric, labels, metric_name):
        if metric_name == 'daily':
            self.gauge_daily.labels(worker_name=labels[0], coin=labels[1]).set(metric)
        elif metric_name == 'hourly':
            self.gauge_hourly.labels(worker_name=labels[0], coin=labels[1]).set(metric)
