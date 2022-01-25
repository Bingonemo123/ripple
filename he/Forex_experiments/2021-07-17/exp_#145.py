"""
Experiment description:
check for reality of expretiment and real trainding. To compare histrycal data of
06/7/2021 and practice trading of that day will be compared.



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
import operator
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
        opcode_data=connector.get_all_ACTIVES_OPCODE()
        ALL_Asset = connector.get_all_open_time()
        '''        
        instrument_type='forex'
        connector.subscribe_top_assets_updated(instrument_type)
        
        def opcode_to_name(opcode_data,opcode):
            return list(opcode_data.keys())[list(opcode_data.values()).index(opcode)]            

        while True:
            if connector.get_top_assets_updated(instrument_type)!=None:
                break

        top_assets=connector.get_top_assets_updated(instrument_type) # real time prices

        # for asset in top_assets:
        #     print(asset, " <<<<>>>>>")

        diff_trading_day={}
        for asset in top_assets:
            opcode=asset["active_id"]
            diff_trading_day_value=asset["diff_trading_day"]["value"]
            try:
                name=opcode_to_name(opcode_data,opcode)
                diff_trading_day[name]=diff_trading_day_value
            except:
                pass
        
        sorted_diff_trading_day= sorted(diff_trading_day.items(), key=operator.itemgetter(1))

        real_time_assets_diff_trade =  ([x[0] for x in reversed(sorted_diff_trading_day)])
        '''
        date = datetime.date(year= 2021, month=7, day=7)
        end_from_time = time.mktime(date.timetuple())
        past_time_assets_diff_trade = []
        for  f in  ALL_Asset['forex'].keys():

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


        def past_history(f, date=end_from_time):

            psdata = connector.get_candles(f, 86400, 31, date)
            leverage=max(connector.get_available_leverages('forex',f)[1].get('leverages')[0].get('regulated'))
            for candle in psdata:
                if candle.get('max') > ((1.055/leverage) + 1) * data[-1].get('max'):
                    return True
            else:
                return False


        filt_past_time_assets = []
        for f in past_time_assets:
            if past_history(f):
                filt_past_time_assets.append(f)
        buyed_fs = []
        prd = {}
        closed = 0
        for mt in range(1440):
            if connector.check_connect()==False:#detect the websocket is close
                print("try reconnect")
                check,reason=connector.connect()         
                if check:
                    print("Reconnect successfully")
                else:
                    print("No Network")

            #buy
            for f in filt_past_time_assets:
                if len(buyed_fs) >= 3:
                    break
                if f in buyed_fs:
                    continue


                curpr=connector.get_candles(f, 60, 1, end_from_time + mt*60)
                buyed_fs.append(f)
                prd[f] =  curpr[-1].get('max')
        
            # check 

            for f in buyed_fs:

                leverage=max(connector.get_available_leverages('forex',f)[1].get('leverages')[0].get('regulated'))
                curpr=connector.get_candles(f, 120, 1, end_from_time + mt*3*60)
                if curpr[-1].get('max')  > ((0.06/leverage)+ 1)*prd[f]:
                    buyed_fs.remove(f)
                    closed += 1
            print(mt, end=" :: ", flush=True)

        logger.info("\n")
        logger.info(closed)
                    

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.warning(str(e))
        logger.warning([exc_type, fname, exc_tb.tb_lineno])
        Internet_protocols.email(str(e), subj='Error')
        time.sleep(sleep_time)
        logger.info('Restart')
        if os.name == 'posix':
            os.system('sudo reboot')
        else:
            os.system('restarts now')