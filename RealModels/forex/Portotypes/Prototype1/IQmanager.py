from iqoptionapi.stable_api import IQ_Option
import Internet_protocols
import logging.handlers
import commision
import datetime
import pathlib
import logging
import time
import sys
import os
connector =IQ_Option("ww.bingonemo@gmail.com","JF*#3C5va&_NDqy")
connector.connect()
       
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

#----------------------------------------------------------------------------#
connector.change_balance("PRACTICE")
instrument_type="cfd"
side="buy"
type_market="market"
limit_price=None 
stop_price=None 
stop_lose_kind=None 
stop_lose_value=None 
take_profit_kind='percent' 
take_profit_value=3 
use_trail_stop=False 
auto_margin_call=True 
use_token_for_commission=False 
#----------------------------------------------------------------------------#
def run():
    try:
        global stock_buy
        logger.info('while #1')
        while True:
            if connector.check_connect() == False:
                check,reason=connector.connect()
            
            if connector.get_positions(instrument_type)[1].get('total') >= 20:
                logger.info('sleep #1')
                time.sleep(60*3)
                logger.info('wake #1')
            else:
                stock_buy = [x.get('instrument_id') for x in connector.get_positions(instrument_type)[1].get('positions')]
                logger.info(["Open stocks:", stock_buy])
                break
        logger.info('unwhile #1')
        balance = connector.get_balance()
        logger.info(str(balance)+'$')

        ALL_Asset=connector.get_all_open_time()

        volatility_stocks = commision.stocks_mm(connector)

        addstock=[]
        for stock in range(20-len(stock_buy)):
            for x in volatility_stocks:
                # logger.info('while #2')
                while True:
                    if connector.check_connect() == False:
                        check,reason=connector.connect()
                    else:
                        break
                # logger.info('unwhile #2')
                if x in stock_buy or x in addstock:
                    continue
                if ALL_Asset[instrument_type].get(x, {"open": False})["open"]:
                    if commision.past_history(connector, x):
                        addstock.append(x)
                        break
            if len(addstock) > 1 and stock ==  20-len(stock_buy) -1:
                break
        else:
            logger.info('No useful stocks')
            logger.info('sleep #2')
            time.sleep(60*3)    
            logger.info('wake #2') 

        logger.info('while #3')
        while True:
            if connector.check_connect() == False:
                 check,reason=connector.connect()
            else:
                break
        logger.info('unwhile #3')
        """
        for stk in addstock:
          leverage=max(connector.get_available_leverages(instrument_type,stk)[1].get('leverages')[0].get('regulated'))
          amount = ((balance/20)*0.95) /leverage if ((balance/20)*0.95) /leverage < 20000 else 20000
          check,id=connector.buy_order(instrument_type= instrument_type, instrument_id=stk,
                    side=side, amount=amount,leverage=leverage,
                    type=type_market,limit_price=limit_price, stop_price=stop_price,
                    stop_lose_value=stop_lose_value, stop_lose_kind=stop_lose_kind,
                    take_profit_value=take_profit_value, take_profit_kind=take_profit_kind,
                    use_trail_stop=use_trail_stop, auto_margin_call=auto_margin_call,
                    use_token_for_commission=use_token_for_commission)
        """
        logger.info(['Added stocks', addstock])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Internet_protocols.email(str(e), subj='Error')
        logger.exception(str(e))
        logger.exception([exc_type, fname, exc_tb.tb_lineno])
        time.sleep(60*3)