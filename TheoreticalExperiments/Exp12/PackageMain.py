import multiprocessing as mp
from PackageDependencies.MetaTrader import connector
from PackageDependencies.LoopFunctions import LoopUtilities
from PackageDependencies.Constans import *
import time

from PackageDependencies.GuiFunctions import PrintUtils

lu = LoopUtilities()
gui = PrintUtils()

if __name__ == '__main__':
    lp = mp.Process(target=lu.loop_flow)
    guip = mp.Process(target=gui.loop_flow)
    lp.start()
    guip.start()
    lp.join()
    guip.join()
