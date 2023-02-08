# Epxperiment to solve Catalan number problem
from math import factorial as fact
import numpy as np
from gmpy2 import divexact
from functools import cache
from math import comb

@cache
def cat_direct(n):
    if n == 1:
        return 1
    elif n == 2:
        return 1
    return divexact(cat_direct(n-1)*(4*n-6), n)

@cache
def unktrg(n, k):
    if n == 1 or n == 2:
        return cat_direct(k)
    elif n<= 0:
        return 0
    else:
        return sum([unktrg(x, k - 1) for x in range(n-1, k )])


for k in range (0, 20):
    print((4/(k + 4))*comb(2*k + 3, k))


print(unktrg(10, 10))
