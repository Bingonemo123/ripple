import numpy as np

def cbrute(m, p, Bs, n):
    shape = 1000
    zerosarg = np.zeros(shape, dtype=np.int)
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





