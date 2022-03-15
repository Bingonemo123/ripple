from PackageDependencies.MetaTrader import connector
from PackageDependencies.Constans import *
from PackageDependencies import Timeout
from PackageDependencies import GlobalFunctions
import numpy as np
import threading
from datetime import timedelta

class LoopUtilities():
    def __init__(self):
        for f in trdesk:
            t = threading.Thread(target=self.get_rates, args=(f,))
            t.start()
           
    def get_rates(self, f):
        rates = Timeout.datamine(connector, f=f, frame=connector.TIMEFRAME_M1, t=strd, count=10080)
        rerates = np.zeros((len(rates), 8), dtype=float)
        for i in range(len(rates)):
            for x in range(8):
                rerates[i][x] = rates[i][x]
        cd[f] = rerates
        crp[f] = rates[-1][crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume

    def get_new_data(self):
        self.actdesk = []
        for f in trdesk:
            t = threading.Thread(target=self.get_current_price, args=(f,))
            t.start()

    def get_current_price(self, f):
        rates = Timeout.datamine(connector, f=f, frame=connector.TIMEFRAME_M1, t=currd, count=1)
        if rates[0][0] != cd[f][-1][0]:
            cd[f] = np.roll(cd[f], -1, axis=0)
            for x in range(8):
                cd[f][-1][x] = rates[0][x]
            crp[f] = rates[-1][crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
            self.actdesk.append(f)

    def check_positions(self):
        for pos in ap:
            if pos[1] in self.actdesk:
                ### check if autoclose activated
                if pos[5] <= crp[pos[1]]: # close olhc = 1 a.k.a open
                    GlobalFunctions.close_pos(pos[0])
                    autoclosed += 1
                ### check if position is outoff margin
                if margin_balance <= 0:
                    marginclosed += len(ap)
                    GlobalFunctions.close_positions(ap)

    def check_cutout(self):
        cutout = 4
        if currd - lct >= timedelta(hours=cutout):
            total_profit = sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) for i in ap])
            if total_profit > 0:
                cutoutclosed += len(ap)
                cutoutindx += 1
                lct = currd
                GlobalFunctions.close_positions(ap)

    def main_filter (self):
        self.Filter = []
        for f in self.actdesk:
            if f in [i[1] for i in ap]:
                continue
            for indx in position_history:
                if position_history[indx].get('Name') == f:
                    if (currd - position_history[indx].get('Buying_time', 0)) < timedelta(hours=delay):
                        break
            else:
                self.Filter.append(f)
        return self.Filter
    
