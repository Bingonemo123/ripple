# Ripple Journal

## Ripple 4.0

1.03.2023

- [ ] Remove bias from future tertiary data

18.02.2023

- [ ] Tertiary Patterns
- [ ] Correspond Tertiary pattern to upward or downward movement of market

08.02.2023

- [x] change parametergen to generate exact after pattens aka not only [pattern]*^ but rather [pattern]^
- [x] Test new parameters on 2019 EURUSD Data
- [x] continues Search Saves all preview length libraries determine if they are usefully and if not prevent them from saving
- [x] No powerful trend discovered max length: 10

03.02.2023

- sorted and cleaned package, better folder management
- [ ] Generate more broad pattern recognition
  - [ ] change parametergen to generate exact after pattens aka not only [pattern]*^ but rather [pattern]^

## Ripple_3.0

02.02.2034

- [x] load generated Trends in real.ipynb
- [ ] load Test Tick Data EURUSD 2020
- Detected Possible Flaw
  - loading csv and converting to array will give string not float type. Comparison between string may be by length not by number.
- [x] Convert Strings to floats
- [ ] Rerun trend finder with corrected floats
- [x] Checked parametergen, working correctly

23.01.2023

- [ ] load generated Trends in real.ipynb and test for errors

14.01.2023

- [x] Choose Tick and Period for UDpatterns recognition [ EURUSD whole 2019 year 1min ]
- [x] Download Ticks and Save Locally [Data\EURUSD\DAT_MT_EURUSD_M1_2019.csv]
- [x] Find Trends
  - [x] Choose alt_hypo_perc Threshold [0.05]
  - [x] Choose Trend Length Limit [10]
  - [x] Run trend_finder.py
  - [x] Count total trends found [8036]
  - [x] Check Everything
    - [x] find if there is reason why only trends with p < 0.36755 [till trend length 8 no trend with greater than 0.6 was detected - likely do to data itself]
- [ ] Test Trends
  - [x] Choose Ticks for testing [ EURUSD whole 2020 year 1min]
  - [x] Download Ticks and Save Locally
  - [ ] load generated Trends in real.ipynb and test for errors
