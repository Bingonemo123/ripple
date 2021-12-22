import MetaTrader5 as mt5
import model_3.timeout as timeout
# connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown() 

account=5394724
authorized=mt5.login(account, password="m51djnLG", server="FxPro-MT5")
if not authorized:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))

seconds_in_year = 31_536_000

candle_size = 3600
quantity =  seconds_in_year / candle_size
print(timeout.custom_profit(mt5))

mt5.shutdown()