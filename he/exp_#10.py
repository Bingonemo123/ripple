# mathematical experiment 
import math
import numpy as np
import itertools as it

n = 3

def recur(k):
    if k == 2:
        return n-1
    else:
        return (k + 1)*(recur(k - 1)) - k*(k-1)/2

def brutlin( k):

    testn = 0
    for k in it.product([0, 1], repeat=n-1 + 2*(k - 1)):
        cs = 0
        for m in k:
            if m == 0:
                cs -= 1
            else:
                cs += 1
            if cs < 0:
                # print(k, 'Lose')
                break
            elif cs >= n:
                # print(k, 'Early win')
                break
        
        if cs == n -1:
            testn += 1
            # print(k, f'Candidate Number {testn}' )
        else:
            pass
            # print(k, 'Low or high')
    return testn


def lin(k):
    if k ==1:
        return 1
    elif k == 2:
        return n - 1
    lp = math.factorial(k + 1) * (n - 1) /6
    rp = sum([math.factorial(k + 1)* ((i - 1)*(i)/2) / math.factorial(i + 1) for i in range(3, k + 1)])
    return lp - rp


# s = 0
# k = 0
# while True:
#     onewayprob = (1/2)**(n + 2 * k)
#     print(onewayprob)
#     totalways = brutlin(k + 1)
#     print(totalways)
#     productprob = onewayprob * totalways
#     print(productprob)
#     s += productprob
#     k += 1
#     print(k, s)
#     input()

# total = 0
# win = 0

# while True:
#     f = 0
#     while True:
        
#         if np.random.choice([True, False]):
#             f += 1
#         else:
#             f -= 1

#         if f>= 3:
#             win += 1
#             break
            
#         elif f < 0:
#             break
#     total += 1

#     print(win, total, win/total)

for n in range(3, 10):
    print( n)

    for j in range(10):
        print(brutlin(j), end= ':')