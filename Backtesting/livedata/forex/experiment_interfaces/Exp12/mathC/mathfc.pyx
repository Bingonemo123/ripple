import scipy.stats
import numpy as np

def Wolf424B(m, p, Bs, n):
    shape = 1000
    zerosarg = np.zeros(shape, dtype=int)
    randomlib = np.random.choice([True, False],size=(91, shape), p=[p, (1 - p)])

    win = 0
    lose = 0
    for x in range(shape):
        B = Bs
        for y in range(91):
            if B/n <= 1:
                lose += 1
                zerosarg[x] = y
                break
            if B >= 2*Bs:
                win +=1
                zerosarg[x] = y
                break
            if randomlib[y][x]:
                B += (B/n) * m
            else:
                B -= (B/n)
        else:
            lose += 1
            zerosarg[x] = y 

    return win, lose, np.mean(zerosarg)


def ProximaCentauri (CurDelta, opening_price, mu, leverage):

    ANSmean, delta_price_mean, delta_price_std, s_1 = mu

    disDeltaPrice = scipy.stats.norm(delta_price_mean,  delta_price_std)
    ### Calculations
    pr = (disDeltaPrice.sf(CurDelta)/disDeltaPrice.sf(0)) - disDeltaPrice.cdf(0)
    closing_price = opening_price + CurDelta
    m = ((closing_price/opening_price) - 1) * leverage
    expected_value = m*(pr*s_1) - ( 1- pr*s_1)
    return expected_value, m, pr



def Kruger60B (current_price, leverage, mu):
    ### best expected value calculator
    ANSmean, delta_price_mean, delta_price_std, s_1 = mu

    firstsel = np.linspace(0, delta_price_mean + 3 * delta_price_std, 10)
    gsel = None
    for delta_price in firstsel:
        ev = ProximaCentauri(delta_price, current_price, mu, leverage)
        if gsel is None:
            gsel = ev + (delta_price,)
        elif ev[0] > gsel[0]:
            gsel = ev + (delta_price,)

    
    if gsel[1] == 0:
        secondsel = np.linspace(0, firstsel[1], 10)
    else:
        secondsel = np.linspace(gsel[1] - firstsel[1] , gsel[1] + firstsel[1], 11)

    for delta_price in secondsel:
        ev = ProximaCentauri(delta_price, current_price, mu, leverage)
        if gsel is None:
            gsel = ev + (delta_price,)
        elif ev[0] > gsel[0]:
            gsel = ev + (delta_price,)

    return gsel

def ProcyonB (m, p, Bs):
    firstsel = np.linspace(1, 100, 11).astype(int)
    gsel = None
    for n in firstsel:
        wlm = Wolf424B(m, p, Bs, n)
        if gsel is None:
            gsel = wlm + (n,)
        elif wlm[0] > gsel[0]:
            gsel = wlm + (n,)
        elif wlm[0] == gsel[0] and gsel[2] > wlm[2]:
            gsel = wlm + (n,)
    
    if gsel[3] == 1:
        secondsel = np.linspace(2, 9, 8).astype(int)
    else:
        secondsel = np.linspace(gsel[3] - 5, gsel[3] + 5, 11).astype(int)

    for n in secondsel:
        wlm = Wolf424B(m, p, Bs, n)
        if gsel is None:
            gsel = wlm + (n,)
        elif wlm[0] > gsel[0]:
            gsel = wlm + (n,)
        elif wlm[0] == gsel[0] and gsel[2] > wlm[2]:
            gsel = wlm + (n,)

    return gsel

def EpsilonIndiBb (current_price, leverage, mu, balance):
    ev, m, pr, delta_price =  Kruger60B(current_price, leverage, mu)

    if ev <= 0:
        return (None, None, None)
   
    win, lose, runmean, n = ProcyonB(m, mu[3] * pr, balance)


    score = ( win * pr  ** (n) )/ ( runmean * (1-pr) ** (np.log( n )) )

    return m, n, score


def EZAquariiB (names, prices, means_data, leverages, balance):

    scoreboard = [np.NINF]

    for name, price, leverage in zip(names, prices, leverages):

        for data in means_data:
            if data == name:
                mu = means_data[data]
                break
        else:
            continue

        m, n, x = EpsilonIndiBb(price, leverage, mu, balance)

        if x is None:
            continue

        if x > scoreboard[0]:
            scoreboard = [x, (name, m, n, leverage)]
        
    if scoreboard == [np.NINF]:
        return None
        
    return scoreboard

    



