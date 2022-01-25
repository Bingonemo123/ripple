from finviz.screener import Screener
from yahoofinancials import YahooFinancials
from datetime import date, timedelta

def volatility():

    filters = ['exch_nasd', 'idx_sp500']  # Shows companies in NASDAQ which are in the S&P500
    stock_list = Screener(table='Performance', order='-volatility1w')

    return [x.get('Ticker') for x in stock_list]



def past_history(ticker):
    yahoo_financials = YahooFinancials(ticker)
    historical_stock_prices = yahoo_financials.get_historical_price_data((date.today() - timedelta(days=30)).isoformat(),
     date.today().isoformat(), 'daily')

    for x in historical_stock_prices.get(ticker).get('prices'):
        if x.get('high') >  historical_stock_prices.get(ticker).get('prices')[-1].get('high'):
            return True
            break

    else:
        return False


