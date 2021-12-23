import MetaTrader5 as mt5
import timeout
# connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

account = 5394724
authorized = mt5.login(account, password="m51djnLG", server="FxPro-MT5")
if not authorized:
    print("failed to connect at account #{}, error code: {}".format(
        account, mt5.last_error()))

N = mt5.symbol_info('NARI.O')._asdict()
E = mt5.symbol_info('EURUSD')._asdict()

for n in N:
    print(f'{n} :: {N[n]} :: { E[n]}')