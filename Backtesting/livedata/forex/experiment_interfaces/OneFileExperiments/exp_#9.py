from forex_python.converter import CurrencyRates
import datetime 
import tqdm
import pandas as pd
c = CurrencyRates()


data_obj = pd.DataFrame()
date_obj = datetime.datetime.today() - datetime.timedelta(days=1)
for x in tqdm.tqdm(range(365)):
    data_obj = data_obj.append(c.get_rates('USD', date_obj), ignore_index=True)
    date_obj -= datetime.timedelta(days=1)

data_obj.to_csv('USD_daily.csv')