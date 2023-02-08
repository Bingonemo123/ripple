"""Finding Trends with Convolution"""
import logging
import itertools
import pickle
import numpy as np
from scipy.stats import binom
from scipy import integrate

fx = np.loadtxt(r"Data\EURUSD\DAT_MT_EURUSD_M1_2019.csv",
                delimiter=",", dtype=str)

fx = fx[:, 5]
fx = fx.astype(np.float64)
fx = fx[:-1] < fx[1:]

logging.basicConfig(filename="c.log", encoding='utf-8', level=logging.DEBUG)


def parametergen():
    """generator
    generates all possibilites of (up down *) step by step
    and increase in size starting from r
    """
    try:
        raise OSError
        # r = pickle.load(open("r.pickle", "rb"))
    except (OSError, IOError) as e:
        r = 0
        pickle.dump(r, open("r.pickle", "wb"))
    while True:
        print("Trend Lenght", r)
        middlegen = itertools.product(["*", "↑", "↓"], repeat=r)
        for u in middlegen:
            for i in [0, 1]:
                prefixed = ["↑", "↓"][i] + "".join(u)
                postfixed = prefixed + "*↑"
                yield postfixed
        r += 1
        pickle.dump(r, open("r.pickle", "wb"))


def Spread(x):
    return 2*x - 1


def generateLibrary(l):
    '''Generetes Library occurences all possible Up and Downs in fx(historical Data)
    for example: if l = 3 and fx = [up, down, up, up, up, down, up, down, down]
    fx actuely must list of True and False boleans
    library will return {
        '↓↓↓' : 0, '↓↓↑': 0, '↓↑↓': 1, '↓↑↑': 1, 
        '↑↓↓': 1, '↑↓↑':2 , '↑↑↓': 1, '↑↑↑': 1 
    }
    '''
    g = itertools.product([True, False], repeat=l)
    resultLibrary = {}

    for v in g:
        v = np.array(v)
        LENGHTv = len(v)
        RERVSPREAD = Spread(np.flip(v))
        CONVOLVE = np.convolve(fx, RERVSPREAD)
        UNPAD = CONVOLVE[LENGHTv-1:(1-LENGHTv if LENGHTv > 1 else None)]
        v_count = sum(UNPAD >= sum(v))
        resultLibrary["".join(["↑" if x else "↓" for x in v])] = v_count
    return resultLibrary

if __name__ == "__main__":        
    Library = {} 
    y = parametergen()
    for u in y:
        SAMElengthLIBRARY = Library.get(len(u), False)  # contains occurence counts of all same lenght trends
        if not SAMElengthLIBRARY:
            SAMElengthLIBRARY = Library.setdefault(len(u), generateLibrary(len(u))) # generates library for lenght of trend


        Numerator = 0
        Denominator = 0

        for species in SAMElengthLIBRARY:
            for bit in range(len(species)-1):
                if u[bit] == "*":
                    continue
                elif u[bit] == species[bit]:
                    continue
                else:
                    break
            else:
                if species[-1] == "↑":
                    Numerator += SAMElengthLIBRARY[species]
                    Denominator += SAMElengthLIBRARY[species]
                else:
                    Denominator += SAMElengthLIBRARY[species]

        if Numerator/Denominator > 0.63235:
            print (u, Numerator, Denominator, f"E[r]: { (Numerator + 1)/ (Denominator + 2)}")
            input()

        if Numerator/Denominator > 0.63235 or Numerator/Denominator < 0.36765:
            def costume_binom(x):
                return binom.pmf(Numerator, Denominator, x) * (Denominator + 1)

            alt_hypo_perc = integrate.quad(costume_binom, 0.36765, 0.63235)
            if alt_hypo_perc[0] <= 0.05:
                # logging.info(" ".join([u,  f"{Numerator/Denominator:.2%}"]))
                print (u, Numerator, Denominator, f"E[r]: { (Numerator + 1)/ (Denominator + 2)}")


                print(f"Percentage of Alt hypothesis(True Randomness) {alt_hypo_perc} ")
