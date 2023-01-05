import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr
import pandas as pd
from scipy.stats import norm

from QuantitativeFinanceApi.application.api.common.QFLogger import QFLogger

logger = QFLogger(logger_name=__name__).get_logger()

NUM_OF_SIMULATIONS = 10000


NUM_TRADING_DAYS = 252

'''
S0  it is the initial value of the stock
T   time horizont
N   number of items to generate (days)
mu  mean of the random walk - risk-free rate
sigma   random fluctuation around the mean
        the size of the sigma is the size the fluctuation
'''
def stock_monte_carlo(S0, mu, sigma, N=365, num_simulations=NUM_OF_SIMULATIONS):
    logger.info("S0:    {}".format(S0))
    logger.info("mu:    {}".format(mu))
    logger.info("sigma: {}".format(sigma))

    result = []
    t = 1  # day by day
    # number of simulations - possible S(t) realization (of the process)
    for _ in range(num_simulations):
        prices = [S0]
        for _ in range(N):
            simulated_price = prices[-1] * np.exp((mu - 0.5 * sigma ** 2) * t + sigma * np.random.normal())
            prices.append(simulated_price)
        result.append(prices)
    simulation_data = pd.DataFrame(result)
    # the given columns will contain the tie series for a given simulation (transpose)
    simulation_data = simulation_data.T
    # mean simulation
    logger.info(simulation_data)
    return simulation_data


def plot_simulation(simulation_data):
    plt.plot(simulation_data)
    plt.show()


def plot_simulation_mean(simulation_data):
    simulation_data['mean'] = simulation_data.mean(axis=1)
    plt.plot(simulation_data['mean'])
    plt.show()


def result_price(ticker, simulation_data):
    price = float(simulation_data.mean(axis=1).tail(1))
    logger.info('ticker: {}, future price: {:.2f}'.format(ticker, price))
    return price


# Compute Logarithmic Daily Returns
def log_returns(data):
    #return np.log(1 + data.pct_change())
    return data.pct_change()


# Calculate Drift
def drift_calc(data):
    lr = log_returns(data)
    u = lr.mean()
    var = lr.var()
    drift = u-(0.5*var)
    try:
        return drift.values[0]
    except:
        logger.warning('WARNING....', drift_calc)
        return drift


# Compute Daily Returns
def daily_returns(data, days, iterations):
    ft = drift_calc(data)
    try:
        stv = log_returns(data).std().values
    except:
        stv = log_returns(data).std()
        logger.warning('WARNING.... daily_returns')
    dr = np.exp(ft + stv * norm.ppf(np.random.rand(days, iterations)))
    return dr


def calc_sigma(data_temp):
    data = data_temp.copy()
    data['diff'] = log_returns(data)
    data['sqrt'] = data['diff'] ** 2
    sigma = np.sqrt(data['sqrt'].mean())
    return sigma


def monte_carlo_price_simulation(ticker,
                                 data_set,
                                 future_days,
                                 num_simulations=NUM_OF_SIMULATIONS):
    close_price = float(data_set.tail(1))
    log_return = log_returns(data_set)
    mean = log_return.mean()
    sigma = calc_sigma(data_set)
    simulation_data = stock_monte_carlo(close_price, mean, sigma, future_days, num_simulations)
    #plot_simulation(simulation_data)
    #plot_simulation_mean(simulation_data)
    future_price = result_price(ticker, simulation_data)
    return '{:.8f}'.format(close_price), '{:.8f}'.format(future_price)


# https://medium.com/analytics-vidhya/monte-carlo-simulations-for-predicting-stock-prices-python-a64f53585662
# https://github.com/eliasmelul/finance_portfolio
if __name__ == '__main__':
    '''
    monte_carlo_price_simulation(ticker='btc',
                                 from_date='2010-01-01',
                                 to_date='2022-06-14',
                                 quote_currency='usd',
                                 future_date=365)
    '''