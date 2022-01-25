from iqoptionapi.stable_api import IQ_Option
import time
connector =IQ_Option("levanmikeladze123@gmail.com" ,"591449588")
connector.connect()


def custom_forex(connector, f):
    candles = connector.get_candles(f[:6], 5, 1, time.time())
    return candles[-1]['close']


def custom_forex_bid(connector, f):
    connector.start_candles_stream(f[:6], 1, 1)
    candles = connector.get_realtime_candles(f[:6], 1)
    bid = [candles[x].get("bid") for x in candles]
    return bid[0]


def custom_profit(connector):
    data = connector.get_positions('forex')
    price_ref = {}
    total_profit = 0
    total_margin = 0
    for position in data[1].get('positions'):
        inst_id = position.get('instrument_id')
        leverage = position.get('leverage')
        buy_price = position.get('open_underlying_price')
        margin = position.get('margin')
        if inst_id not in price_ref:
            cprice = custom_forex_bid(connector, inst_id)
            price_ref[inst_id] = cprice
        
        profit = (price_ref[inst_id] - buy_price )*leverage*margin/buy_price
        total_profit += profit
        total_margin += margin

    
    return total_profit, total_margin, data[1].get('positions')

while True:
    print (custom_profit(connector)[0])