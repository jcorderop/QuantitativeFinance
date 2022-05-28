import numpy.random as npr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from application.api.capm.CapmService import preparing_data_set
from poc.models.CommonModel import calculate_volatility, calculate_return_pct

NUM_OF_SIMULATIONS = 10000000


'''
S0  it is the initial value of the stock
T   time horizont
N   number of items to generate (days)
mu  mean of the random walk - risk-free rate
sigma   random fluctuation around the mean
        the size of the sigma is the size the fluctuation
'''
def stock_monte_carlo(S0, mu, sigma, N=365):
    result = []
    t = 1 # day by day
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
    simulation_data['mean'] = simulation_data.mean(axis=1)
    print(simulation_data)
    return simulation_data


def plot_simulation(simulation_data):
    plt.plot(simulation_data)
    plt.show()


def plot_simulation_mean(simulation_data):
    plt.plot(simulation_data['mean'])
    plt.show()


def result_price(simulation_data):
    print('Prediction for future stock price: $%0.2f' % simulation_data['mean'].tail(1))


if __name__ == '__main__':
    prices = preparing_data_set(['btc'], '2014-01-01', '2022-05-28', 'usd')
    cypto_price = float(prices.tail(1)['btc'])
    print("Price: ", cypto_price)
    mean = calculate_return_pct(prices)
    print("mean: ", mean)
    volatility = calculate_volatility(prices)
    print("Volatility: ", volatility)
    print(prices)
    simulation_data = stock_monte_carlo(cypto_price, mean, volatility)
    plot_simulation(simulation_data)
    plot_simulation_mean(simulation_data)
    result_price(simulation_data)