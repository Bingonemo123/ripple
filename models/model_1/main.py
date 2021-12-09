from iqoptionapi.stable_api import IQ_Option
import logging.handlers
import logging
import time
import sys
import os
import pathlib
import json
import mathf
from pushover import Client
import timeout

connector =IQ_Option("ww.bingonemo@gmail.com","JF*#3C5va&_NDqy")
connector.connect()

'''----------------------------------------------------------------------------------------------'''
if os.name == 'posix':
    path = pathlib.PurePosixPath(os.path.abspath(__file__)).parent
else:
    path = pathlib.PureWindowsPath(os.path.abspath(__file__)).parent
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
rotatingfile_handler.setLevel(logging.DEBUG)
rotatingfile_handler.setFormatter(formatter)
logger.addHandler(rotatingfile_handler)
#----------------------------------------------------------------------------#
connector.change_balance("PRACTICE")
instrument_type="forex"
side="buy"
type_market="market"
limit_price=None 
stop_price=None 
stop_lose_kind=None 
stop_lose_value=None 
take_profit_kind='percent' 
take_profit_value=6
use_trail_stop=False 
auto_margin_call=True 
use_token_for_commission=False 

#----------------------------------------------------------------------------#
client = Client("ud1pmkki74te12d3bicw24r99kb38z", api_token="aq7rx1r3o55k6rtobcq8xwv66u8jgw")
client.send_message(os.getcwd(), title="M1 I0")
#----------------------------------------------------------------------------#
while True:
    try:
        try:
            data = json.load(open(path/'data.json', 'r'))
        except FileNotFoundError:
            data = []
            json.dump(data, open(path/'data.json', 'w'))

        means_data = json.load(open(path/'market_mean.json', 'r'))

        timeout.custom_reconnect(connector)

        ### Cut Out
        cutout = 4
        for d in data[::-1]:
            if d.get("Name") == 'Cut Out':
                sttime = d.get("Time")
                if time.time() - sttime >= cutout * 3600:
                    total_profit, total_margin, msg = timeout.custom_profit(connector)
                    if total_profit > 0:
                        data.append({'Name' : 'Cut Out',
                                'Id' : d.get('Id') + 1,
                                'Time': time.time(),
                                'Profit': total_profit,
                                'Investment': total_margin,
                                'Total Positions': len(msg),
                                'Time Delta': round((time.time() - sttime)/3600, 3)
                            })
                        for position in msg:
                            timeout.custom_close(connector, position)
                        logger.info(str(data[-1]))
                        client.send_message(str(data[-1]), title=f"M1 {os.getcwd()}")
                        break
        else:
            data.append({'Name' : 'Cut Out',
                                'Id' : 1,
                                'Time': time.time(),
                                'Profit': None,
                                'Investment': None,
                                'Total Positions': None,
                                'Time Delta': None
                            })
            client.send_message(str(data[-1]), title=f"M1 {os.getcwd()}")

        ### Open Assets 

        ALL_Asset=timeout.custom_all_asets(connector)

        open_cdf = [x for x in ALL_Asset['cfd'] if ALL_Asset['cfd'][x].get('open')]
        open_forex = [x for x in ALL_Asset['forex'] if ALL_Asset['forex'][x].get('open')]


        ### Filter new positions
        delay = 8
        FilterForex = []
        for f in open_forex:
            for d in data[::-1]:
                if d.get('Name') == f:
                    if (time.time() - d.get('Buying_time')) > delay * 3600:
                        FilterForex.append(f)
                    break
            else:
                FilterForex.append(f)

        open_forex = FilterForex
        #Get real time prices 
        
        checklist = []
        pricelist = []
        leverages = []
        for f in open_forex:
            price = timeout.custom_forex(connector, f)
            if not isinstance(price, (float, int)):
                logger.info(f'M1Sk1 Reason: {price}')
                continue
            fleverage = timeout.custom_forex_leverage(connector, f)
            if not isinstance(fleverage, (float, int)):
                logger.info(f'M1Sk2 Reason: {fleverage}')
                continue

            checklist.append(f)
            pricelist.append(price)
            leverages.append(fleverage)
            timeout.custom_reconnect(connector)

        balance = timeout.get_custom_balance(connector)
        
        foundmark = mathf.EZAquariiB(checklist, pricelist, means_data, leverages, balance)
        if foundmark == None:
            logger.info('SE1 [winter sleep]')
            time.sleep(60*3)
            continue
        
        name, m, n, leverage = foundmark[1]

        if balance/(leverage * n) < 1:
            logger.info('SE2 [balance shortage]')
            time.sleep(60*3)
            continue
        elif balance/(leverage * n) > 20000:
            amount = 20000
        else:
            amount = balance/(leverage * n)

        take_profit_value = int( 100 * m )

        check,id=connector.buy_order(instrument_type= instrument_type, instrument_id=name,
                    side=side, amount=amount,leverage=leverage,
                    type=type_market,limit_price=limit_price, stop_price=stop_price,
                    stop_lose_value=stop_lose_value, stop_lose_kind=stop_lose_kind,
                    take_profit_value=take_profit_value, take_profit_kind=take_profit_kind,
                    use_trail_stop=use_trail_stop, auto_margin_call=auto_margin_call,
                    use_token_for_commission=use_token_for_commission)

        if check == True:
            position_id = connector.get_position(id)[1].get('position').get('id')
            data.append({'Name' : name,
                            'Id' : id,
                            'Buying_time': time.time(),
                            'Amount': amount,
                            'Balance': balance,
                            'leverage': leverage,
                            'TakeProfitValue': take_profit_value,
                            'Position_Id': position_id
                        }) # add exam

        json.dump(data, open(path/'data.json', 'w'))
        logger.info(f'Total elements in data: {len(data)}')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.exception(str(e))
        logger.exception([exc_type, fname, exc_tb.tb_lineno])
        client.send_message(exc_type, title=f'M1E {os.getcwd()}')
        logger.info('SE3 [Error hold]')
        time.sleep(60*3)
