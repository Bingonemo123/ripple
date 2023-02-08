import random
from datetime import datetime
import plotext as plt
import numpy as np
from os import system


plt.datetime.set_datetime_form(date_form= '%d/%m/%Y')
#start = plt.datetime.string_to_datetime("11/07/2020")

end = plt.datetime.today.datetime
import MetaTrader5 as mt5
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_D1, end, 200)
rerates = np.zeros((len(rates), 8), dtype=float)
for i in range(len(rates)):
        for x in range(8):
            rerates[i][x] = rates[i][x]



for f in range(100):
    plt.clt()
    plt.clp()
    plt.clc()
    plt.cls()
    prices = [x[4] for x in rerates[f:f+100]]
    # dates = [plt.datetime.datetime_to_string(datetime.fromtimestamp(el[0])) for el in rerates[f:f + 100]]
    plt.plot( prices)
    plt.title("Google Stock Price")
    plt.ylabel("$ Stock Price")
    plt.clc()
    plt.show()

