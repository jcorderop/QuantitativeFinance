import numpy as np


def calculate_return_log(prices):
    # calculate daily logarithmic return
    prices['returns'] = (np.log(prices /prices.shift(-1)))
    return prices.returns.mean()


def calculate_return_pct(prices):
    # calculate daily logarithmic return
    prices['returns'] = prices.pct_change()
    return float(prices.returns.mean())


def calculate_volatility(prices):
    # calculate daily standard deviation of returns
    daily_std = np.std(prices.returns)
    # annualized daily standard deviation
    # 252 trading days
    # Notice that square root is the same as **.5, which is the power of 1/2.
    prices['volatility'] = daily_std * 252 ** 0.5 # volatility
    std = daily_std * 252 ** 0.5 # volatility
    return float(std)