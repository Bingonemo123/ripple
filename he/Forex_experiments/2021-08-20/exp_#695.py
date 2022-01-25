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
       

        date = datetime.date(year= 2021, month=8, day=18)  # day must be + 1,beacuse this is end date
        end_from_time = time.mktime(date.timetuple())
        
        
        # Volatility with standart deviation
      
        past_time_vol_assets = []
        for f in tqdm(ALL_Asset['forex'].keys()):
            data = connector.get_candles(f, 86400, 200, end_from_time)


            percList = []
            for candle in data:
                percent = (candle.get('max') - candle.get('min'))/ candle.get('min')
                percList.append(percent)


            volatility = sum(percList)/len(percList)


            # storting 
            count = 0
            for ps in past_time_vol_assets:
                if ps[1] < volatility:
                    past_time_vol_assets = past_time_vol_assets[:count] + [(f, volatility)] + past_time_vol_assets[count:]
                    break
                count += 1
            else:
                past_time_vol_assets.append((f, volatility))
        past_time_assets = [x[0] for x in past_time_vol_assets ]
        data_assets =  [x[1] for x in past_time_vol_assets ]
        print (past_time_assets)
        print( past_time_vol_assets)
        print(sum(data_assets)/len(data_assets))


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