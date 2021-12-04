from scipy import stats
from scipy import special
import matplotlib.pyplot as plt
import numpy as np
fig, ax = plt.subplots(1, 1)

mu = 3

gline = np.linspace(0, 10, 11)

def CNcdf(x, m):
    delta = 10000
    line = np.linspace(0, x, delta)   

    return (np.e ** (-m)) * np.sum((m**line) / special.gamma(line + 1) * (x / delta ))



ax.plot(gline,  [CNcdf(x, mu ) for x in gline])



pdis = stats.poisson.cdf(gline, mu)
ax.plot(gline,  pdis)
plt.show()
print(pdis)
print([CNcdf(x, mu ) for x in gline])