from  src import minerstat_api, hive_api_wrapper, prometheus_metrics



def test_minerstat():
    """
    check availiability of minerstat
    """ 
    minerstat_obj = minerstat_api.Wrapper()
    assert type(minerstat_obj.get_coin_info(ticker='BTC')) == dict