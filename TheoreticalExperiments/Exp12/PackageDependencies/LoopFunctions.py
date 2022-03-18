import curses
import os
import sys
import threading
from datetime import timedelta

import numpy as np

from PackageDependencies import GlobalFunctions, Timeout
from PackageDependencies.Constans import *
from PackageDependencies.Means.meanv1.MeanFunctions import mean
from PackageDependencies.MetaTrader import connector
from PackageDependencies.Strategies import mathfc


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
        global actdesk
        actdesk = []
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
            actdesk.append(f)

    def check_positions(self):
        global autoclosed, marginclosed
        for pos in ap:
            if pos[1] in actdesk:
                ### check if autoclose activated
                if pos[5] <= crp[pos[1]]: # close olhc = 1 a.k.a open
                    GlobalFunctions.close_pos(pos[0])
                    autoclosed += 1
                ### check if position is outoff margin
                if margin_balance <= 0:
                    marginclosed += len(ap)
                    GlobalFunctions.close_positions(ap)

    def check_cutout(self):
        global lct, cutoutindx, cutoutclosed
        cutout = 4
        if currd - lct >= timedelta(hours=cutout):
            total_profit = sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) for i in ap])
            if total_profit > 0:
                cutoutclosed += len(ap)
                cutoutindx += 1
                lct = currd
                GlobalFunctions.close_positions(ap)

    def main_filter (self):
        global Filter
        delay = 8
        Filter = []
        for f in actdesk:
            if f in [i[1] for i in ap]:
                continue
            for indx in position_history:
                if position_history[indx].get('Name') == f:
                    if (currd - position_history[indx].get('Buying_time', 0)) < timedelta(hours=delay):
                        break
            else:
                Filter.append(f)
        return Filter
    
    def run_strategy(self):
        global foundmark
        pricelist = []
        leverages = []
        for f in Filter:
            pricelist.append(crp[f])
            leverages.append(leveg)

        
        foundmark = mathfc.EZAquariiB(Filter, pricelist, means_data, leverages, safe_balance)
        if foundmark != None:
            self.name = foundmark[1][0]
            self.m = foundmark[1][1]
            self.n = foundmark[1][2]
            self.leverage = foundmark[1][3]
            ### 7. get name, m, n and leverage if available
            return foundmark[1] # name, m, n, leverage 

    def theoretical_buy(self):
        global curr_balance, id_index
        if safe_balance/ self.n < 1:
            amount = 1
        elif safe_balance/ self.n > 20000:
            amount = 20000
        else:
            amount = safe_balance/ self.n

        take_profit_value = ((self.m/self.leverage) + 1) * crp[self.name]

        if amount <= safe_balance:
            id_index += 1
            curr_balance -= amount
            if curr_balance < 0:
                pass
            else:
                amount_tlots = amount * self.leverage / crp[self.name]# amount of theortical lots
                ap.append([id_index, self.name, crp[self.name], currd, amount, take_profit_value, self.leverage, amount_tlots])
                position_history[id_index] = {'Id' : id_index,
                                'Name' : self.name,
                                'Opening_price' : crp[self.name],
                                'Buying_time': currd,
                                'Amount': amount,
                                'TakeProfitValue': take_profit_value,
                                'leverage': self.leverage,
                                'Amount_tlots': amount_tlots,
                                'Balance': curr_balance,
                                'SafeBalance': safe_balance,
                            } # add exam

    def bundle_mean_strategy_buy(self):
        if safe_balance > 0:
            for f in Filter:
                means_data[f] = mean(f)

            if self.run_strategy() is not None:
                self.theoretical_buy()

    def flow(self):
        self.get_new_data()
        self.check_positions()
        self.check_cutout()
        self.main_filter()
        self.bundle_mean_strategy_buy()

    def loop_flow(self):
        global currd
        while True:
            try:
                currd += timedelta(minutes=1)
                self.flow()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(str(e))
                print([exc_type, fname, exc_tb.tb_lineno])
                # client.send_message(exc_type, title=f'M{prc * "P"}{modeln}E {os.getcwd()}')
                curses.endwin()
