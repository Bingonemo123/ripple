import MetaTrader5 as mt5
 
# connect to MetaTrader 5
if not mt5.initialize(portable=True):
    print("initialize() failed")
    mt5.shutdown() 

account=5394724
authorized=mt5.login(account, password="m51djnLG", server="FxPro-MT5")
if authorized:
    # display trading account data 'as is'
    print(mt5.account_info())
    # display trading account data in the form of a list
    print("Show account_info()._asdict():")
    account_info_dict = mt5.account_info()._asdict()
    for prop in account_info_dict:
        print("  {}={}".format(prop, account_info_dict[prop]))
else:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))