import functools
from threading import Thread
import time
import traceback

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
                    res[0] = f'{e}::{ "".join(traceback.format_tb(e.__traceback__)) } :: {args, kwargs}'
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

@timeout(120)
def custom_reconnect(connector):
    while True:
        if connector.check_connect() == False:
            check,reason=connector.connect()
        else:
            break

@timeout(120)
def custom_opc(connector):
    return connector.get_all_ACTIVES_OPCODE()

@softtimeout(120)
def custom_all_asets(connector):
    ALL_Asset=connector.get_all_open_time() # loop warning
    return ALL_Asset

@softtimeout(10)
def custom_price(connector, f):
    candles = connector.get_candles(f, 5, 1, time.time())
    return candles[-1]['close']

@softtimeout(120)
def custom_bid(connector, f):
    connector.start_candles_stream(f, 1, 1)
    candles = connector.get_realtime_candles(f, 1)
    bid = [candles[x].get("bid") for x in candles]
    connector.stop_candles_stream(f, 1)
    return bid[0]

@softtimeout(1200)
def custom_profit(connector, instruments):
    price_ref = {}
    total_profit = 0
    total_margin = 0
    msg = []
    for inst in instruments:
        data = connector.get_positions(inst)
        for position in data[1].get('positions'):
            inst_id = position.get('instrument_id')
            leverage = position.get('leverage')
            buy_price = position.get('open_underlying_price')
            margin = position.get('margin')
            if inst_id not in price_ref:
                cprice = custom_bid(connector, inst_id)
                price_ref[inst_id] = cprice

            
            profit = (price_ref[inst_id] - buy_price )*leverage*margin/buy_price
            total_profit += profit
            total_margin += margin
            msg.append(position)

    return total_profit, total_margin, msg

@softtimeout(10)
def custom_leverage(connector, f, inst, prc):
    if prc:
        return max(connector.get_available_leverages(inst, f)[1].get('leverages')[0].get('regulated'))
    else:
        return min(connector.get_available_leverages(inst, f)[1].get('leverages')[0].get('regulated'))

@softtimeout(10)
def custom_close(connector, position):
    posid = position.get('order_ids')[0]
    connector.close_position(posid)

def get_custom_balance(connector, timeout = 60):
    connector.api.balances_raw = None
    connector.api.get_balances()
    stt = time.time()
    while connector.api.balances_raw == None and time.time() - stt < timeout:
        pass
    if connector.api.balances_raw == None:
        return None
    for balance in connector.api.balances_raw["msg"]:
            if balance["id"] == connector.get_balance_id():
                return balance["amount"]

