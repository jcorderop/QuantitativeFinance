import yfinance as yf
import pandas as pd

def download_data(stocks, start_date, end_date):
    # name of the stocks(key) - stocks values
    stock_data = {}

    for stock in stocks:
        ticker = yf.Ticker(stock)
        stock_data[stock] = ticker.history(start=start_date, end=end_date)['Close']
        print(stock_data)
    return pd.DataFrame(stock_data)