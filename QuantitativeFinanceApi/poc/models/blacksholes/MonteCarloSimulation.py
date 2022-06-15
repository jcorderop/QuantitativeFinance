import math

import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr
import pandas as pd
import seaborn as sns
from scipy.stats import norm

from QuantitativeFinanceApi.application.api.capm.CapmService import preparing_data_set

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
def stock_monte_carlo(S0, mu, sigma, N=365):
    print("S0: ", S0)
    print("mu: ", mu)
    print("sigma: ", sigma)

    result = []
    t = 1  # day by day
    # number of simulations - possible S(t) realization (of the process)
    for _ in range(NUM_OF_SIMULATIONS):
        prices = [S0]
        for _ in range(N):
            simulated_price = prices[-1] * np.exp((mu - 0.5 * sigma ** 2) * t + sigma * np.random.normal())
            prices.append(simulated_price)
        result.append(prices)
    simulation_data = pd.DataFrame(result)
    # the given columns will contain the tie series for a given simulation (transpose)
    simulation_data = simulation_data.T
    # mean simulation
    print(simulation_data)
    return simulation_data


def plot_simulation(simulation_data):
    plt.plot(simulation_data)
    plt.show()


def plot_simulation_mean(simulation_data):
    simulation_data['mean'] = simulation_data.mean(axis=1)
    plt.plot(simulation_data['mean'])
    plt.show()


def result_price(simulation_data):
    print('Prediction for future stock price: $%0.2f' % simulation_data['mean'].tail(1))


# Compute Logarithmic Daily Returns
def log_returns(data):
    #return np.log(1 + data.pct_change())
    return data.pct_change()


def log_returns2(data):
    # shifting the data means first calculation will be NaN
    log_daily_return = np.log(data / data.shift(1))
    # return from second date
    return log_daily_return[1:]

# Calculate Drift
def drift_calc(data):
    lr = log_returns(data)
    u = lr.mean()
    var = lr.var()
    drift = u-(0.5*var)
    try:
        return drift.values[0]
    except:
        print('WARNING....', drift_calc)
        return drift

# Compute Daily Returns
def daily_returns(data, days, iterations):
    ft = drift_calc(data)
    try:
        stv = log_returns(data).std().values
    except:
        stv = log_returns(data).std()
        print('WARNING.... daily_returns')
    dr = np.exp(ft + stv * norm.ppf(np.random.rand(days, iterations)))
    return dr


# https://www.fool.com/knowledge-center/how-to-calculate-annualized-volatility.aspx
def volatility_calc(data):
    lr = log_returns(data)
    daily_std = np.std(lr)
    # annualized daily standard deviation
    std = daily_std * math.sqrt(NUM_TRADING_DAYS)
    return float(std)


def volatility_calc2(data):
    lr = log_returns(data)
    daily_std = np.std(lr)
    # annualized daily standard deviation
    std = log_returns(data).std()# * NUM_TRADING_DAYS ** 0.5 # volatility
    return float(std)

def volatility_calc3(data, field='Close'):
    print('---------------------------------')
    lr = log_returns(data)
    variance = data.var()
    print('variance:', variance)
    print('mean:', data.mean())
    sigma = np.sqrt(variance)
    print('---------------------------------')
    return float(sigma)


def cagr_calc(data, field='Close'):
    time_elapsed = (data.index[-1] - data.index[0]).days
    total_growth = (data[field][-1] / data[field][1])
    number_of_years = time_elapsed / 365.0
    cagr = total_growth ** (1 / number_of_years) - 1
    return cagr


def calc_sigma(data_temp,  field='Close'):
    data = data_temp.copy()
    data['diff'] = log_returns(data)
    data['sqrt'] = data['diff'] ** 2
    sigma = np.sqrt(data['sqrt'].mean())
    print("std:", sigma)
    return sigma


# https://medium.com/analytics-vidhya/monte-carlo-simulations-for-predicting-stock-prices-python-a64f53585662
# https://github.com/eliasmelul/finance_portfolio
if __name__ == '__main__':
    field = 'btc'
    data = preparing_data_set([field], '2010-01-01', '2022-05-29', 'usd')
    close_price = float(data.tail(1)[field])

    #field = 'Close'
    #data = download_data_single('AAPL', '2010-01-01', '2022-05-01')
    #close_price = float(data.tail(1)['Close'])

    log_return = log_returns(data)
    mean = log_return.mean().values[0]


    log_return2 = log_returns2(data)
    mean2 = log_return2.mean().values[0]
    # Plot
    sns.distplot(log_return.iloc[1:])  # histplot
    plt.xlabel("Daily Return")
    plt.ylabel("Frequency")
    plt.show()

    #drift = drift_calc(data)
    volatility = volatility_calc(data)
    volatility2 = volatility_calc2(data)
    volatility3 = volatility_calc3(data, field)
    cagr = cagr_calc(data, field)

    print("Price: ", close_price)
    #print("Drift: ", drift)
    print("Mean: ", mean)
    print("Mean2: ", mean2)
    print("Volatility: ", volatility)
    print("Volatility2: ", volatility2)
    print("Volatility3: ", volatility3)

    sigma = calc_sigma(data, field)
    print("Volatility4: ", sigma)

    print("cagr (mean returns) : ", str(round(cagr, 4)))
    print("std_dev (standard deviation of return : )", str(round(volatility2, 4)))

    #simulation_data = stock_monte_carlo(113.17, 0.0002, 0.01)
    '''volatility2 alternatively'''
    simulation_data = stock_monte_carlo(close_price, mean, sigma )
    plot_simulation(simulation_data)
    plot_simulation_mean(simulation_data)
    result_price(simulation_data)

