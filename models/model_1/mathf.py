from scipy import special
import numpy as np
import time
import numba

def CNcdf(x, mu):
    delta = 10000   
    line = np.linspace(0, x, delta)   

    return (np.e ** (-mu)) * np.sum((mu**line) / special.gamma(line + 1) * (x / delta ))


def Pc (price, leverage, mu, m):
    cbetta = price*((m/leverage)+ 1)
    return 1 - CNcdf(cbetta, mu)

def EVc (price, leverage, mu, m):
    pro = Pc(price, leverage, mu, m)
    return m * pro - (1- pro)


def brute(m, p, Bs, n):
    shape = 1000
    win = 0
    lose = 0
    avgstep = np.zeros(shape, dtype=np.int)
    for x in range(shape):
        B = Bs
        for y in range(91):
            if B/n <= 1:
                lose += 1
                avgstep[x] = y
                break
            if B >= 2*Bs:
                win +=1
                avgstep[x] = y
                break
            if np.random.choice([True, False], p=[p, (1 - p)]):
                B += (B/n) * m
            else:
                B -= (B/n)
        else:
            lose += 1
            avgstep[x] = y 
    return win, lose, np.mean(avgstep)


def nbrute(m, p, Bs, n):
    shape = 1000
    zerosarg = np.zeros(shape, dtype=np.int)
    randomlib = np.random.choice([True, False],size=(91, shape), p=[p, (1 - p)])

    @numba.jit(nopython=True)
    def pic(m, Bs, n, zerosarg, randomlib):
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
        return win, lose
    return *pic(m, Bs, n, zerosarg, randomlib), np.mean(zerosarg)


def nmfinder (current_price, leverage, mu, balance):
    mv = np.linspace(0.01, 1, num= 100)
    nv = np.linspace(1, 20, 10) 

    Evv = np.array([EVc(current_price, leverage, mu, z) for z in mv])
    mvc = []
    for x, y in zip(mv, Evv):
        if y >= 0:
            mvc.append(x)

    mv = np.array(mvc)
    
    if len(mv) == 0:
        return 0, 0, np.NINF 

    wincube = np.zeros(shape=(np.size(mv), np.size(nv)))
    meancube = np.zeros(shape=(np.size(mv), np.size(nv)))
    pcube = np.zeros(shape=(np.size(mv), np.size(nv)))
    for x in range(len(mv)):
        for y in range(len(nv)):
            performance = nbrute(mv[x], Pc(current_price, leverage, mu, mv[x]), balance, nv[y])
            wincube[x][y] = performance[0]
            meancube[x][y] = performance[2]
            pcube[x][y] = Pc(current_price, leverage, mu, mv[x])

    ###
    indexcube = []

    for wc,vc, pv in zip(wincube, meancube, pcube):
        holder = []
        for w, v, n, p in zip(wc, vc, nv, pv):
            holder.append(
                ( w * p ** (n) )/ ( v * (1-p) ** (np.log( n )) )
            )

        indexcube.append(holder)

    indexcube = np.array(indexcube)

    maxcoordinates = tuple(zip(*np.where(indexcube == indexcube.max())))[0]

    return mv[maxcoordinates[0]], nv[maxcoordinates[1]], indexcube.max()

def EZAquariiB (names, prices, means, leverages, balance):

    scoreboard = [np.NINF]

    for name, price, leverage in zip(names, prices, leverages):
        if len(name) != 6:
            name = name[:6]
        enlistedname = [name[:3], name[3:]]

        for mean in means:
            if mean[0] == enlistedname or mean[0] == enlistedname[::-1]:
                mu = mean[1]
            else:
                continue

        m, n, x = nmfinder(price, leverage, mu, balance)

        if x > scoreboard[0]:
            scoreboard = [x, (name, m, n, leverage)]
        
    if scoreboard == [np.NINF]:
        return None
        
    return scoreboard

    



