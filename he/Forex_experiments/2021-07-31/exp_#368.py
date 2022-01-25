"""
    Experiment description:
    In this experiment, instead of using day difference to sort markets by their 
    validity, I would use volatility of past day to choose them. Simulation of trading 
    still will be on 06/07/2021 but data would be from previus day. Instead of traiding
    fisrt of all would be compared two list one from traiding day difference and one from volatility
    If there would not be much difference, searching for another method in volatility
    would be continued. 
    old method gives us:            new method gives us:
    ['USDCAD',                      'GBPJPY'
    'NZDCAD',                       'NZDJPY'
    'GBPCAD',                       'AUDJPY'
    'EURCAD',                       'CADJPY'
    'AUDCAD',                       'EURJPY'
    'USDCHF',                       'CHFJPY'
    'EURAUD',                       'USDJPY'
    'NZDCHF',                       'EURNZD'
    'EURGBP',                       'GBPCAD'
    'EURNZD',                       'EURAUD'
    'EURCHF',                       'EURCAD'
    'AUDCHF',                       'USDCAD'
    'NZDUSD',                       'GBPUSD'
    'AUDNZD',                       'NZDCAD'
    'USDJPY',                       'AUDCAD'
    'EURUSD',                       'NZDUSD'
    'GBPUSD',                       'AUDUSD'
    'AUDUSD',                       'AUDNZD'
    'NZDJPY',                       'EURUSD'
    'CHFJPY',                       'NZDCHF'
    'GBPJPY',                       'AUDCHF'
    'EURJPY',                       'CADCHF'
    'AUDJPY',                       'USDCHF'
    'CADCHF',                       'EURGBP'
    'CADJPY'                        'EURCHF']

    list on day before(05/07/2021):
    new method:  ['GBPJPY', 'CHFJPY', 'NZDJPY', 'EURJPY', 'AUDJPY', 'CADJPY', 'USDJPY', 'EURNZD', 'GBPCAD', 'EURAUD', 'EURCAD', 'GBPUSD', 'NZDCAD', 'USDCAD', 'AUDCAD', 'NZDUSD', 'AUDNZD', 'NZDCHF', 'AUDUSD', 'EURUSD', 'AUDCHF', 'CADCHF', 'USDCHF', 'EURGBP', 'EURCHF']

"""
import datetime 
import os
import shutil
import pickle
import Internet_protocols
import logging
import time
import pathlib
import logging.handlers
from iqoptionapi.stable_api import IQ_Option
from tqdm import tqdm
import sys
'''----------------------------------------------------------------------------------------------'''

if os.name == 'posix':
    path = pathlib.PurePosixPath(os.path.abspath(__file__)).parent 
    if 'Forex_experiments' in path.parts:
        path = path.parent / str(datetime.date.today())
    else:
        path = path / 'Forex_experiments'  / str(datetime.date.today())
    # After this, path is equals to current date folder
    file_path = pathlib.PurePosixPath(os.path.abspath(__file__))
else:
    path = pathlib.PureWindowsPath(os.path.abspath(__file__)).parent 
    if 'Forex_experiments' in path.parts:
        path = path.parent / str(datetime.date.today())
    else:
        path = path / 'Forex_experiments'  / str(datetime.date.today())
    # After this, path is equals to current date folder
    file_path = pathlib.PureWindowsPath(os.path.abspath(__file__))
    
try:
    os.mkdir(str(path))
except OSError as ose:
    pass

try:
    experiment_number = pickle.load(open(str(path.parent / 'experiment_number.pkl'), 'rb+')) + 1
except FileNotFoundError:
    experiment_number = 1
pickle.dump(experiment_number, open(str(path.parent / 'experiment_number.pkl'), 'wb+'))

shutil.copy(file_path, path / (file_path.stem + str(experiment_number) + file_path.suffix) )

'''----------------------------------------------------------------------------------------------'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
"""StreamHandler"""
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG) 
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
"""FileHandler"""
rotatingfile_handler = logging.handlers.RotatingFileHandler(path.parent/'main.log', backupCount=5, maxBytes=1073741824)
rotatingfile_handler.setLevel(logging.DEBUG)
rotatingfile_handler.setFormatter(formatter)
logger.addHandler(rotatingfile_handler)

logger.info('Main Entry ' + str(experiment_number))
'''----------------------------------------------------------------------------------------------'''

sleep_time = 60*3


if __name__ == '__main__':
    try:
        Internet_protocols.checkInternetRequests()

        connector =IQ_Option("ww.bingonemo@gmail.com","JF*#3C5va&_NDqy")
        connector.connect()

        connector.update_ACTIVES_OPCODE()
        ALL_Asset = connector.get_all_open_time()
       

        date = datetime.date(year= 2021, month=7, day=6)
        end_from_time = time.mktime(date.timetuple())
        
        # Here goes an old method:: last list is output
        
        past_time_assets_diff_trade = []
        for f in tqdm( ALL_Asset['forex'].keys()):
            data=connector.get_candles(f, 86400, 1, end_from_time)
            diff = data[0].get('close') - data[0].get('open') 
            mean = data[0].get('open') + data[0].get('close')
            count = 0
            for ps in past_time_assets_diff_trade:
                if ps[1] <  diff/(2*mean):
                    past_time_assets_diff_trade =  past_time_assets_diff_trade[:count] + [ (f, diff/(2*mean))] + past_time_assets_diff_trade[count:]
                    break
                count += 1

            else:
                past_time_assets_diff_trade.append((f, diff/(2*mean)))
        past_time_assets = [x[0] for x in past_time_assets_diff_trade ]


        print(past_time_assets)
        
        # Here goes N1 try of volatility
        """
        past_time_vol_assets = []
        for f in tqdm(ALL_Asset['forex'].keys()):
            data = connector.get_candles(f, 120, 720, end_from_time)
            volatility = 0
            for candle in data:
                volatility += candle.get("max") - candle.get("min")

            count = 0
            for ps in past_time_vol_assets:
                if ps[1] < volatility:
                    past_time_vol_assets = past_time_vol_assets[:count] + [(f, volatility)] + past_time_vol_assets[count:]
                    break
                count += 1
            else:
                past_time_vol_assets.append((f, volatility))
        past_time_assets = [x[0] for x in past_time_vol_assets ]
        print (past_time_assets)
        """


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.exception(str(e))
        logger.exception([exc_type, fname, exc_tb.tb_lineno])
        Internet_protocols.email(str(e), subj='Error')
        time.sleep(sleep_time)
        logger.info('Restart')
        if os.name == 'posix':
            os.system('sudo reboot')
        else:
            os.system('shutdown /r')