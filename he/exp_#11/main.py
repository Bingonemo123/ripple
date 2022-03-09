import MetaTrader5 as connector
import logging.handlers
import logging
import time
import sys
import os
import pathlib
import json
import pytz
from datetime import datetime, timedelta
import mathfc as mathf
from pushover import Client
import timeout
import pandas as pd
import numpy as np
import statistics
import tqdm

prc = 'pract' in sys.argv

modeln = 3.1

if not connector.initialize():
    print("initialize() failed")
    connector.shutdown()

account = 5419164
authorized = connector.login(account, password="u2lgFSvc", server="FxPro-MT5")
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
stream_handler.setLevel(logging.WARNING) 
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
"""FileHandler"""
rotatingfile_handler = logging.handlers.RotatingFileHandler(path/f'main{prc * "_prc"}.log', backupCount=5, maxBytes=1073741824)
rotatingfile_handler.setLevel(logging.INFO)
rotatingfile_handler.setFormatter(formatter)
logger.addHandler(rotatingfile_handler)
"""TqdmHandler"""
class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)  
tqdm_handler = TqdmLoggingHandler()
tqdm_handler.setLevel(logging.INFO)
logger.addHandler(tqdm_handler)
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
# client = Client("ud1pmkki74te12d3bicw24r99kb38z", api_token="aq7rx1r3o55k6rtobcq8xwv66u8jgw")
# client.send_message(os.getcwd(), title=f"M{prc * 'P'}{modeln} I0")
#----------------------------------------------------------------------------#
datapath = path/f'data{prc * "_prc"}.json'
'''try:
    data = json.load(open(datapath, 'r'))
except FileNotFoundError:
    data = []
    json.dump(data, open(datapath, 'w'))'''

#----------------------------------------------------------------------------#
'''
List of Data for One week (7 days) for every minite 
list average len: 7*24*60 = 2016
1. (Get data) Every iter new min must be added to list and old min must be deleted. New latest item in list is currecnt price.
    new variables:
    Starting date = monday(time object)
    Current date = time object
    candledata = list of one week data 
1.1. Calculate balances(maybe updated several times)

2. If position is outoff margin or autoclose is activated close position.
3. # Cut out: if time from last cutout is more than 4 hour, cut out. else, continue. If cutout, if profit >0, sell all positions.
    new variables for cutout:
    last_cutout_time = time of last cutout
    total_profit = total profit 
    active_positions = list of open positions
    current_profit(function) = profit of active positions
    colsing_positions(function) = close all active positions
3.1 Check if market was open (for now if not in activedesk actdesk market is closed)
4. Check if Assset is in active positions filter from buying positions.
5. Get ready means, leverage, current prices and balance
6. Run strategy: EZAquariiB
7. get name, m, n and leverage if available
8. Make theoretical buy and put info in active_positions
9. Log and display info
10. update time'''
#----------------------------------------------------------------------------#
'''Variables and functions'''
# 1.
timezone = pytz.timezone("Etc/UTC")
strd = datetime.strptime("01.01.2018", "%d.%m.%Y", ) # Starting date = monday(time object)
strd = strd.replace(tzinfo=timezone)
currd = strd # Current date = time object
cd = {} # candledata = list of one week data 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
trdesk = ["EURUSD", "GBPUSD", "USDJPY", "USDTHB", "USDZAR", "EURZAR", "GBPZAR", "GBPJPY"]
logger.info(f'Starting date: {strd}, format: {type(strd)}')
# 3. Cutout
lct = strd # last cutout time = time of last cutout
tp = 0 # total profit
id_index = 0 # id for positions
ap = [] # active positions position data 
'''(0.id, 1.name, 2.opening price, 3.open time, 4.amount(in money), 5.auto close, 6.leverage,7. amount(in lots))'''
crp = {} # current price
crpohlc = 1 # current price ohlc
init_balance = 10_000
curr_balance = init_balance # init_balance - active_position_buying_amount - closed_win_lose_amount (updated when new position is bought or active closed)
free_balance = init_balance # curr_balance - active_positions_win_lose_amount 
margin_balance = init_balance # curr_balance - active_positions_lose_amount
safe_balance = init_balance # curr_balance  - safe_margin - active_positions_lose_amount 
# safe-balance = curr_balance - Sum(loan) : | loan = pm - v | pm = v * l = a * op
# margin_balance = curr_balance - Sum(am | if op > cp) : | am = bm + v | bm = cm - pm | cm = a * op
# free_balance = curr_balance - Sum(am) : | am = bm + v | bm = cm - pm | cm = a * op
leveg = 3000 # leverage
position_history = []

def calc_balance():
    global curr_balance, margin_balance, free_balance, safe_balance
    free_balance = curr_balance - sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) + i[4] for i in ap])  # v * l ( cp/op - 1) + v
    margin_balance = curr_balance - sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) + i[4] for i in ap if crp[i[1]] < i[2]])  # v * l ( cp/op - 1) + v
    safe_balance = curr_balance - sum([i[4]*(1 - i[6]) for i in ap])  # loan = pm - v | pm = v * l = a * op


def current_profit(ap):
    cp = 0
    for i in ap:
        cp += i[1]
    return cp

def close_pos(ids):
    global tp, curr_balance
    for i in ap:
        logger.debug(f'Closing position {i}')
        if i[0] == ids:
            closing_profit = i[4] * i[6] * (crp[i[1]]/i[2] - 1) + i[4]
            tp += closing_profit
            curr_balance += closing_profit
            ap.remove(i)
            break
    calc_balance()

def close_positions(ap):
    global tp, curr_balance
    for i in ap:
        logger.debug(f'Closing position {i[0]}')
        closing_profit = i[4] * i[6] * (crp[i[1]]/i[2] - 1) + i[4]
        tp += closing_profit
        curr_balance += closing_profit
    ap.clear()
    calc_balance()

#----------------------------------------------------------------------------#
'''Inital Frame data'''
for f in trdesk:
    rates = timeout.datamine(connector, f=trdesk[0], frame=connector.TIMEFRAME_M1, t=strd, count=10080)
    rerates = np.zeros((len(rates), 8), dtype=float)
    for i in range(len(rates)):
        for x in range(8):
            rerates[i][x] = rates[i][x]
    cd[f] = rerates
    crp[f] = rates[-1][crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume

# rates_frame = pd.DataFrame(cd['EURUSD'])
# rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
# print("\nDisplay dataframe with data")
# print(rates_frame)  

currd += timedelta(minutes=1)
#----------------------------------------------------------------------------#
pbar = tqdm.tqdm(total=int((datetime.utcnow().replace(tzinfo=timezone) - strd).total_seconds()/60))


#----------------------------------------------------------------------------#
while True:
    try:
        ### Refresh Data
        # json.dump(data, open(datapath, 'w'))
        ### 1. Get data
        actdesk = [] # active desk: list of market which is active a.k.a. changed a.k.a. maybe not closed
        for f in trdesk:
            rates = timeout.datamine(connector, f=trdesk[0], frame=connector.TIMEFRAME_M1, t=currd, count=1)
            if rates[0][0] != cd[f][-1][0]:
                cd[f] = np.roll(cd[f], -1)
                for x in range(8):
                    cd[f][-1][x] = rates[0][x]
                crp[f] = rates[-1][crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
                actdesk.append(f)

        ### 1.1. Calculate balances
        calc_balance()
        ### 2. Check if position is outoff margin or autoclose is activated close position.
        for pos in ap:
            if pos[1] in actdesk:
                ### check if autoclose activated
                if pos[5] >= crp[pos[1]]:
                    close_pos(pos[0])
                ### check if position is outoff margin
                if margin_balance <= 0:
                    close_positions(ap)

        ### 2.1 Calculate balances
        calc_balance()
        ### 3. Cutout
        cutout = 4
        if currd - lct >= timedelta(hours=cutout):
            total_profit = sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) for i in ap])
            logger.debug(f'TP: {total_profit}')
            if total_profit > 0:
                logger.debug(f'Cutout at {currd} with profit {total_profit}')
                # data.append({'Name' : 'Cut Out',
                #                 'Time': time.time(),
                #                 'Profit': total_profit,
                #                 'Theoretical Time': str(currd),
                #             })
                # json.dump(data, open(datapath, 'w'))
                close_positions(ap)
           
        ### Open Assets 3.1 Check if market was open   
        # open if in actdesk   

        ### Filter new positions
        '''If already bought, continue (not buy same market, while already one is active)
        else, if last time from buy is more than delay, consider buying. '''
        delay = 8
        Filter = []

        for f in actdesk:
            if f in [i[1] for i in ap]:
                continue
            for d in position_history[::-1]:
                if d.get('Name') == f:
                    if (currd - d.get('Buying_time', 0)) > timedelta(hours=delay):
                        Filter.append(f)
                    break
            else:
                Filter.append(f)

        open_s = Filter
        logger.debug(f'Possible Symbols number: {len(open_s)}')
        # 5. Get ready means, leverage, current prices and balance
        
        checklist = []
        pricelist = []
        leverages = []

        for f in open_s:
            checklist.append(f)
            pricelist.append(crp[f])
            leverages.append(leveg)

        ### 5.1. Get ready means
            """
            means classified as 0.ANSmean 1. statisitcs.mean(fset), 2. statistics.stdev(fset), 3.s_1
            Ansmean = just statistical mean of prices(close or open or high or low)
            period_candle_set = Every candle that is after i-th candle and is less than period of time
            peakvalue = max price value in period_candle_set
            peakdiff = current i-th value - peakvalue
            peakdiffset = set of all peakdiffs
            fset = all peakdiff if peak > 0
            s_1 = positiovve peaks / total peaks (percentage of positive peaks)
            old method will be replaced by new method:
            diffthreshold = min value from i-th value to peakvalue (if less isn't considered peak) """

        means_data = {}
        period = 8
        ohlc = 4 # open high low close 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
        

        for f in open_s:
            means_data[f] = [0, 0, 0, 0]
            means_data[f][0] = statistics.mean([i[ohlc] for i in cd[f]]) # ANSmean 

            period_number = int(timedelta(hours=period).seconds/60)
            
            fset = [] # set of all peakdiffs for f
            for i in range(len(cd[f])):
                period_candle_set = cd[f][i:i+period_number] # every candle that is after i-th candle and is less than period of time
                peakvalue = period_candle_set.max(axis=0)[ohlc]
                peakdiff = peakvalue - cd[f][i][ohlc] 
                if peakdiff > 0:
                    fset.append(peakdiff)
            
            s_1 = len(fset) / len(cd[f])

            means_data[f][1] = statistics.mean(fset)
            means_data[f][2] = statistics.stdev(fset)
            means_data[f][3] = s_1


        logger.debug(f'Means: {means_data}')

        ### 6. Run strategy: EZAquariiB
        if safe_balance > 0: # buy if only safe_balance is available

            foundmark = mathf.EZAquariiB(checklist, pricelist, means_data, leverages, safe_balance)
            if foundmark == None:
                logger.debug(f'M{modeln} SE1 [winter sleep]')
            else:
                logger.debug(foundmark)
                
                ### 7. get name, m, n and leverage if available
                name, m, n, leverage = foundmark[1]

                if safe_balance/ n < 1:
                    logger.debug(f'M{modeln} SE2 [balance shortage]')
                    amount = 1
                elif safe_balance/ n > 20000:
                    amount = 20000
                else:
                    amount = safe_balance/ n

                take_profit_value = int( 100 * m )

                ### 8. Make theoretical buy and put info in active_positions
                if amount <= safe_balance:
                    id_index += 1
                    curr_balance -= amount
                    if curr_balance < 0:
                        logger.debug(f'M{modeln} SE3 [balance shortage]')
                    else:
                        amount_tlots = amount * leverage / crp[name]# amount of theortical lots
                        ap.append([id_index, name, crp[name], currd, amount, take_profit_value, leverage, amount_tlots])
                        position_history.append({'Name' : name,
                                        'Id' : id_index,
                                        'Buying_time': currd,
                                        'Amount': amount,
                                        'Balance': curr_balance,
                                        'leverage': leverage,
                                        'TakeProfitValue': take_profit_value
                                    }) # add exam
                        logger.debug(f'Buying {name} with amount {amount}')
                        ### 8.1 Recalculate balance
                        calc_balance()
        else:
            logger.debug(f'low safe_balance {safe_balance}')
        
        ### 9. Log and display info
        # json.dump(data, open(datapath, 'w'))
        logger.debug(f'Total elements in data: {len(position_history)}')

        ### 10. update time
        currd += timedelta(minutes=1)
        pbar.update(1)
        pbar.set_description(f'{currd}')
        logger.debug(f'Current time: {currd}')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.exception(str(e))
        logger.exception([exc_type, fname, exc_tb.tb_lineno])
        # client.send_message(exc_type, title=f'M{prc * "P"}{modeln}E {os.getcwd()}')
        logger.info(f'M{modeln} SE3 [Error hold]')
        time.sleep(60*3)
