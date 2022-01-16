# hiveos_mon
Overview:
This is a MVP project for mining profit visualisation via Grafana\Prometheus using HiveOS and minerstat api.
Requeres preinstalled Python3+ Grafan and Prometheus. Im using this [stuff](https://github.com/stefanprodan/dockprom)

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
#### Metrics
at this moment we have only 3 type of metric. They all Gauge
1) clear_profitline_hourly - shows estimated profit by coin\worker considering power consumption*powercost
2) worker_hashrate - showы worker hashrate
3) coin_price - shows the price of the coin that is currently being mined.
