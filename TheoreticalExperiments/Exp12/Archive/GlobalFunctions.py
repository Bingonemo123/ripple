from PackageDependencies.Constans import *

def calc_balance():
    global curr_balance, margin_balance, free_balance, safe_balance
    free_balance = curr_balance - sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) + i[4] for i in ap])  # v * l ( cp/op - 1) + v
    margin_balance = curr_balance - sum([i[4]*i[6]*((crp[i[1]]/i[2]) - 1) + i[4] for i in ap if crp[i[1]] < i[2]])  # v * l ( cp/op - 1) + v
    safe_balance = curr_balance - sum([i[4]*(i[6] - 1) for i in ap])  # loan = pm - v | pm = v * l = a * op

def close_pos(ids):
    global tp, curr_balance
    for i in ap:
        if i[0] == ids:
            closing_profit = i[4] * i[6] * ((crp[i[1]]/i[2]) - 1) + i[4]
            tp += closing_profit
            curr_balance += closing_profit
            position_history.get(ids).update({'Close Time': currd, 'Close Price': crp[i[1]], 'Profit': closing_profit, 'Closed by': 'Auto'})
            ap.remove(i)
            break
    calc_balance()

def close_positions(ap):
    global tp, curr_balance
    for i in ap:
        closing_profit = i[4] * i[6] * ((crp[i[1]]/i[2]) - 1) + i[4]
        tp += closing_profit
        curr_balance += closing_profit
        position_history.get(i[0]).update({'Close Time': currd, 'Close Price': crp[i[1]], 'Profit': closing_profit, 'Closed by': 'Cluster'})

    ap.clear()
    calc_balance()
