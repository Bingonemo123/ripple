from iqoptionapi.stable_api import IQ_Option
import timeout
import time 
connector =IQ_Option("levanmikeladze123@gmail.com" ,"591449588")
connector.connect()


print(connector.get_candles('FILUSD-L', 60, 1000, time.time()))