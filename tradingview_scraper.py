# -*- coding: utf-8 -*-
"""
Created on Wed May 19 00:07:36 2021

@author: HP
"""

from tradingview_ta import TA_Handler, Interval, Exchange


def speedometer(market):
    handler = TA_Handler(
        symbol=market,
        exchange=Exchange.FOREX,
        screener="forex",
        interval=Interval.INTERVAL_1_DAY,
        timeout=None
    )
    analysis = handler.get_analysis()
    if analysis.summary.get('RECOMMENDATION') in ['STRONG_SELL', 'SELL']:
        return False
    else:
        return True