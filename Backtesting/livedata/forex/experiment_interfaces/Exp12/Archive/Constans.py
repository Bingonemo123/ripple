import pytz
from datetime import datetime
import io
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

maximum_var = [curr_balance, safe_balance, margin_balance, free_balance, len(ap)]
minimum_var = [curr_balance, safe_balance, margin_balance, free_balance]
autoclosed = 0
marginclosed = 0
cutoutclosed = 0
cutoutindx = 0
lastmean = {}

last_graph_update = strd
fake_file = io.StringIO()

means_data = {}
foundmark = None
actdesk = []
Filter = []
