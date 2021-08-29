import operator
import time
def stocks_mm(conn):
    conn.update_ACTIVES_OPCODE()
    opcode_data=conn.get_all_ACTIVES_OPCODE()

    instrument_type='cfd'
    conn.subscribe_top_assets_updated(instrument_type)


    def opcode_to_name(opcode_data,opcode):
        return list(opcode_data.keys())[list(opcode_data.values()).index(opcode)]            

    while True:
        if conn.get_top_assets_updated(instrument_type)!=None:
            break

    top_assets=conn.get_top_assets_updated(instrument_type)


    diff_trading_day={}
    for asset in top_assets:
        opcode=asset["active_id"]
        diff_trading_day_value=asset["diff_trading_day"]["value"]
        try:
            name=opcode_to_name(opcode_data,opcode)
            diff_trading_day[name]=diff_trading_day_value
        except:
            pass
    
    sorted_diff_trading_day= sorted(diff_trading_day.items(), key=operator.itemgetter(1))

    return ([x[0] for x in reversed(sorted_diff_trading_day)])

def past_history(conn, ticker):
    end_from_time=time.time()

    data=conn.get_candles(ticker, 86400, 31, end_from_time)
    print(data)
    input()
    for candle in data:
        if candle.get('max') > data[-1].get('max'):
            return True
    else:
        return False 