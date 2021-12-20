import tqdm
from iqoptionapi.stable_api import IQ_Option
import json 
import statistics
import time
import timeout
import numpy as np

connector =IQ_Option("ww.bingonemo@gmail.com","JF*#3C5va&_NDqy")
connector.connect()

seconds_in_month = 2_592_000 
max_dict = 1000
ALL_Asset=connector.get_all_open_time()
crpt = [x for x in ALL_Asset['crypto'] if ALL_Asset['crypto'][x].get('open')]
iqcomb = [("NZD", "SEK"),("NZD", "USD"),("CAD", "TRY"),("EUR", "CHF"),("USD", "THB"),("EUR", "TRY"),("GBP", "AUD"),("AUD", "USD"),("EUR", "MXN"),("USD", "CHF"),("NOK", "DKK"),("EUR", "NOK"),("SEK", "JPY"),("CAD", "NOK"),("NOK", "SEK"),("GBP", "HUF"),("GBP", "SGD"),("AUD", "NZD"),("GBP", "JPY"),("CHF", "SEK"),("AUD", "NOK"),("GBP", "NOK"),("AUD", "DKK"),("EUR", "AUD"),("AUD", "CHF"),("GBP", "CHF"),("AUD", "CAD"),("CHF", "DKK"),("AUD", "TRY"),("NZD", "CHF"),("USD", "SEK"),("GBP", "NZD"),("EUR", "DKK"),("NZD", "DKK"),("CAD", "SGD"),("EUR", "GBP"),("EUR", "CAD"),("USD", "CZK"),("AUD", "MXN"),("EUR", "NZD"),("GBP", "PLN"),("NZD", "NOK"),("AUD", "SGD"),("GBP", "SEK"),("NZD", "CAD"),("NZD", "MXN"),("NZD", "TRY"),("CHF", "SGD"),("USD", "MXN"),("EUR", "HUF"),("GBP", "CAD"),("USD", "TRY"),("USD", "JPY"),("EUR", "USD"),("AUD", "SEK"),("CHF", "NOK"),("USD", "PLN"),("USD", "HUF"),("CHF", "JPY"),("GBP", "ILS"),("NZD", "JPY"),("CHF", "TRY"),("CAD", "JPY"),("USD", "RUB"),("SGD", "JPY"),("GBP", "USD"),("CAD", "PLN"),("DKK", "SGD"),("NZD", "SGD"),("AUD", "JPY"),("NOK", "JPY"),("PLN", "SEK"),("USD", "SGD"),("GBP", "MXN"),("USD", "CAD"),("SEK", "DKK"),("DKK", "PLN"),("CAD", "MXN"),("GBP", "TRY"),("EUR", "SGD"),("NZD", "ZAR"),("EUR", "CZK"),("EUR", "JPY"),("CAD", "CHF"),("USD", "INR"),("USD", "BRL"),("USD", "NOK"),("USD", "DKK")]

@timeout.softtimeout(5)
def cades (f):
    return connector.get_candles(f[:6], 3600, max_dict, time.time())

result = []
for f in tqdm.tqdm(crpt):
    if f not in connector.get_all_ACTIVES_OPCODE():
        continue
    print(f)
    ANS = cades(f)
    print('zzz', ANS)
    if isinstance(ANS, str):
        continue
    ANSmean = statistics.mean([x.get('close') for x in ANS])

    period = 8 * 3600

    peakdiffset = []
    timediffset = []
    percset = []
    idiffset = []

    for i in ANS:
        if  ANS[-1]['from'] - i['from'] < period:
            continue
        period_candle_set = []
        for k in ANS:
            if k["from"] - i["from"] <= period and k["from"] - i["from"] > 0:
                period_candle_set.append(k)

        if len(period_candle_set) == 0:
            continue


        peakvalue = {'close': np.NINF}
        maxpeakvalue = {'max': np.NINF}

        for x in period_candle_set:
            if x['close'] > peakvalue['close']:
                peakvalue = x
            
            if x['max'] > maxpeakvalue['max']:
                maxpeakvalue = x

        peakdiff = peakvalue['close'] - i['close']
        maxpeakdiff = maxpeakvalue['close'] - i['max']
        timediff = peakvalue['from'] - i['from']
        maxtimediff = maxpeakvalue['from'] - i['from']

        perc = peakdiff/i['close']

        idiff = ANSmean - i['close']

        peakdiffset.append(peakdiff)
        timediffset.append(timediff)
        percset.append(perc)
        idiffset.append(idiff)

        fset = [x for x in peakdiffset if x >= 0]
        s_1 = len(fset)/len(peakdiffset)

        result.append(((f[:3], f[3:6]), ANSmean, statistics.mean(fset), statistics.stdev(fset), s_1))


json.dump(result, open('month_means.json', 'w'))




