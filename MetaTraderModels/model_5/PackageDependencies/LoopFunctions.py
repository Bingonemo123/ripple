import io
import os
import sys

from datetime import datetime, timedelta

import numpy as np

from PackageDependencies import Timeout
from PackageDependencies.Means.meanv2.MeanFunctions import mean
from PackageDependencies.MetaTrader import connector
from PackageDependencies.Strategies import mathfc


class LoopUtilities():
    def __init__(self):
        self.strd = datetime.now()
        self.cd = {} # candledata = list of one week data 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
        self.trdesk = ["EURUSD", "GBPUSD", "USDJPY", "USDTHB", "USDZAR", "EURZAR", "GBPZAR", "GBPJPY"]
        # 3. Cutout
        self.lct = self.strd # last cutout time = time of last cutout
        self.tp = 0 # total profit
        self.id_index = 0 # id for positions
        self.ap = [] # active positions position data 
        '''(0.id, 1.name, 2.opening price, 3.open time, 4.amount(in money), 5.auto close, 6.leverage,7. amount(in lots), 8.mt_ticket)'''
        self.crp = {} # current price
        self.crpohlc = 1 # current price ohlc
        self.init_balance = Timeout.get_custom_balance(connector)
        self.curr_balance = self.init_balance # init_balance - active_position_buying_amount - closed_win_lose_amount (updated when new position is bought or active closed)
        self.free_balance = self.init_balance # curr_balance - active_positions_win_lose_amount 
        self.margin_balance = self.init_balance # curr_balance - active_positions_lose_amount
        self.safe_balance = self.init_balance # curr_balance  - safe_margin - active_positions_lose_amount 
        # safe-balance = curr_balance - Sum(loan) : | loan = pm - v | pm = v * l = a * op
        # margin_balance = curr_balance - Sum(am | if op > cp) : | am = bm + v | bm = cm - pm | cm = a * op
        # free_balance = curr_balance - Sum(am) : | am = bm + v | bm = cm - pm | cm = a * op
        self.leveg = 3000 # leverage
        self.position_history = {}

        self.maximum_var = [self.curr_balance, self.safe_balance, self.margin_balance, self.free_balance, len(self.ap)]
        self.minimum_var = [self.curr_balance, self.safe_balance, self.margin_balance, self.free_balance]
        self.autoclosed = 0
        self.marginclosed = 0
        self.cutoutclosed = 0
        self.cutoutindx = 0
        self.lastmean = {}

        self.last_graph_update = self.lct
        self.fake_file = io.StringIO()

        self.means_data = {}
        self.foundmark = None
        self.actdesk = []
        self.Filter = []

        for f in self.trdesk:
            self.get_rates(f)
           
    def get_rates(self, f):
        rates = Timeout.datamine(connector, f=f, frame=connector.TIMEFRAME_M1, t=self.strd, count=10080)
        rerates = np.zeros((len(rates), 8), dtype=float)
        for i in range(len(rates)):
            for x in range(8):
                rerates[i][x] = rates[i][x]
        self.cd[f] = rerates
        self.crp[f] = rates[-1][self.crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume

    def get_new_data(self):
        self.actdesk = []
        for f in self.trdesk:
            rates = Timeout.datamine(connector, f=f, frame=connector.TIMEFRAME_M1, t=datetime.now(), count=1)
            if rates[0][0] != self.cd[f][-1][0]:
                self.cd[f] = np.roll(self.cd[f], -1, axis=0)
                for x in range(8):
                    self.cd[f][-1][x] = rates[0][x]
                self.crp[f] = rates[-1][self.crpohlc] # current price : 0.time 1.open 2.high 3.low 4.close 5.tick_volume 6.spread 7.real_volume
                self.actdesk.append(f)

    def calc_balance(self):
        self.free_balance = self.curr_balance - sum([i[4]*i[6]*((self.crp[i[1]]/i[2]) - 1) + i[4] for i in self.ap])  # v * l ( cp/op - 1) + v
        self.margin_balance = self.curr_balance - sum([i[4]*i[6]*((self.crp[i[1]]/i[2]) - 1) + i[4] for i in self.ap if self.crp[i[1]] < i[2]])  # v * l ( cp/op - 1) + v
        self.safe_balance = self.curr_balance - sum([i[4]*(i[6] - 1) for i in self.ap])  # loan = pm - v | pm = v * l = a * op
 
    def check_positions(self):
        pmm = Timeout.custom_profit(connector)
        if isinstance(pmm, (str, Exception)):
            return pmm

        poshold_ticket = [position.ticket for position in pmm[2]]

        for pos in self.ap:
            if pos[8] not in poshold_ticket:
                closing_profit = pos[4] * pos[6] * ((self.crp[pos[1]]/pos[2]) - 1) + pos[4]   
                self.tp += closing_profit
                self.curr_balance += closing_profit
                self.position_history.get(pos[0]).update({'Close Time': datetime.now(), 'Close Price': self.crp[pos[1]], 'Profit': closing_profit, 'Closed by': 'Auto'}) 
                self.ap.remove(pos)

    def check_cutout(self):
        cutout = 4
        if datetime.now() - lct >= timedelta(hours=cutout):
            pmm = Timeout.custom_profit(connector)
            if isinstance(pmm, (str, Exception)):
                return pmm

            total_profit, total_margin, msg = pmm
            if total_profit > 0:
                self.cutoutclosed += len(self.ap)
                self.cutoutindx += 1
                lct = datetime.now()
                for position in msg:
                    clres = Timeout.custom_close(connector, position)
                    if clres is not True:
                        return clres

    def main_filter (self):
        delay = 8
        self.Filter = []

        pmm = Timeout.custom_profit(connector)
        if isinstance(pmm, (str, Exception)):
            return pmm
        total_profit, total_margin, msg = pmm

        for f in self.actdesk:
            if f in [pos.symbol for pos in msg]:
                continue
            for indx in self.position_history:
                if self.position_history[indx].get('Name') == f:
                    if (datetime.now() - self.position_history[indx].get('Buying_time', 0)) < timedelta(hours=delay):
                        break
            else:
                self.Filter.append(f)
        return self.Filter
    
    def run_strategy(self):
        pricelist = []
        leverages = []
        for f in self.Filter:
            price = Timeout.custom_price(connector, f)
            if not isinstance(price, (float, int)):
                return price
            fleverage = Timeout.custom_leverage(connector)
            if not isinstance(fleverage, (float, int)):
                return fleverage
            pricelist.append(price)
            leverages.append(fleverage)

        foundmark = mathfc.EZAquariiB(self.Filter, pricelist, self.means_data, leverages, self.safe_balance)
        if foundmark != None:
            self.name = foundmark[1][0]
            self.m = foundmark[1][1]
            self.n = foundmark[1][2]
            self.leverage = foundmark[1][3]
            ### 7. get name, m, n and leverage if available
            return foundmark[1] # name, m, n, leverage 

    def demo_buy(self):
        if self.safe_balance/ self.n < 1:
            self.amount = 1
        elif self.safe_balance/ self.n > 20000:
            self.amount = 20000
        else:
            self.amount = self.safe_balance/ self.n

        take_profit_value = ((self.m/self.leverage) + 1) * self.crp[self.name]

        if self.amount <= self.safe_balance:
            self.id_index += 1
            self.curr_balance -= self.amount
            if self.curr_balance < 0:
                pass
            else:
                ####### ORDER #######
                self.mt_order(self)
                if self.mt_verify(self) == True:
                    ####### ORDER #######
                    amount_tlots = self.amount * self.leverage / self.crp[self.name]# amount of theortical lots
                    self.ap.append([self.id_index, self.name, self.crp[self.name], datetime.now(), self.amount, take_profit_value, self.leverage, amount_tlots, self.mt_order_check.order])
                    self.position_history[self.id_index] = {'Id' : self.id_index,
                                    'Name' : self.name,
                                    'Opening_price' : self.crp[self.name],
                                    'Buying_time': datetime.now(),
                                    'Amount': self.amount,
                                    'TakeProfitValue': take_profit_value,
                                    'leverage': self.leverage,
                                    'Amount_tlots': amount_tlots,
                                    'Balance': self.curr_balance,
                                    'SafeBalance': self.safe_balance,
                                    'Mt Order Id': self.mt_order_check.order
                                } # add exam


    def mt_order(self):
        cpbh =  Timeout.custom_prebuy(connector, self.name)
        if not isinstance(cpbh, tuple):
            return cpbh

        point, volume_step, current_price, margin, volume_max = cpbh

        volume = self.amount / margin
        if volume > volume_max:
            volume = volume_max
        volume = (volume // volume_step) * volume_step

        closing_price =  ((self.m/self.leverage) + 1) * current_price
        closing_price = (closing_price // point ) * point
        if closing_price < current_price:
            closing_price = 0

        self.mt_request = {
                "action": connector.TRADE_ACTION_DEAL,
                "symbol": self.name,
                "volume": volume,
                "type": connector.ORDER_TYPE_BUY,
                "price": current_price,
                # "sl": 0,
                "tp": closing_price,
                "comment": f"Placed by model Model5",
                "type_time": connector.ORDER_TIME_GTC,
                "type_filling": connector.ORDER_FILLING_IOC,
        }

        self.mt_order_check = connector.order_send(self.mt_request)

    def mt_verify(self):
        if self.mt_order_check.comment == 'No prices':
            avvol = Timeout.custom_volmeter(connector, self.name)
            if not isinstance(avvol, (float, int)):
                return avvol
            self.mt_request['volume'] = avvol
            self.mt_order_check = connector.order_send(self.mt_request)
        
        if self.mt_order_check.comment == 'Invalid stops':
            del self.mt_request['tp']
            self.mt_order_check = connector.order_send(self.mt_request)

        if self.mt_order_check.comment == 'Market closed':
            return 'Market closed'

        if self.mt_order_check == connector.TRADE_RETCODE_DONE:
            return True

    def bundle_mean_strategy_buy(self):
        if self.safe_balance > 0:
            for f in self.Filter:
                self.means_data[f] = mean(f, self.cd[f])

            if self.run_strategy() is not None:
                self.demo_buy()

    def flow(self):
        self.get_new_data()
        self.check_positions()
        self.check_cutout()
        self.main_filter()
        self.bundle_mean_strategy_buy()

    def loop_flow(self):
        while True:
            try:
                self.flow()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(str(e))
                print([exc_type, fname, exc_tb.tb_lineno])
