from Backtesting.staticdata.options.binary_patterns.context import BinaryController


controller = BinaryController()

controller.load_m1_csv('Data\EURUSD\DAT_MT_EURUSD_M1_2019.csv')

controller.continuousSearch()
