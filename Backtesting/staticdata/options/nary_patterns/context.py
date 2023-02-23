import numpy as np

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
