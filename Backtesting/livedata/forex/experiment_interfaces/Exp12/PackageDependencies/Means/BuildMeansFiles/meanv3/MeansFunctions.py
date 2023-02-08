import statistics
ohlc = 4

def mean(f, cdata):
    ohlcset = [i[ohlc] for i in cdata]
    a = statistics.mean(ohlcset)
    b = statistics.stdev(ohlcset)
    return [a, b]
