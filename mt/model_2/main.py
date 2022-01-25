import MetaTrader5 as connector
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

prc = 'pract' in sys.argv

modeln = 2.1

if not connector.initialize():
    print("initialize() failed")
    connector.shutdown()

account = 5394724
authorized = connector.login(account, password="m51djnLG", server="FxPro-MT5")
if not authorized:
    print("failed to connect at account #{}, error code: {}".format(
        account, connector.last_error()))

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
rotatingfile_handler = logging.handlers.RotatingFileHandler(path/f'main{prc * "_prc"}.log', backupCount=5, maxBytes=1073741824)
rotatingfile_handler.setLevel(logging.DEBUG)
rotatingfile_handler.setFormatter(formatter)
logger.addHandler(rotatingfile_handler)
#----------------------------------------------------------------------------#

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
client.send_message(os.getcwd(), title=f"M{prc * 'P'}{modeln} I0")
#----------------------------------------------------------------------------#
datapath = path/f'data{prc * "_prc"}.json'
try:
    data = json.load(open(datapath, 'r'))
except FileNotFoundError:
    data = []
    json.dump(data, open(datapath, 'w'))

means_data = json.load(open(path/'month_means.json', 'r'))
#----------------------------------------------------------------------------#
while True:
    try:
        ### Cut Out
        cutout = 4
        for d in data[::-1]:
            if d.get("Name") == 'Cut Out':
                sttime = d.get("Time")
                if (time.time() - sttime) >= (cutout * 3600 ):
                    pmm = timeout.custom_profit(connector)
                    if isinstance(pmm, (str, Exception)):
                        logger.info(f'M{modeln}Sk1 Reason: {pmm}')
                        break
  
                    total_profit, total_margin, msg = pmm
                    logger.info(f'TP: {total_profit}')
                    if total_profit > 0:
                        data.append({'Name' : 'Cut Out',
                                'Id' : d.get('Id') + 1,
                                'Time': time.time(),
                                'Profit': total_profit,
                                'Investment': total_margin,
                                'Total Positions': len(msg),
                                'Time Delta': round((time.time() - sttime)/3600, 3)
                            })
                        json.dump(data, open(datapath, 'w'))
                        for position in msg:
                            clres = timeout.custom_close(connector, position)
                            if clres is not True:
                                logger.info(f'M{modeln}Sk2 Reason: {clres}')
                        logger.info(str(data[-1]))
                        client.send_message(str(data[-1]), title=f"M{prc * 'P'}{modeln} {os.getcwd()}")
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
            json.dump(data, open(datapath, 'w'))
            logger.info(str(data[-1]))

        ### Open Assets 

        ALL_Asset=timeout.custom_all_asets(connector)
        if isinstance(ALL_Asset, (str, Exception)):
            logger.info(f'M{modeln}Sk3 Reason: {ALL_Asset}')
            continue

    
        open_s = []

        for x in ALL_Asset:
            sft = timeout.custom_safty(connector, x.name)
            if not isinstance(sft, bool):
                logger.info(f'M{modeln}Sk4 Reason: {sft}')
                continue
            if sft:
                open_s.append(x.name)
        

        ### Filter new positions
        delay = 8
        Filter = []

        pmm = timeout.custom_profit(connector)
        if isinstance(pmm, (str, Exception)):
            logger.info(f'M{modeln}Sk5 Reason: {pmm}')
            break

        total_profit, total_margin, msg = pmm
        poshold = [pos.symbol for pos in msg]

        for f in open_s:
            if f in poshold:
                continue
            for d in data[::-1]:
                if d.get('Name') == f:
                    if (time.time() - d.get('Buying_time')) > delay * 3600:
                        Filter.append(f)
                    break
            else:
                Filter.append(f)

        open_s = Filter
        #Get real time prices 
        
        checklist = []
        pricelist = []
        leverages = []

        for f in open_s:
            price = timeout.custom_price(connector, f)
            if not isinstance(price, (float, int)):
                logger.info(f'M{modeln}Sk6 Reason: {price}')
                continue
            fleverage = timeout.custom_leverage(connector)
            if not isinstance(fleverage, (float, int)):
                logger.info(f'M{modeln}Sk7 Reason: {fleverage}')
                continue

            checklist.append(f)
            pricelist.append(price)
            leverages.append(fleverage)

        balance = timeout.get_custom_balance(connector)
        if not isinstance(balance, (float, int)):
            logger.info(f'M{modeln}Sk8 Reason: {balance}')
            continue
        

        foundmark = mathf.EZAquariiB(checklist, pricelist, means_data, leverages, balance)
        if foundmark == None:
            logger.info(f'M{modeln} SE1 [winter sleep]')
            time.sleep(60*3)
            continue
        logger.info(foundmark)
        
        name, m, n, leverage = foundmark[1]

        if balance/(leverage * n) < 1:
            logger.info(f'M{modeln} SE2 [balance shortage]')
            time.sleep(60*3)
            continue
        elif balance/(leverage * n) > 20000:
            amount = 20000
        else:
            amount = balance/(leverage * n)

        take_profit_value = int( 100 * m )

        #### ORDER ####
        cpbh =  timeout.custom_prebuy(connector, name)
        if not isinstance(cpbh, tuple):
            logger.info(f'M{modeln}Sk9 Reason: {cpbh}')
            continue

        point, volume_step, price, margin, volume_max = cpbh

        volume = amount / margin
        if volume > volume_max:
            volume = volume_max
        volume = (volume // volume_step) * volume_step

        closing_price =  ((m/leverage) + 1) * price
        closing_price = (closing_price // point ) * point
        request = {
                "action": connector.TRADE_ACTION_DEAL,
                "symbol": name,
                "volume": volume,
                "type": connector.ORDER_TYPE_BUY,
                "price": price,
                # "sl": 0,
                "tp": closing_price,
                "comment": f"Placed by model {modeln}",
                "type_time": connector.ORDER_TIME_GTC,
                "type_filling": connector.ORDER_FILLING_IOC,
        }

        check = connector.order_send(request)

        if check.comment == 'No prices':
            avvol = timeout.custom_volmeter(connector, f)
            if not isinstance(avvol, (float, int)):
                logger.info(f'M{modeln}Sk10 Reason: {avvol}')
                request['Name'] = name
                request['Buying_time'] = time.time()
                data.append(request)
                continue
            request['volume'] = avvol
            check = connector.order_send(request)

        if check.comment == 'Invalid stops':
            del request['tp']
            check = connector.order_send(request)

        if check.comment == 'Market closed':
            data.append({'Name' : name,
                            'Id' : 'Market closed',
                            'Buying_time': time.time(),
                            'Amount': amount,
                            'Balance': balance,
                            'leverage': leverage,
                            'TakeProfitValue': take_profit_value,
                            'Position_Id': 'Market closed'
                        }) # add exam


        elif check.retcode != connector.TRADE_RETCODE_DONE:
            logger.warning("2. order_send failed, retcode={}".format(check.retcode))
            # request the result as a dictionary and display it element by element
            result_dict=check._asdict()
            for field in result_dict.keys():
                logger.warning("   {}={}".format(field,result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field=="request":
                    traderequest_dict=result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        logger.warning("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
            continue

        else:
            position_id = check.order
            data.append({'Name' : name,
                            'Id' : position_id,
                            'Buying_time': time.time(),
                            'Amount': amount,
                            'Balance': balance,
                            'leverage': leverage,
                            'TakeProfitValue': take_profit_value,
                            'Position_Id': position_id
                        }) # add exam
        json.dump(data, open(datapath, 'w'))
        logger.info(f'Total elements in data: {len(data)}')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.exception(str(e))
        logger.exception([exc_type, fname, exc_tb.tb_lineno])
        client.send_message(exc_type, title=f'M{prc * "P"}{modeln}E {os.getcwd()}')
        logger.info(f'M{modeln} SE3 [Error hold]')
        time.sleep(60*3)
