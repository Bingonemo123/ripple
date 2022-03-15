import multiprocessing as mp
from PackageDependencies.MetaTrader import connector
from PackageDependencies.LoopFunctions import LoopUtilities
from PackageDependencies.Constans import *
import time

tst = time.perf_counter()
lu = LoopUtilities()
print(time.perf_counter() - tst)
