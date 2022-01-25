import tqdm
import json 
import statistics
import numpy as np
import MetaTrader5 as mt5
 
# connect to MetaTrader 5
if not mt5.initialize(portable=True):
    print("initialize() failed")
    mt5.shutdown() 

account=5394724
authorized=mt5.login(account, password="m51djnLG", server="FxPro-MT5")
if not authorized:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))

seconds_in_month = 2_592_000 
seconds_in_year = 31_536_000


candle_size = 3600 # 3600 is one hour
quantity =  seconds_in_year / candle_size

ALL_Asset=mt5.symbols_get()
try:
    result = json.load(open(r'C:\Users\HP\Documents\repos\Ripple_3.0\mt\model_3\month_means.json', 'r'))
except FileNotFoundError:
    result = {}

for symbol in tqdm.tqdm(ALL_Asset):

    if symbol.name in result:
        continue

    ANS = mt5.copy_rates_from_pos(symbol.name, mt5.TIMEFRAME_H1, 0, int(quantity))

    tqdm.tqdm.write(symbol.name)
    ANSmean = statistics.mean([x[4] for x in ANS])

    period = 8 * 3600

    peakdiffset = []


    idx = 0
    for i in ANS:
        if  ANS[-1][0] - i[0] < period:
            continue
        period_candle_set = []

        k = 1
        while True:
            if idx + k >= len(ANS):
                break
            if ANS[idx + k][0] - i[0] <= period:
                period_candle_set.append(ANS[idx + k])
            else:
                break
            k += 1

        if len(period_candle_set) == 0:
            continue
        

        peakvalue = [np.NINF] * 5

        for x in period_candle_set:
            if x[4] > peakvalue[4]:
                peakvalue = x
            
        peakdiff = peakvalue[4] - i[4]

        peakdiffset.append(peakdiff)

        fset = [x for x in peakdiffset if x >= 0]
        s_1 = len(fset)/len(peakdiffset)
        idx += 1

    result[symbol.name] = [ ANSmean, statistics.mean(fset), statistics.stdev(fset), s_1]


    json.dump(result, open(r'C:\Users\HP\Documents\repos\Ripple_3.0\mt\model_3\month_means.json', 'w'))




