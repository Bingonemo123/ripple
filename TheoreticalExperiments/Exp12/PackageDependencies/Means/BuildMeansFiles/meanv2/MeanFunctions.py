import statistics
from datetime import timedelta
period = 8
ohlc = 4

def mean(f, cdata):
    a = statistics.mean([i[ohlc] for i in cdata]) # ANSmean 

    period_number = int(timedelta(hours=period).seconds/60)
    
    fset = [] # set of all peakdiffs for f
    for i in range(len(cdata)):
        period_candle_set = cdata[i:i+period_number] # every candle that is after i-th candle and is less than period of time
        peakvalue = period_candle_set.max(axis=0)[ohlc]
        peakdiff = peakvalue - cdata[i][ohlc] 
        if peakdiff > 0:
            fset.append(peakdiff)
    
    s_1 = len(fset) / len(cdata)

    b = statistics.mean(fset)
    c = statistics.stdev(fset)

    return [a, b, c, s_1]
       
