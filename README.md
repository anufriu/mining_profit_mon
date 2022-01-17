# hiveos worker profit monitoring
Overview:
This is a MVP project for estimated mining profit visualisation via Grafana\Prometheus using HiveOS and minerstat api.
Requeres preinstalled Python3+ Grafana and Prometheus. Im using this [stuff](https://github.com/stefanprodan/dockprom)
![How it looks](https://github.com/anufriu/mining_profit_mon/blob/master/images/new_preview.png)

## INSTALLATION
__clone this repo__
```
git clone git@github.com:anufriu/hiveos_mon.git
```
__install requerenment packages__
```
python3 -m pip install requirements.txt
```
### First run
__create config file__
```
cp config_samle.ini config.ini
```
__open file with your favorite text editor and fill the parameters__
```
[hiveos]
token='Authorization: Bearer YOURHIVEOSTOKEN'
[constants]
powercost=0.1
[hiveon_stat]
miner_wallet='ETHWALLET'
```
__start the code__
```
python3 main.py
```
#### Creating grafana dashboard
you can export [this](https://github.com/anufriu/hiveos_mon/blob/master/grafana_preset/Miner%20stat-example.json) file to grafana or create new dashboard
##### Metrics
at this moment we have only 3 type of metric. They all Gauge
1) clear_profitline_hourly - shows estimated profit by coin\worker considering power consumption*powercost
2) worker_hashrate - showы worker hashrate
3) coin_price - shows the price of the coin that is currently being mined.

###### Prometheus configuration
prometehus http server starts on port 8910 by default, you can change this in config.ini file
on host with prometheus which scraping metrics edit the __prometeus.yml__ file
with this:
```
scrape_configs:  
  - job_name: 'JOBNAME'
    scrape_interval: 90s
    static_configs:
      - targets: ['YURHOSTIP:PORTFROMCONFIG']
```
Feel free to contribute
