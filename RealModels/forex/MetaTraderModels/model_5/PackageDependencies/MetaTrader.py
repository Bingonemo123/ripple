import MetaTrader5 as connector


if not connector.initialize():
    print("initialize() failed")
    connector.shutdown()

account = 5419164
authorized = connector.login(account, password="u2lgFSvc", server="FxPro-MT5")
if not authorized:
    print("failed to connect at account #{}, error code: {}".format(
        account, connector.last_error()))


"""
just-forex demo 
account: 124199
password: aDpkhKRq47c9NMA
server: Justforex-Demo
"""
