import sys
import MetaTrader5 as mt5
import numpy as np
import statistics
import peakcl
import model_3.mathfc as fc

###
seconds_in_month = 2_592_000 
seconds_in_year = 31_536_000

candle_size = 3600 # 3600 is one hour
quantity =  seconds_in_month / candle_size
###
sname = sys.argv[-1]

leverage = 100

balance = 45.9

####

if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

account = 5394724
authorized = mt5.login(account, password="m51djnLG", server="FxPro-MT5")
if not authorized:
    print("failed to connect at account #{}, error code: {}".format(
        account, mt5.last_error()))

symbol = mt5.symbol_info(sname)
print(symbol.name)
ANS = mt5.copy_rates_from_pos(symbol.name, mt5.TIMEFRAME_H1, 0, int(quantity))

mu = peakcl.mpeak(ANS)
ANSmean, delta_price_mean, delta_price_std, s_1 = mu
print(f'ANSMEAN: {ANSmean}')
print(f'Delta_price_mean {delta_price_mean} ')
print(f'delta_price_std {delta_price_std}')
print(f's_1 {s_1}')

print(f'price {symbol.bid}')
print(f'leverage {leverage}')
print(f'Balance {balance}')
print(fc.EpsilonIndiBb(36900, leverage, mu, balance))