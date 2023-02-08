# mathematical experiment 
import math
import numpy as np
import itertools as it
import functools
n = 8

def real():
    win = 0
    total = 0
    while True:
        f = 0
        while True:
            
            if np.random.choice([True, False]):
                f += 1
            else:
                f -= 1

            if f>= n:
                win += 1
                break
                
            elif f < 0:
                break
        total += 1

        print(win, total, win/total)


def markov():
    matric = [
        [1, *[0 for _ in range(n-1)]],
        *[[ *[0 for y in range(x)], 0.5, 0, 0.5, *[0 for y in range(n - 3 - x)]] for x in range(n-2)],
        [*[0 for _ in range(n-1)], 1]
    ]

    initstate = [0, 1,  *[0 for _ in range(n-2)]]

    for _ in range(100):
        matric = np.matmul(matric, matric)


        print(matric)

def bruteforce():
    # lower catalan numbers; predicted not complete

    for steplimit in range(1, 40):
        paths = 0
        for walk in it.product([-1, 1], repeat=2*steplimit):
            sium = 0
            for step in walk:
                sium += step
                if sium < 0:
                    break
                elif sium >= n:
                    break
            if sium == n - 1:
                paths += 1

        print(paths)

@functools.cache
def recurrentlower(k, j):
    if k == j:
        return 1
    elif k == n - 1:
        return recurrentlower(k - 1, j - 1)
    elif k == 0:
        return recurrentlower(1, j-1)
    else:
        return recurrentlower(k + 1, j- 1) + recurrentlower(k - 1, j - 1)


for k in range(0, 41):
    print(recurrentlower(n - 1, n - 1 + 2*k))

