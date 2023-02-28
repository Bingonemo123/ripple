from Backtesting.staticdata.options.tertiary_patterns.context import TertiaryController
from Backtesting.staticdata.options.tertiary_patterns.csv_writer import TertiaryCsvTrends

import numpy as np
np.set_printoptions(linewidth=np.inf)

tc = TertiaryController()

# tc.load_m1_csv('Data\EURUSD\DAT_MT_EURUSD_M1_2019.csv')
tc.load_gbm(20)

np.savetxt('random_raw.csv', tc.raw_m1_csv)
np.savetxt('random_tert.csv', tc.tertiary_m1)
tc.continuous_trend_search(filename='gbm_20')
