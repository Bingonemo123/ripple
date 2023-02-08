import numpy as np
import itertools
from scipy.stats import binom
from scipy import integrate

class BinaryRawData:

    def __init__(self):
        pass

    def load_m1_csv(self, filename, column=5, delimiter=","):
        fx = np.loadtxt(filename, delimiter=delimiter, dtype=str)
        fx = fx[:, column] # get 5th column of data
        fx = fx.astype(np.float64)
        self.m1_csv = fx[:-1] < fx[1:]

        return self.m1_csv


class BinaryController(BinaryRawData):

    def __init__(self):
        pass

    def binarypatterngen(self, r=0):
        """generator
        generates all possibilites of (up down *) patterns step by step
        and increase in size starting from r
        """
        while True:
            yield ['trend lenght', r + 2]
            middlegen = itertools.product(["*", "↑", "↓"], repeat=r)
            for u in middlegen:
                for i in [0, 1]:
                    prefixed = ["↑", "↓"][i] + "".join(u)
                    postfixed = prefixed + "↑"
                    yield postfixed
            r += 1

    @staticmethod
    def Spread(x):
        return 2*x - 1

    def generateLibrary(self, l):
        '''Generetes Library occurences all possible Up and Downs in fx(historical Data)
        for example: if l = 3 and fx = [up, down, up, up, up, down, up, down, down]
        fx actuely must list of True and False boleans
        library will return {
            '↓↓↓' : 0, '↓↓↑': 0, '↓↑↓': 1, '↓↑↑': 1, 
            '↑↓↓': 1, '↑↓↑':2 , '↑↑↓': 1, '↑↑↑': 1 
        }

        Warning: very hardvare intensive
        '''
        g = itertools.product([True, False], repeat=l)
        resultLibrary = {}

        for v in g:
            v = np.array(v)
            LENGHTv = len(v)
            RERVSPREAD = self.Spread(np.flip(v))
            CONVOLVE = np.convolve(self.m1_csv, RERVSPREAD)
            UNPAD = CONVOLVE[LENGHTv-1:(1-LENGHTv if LENGHTv > 1 else None)]
            v_count = sum(UNPAD >= sum(v))
            resultLibrary["".join(["↑" if x else "↓" for x in v])] = v_count
        return resultLibrary
    
    def patterncompatibleNDSearch(self, Library, pattern):
        Numerator = 0
        Denominator = 0

        for species in Library:
            for bit in range(len(species)-1):
                if pattern[bit] == "*":
                    continue
                elif pattern[bit] == species[bit]:
                    continue
                else:
                    break
            else:
                if species[-1] == "↑":
                    Numerator += Library[species]
                    Denominator += Library[species]
                else:
                    Denominator += Library[species]
        
        return Numerator, Denominator


    
    def continuousSearch(self):
        '''Searches for patterns starting with lenght 1

        Generates feature Library for n lenght pattern
        than 
        
        '''

        self.binaryfeatures = self.binarypatterngen()
        self.SAMElengthLIBRARY = False
        for binarypattern in self.binaryfeatures:
            if binarypattern[0] == 'trend lenght':
                # generates library for lenght of trend
                print(f'Generating Library for Patterns Lenght: {binarypattern[1]}')
                self.SAMElengthLIBRARY = self.generateLibrary(binarypattern[1])  # contains occurence counts of all same lenght trends
                continue

            Numerator, Denominator = self.patterncompatibleNDSearch(self.SAMElengthLIBRARY, binarypattern)

            # ----------- printing --------------------- #

            if Numerator/Denominator > 0.63235 or Numerator/Denominator < 0.36765:
                def costume_binom(x):
                    return binom.pmf(Numerator, Denominator, x) * (Denominator + 1)

                alt_hypo_perc = integrate.quad(costume_binom, 0.36765, 0.63235)
                if alt_hypo_perc[0] <= 0.05:
                    # logging.info(" ".join([u,  f"{Numerator/Denominator:.2%}"]))
                    print('-------- Accepted ---------')
                else: 
                    print('--------- Not Enough Power ----------')

                print (binarypattern, Numerator, Denominator, f"E[r]: { (Numerator + 1)/ (Denominator + 2)}")
                print(f"Percentage of Alt hypothesis(True Randomness) {alt_hypo_perc} ")
