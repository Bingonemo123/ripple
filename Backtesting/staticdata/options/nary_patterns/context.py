import numpy as np
from random import gauss, seed
from math import sqrt, exp

class NaryRawData:

    def load_m1_csv(self, filename, column=5, delimiter=','):
        fx = np.loadtxt(filename, delimiter=delimiter, dtype=str)
        fx = fx[:, column]
        fx = fx.astype(np.float64)
        self.raw_m1_csv = fx
        return self.raw_m1_csv

    def load_random(self, n=100):
        self.raw_m1_csv = np.random.random(n)
        return self.raw_m1_csv

    def load_monte_carlo(self, n=100):
        fx = [1,]

        for y in range(n):
            fx.append(
                fx[-1] * (1 + np.random.normal())
                )

        self.raw_m1_csv = np.array(fx)   
        return self.raw_m1_csv
    
    def create_GBM(self, s0, mu, sigma):
        """
        Generates a price following a 
        geometric brownian motion process 
        based on the input of the arguments:
        - s0: Asset inital price.
        - mu: Interest rate expressed annual terms.
        - sigma: Volatility expressed annual terms. 
        """
        st = s0
        def generate_value():
            nonlocal st

            st *= exp(
                    (mu - 0.5 * sigma ** 2) *
                    (1. / 365.) + sigma * sqrt(1./365.) * 
                    gauss(mu=0, sigma=1)
            )

            return st
        
        return generate_value


    def load_gbm(self, n=100, s0=100, mu=0, sigma=0.05):
        gbm = self.create_GBM(s0, mu, sigma)

        st_list = []
        for _ in range(n):

            st = gbm()

            st_list.append(st)

        self.raw_m1_csv = np.array(st_list)   
        return self.raw_m1_csv

        
