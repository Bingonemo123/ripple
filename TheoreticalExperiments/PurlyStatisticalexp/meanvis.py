from datetime import datetime, timezone, timedelta
import MetaTrader5 as mt5

if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()
import pandas as pd

utc_from = datetime.now(timezone.utc)
rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_H4, utc_from, 1000000)
rates_frame = pd.DataFrame(rates)
rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
