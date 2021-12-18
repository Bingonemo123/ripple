from iqoptionapi.stable_api import IQ_Option
import timeout

connector =IQ_Option("levanmikeladze123@gmail.com" ,"591449588")
connector.connect()



while True:
    try:
        total_profit, total_margin, msg = timeout.custom_profit(connector)
    except ValueError:
        print(str(timeout.custom_profit(connector)))
        raise Exception
