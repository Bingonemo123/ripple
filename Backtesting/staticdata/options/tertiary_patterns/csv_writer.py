import time
import os
from pathlib import Path
import csv

class TertiaryCsvTrends:

    save_dir = Path('GeneratedData/options')
    filetype = '.csv'

    def __init__(self, filename=None, fieldnames=None) -> None:
        if filename is None:
            filename = 'trends'
            filename += time.strftime("%Y%m%d")

        if fieldnames is None:
            self.fieldnames= ['pattern', 
                             'numerator', 
                             'denominator', 
                             'power', 
                             'time frame', 
                             'occurred']
        
        self.filepath = self.check_increase(filename)
        self.writeheader()

    def writeheader(self):
        with open(self.filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()

    def check_increase(self, fn):
        i = 0
        while os.path.exists((self.save_dir/
                                f'{fn}_{i}').with_suffix(self.filetype)):
            i += 1
        return (self.save_dir/f'{fn}_{i}').with_suffix(self.filetype)
 
    def save_trend(self, tdata=None, **kwargs):
        if isinstance(tdata, dict):
            with open(self.filepath, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)

                writer.writerow(tdata)
