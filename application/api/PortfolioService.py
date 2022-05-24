import time

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from application.api.Constants import DateFormats
from application.api.coinGecko.CoinGeckoApi import CoinGeckoApi
from application.api.model.markowitz.MarkowitzModelApi import MarkowitzModelApi

CRYPTO_TICKERS = ['btc', 'eth', 'bnb', 'sol', 'luna', 'xrp',
                  'leo', 'kcs', 'ftm', 'midas', 'ftt',
                  'cro', 'cake', 'shib', 'ada', 'avax',
                  'trx', 'ltc', 'matic', 'okb', 'klay']

FROM_DATE = '2017-01-01'
TO_DATE = '2022-01-01'

QUOTE_CURRENCY = 'usd'

NUM_TRADING_DAYS = 365


def loading_historical_data(list_of_tickers, from_date, to_date, quote_currency):
    papi = CoinGeckoApi(quote_currency)
    data_series = {}
    for ticker in list_of_tickers:
        data_series[ticker] = papi.get_historical_prices(ticker, from_date, to_date)
        time.sleep(2.5)
    return pd.DataFrame(data_series)


def show_data(data_set):
    print('Data set:')
    print(data_set)
    data_set.plot(figsize=(10, 5))
    plt.show()


def portfolio_calculation(data_set, period):
    mmapi = MarkowitzModelApi(data_set, period)
    mmapi.calculate_return()
    mmapi.create_portfolios()
    mmapi.calculate_optimized_portfolio()


def calculate_portfolio():
    data_set = loading_historical_data(CRYPTO_TICKERS, FROM_DATE, datetime.now().strftime(DateFormats.date_format), QUOTE_CURRENCY)
    print('Plotting data-set...')
    show_data(data_set)

    portfolio_calculation(data_set, NUM_TRADING_DAYS)


if __name__ == '__main__':
    calculate_portfolio()