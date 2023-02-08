import io
import os
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

import numpy as np
import pytz
import logging
import pickle

logging.basicConfig(filename='2wp6.txt', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

from PackageDependencies import Timeout
from PackageDependencies.GuiFunctions import CursesUtilities
from PackageDependencies.Means.meanv3.MeanFunctions import mean
from PackageDependencies.MetaTrader import connector
from PackageDependencies.Strategies.version2 import mathf


class LoopUtilities():
    def __init__(self):
        self.timezone = pytz.timezone("Etc/UTC")
        self.strd =  datetime.strptime("01.01.2018", "%d.%m.%Y", )
        self.strd = self.strd.replace(tzinfo=self.timezone)
        self.currd = self.strd
        self.cd = {} # candledata = list of one week data 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
        self.trdesk = ["EURUSD", "GBPUSD", "USDJPY", "USDTHB", "USDZAR", "EURZAR", "GBPZAR", "GBPJPY"]# [x.name for x in Timeout.custom_all_asets(connector)]
        # 3. Cutout
        self.lct = self.strd # last cutout time = time of last cutout
        self.tp = 0 # total profit
        self.id_index = 0 # id for positions
        self.ap = [] # active positions position data 
        '''(0.id, 1.name, 2.opening price, 3.open time, 4.amount(in money), 5.auto close, 6.leverage,7. amount(in lots), 8.mt_ticket)'''
        self.crp = {} # current price
        self.crpohlc = 1 # current price ohlc
        self.init_balance = 100
        self.curr_balance = self.init_balance # init_balance - active_position_buying_amount - closed_win_lose_amount (updated when new position is bought or active closed)
        self.free_balance = self.init_balance # curr_balance - active_positions_win_lose_amount 
        self.margin_balance = self.init_balance # curr_balance - active_positions_lose_amount
        self.safe_balance = self.init_balance # curr_balance  - safe_margin - active_positions_lose_amount 
        # safe-balance = curr_balance - Sum(loan) : | loan = pm - v | pm = v * l = a * op
        # margin_balance = curr_balance - Sum(am | if op > cp) : | am = bm + v | bm = cm - pm | cm = a * op
        # free_balance = curr_balance - Sum(am) : | am = bm + v | bm = cm - pm | cm = a * op
        self.leveg = 200 # leverage
        self.position_history = {}

        self.maximum_var = [self.curr_balance, self.safe_balance, self.margin_balance, self.free_balance, len(self.ap)]
        self.minimum_var = [self.curr_balance, self.safe_balance, self.margin_balance, self.free_balance]
        self.autoclosed = 0
        self.marginclosed = 0
        self.cutoutclosed = 0
        self.cutoutindx = 0
        self.lastmean = {}

        self.last_graph_update = self.strd
        self.fake_file = io.StringIO()

        self.means_data = {}
        self.foundmark = None
        self.actdesk = []
        self.Filter = []
        self.iteration = 0
        self.drawing_time = 0
        self.last_foundmark_run = self.strd
        self.last_foundmark_iter = 0
        self.last_mean_calc_time = 0

        for f in self.trdesk:
            print(f)
            self.get_rates(f)
        
        self.gui = CursesUtilities(self)
        self.last_gui_update = datetime.now()
        self.gui.flow(self)
           
    def get_rates(self, f):
        rates = Timeout.datamine(connector, f=f, frame=connector.TIMEFRAME_H4, t=self.strd, count=42)
        rerates = np.zeros((len(rates), 8), dtype=float)
        for i in range(len(rates)):
            for x in range(8):
                rerates[i][x] = rates[i][x]
        self.cd[f] = rerates
        self.crp[f] = rates[-1][self.crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume

    def get_new_data(self):
        self.actdesk = []
        for f in self.trdesk:
            rates = Timeout.datamine(connector, f=f, frame=connector.TIMEFRAME_H4, t=self.currd, count=1)
            if rates[0][0] != self.cd[f][-1][0]:
                self.cd[f] = np.roll(self.cd[f], -1, axis=0)
                for x in range(8):
                    self.cd[f][-1][x] = rates[0][x]
                self.crp[f] = rates[-1][self.crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
                self.actdesk.append(f)

    def calc_balance(self):
        self.free_balance = self.curr_balance + sum([i[4]*i[6]*((self.crp[i[1]]/i[2]) - 1) + i[4] for i in self.ap])  # v * l ( cp/op - 1) + v
        self.margin_balance = self.curr_balance + sum([i[4]*i[6]*((self.crp[i[1]]/i[2]) - 1) + i[4] for i in self.ap if self.crp[i[1]] < i[2]])  # v * l ( cp/op - 1) + v
        self.safe_balance = self.curr_balance - sum([i[4]*(i[6] - 1) for i in self.ap])  # loan = pm - v | pm = v * l = a * op
        # Sometimes margin_balance can be more than curr_balance, 
        # because margin_balance also contains investment which is substracted from curr_balance,
        #  and if price is not low enough,investment amount (v) will be added to margin balance and not currbalance
    def close_pos(self, ids):
        for i in self.ap:
            if i[0] == ids:
                closing_profit = i[4] * i[6] * ((self.crp[i[1]]/i[2]) - 1) + i[4]
                self.tp += closing_profit
                self.curr_balance += closing_profit
                self.position_history.get(ids).update({'Close Time': self.currd, 'Close Price': self.crp[i[1]], 'Profit': closing_profit, 'Closed by': 'Auto'})
                self.ap.remove(i)
                break
        self.calc_balance()

    def close_positions(self):
        for i in self.ap:
            closing_profit = i[4] * i[6] * ((self.crp[i[1]]/i[2]) - 1) + i[4]
            self.tp += closing_profit - i[4]
            self.curr_balance += closing_profit
            self.position_history.get(i[0]).update({'Close Time': self.currd, 'Close Price': self.crp[i[1]], 'Profit + Investment': closing_profit,
             'Closed by': 'Cluster', 'Profit': closing_profit - i[4]})

        self.ap.clear()
        self.calc_balance()

    def check_positions(self):
        for pos in self.ap:
            if pos[1] in self.actdesk:
                ### check if autoclose activated
                if pos[5] is not None:
                    if pos[5] <= self.crp[pos[1]]: # close olhc = 1 a.k.a open
                        self.close_pos(pos[0])
                        self.autoclosed += 1
                ### check if position is outoff margin
                if self.margin_balance <= 0:
                    self.marginclosed += len(self.ap)
                    self.close_positions()

    def check_cutout(self):
        cutout = 1
        if self.currd - self.lct >= timedelta(hours=cutout):
            total_profit = sum([i[4]*i[6]*((self.crp[i[1]]/i[2]) - 1) for i in self.ap])
            if total_profit > 0:
                self.cutoutclosed += len(self.ap)
                self.cutoutindx += 1
                self.lct = self.currd
                self.close_positions()

    def main_filter (self):
        delay = 8
        self.Filter = []
        for f in self.actdesk:
            if f in [i[1] for i in self.ap]:
                continue
            for indx in self.position_history:
                if self.position_history[indx].get('Name') == f:
                    if (self.currd - self.position_history[indx].get('Buying_time', 0)) < timedelta(hours=delay):
                        break
            else:
                self.Filter.append(f)
        return self.Filter
    
    def run_strategy(self):
        pricelist = []
        leverages = []
        for f in self.Filter:
            pricelist.append(self.crp[f])
            leverages.append(self.leveg)

        self.foundmark = mathf.EZAquariiB(self.Filter, pricelist, self.means_data, leverages, self.safe_balance)
        
        self.last_foundmark_run = self.currd
        self.last_foundmark_iter = self.iteration
        
        if self.foundmark != None:
            self.name = self.foundmark[1][0]
            self.m = self.foundmark[1][1]
            self.n = self.foundmark[1][2]
            self.leverage = self.foundmark[1][3]
            ### 7. get name, m, n and leverage if available
            return self.foundmark[1] # name, m, n, leverage 


    def theoretical_buy(self):
        if self.safe_balance/ (self.n * self.leverage)< 1:
            self.amount = 1
        elif self.safe_balance/ (self.n * self.leverage) > 200:
            self.amount = 200
        else:
            self.amount = self.safe_balance/ (self.n * self.leverage)


        if self.m == None:
            take_profit_value = None
        else:
            take_profit_value = ((self.m/self.leverage) + 1) * self.crp[self.name]
        

        if self.amount <= self.curr_balance: # if self.amount <= self.safe_balance: !!! DON'T DELETE !!!
            if self.curr_balance < 0:
                pass
            else:
                self.id_index += 1
                self.curr_balance -= self.amount
                amount_tlots = self.amount * self.leverage / self.crp[self.name]# amount of theortical lots
                self.ap.append([self.id_index, self.name, self.crp[self.name], self.currd, self.amount, take_profit_value, self.leverage, amount_tlots])
                self.position_history[self.id_index] = {'Id' : self.id_index,
                                'Name' : self.name,
                                'Opening_price' : self.crp[self.name],
                                'Buying_time': self.currd,
                                'Amount': self.amount,
                                'TakeProfitValue': take_profit_value,
                                'leverage': self.leverage,
                                'Amount_tlots': amount_tlots,
                                'Balance': self.curr_balance,
                                'SafeBalance': self.safe_balance,
                            } # add exam

    def bundle_mean_strategy_buy(self):
        if self.margin_balance > 50: # !!! DON'T DELETE !!! if safe_balance < 0 no meaning to run strategy change strategy balance input
            for f in self.Filter:
                mean_calc_start_time  = time.perf_counter()
                self.means_data[f] = mean(f, self.cd[f])
                self.last_mean_calc_time = time.perf_counter() - mean_calc_start_time
            if self.run_strategy() is not None:
                self.theoretical_buy()

    def flow(self):
        self.get_new_data()
        self.check_positions()
        self.calc_balance()
        self.check_cutout()
        self.calc_balance()
        self.main_filter()
        self.bundle_mean_strategy_buy()
        self.calc_balance()

    def loop_flow(self):
        try:
            while True:
                self.currd += timedelta(minutes=1)
                self.flow()
                if datetime.now() - self.last_gui_update > timedelta(seconds=2):
                        self.iteration += 1
                        self.last_gui_update = datetime.now()
                        start_drawing_time = time.perf_counter()
                        self.gui.flow(self)
                        self.drawing_time = time.perf_counter() - start_drawing_time

                if self.currd >= datetime.now(timezone.utc) or self.curr_balance <= 0:
                    pickle.dump(self.position_history, open('position_history.p', 'wb'))
                    break
                if (self.currd - self.strd) % timedelta(days=14) == timedelta(0): 
                    logging.info(str(self.tp) +' |||  ' +  str((self.currd - self.strd)))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(str(e))
            print([exc_type, fname, exc_tb.tb_lineno])
            print("".join(traceback.format_tb(e.__traceback__)))
            self.gui.curses.endwin()
            input('Press any key to continue')

    