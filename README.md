# IMPORTANT!!! This tool has currently stopped working, when the hiveos team fixes the api authorization it will be fine again. see [this](https://hiveon.com/forum/t/hive-api-v2/4490) for more information
# hiveos worker profit monitoring
Overview:
This is a MVP project for estimated mining profit visualisation via Grafana\Prometheus using HiveOS and minerstat api.
Requeres preinstalled Python3+ Grafana and Prometheus. Im using this [stuff](https://github.com/stefanprodan/dockprom)
![How it looks](https://github.com/anufriu/mining_profit_mon/blob/master/images/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202022-02-22%20%D0%B2%2017.35.49.png)

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
python3 main.py -c $PATHTOCONFIGFILE
```
#### Creating grafana dashboard
you can export [this](https://github.com/anufriu/hiveos_mon/blob/master/grafana_preset/Miner%20stat-example.json) file to grafana or create new dashboard
##### Metrics
at this moment we have only 3 type of metric. They all Gauge
1) clear_profitline_hourly - shows estimated profit by coin\worker considering power consumption*powercost
2) worker_hashrate - showы worker hashrate
3) coin_price - shows the price of the coin that is currently being mined.
4) network_hashrate - network hashrate summary
5) worker_incoin_profit - worker estimated profit in current mining coin
6) * two_miners_actual_profitline_24h - optional if you using 2miners pool you can add your wallet address in config and set 2minerstat parameter to enabled=True ut can support any coin, but myltiplyer calculated only for ETH and RVN. pls open issue\pull request to change it.


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
