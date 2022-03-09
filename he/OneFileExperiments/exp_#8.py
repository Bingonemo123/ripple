from scipy import special
import numpy as np

def CNcdf(x, m):
    delta = 10000
    line = np.linspace(0, x, delta)   

    return (np.e ** (-m)) * np.sum((m**line) / special.gamma(line + 1) * (x / delta ))


mu = 1  # average price
betta = 0.3 # current price
leverage = 1

m = 0.01 # winning rate

def closing_betta (m):
    '''price at which must market reach to get win m'''
    return betta*((m/leverage)+ 1)   

cbetta = closing_betta(m)

pro = 1 - CNcdf(cbetta, mu)

print(cbetta, pro)

expectedvalue = m * pro - ( 1 - pro )

print(expectedvalue)
#  m and p relationation must be > 1