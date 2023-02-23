import numpy as np
import itertools
from ..nary_patterns.context import NaryRawData
from scipy.stats import binom
from scipy import integrate
from .csv_writer import TertiaryCsvTrends

class TertiaryRawData(NaryRawData):

    time_stamps = np.array([
        0, 1, 5, 10, 15, 20, 
        30, 60, 120, 180, 240,
        300, 1440, 2880])

    def into_tertiles(self, a=None):
        if a is None:
            a = self.raw_m1_csv

        q1 = np.quantile(a, .33333)
        q2 = np.quantile(a, .66666)

        condlist = [a < q1,
                    (q1 <= a) & (a <= q2),
                    a > q2
                    ]

        return np.select(condlist, [1, 2, 4])
    
    def load_m1_csv(self, filename, column=5, delimiter=','):
        super().load_m1_csv(filename, column, delimiter)
        self.tertiary_m1 = self.into_tertiles(self.raw_m1_csv)
        return self.tertiary_m1
    
    def load_random(self, n=100):
        super().load_random(n)
        self.tertiary_m1 = self.into_tertiles(self.raw_m1_csv)
        return self.tertiary_m1

class TertiaryController(TertiaryRawData):

    upper_perc_limit = 0.63235
    lower_perc_limit = 0.36765

    def tertiary_patterngen(self, r=1):
        """ Generator
        generates all possibilites of tertiary patterns step by step
        and increase in size starting from r = 1
        0 - None, and others by binary composition
        7- Any from [1, 2, 4]
        """
        while True:
            middlegen = itertools.product(range(1, 8), repeat=r)
            for pattern in middlegen:
                yield pattern
            r += 1

    def sieve_library(self, a, features):
        palette = (a == features[0])
        for idx, f in enumerate(features[1:]):
            palette = palette[:-1] & (a[idx + 1:] == f)
        return palette
        
    def make_library(self, l , a=None):
        ''' Makes Dictionary numbers of all possibilities lenght l
        a is tertriary data [1, 2 , 4]
        '''
        if a is None:
            a = self.tertiary_m1
        featuregen = itertools.product([1, 2, 4], repeat=l)
        result_library = {} # TODO: store in l-dim array
        for features in featuregen:
            result_library[features] = self.sieve_library(a, features).sum()
        return result_library
    
    def extract_trends(self, f, rd=None, td=None):
        if rd is None:
            rd = self.raw_m1_csv
        if td is None:
            td = self.tertiary_m1
        trunc_raw_data = rd[len(f)-1:] # remove first unused bits of data from raw data
        features_idx = np.where(  # find indecis of where features accure
                        self.sieve_library(
                            td, 
                            f)
                    )
        selector = self.time_stamps.reshape(
            self.time_stamps.size, 1) + features_idx 
        nanselector = np.where(selector < trunc_raw_data.size, True, np.nan)
        raw_selected = np.take( trunc_raw_data, selector, mode='clip' ) # at most 32?
        raw_nan_selected = raw_selected * nanselector
        diff_selected = raw_nan_selected - raw_nan_selected[0]
        bin_nan_selected = ((diff_selected > 0) * nanselector) 
        # first element in total trends (second row) is count of all features
        return np.array([
                        np.nansum(bin_nan_selected, axis=1),
                        np.count_nonzero(
                                ~np.isnan(bin_nan_selected), 
                                axis=1)
                        ])


    def make_trend_lib (self, l, rd=None, td=None):
        # modify make_library to return feature location
        if rd is None:
            rd = self.raw_m1_csv
        if td is None:
            td = self.tertiary_m1

        featuregen = itertools.product([1, 2, 4], repeat=l)
        result_library = {} # TODO: store in l-dim array
        for features in featuregen:
            result_library[features] = self.extract_trends(features)
        return result_library
    
    def iscompatible(self, features, pattern):
        for f, p in zip(features, pattern):
                if f & p == 0:
                    return False
        else:        
            return True
    
    def search_setup(self):
        self.tertiary_patterns = self.tertiary_patterngen()
        self.same_length_lib = False
        self.lib_length = 0

        self.csv_tw = TertiaryCsvTrends()

    def continuous_search(self):
        # TODO: fast skip 0 summed patterns
        self.search_setup()

        for pattern in self.tertiary_patterns:
            if len(pattern) > self.lib_length:
                self.lib_length += 1
                self.same_length_lib = self.make_library(self.lib_length)

            pattern_sum = 0
            for features in self.same_length_lib:
                if self.iscompatible(features, pattern): 
                    pattern_sum += self.same_length_lib[features]

            print(pattern, pattern_sum)
            input()

    def stat_power_check(self, n, d):
        def costume_binom(x):
            return binom.pmf(n, d, x) * (d + 1)
        alt_hypo_perc = integrate.quad(costume_binom, 
                                        self.lower_perc_limit, 
                                        self.upper_perc_limit)
        if alt_hypo_perc[0] <= 0.05:
            return True, alt_hypo_perc
        else: 
            return False, alt_hypo_perc


    def continuous_trend_search(self, stdout=None):
        self.search_setup()

        for pattern in self.tertiary_patterns:
            if len(pattern) > self.lib_length:
                self.lib_length += 1
                self.same_length_lib = self.make_trend_lib(self.lib_length)
                print(f'-----lib length {self.lib_length} ---------')

            trend_count_timebased = np.zeros((2, self.time_stamps.size))
            for features in self.same_length_lib:
                if self.iscompatible(features, pattern):
                    trend_count_timebased += self.same_length_lib[features]
            total_trend_count = trend_count_timebased[1][0]
            trend_count_timebased = trend_count_timebased[:,1:]

            with np.errstate(divide='ignore', invalid='ignore'):
                trend_perc_timebased = trend_count_timebased[0]/trend_count_timebased[1]


            if np.any( 
                    (trend_perc_timebased>self.upper_perc_limit) |
                    (trend_perc_timebased<self.lower_perc_limit)
                    ):
                numerators = trend_count_timebased[0][
                    (trend_perc_timebased>self.upper_perc_limit) |
                    (trend_perc_timebased<self.lower_perc_limit)
                    ]
                denominators = trend_count_timebased[1][
                    (trend_perc_timebased>self.upper_perc_limit) |
                    (trend_perc_timebased<self.lower_perc_limit)
                    ]
                
                timeframes =  self.time_stamps[1:][
                    (trend_perc_timebased>self.upper_perc_limit) |
                    (trend_perc_timebased<self.lower_perc_limit)
                    ]
                
                for n, d, t in zip(numerators, denominators, timeframes):
                    accepted, power = self.stat_power_check(n, d)
                    if accepted:
                        self.csv_tw.save_trend(
                            {
                            'pattern': pattern, 
                             'numerator': n, 
                             'denominator': d, 
                             'power': power[0], 
                             'time frame': t, 
                             'occurred': total_trend_count
                            }
                        )
                        if stdout:
                            print('-------- Accepted ---------')
                            print(pattern, '\n', trend_perc_timebased)
                            print(trend_count_timebased)
                            print('power - ', power)
                            print('total trend count - ', total_trend_count)
                            print('accepted timeframe - ', t)
                            print(f'{n=}, {d=}, perc - {n/d:.2f}')

