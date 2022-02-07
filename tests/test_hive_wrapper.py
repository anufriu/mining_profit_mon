import configparser

from src import hive_api_wrapper

path = 'src/config.ini'
config = configparser.ConfigParser()
config.read(path)
hiveos_token = config['hiveos'].get('token')

testclass= hive_api_wrapper.Wrapper(hiveos_token)

def test_request_preset_wrong_req_type():
    """
    check requests types and
    what it returns
    """
    assert testclass.h_req_preset(endpoint='farms', req_type='put') == None




