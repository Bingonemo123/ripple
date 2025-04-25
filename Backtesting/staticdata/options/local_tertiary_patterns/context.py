# Rewrite 
from ..tertiary_patterns.context import TertiaryController
import itertools
import numpy as np

class LocalTertiaryTrendsExtractor(TertiaryController):

    def extract_local_trends(self, f, rd=None, td=None):
        if rd is None:
            rd = self.raw_m1_csv
        if td is None:
            td = self.tertiary_m1
        trunc_raw_data = rd[len(f)-1:] # remove first unused bits of data from raw data
        features_idx = np.where(  # finds indicis of where features occur
                        self.sieve_library(
                            td, 
                            f)
                    )
        selector = self.time_stamps.reshape(
            self.time_stamps.size, 1) + features_idx 
        
        nanselector = np.where(selector < trunc_raw_data.size, True, np.nan)
        localselector = np.where(selector > (len(td) - len(f)), True, np.nan)
        raw_selected = np.take( trunc_raw_data, selector, mode='clip' ) # at most 32?
        local_selected = raw_selected * localselector
        raw_nan_selected = local_selected * nanselector
        diff_selected = raw_nan_selected - raw_selected[0]
        bin_nan_selected = ((diff_selected > 0) * nanselector) 
        # first element in total trends (second row) is count of all features
        return np.array([
                        np.nansum(bin_nan_selected, axis=1),
                        np.count_nonzero(
                                ~np.isnan(bin_nan_selected), 
                                axis=1)
                        ])

class LocalTertiaryLibrary(LocalTertiaryTrendsExtractor):

    def make_local_lib (self, l, rd=None):
        if rd is None:
            rd = self.raw_m1_csv

        result_library = {}

        for cursor_pointer in range(1, len(rd)):

            prime_rd = rd[:cursor_pointer]
            prime_td = self.into_tertiles(prime_rd)

            featuregen = itertools.product([1, 2, 4], repeat=l)
            for features in featuregen:
                local_timebased_findings = self.extract_local_trends(features,
                                                                   rd=rd,
                                                                   td=prime_td)

                if features not in result_library:
                    result_library[features] = local_timebased_findings
                else:
                    result_library[features] += local_timebased_findings
        return result_library


class LocalTertiaryLengthWiseSearch(LocalTertiaryLibrary):

    def search(self, filename=None, stdout=None):
        self.search_setup(filename)

        for pattern in self.tertiary_patterns:
            if len(pattern) > self.lib_length:
                self.lib_length += 1
                self.same_length_lib = self.make_local_lib(self.lib_length)
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
