import math
import scipy.stats

LIMIT =  (27 * 80)/(330_000_000 * 9)

def EpsilonIndiBb (mean, std, cp): # probability of going up
    ccp = 2*mean - ((mean**2)/cp)
    return scipy.stats.norm.sf(ccp, mean, std)


def EZAquariiB (names, prices, means_data, leverages, balance):
    
    scoreboard = 0
    blackboard = []
    for name, price, lev in zip(names, prices, leverages):
        EI = EpsilonIndiBb(means_data[name][0], means_data[name][1], price)
        if EI > scoreboard:
            scoreboard = EI
            if EI == 1:
                n = 1
            else:
                n = math.ceil(math.log(LIMIT, (1- EI)))
            blackboard = [name, None, n, lev]

    if blackboard == []:
        return None
        
    return [scoreboard, blackboard]

# print(EpsilonIndiBb(2, 0.01, 2.345))
# print(EZAquariiB(['EURUSD', 'ESDMNB'], [1.345, 2.345], {'EURUSD': [2, 0.01], 'ESDMNB': [2, 0.01]}, [1, 1], 100))
