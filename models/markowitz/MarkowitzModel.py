import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimization

# Stocks of the index
stocks = ['AAPL', 'WMT', 'TSLA', 'GE', 'AMZN', 'DB']

# Historical data - define Start and End dates
start_date = '2010-01-01'
end_date = '2022-01-01'


def download_data():
    # name of the stocks(key) - stocks values
    stock_data = {}

    for stock in stocks:
        ticker = yf.Ticker(stock)
        stock_data[stock] = ticker.history(start=start_date, end=end_date)['Close']

    return pd.DataFrame(stock_data)


def show_data(data):
    data.plot(figsize=(10, 5))
    plt.show()


if __name__ == '__main__':
    data_set = download_data()
    print(data_set)
    show_data(data_set)