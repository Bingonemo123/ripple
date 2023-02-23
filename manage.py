from Backtesting.staticdata.options.tertiary_patterns.context import TertiaryController
from Backtesting.staticdata.options.tertiary_patterns.csv_writer import TertiaryCsvTrends

import numpy as np
np.set_printoptions(linewidth=np.inf)

tc = TertiaryController()

tc.load_m1_csv('Data\EURUSD\DAT_MT_EURUSD_M1_2019.csv')

tc.continuous_trend_search()
