import curses
import io
import json
import logging
import logging.handlers
import os
import pathlib
import statistics
import sys
import time
from contextlib import redirect_stdout
from datetime import datetime, timedelta

import MetaTrader5 as connector
import numpy as np
import pandas as pd
import pytz
import tqdm
from pushover import Client

import mathfc as mathf
import timeout
import plotext as plt

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
position_history = {}

def calc_balance():
    global curr_balance, margin_balance, free_balance, safe_balance
    free_balance = curr_balance - sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) + i[4] for i in ap])  # v * l ( cp/op - 1) + v
    margin_balance = curr_balance - sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) + i[4] for i in ap if crp[i[1]] < i[2]])  # v * l ( cp/op - 1) + v
    safe_balance = curr_balance - sum([i[4]*(i[6] - 1) for i in ap])  # loan = pm - v | pm = v * l = a * op


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
            closing_profit = i[4] * i[6] * ((crp[i[1]]/i[2]) - 1) + i[4]
            tp += closing_profit
            curr_balance += closing_profit
            position_history.get(ids).update({'Close Time': currd, 'Close Price': crp[i[1]], 'Profit': closing_profit, 'Closed by': 'Auto'})
            ap.remove(i)
            break
    calc_balance()

def close_positions(ap):
    global tp, curr_balance
    for i in ap:
        logger.debug(f'Closing position {i[0]}')
        closing_profit = i[4] * i[6] * ((crp[i[1]]/i[2]) - 1) + i[4]
        tp += closing_profit
        curr_balance += closing_profit
        position_history.get(i[0]).update({'Close Time': currd, 'Close Price': crp[i[1]], 'Profit': closing_profit, 'Closed by': 'Cluster'})

    ap.clear()
    calc_balance()

plt.colorless()
plt.xlabel('Time')
last_graph_update = strd

def draw_plot(cols, lines, f):
    PlotFile = io.StringIO()
    with redirect_stdout(PlotFile):
        plt.clp()
        plt.clc()
        plt.cls()
        plt.plot_size(lines -1 , cols -1)
        y = [i[crpohlc] for i in cd[f][-100:]]
        plt.plot(y)
        plt.title(f)
        plt.show()
    PlotFile.seek(0)
    w = PlotFile.readlines()
    return w
#----------------------------------------------------------------------------#
'''Inital Frame data'''
for f in trdesk:
    logger.info(f'Getting data for {f}')
    rates = timeout.datamine(connector, f=f, frame=connector.TIMEFRAME_M1, t=strd, count=10080)
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
fake_file = io.StringIO()
stdscr = curses.initscr()
progressbarwin = curses.newwin(3, curses.COLS, 0, 0)
progressbarwin.box()
pbar = tqdm.tqdm(total=int((datetime.utcnow().replace(tzinfo=timezone) - strd).total_seconds()/60), file=fake_file, ncols = curses.COLS-2)
pbar.set_description('│')
infowin = curses.newwin(curses.LINES - 6, curses.COLS//4, 3, 0)
statuswin = curses.newwin(3, curses.COLS, curses.LINES-3, 0)
graphwin = curses.newwin(curses.LINES - 6, curses.COLS - curses.COLS//4, 3, curses.COLS//4)

def refresh_status(text):
    statuswin.clear()
    statuswin.box()
    statuswin.addstr(1, 1, text)
    statuswin.refresh()
#----------------------------------------------------------------------------#
maximum_var = [curr_balance, safe_balance, margin_balance, free_balance, len(ap)]
minimum_var = [curr_balance, safe_balance, margin_balance, free_balance]
autoclosed = 0
marginclosed = 0
cutoutclosed = 0
cutoutindx = 0
lastmean = {}
#----------------------------------------------------------------------------#
while True:
    try:
        ### Refresh Data
        # json.dump(data, open(datapath, 'w'))
        ### 1. Get data
        refresh_status('Getting data...')
        actdesk = [] # active desk: list of market which is active a.k.a. changed a.k.a. maybe not closed
        for f in trdesk:
            rates = timeout.datamine(connector, f=f, frame=connector.TIMEFRAME_M1, t=currd, count=1)
            if rates[0][0] != cd[f][-1][0]:
                cd[f] = np.roll(cd[f], -1, axis=0)
                for x in range(8):
                    cd[f][-1][x] = rates[0][x]
                crp[f] = rates[-1][crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
                actdesk.append(f)

        ### 1.1. Calculate balances
        calc_balance()
        ### 2. Check if position is outoff margin or autoclose is activated close position.
        refresh_status('Checking positions...')
        for pos in ap:
            if pos[1] in actdesk:
                ### check if autoclose activated
                if pos[5] <= crp[pos[1]]: # close olhc = 1 a.k.a open
                    close_pos(pos[0])
                    autoclosed += 1
                ### check if position is outoff margin
                if margin_balance <= 0:
                    marginclosed += len(ap)
                    close_positions(ap)

        ### 2.1 Calculate balances
        calc_balance()
        ### 3. Cutout
        refresh_status('Cutout...')
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
                cutoutclosed += len(ap)
                cutoutindx += 1
                lct = currd
                close_positions(ap)
           
        ### Open Assets 3.1 Check if market was open   
        # open if in actdesk   

        ### Filter new positions
        refresh_status('Filtering new positions...')
        '''If already bought, continue (not buy same market, while already one is active)
        else, if last time from buy is more than delay, consider buying. '''
        delay = 8
        Filter = []

        for f in actdesk:
            if f in [i[1] for i in ap]:
                continue
            for indx in position_history:
                if position_history[indx].get('Name') == f:
                    if (currd - position_history[indx].get('Buying_time', 0)) < timedelta(hours=delay):
                        break
            else:
                Filter.append(f)

        open_s = Filter
        logger.debug(f'Possible Symbols number: {len(open_s)}')
        # 5. Get ready means, leverage, current prices and balance
        refresh_status('Getting ready...')
        
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
        ohlc = 4 # open high low close 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume # mean ohlc
        

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
        refresh_status('Running strategy...')
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

                take_profit_value = ((m/leverage) + 1) * crp[name]

                ### 8. Make theoretical buy and put info in active_positions
                refresh_status('Making theoretical buy...')
                if amount <= safe_balance:
                    id_index += 1
                    curr_balance -= amount
                    if curr_balance < 0:
                        logger.debug(f'M{modeln} SE3 [balance shortage]')
                    else:
                        amount_tlots = amount * leverage / crp[name]# amount of theortical lots
                        ap.append([id_index, name, crp[name], currd, amount, take_profit_value, leverage, amount_tlots])
                        position_history[id_index] = {'Id' : id_index,
                                        'Name' : name,
                                        'Opening_price' : crp[name],
                                        'Buying_time': currd,
                                        'Amount': amount,
                                        'TakeProfitValue': take_profit_value,
                                        'leverage': leverage,
                                        'Amount_tlots': amount_tlots,
                                        'Balance': curr_balance,
                                        'SafeBalance': safe_balance,
                                    } # add exam
                        logger.debug(f'Buying {name} with amount {amount}')
                        ### 8.1 Recalculate balance
                        calc_balance()
        else:
            logger.debug(f'low safe_balance {safe_balance}')
        
        ### 9. Log and display info
        refresh_status('Logging and displaying info...')
        # json.dump(data, open(datapath, 'w'))
        logger.debug(f'Total elements in data: {len(position_history)}')

       
        pbar.update(1)
        pbar.set_description(f'│ {currd}')
        fake_file.flush()
        fake_file.seek(0)
        progressbarwin.addstr(1, 2, fake_file.readline())

        infowin.clear()
        infowin.box()
        infowin.addstr(1, 1, f'Current Balance {curr_balance:,.2f}')
        infowin.addstr(2, 1, f'Safe Balance {safe_balance:,.2f}')
        infowin.addstr(3, 1, f'Margin Balance {margin_balance:,.2f}')
        infowin.addstr(4, 1, f'Free Balance {free_balance:,.2f}')
        infowin.addstr(5, 1, f'Total Profit {tp:,.2f}')

        maxcheckvars = [curr_balance, safe_balance, margin_balance, free_balance, len(ap)]
        for x in range(len(maxcheckvars)):
            if maximum_var[x] < maxcheckvars[x]:
                maximum_var[x] = maxcheckvars[x]

        mincheckvars = [curr_balance, safe_balance, margin_balance, free_balance]
        for x in range(len(mincheckvars)):
            if minimum_var[x] > mincheckvars[x]:
                minimum_var[x] = mincheckvars[x]

        infowin.addstr(6, 1, f'Max Current Balance {maximum_var[0]:,.2f}')
        infowin.addstr(7, 1, f'Max Safe Balance {maximum_var[1]:,.2f}')
        infowin.addstr(8, 1, f'Max Margin Balance {maximum_var[2]:,.2f}')
        infowin.addstr(9, 1, f'Max Free Balance {maximum_var[3]:,.2f}')
        infowin.addstr(10, 1, f'Min Current Balance {minimum_var[0]:,.2f}')
        infowin.addstr(11, 1, f'Min Safe Balance {minimum_var[1]:,.2f}')
        infowin.addstr(12, 1, f'Min Margin Balance {minimum_var[2]:,.2f}')
        infowin.addstr(13, 1, f'Min Free Balance {minimum_var[3]:,.2f}')
        
        infowin.addstr(15, 1, f'Active Positions {len(ap)}')
        infowin.addstr(16, 1, f'Total Positions {len(position_history)}')
        infowin.addstr(17, 1, f'AutoClosed {autoclosed}')
        infowin.addstr(18, 1, f'MarginClosed {marginclosed}')
        infowin.addstr(19, 1, f'CutoutClosed {cutoutclosed}')
        infowin.addstr(20, 1, f'Total Closed {autoclosed + marginclosed + cutoutclosed}')
        infowin.addstr(21, 1, f'Max Active Positions {maximum_var[4]}')

        infowin.addstr(23, 1, f'Active Desk {len(actdesk)}')
        infowin.addstr(24, 1, f'Possible Symbols {len(open_s)}')
        infowin.addstr(25, 1, f'Cutout Index {cutoutindx}')

        h = 0
        for f in trdesk:
            infowin.addstr(27 + h, 1, f'{f} {crp.get(f, "NaN"):<20}') # prices
            if f in [i[1] for i in ap]:
                infowin.addstr('x')
            h += 1
        z = 1
        for f in trdesk:
            infowin.addstr(27 + h + z, 1, f'{f} ')
            prmeans = means_data.get(f, lastmean.get(f, ["NaN"]))
            if f in means_data:
                lastmean[f] = means_data[f]
            
            if prmeans[0] == "NaN":
                infowin.addstr(f'{prmeans[0]}')
            else:
                for x in prmeans:
                    infowin.addstr(f'{x:10.4f} ')
            z += 1

        if len(position_history) > 0:
            selected_position = position_history.get(max([x for x in position_history if len(position_history[x]) > 10], default=None), False)
            if selected_position:
                z += 1
                infowin.addstr(27 + h + z, 1, f'Latest Closed Position')
                z += 1 
                for d in selected_position:
                    selected_data = selected_position[d]
                    if isinstance(selected_data, float):
                        selected_data = f'{selected_data:,}'
                    infowin.addstr(27 + h + z, 1, f'{d:{(curses.COLS//8) -3 }}  {f"{selected_data}":<{(curses.COLS//8) -3}}')
                    z += 1
        
        if foundmark:
            infowin.addstr(27 + h + z, 1, f'Foundmark {foundmark[1][0]} {foundmark[0]}')
        # pbar.write(f'Current Balance: {curr_balance}, Safe Balance: {safe_balance}, Total Profit: {tp}')
        infowin.refresh()
        progressbarwin.refresh()
        ### draw the graph
        if currd - last_graph_update >= timedelta(minutes=15):
            graphwin.clear()
            w = draw_plot(curses.LINES - 6, curses.COLS - curses.COLS//4, 'EURUSD')
            
            k = 0
            for i in w:
                for c in i:
                    graphwin.addstr(c)
                k += 1
            graphwin.refresh()
            last_graph_update = currd

        ### 10. update time
        refresh_status('Updating time...')
        currd += timedelta(minutes=1)
        logger.debug(f'Current time: {currd}')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.exception(str(e))
        logger.exception([exc_type, fname, exc_tb.tb_lineno])
        # client.send_message(exc_type, title=f'M{prc * "P"}{modeln}E {os.getcwd()}')
        logger.info(f'M{modeln} SE3 [Error hold]')
        curses.endwin()
        time.sleep(60*3)
