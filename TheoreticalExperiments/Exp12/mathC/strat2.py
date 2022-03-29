import scipy.stats
import math

def prob (mean, std, cp): # probability of going up
    ccp = 2*mean - ((mean**2)/cp)
    return scipy.stats.norm.sf(ccp, mean, std)

p = prob(3, 1, 2)

limit = (27 * 80)/(330_000_000 * 9)
print( math.ceil(math.log(limit, (1- p))))
print((1- p) ** 5 < limit)
