from iqoptionapi.stable_api import IQ_Option
# import Internet_protocols
import logging.handlers
import logging
import time
import sys
import os
import pickle
import pathlib
import os
import datetime
import json
connector = IQ_Option("ww.bingonemo@gmail.com", "JF*#3C5va&_NDqy")
connector.connect()


'''----------------------------------------------------------------------------------------------'''
if os.name == 'posix':
    path = pathlib.PurePosixPath(os.path.abspath(__file__)).parent
    if 'Forex_experiments' in path.parts:
        path = path.parent / str(datetime.date.today())
    else:
        path = path / 'Forex_experiments' / str(datetime.date.today())
    # After this, path is equals to current date folder
    file_path = pathlib.PurePosixPath(os.path.abspath(__file__))
else:
    path = pathlib.PureWindowsPath(os.path.abspath(__file__)).parent
    if 'Forex_experiments' in path.parts:
        path = path.parent / str(datetime.date.today())
    else:
        path = path / 'Forex_experiments' / str(datetime.date.today())
    # After this, path is equals to current date folder
    file_path = pathlib.PureWindowsPath(os.path.abspath(__file__))

try:
    os.mkdir(str(path))
except OSError as ose:
    pass

try:
    experiment_number = pickle.load(
        open(str(path.parent / 'experiment_number.pkl'), 'rb+')) + 1
except FileNotFoundError:
    experiment_number = 1
pickle.dump(experiment_number, open(
    str(path.parent / 'experiment_number.pkl'), 'wb+'))

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
rotatingfile_handler = logging.handlers.RotatingFileHandler(path/'main.log', backupCount=5, maxBytes=1073741824)
rotatingfile_handler.setLevel(logging.INFO)
rotatingfile_handler.setFormatter(formatter)
logger.addHandler(rotatingfile_handler)
#----------------------------------------------------------------------------#
logger.info(file_path.stem + '  ' + str(experiment_number))

#----------------------------------------------------------------------------#
connector.change_balance("PRACTICE")
instrument_type = "forex"
side = "buy"
type_market = "market"
limit_price = None
stop_price = None
stop_lose_kind = None
stop_lose_value = None
take_profit_kind = 'percent'
take_profit_value = 1
use_trail_stop = False
auto_margin_call = True
use_token_for_commission = False
#----------------------------------------------------------------------------#
datapath = path / ('data_' + file_path.stem + '.pkl')
#----------------------------------------------------------------------------#
while True:
    try:
        try:
            data = pickle.load(open(datapath, 'rb'))
        except:
            data = []
            pickle.dump(data, open(datapath, 'bw'))
        logger.debug('w1')
        while True:
            if connector.check_connect() == False:
                check, reason = connector.connect()
            else:
                break
        logger.debug('uw1')

        ALL_Asset = connector.get_all_open_time()  # loop warning

        open_digits = [x for x in ALL_Asset[instrument_type]if ALL_Asset[instrument_type][x].get('open')]

        for i in range(5):

            checklist = []
            for f in open_digits:
                connector.start_candles_stream(f[:6], 5, 600)  # loop warning
                candles = list(
                    connector.get_realtime_candles(f[:6], 5).values())
                # Exams
                s = sum([1 for c in candles if c.get('close') > candles[-1].get('close')])
                ms = sum([1 for c in candles if c.get('max') > candles[-1].get('close')])
                buy_value = candles[-1].get('close')
                buying_time = time.time()
                # Exams

                check, id = connector.buy_order(instrument_type=instrument_type, instrument_id=f,
                                                side=side, amount=1, leverage=3,
                                                type=type, limit_price=limit_price, stop_price=stop_price,
                                                stop_lose_value=stop_lose_value, stop_lose_kind=stop_lose_kind,
                                                take_profit_value=take_profit_value, take_profit_kind=take_profit_kind,
                                                use_trail_stop=use_trail_stop, auto_margin_call=auto_margin_call,
                                                use_token_for_commission=use_token_for_commission)
                if check == True:
                    checklist.append(
                        (id, s, ms, buy_value, buying_time))  # add exam

            for chl in checklist:
                sst = time.time()
                while time.time() - sst < 120:
                    check, win = connector.get_position(chl[0])
                    if win['position']['status'] == 'closed':
                        # add exam
                        data.append((win['position']['pnl_realized'] , chl[1], chl[2], chl[3], time.time() - chl[4]))
                        break
            logger.debug(checklist)
           
        pickle.dump(data, open(datapath, 'bw'))
        logger.debug(len(data))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.exception(str(e))
        logger.exception([exc_type, fname, exc_tb.tb_lineno])
        time.sleep(60*3)

