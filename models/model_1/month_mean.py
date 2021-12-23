

import json
import statistics
import time

import tqdm
from iqoptionapi.stable_api import IQ_Option

connector = IQ_Option("ww.bingonemo@gmail.com", "JF*#3C5va&_NDqy")
connector.connect()

seconds_in_month = 2_592_000
max_dict = 1000
ALL_Asset = connector.get_all_open_time()
frx = [x for x in ALL_Asset['forex'] if ALL_Asset['forex'][x].get('open')]
crpt = [x for x in ALL_Asset['crypto'] if ALL_Asset['crypto'][x].get('open')]
iqcomb = frx + crpt
result = []
for f in tqdm.tqdm(iqcomb):
    if f not in connector.get_all_ACTIVES_OPCODE():
        continue
    candles = connector.get_candles(f, 3600, max_dict, time.time())
    mean = statistics.mean([x.get('close') for x in candles])
    tqdm.tqdm.write(str((f, mean)))
    result.append(
        ((f[:3], f[3:6]), mean)
    )


json.dump(result, open(
    r'C:\Users\HP\Documents\repos\Ripple_3.0\models\model_1\month_means.json', 'w'))
