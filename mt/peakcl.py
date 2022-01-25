
import statistics
import numpy as np
def mpeak (ANS, period = 8 * 3600):


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

    delta_price_mean = statistics.mean(fset)
    delta_price_std = statistics.stdev(fset)


    return [ ANSmean, statistics.mean(fset), statistics.stdev(fset), s_1]