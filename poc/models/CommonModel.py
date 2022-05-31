import yfinance as yf
import pandas as pd
import numpy as np


def download_data_common(stocks, start_date, end_date):
    # name of the stocks(key) - stocks values
    stock_data = {}

    for stock in stocks:
        ticker = yf.Ticker(stock)
        stock_data[stock] = ticker.history(start=start_date, end=end_date)['Close']
        print(stock_data)
    return stock_data


def download_data(stocks, start_date, end_date):
    json_prices = download_data_common(stocks, start_date, end_date)
    return pd.DataFrame(json_prices)


def download_data_single(stock_symbol, start_date, end_date):
    json_prices = download_data_common([stock_symbol], start_date, end_date)
    prices = pd.DataFrame(json_prices[stock_symbol])
    return pd.DataFrame(prices)


def calculate_return_log(prices):
    # calculate daily logarithmic return
    prices['returns'] = (np.log(prices /
                                prices.shift(-1)))
    return prices.returns.mean()


def calculate_return_pct(prices):
    # calculate daily logarithmic return
    prices['returns'] = prices.pct_change()
    return float(prices.returns.mean())


def calculate_volatility(prices):
    # calculate daily standard deviation of returns
    daily_std = np.std(prices.returns)
    # annualized daily standard deviation
    prices['volatility'] = daily_std * 252 ** 0.5 # volatility
    std = daily_std * 252 ** 0.5 # volatility
    return float(std)