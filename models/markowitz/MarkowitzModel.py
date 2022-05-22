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

# on average there are 252 trading days
NUM_TRADING_DAYS = 252

# on average there are 365 calendar days
NUM_CALENDAR_DAYS = 365

# It will generate random w (different portfolios)
NUM_PORTFOLIOS = 10000

def download_data():
    # name of the stocks(key) - stocks values
    stock_data = {}

    for stock in stocks:
        ticker = yf.Ticker(stock)
        stock_data[stock] = ticker.history(start=start_date, end=end_date)['Close']

    return pd.DataFrame(stock_data)


def show_data(data_set):
    print('Data set:')
    print(data_set)
    data_set.plot(figsize=(10, 5))
    plt.show()


# log daily return
# S(t+1) / S(t)
# NORMALIZATION - to measure all variables in comparable metrics
def calculate_return(data_set):
    # shifting the data means first calculation will be NaN
    log_daily_return = np.log(data_set / data_set.shift(1))
    # return from second date
    return log_daily_return[1:]


# instead of daily metric we can to calculate them by period
def show_statistics(data_set_returns, period):
    print('Data set - mean:')
    print(calculate_mean_by_period(data_set_returns, period))

    print('Data set - covariance:')
    print(calculate_covariance_by_period(data_set_returns, period))


def calculate_mean_by_period(data_set_returns, period):
    return data_set_returns.mean() * period


def calculate_covariance_by_period(data_set_returns, period):
    return data_set_returns.cov() * period


def show_portfolio_statistics(data_set_returns, weights, period):
    print('Expected portfolio mean (return): ', calculate_portfolio_return(data_set_returns, weights, period))
    print('Expected portfolio volatility (standard deviation): ', calculate_portfolio_volatility(data_set_returns, weights, period))


# Expected portfolio mean (return)
def calculate_portfolio_return(data_set_returns, weights, period):
    return np.sum(data_set_returns.mean() * weights) * period


# Expected portfolio volatility (standard deviation)
def calculate_portfolio_volatility(data_set_returns, weights, period):
    return np.sqrt(np.dot(weights.T, np.dot(data_set_returns.cov() + period, weights)))


def generate_portfolios(data_set_returns, period):
    portfolio_weights = []
    portfolio_mean = []
    portfolio_risk = []

    for _ in range(NUM_PORTFOLIOS):
        w = np.random.random(len(stocks))
        # normalize to 1
        w /= np.sum(w)
        portfolio_weights.append(w)
        portfolio_mean.append(calculate_portfolio_return(data_set_returns, w, period))
        portfolio_risk.append(calculate_portfolio_volatility(data_set_returns, w, period))

    return np.array(portfolio_weights), np.array(portfolio_mean), np.array(portfolio_risk)


def show_portfolios(portfolio_mean, portfolio_risk):
    plt.figure(figsize=(10, 6))
    plt.scatter( portfolio_risk, portfolio_mean, c=portfolio_mean/portfolio_risk, marker='o')
    plt.grid(True)
    plt.xlabel("Expected Volatility")
    plt.ylabel("Expected Return")
    plt.colorbar(label="Sharp Ratio")
    plt.show()


if __name__ == '__main__':
    print('Loading data...')
    data_set = download_data()

    print('Calculating return...')
    log_daily_return = calculate_return(data_set)
    print('Showing statistics from return...')
    show_statistics(log_daily_return, NUM_TRADING_DAYS)

    print('Generating random portfolios...')
    portfolio_weights, portfolio_mean, portfolio_risk = generate_portfolios(log_daily_return, NUM_TRADING_DAYS)
    print('Plotting portfolios...')
    show_portfolios(portfolio_mean, portfolio_risk)

    #print('Plotting data-set...')
    #show_data(data_set)