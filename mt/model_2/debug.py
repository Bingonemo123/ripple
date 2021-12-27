import MetaTrader5 as mt5
import datetime
import calendar
import time
# connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

account = 5394724
authorized = mt5.login(account, password="m51djnLG", server="FxPro-MT5")
if not authorized:
    print("failed to connect at account #{}, error code: {}".format(
        account, mt5.last_error()))

N = mt5.symbol_info('BCP.LS')._asdict()
E = mt5.symbol_info('EURUSD')._asdict()

M = 'VVY.AS'

if mt5.market_book_add(M):
    while True:
        items = mt5.market_book_get(M)
        if items:
            for it in items:
                if it.type == 2:
                # order content
                    print(it.volume)
        mt5.market_book_release(M)
else:
    print("mt5.market_book_add('EURUSD') failed, error code =",mt5.last_error())