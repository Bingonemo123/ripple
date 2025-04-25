from Backtesting.staticdata.options.local_tertiary_patterns.context import LocalTertiaryLengthWiseSearch

import numpy as np
np.set_printoptions(linewidth=np.inf)

tc = LocalTertiaryLengthWiseSearch()

tc.load_gbm()
tc.search(stdout=True)
