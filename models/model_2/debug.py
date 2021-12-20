from iqoptionapi.stable_api import IQ_Option
import timeout
import time 
connector =IQ_Option("levanmikeladze123@gmail.com" ,"591449588")
connector.connect()
connector.change_balance("PRACTICE")

l = max(connector.get_available_leverages('crypto', 'BTCUSD')[1].get('leverages')[0].get('regulated'))
print(l)