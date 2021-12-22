import functools
from threading import Thread
import time

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception(f'function [%s] timeout [%s seconds] exceeded! Arguments {args, kwargs}' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

def softtimeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [f'function [%s] timeout [%s seconds] exceeded! Arguments {args, kwargs}' % (func.__name__, timeout)]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print('Error starting thread')
                raise je
            ret = res[0]
            return ret
        return wrapper
    return deco

#----------------------------------------------------------------------------#

@softtimeout(120)
def custom_all_asets(connector):
    ALL_Asset= connector.symbols_get() # loop warning
    return ALL_Asset

@softtimeout(10)
def custom_price(connector, f):
    candles = connector.copy_rates_from_pos(f, connector.TIMEFRAME_M1, 0, 1)
    return candles[-1][4]

@softtimeout(10)
def custom_bid(connector, f):
    return connector.symbol_info(f).bid

@softtimeout(10)
def custom_profit(connector):
    total_profit = 0
    total_margin = 0
    data = connector.positions_get()
    for position in data:
        leverage = custom_leverage(connector)
        buy_price = position.price_open
        margin = position.volume * buy_price

        cprice = custom_bid(connector, position.symbol)
        
        profit = (cprice - buy_price )*leverage*margin/buy_price
        total_profit += profit
        total_margin += margin

    return total_profit, total_margin, data

@softtimeout(10)
def custom_leverage(connector):
    return connector.account_info().leverage

@softtimeout(10)
def custom_close(connector, position):
    posid = position.get('order_ids')[0]
    connector.close_position(posid)

@timeout(10)
def get_custom_balance(connector):
    return connector.account_info().balance
