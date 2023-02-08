
import datetime
class M ():
    def __init__ (self):
        self.curr_balance = 99

        self.crp = {'EURUSD': 1.20023, 'GBPUSD': 1.35065, 'USDJPY': 112.594, 'USDTHB': 32.549, 'USDZAR': 12.333, 'EURZAR': 14.81544, 'GBPZAR': 16.66947, 'GBPJPY': 151.969}

        self.ap  =[ [1, 'GBPJPY', 152.1, datetime.datetime(2018, 1, 2, 0, 0), 1, None, 100, 0.6574621959237344]]
        # (0.id, 1.name, 2.opening price, 3.open time, 4.amount(in money), 5.auto close, 6.leverage,7. amount(in lots), 8.mt_ticket)

    def calc_balance(self):
            self.free_balance = self.curr_balance + sum([i[4]*i[6]*((self.crp[i[1]]/i[2]) - 1) + i[4] for i in self.ap])  # v * l ( cp/op - 1) + v
            self.margin_balance = self.curr_balance + sum([i[4]*i[6]*((self.crp[i[1]]/i[2]) - 1) + i[4] for i in self.ap if self.crp[i[1]] < i[2]])  # v * l ( cp/op - 1) + v
            self.safe_balance = self.curr_balance - sum([i[4]*(i[6] - 1) for i in self.ap])  # loan = pm - v | pm = v * l = a * op



m = M()
m.calc_balance()
print(m.margin_balance)
