import functools
from threading import Thread
import datetime
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

@softtimeout(120)
def custom_all_asets(connector):
    ALL_Asset = connector.symbols_get() # loop warning
    return ALL_Asset

@softtimeout(120)
def custom_safty(connector, f):
    symbol_info = connector.symbol_info(f)
    if symbol_info is None:
        return False
    if not symbol_info.visible:
        if not connector.symbol_select(f, True):
            return False

    tz = datetime.timezone(datetime.timedelta(hours=+2))
    symbol_time = datetime.datetime.fromtimestamp(symbol_info.time, tz=tz).replace(tzinfo=None)
    if (datetime.datetime.now() - symbol_time).total_seconds() > 3600:
        return False
    

    return True


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
        name = position.symbol
        leverage = connector.account_info().leverage
        lottoamount =  connector.symbol_info(name).trade_contract_size
        buy_price = position.price_open
        margin = position.volume * lottoamount * buy_price / leverage

        total_profit += position.profit
        total_margin += margin

    return total_profit, total_margin, data

@softtimeout(10)
def custom_leverage(connector):
    return connector.account_info().leverage

@softtimeout(10)
def custom_close(connector, position):
    symbol_info = connector.symbol_info(position.symbol)
    volume_max = symbol_info.volume_max
    if position.volume > volume_max:
        volume = volume_max
    else:
        volume = position.volume

    close_request={
        "action": connector.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": volume,
        "type": connector.ORDER_TYPE_SELL,
        "position": position.ticket,
        "price": connector.symbol_info_tick( position.symbol).bid,
        "comment": "Close Position",
        "type_time": connector.ORDER_TIME_GTC, # good till cancelled
        "type_filling": connector.ORDER_FILLING_IOC,
    }
    result=connector.order_send(close_request)
    if result.retcode != connector.TRADE_RETCODE_DONE:
        ret = ""
        ret += "2. order_send failed, retcode={}".format(result.retcode)
        # request the result as a dictionary and display it element by element
        result_dict=result._asdict()
        for field in result_dict.keys():
            ret +="   {}={}".format(field,result_dict[field])
            # if this is a trading request structure, display it element by element as well
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    ret += "       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed])
        return ret
    return True
    

@timeout(10)
def get_custom_balance(connector):
    return connector.account_info().balance

@softtimeout(120)
def custom_prebuy(connector, f):
    symbol_info = connector.symbol_info(f)
    point = symbol_info.point
    volume_step = symbol_info.volume_step
    price = connector.symbol_info_tick(f).ask
    margin = connector.order_calc_margin(connector.ORDER_TYPE_BUY, f, 1, price)
    volume_max = symbol_info.volume_max

    return point, volume_step, price, margin, volume_max
