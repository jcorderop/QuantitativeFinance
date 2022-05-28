import numpy.random as npr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from poc.models.CommonModel import download_data, download_data_single, calculate_volatility


class OptionPricing:

    '''
    S0  it is the initial value of the stock
    E   strike price
    T   time horizont (time to maturity or expiry)
    rf  risk-free rate
    sigma   random fluctuation around the mean (volatility or standard deviation)
            the size of the sigma is the size the fluctuation
    iterations  what is needed for the monte-carlo simulation
    '''
    def __init__(self, S0, E, T, rf, sigma, iterations):
        self.S0 = S0
        self.E = E
        self.T = T
        self.rf = rf
        self.sigma = sigma
        self.iterations = iterations

    def call_option_simulation(self):
        # 2 columns
        # fist with 0s => pay off function => max(0, S-E) for call option
        # second column will store the payoff
        option_data = np.zeros([self.iterations, 2])

        # Wiener process
        # dimensions: 1 dimensional array with as many items as the iterations
        # np.random.normal = 0
        # 1 is the variance or standard deviation
        # with one row and columns as iterations
        rand = np.random.normal(0, 1, [1, self.iterations])
        print("rand:")
        print(rand)

        t = 1 # day by day
        # simulation equation for the S(t) for the price at T (maturity)
        simulated_price = self.S0 * np.exp(self.T * (self.rf - 0.5 * self.sigma ** 2) * t + self.sigma * np.sqrt(self.T) * rand)
        print("simulated_price:")
        print(simulated_price)

        # calculate S-E because it is needed to calculate the max(S-E, 0)
        option_data[:, 1] = simulated_price - self.E
        print("option_data:")
        print(option_data)

        # average for the Monte-Carlo simulation
        # max returns => the max(0, S-E) according to the formula
        average = np.sum(np.amax(option_data, axis=1)) / float(self.iterations)
        print("average:")
        print(average)

        # apply the discount factor => exp(-rT) => to calculate the today's price
        option_price = np.exp(-1.0 * self.rf * self.T) * average
        print("Call Option Price: ", option_price)
        return option_price


    def put_option_simulation(self):
        # 2 columns
        # fist with 0s => pay off function => max(E-S, 0) for put option
        # second column will store the payoff
        option_data = np.zeros([self.iterations, 2])

        # Wiener process
        # dimensions: 1 dimensional array with as many items as the iterations'
        # np.random.normal = 0
        # 1 is the variance or standard deviation
        # with one row and columns as iterations
        rand = np.random.normal(0, 1, [1, self.iterations])
        print("rand:")
        print(rand)

        t = 1 # day by day
        # simulation equation for the S(t) for the price at T (maturity)
        simulated_price = self.S0 * np.exp(self.T * (self.rf - 0.5 * self.sigma ** 2) * t + self.sigma * np.sqrt(self.T) * rand)
        print("simulated_price:")
        print(simulated_price)

        # calculate S-E because it is needed to calculate the max(E-S, 0)
        option_data[:, 1] = self.E - simulated_price
        print("option_data:")
        print(option_data)

        # average for the Monte-Carlo simulation
        # max returns => the max(E-S, 0) according to the formula
        average = np.sum(np.amax(option_data, axis=1)) / float(self.iterations)
        print("average:")
        print(average)

        # apply the discount factor => exp(-rT) => to calculate the today's price
        option_price = np.exp(-1.0 * self.rf * self.T) * average
        print("Put Option Price: ", option_price)
        return option_price

if __name__ == '__main__':
    #model = OptionPricing(100, 100, 1, 0.05, 0.2, 10000000)
    stock_name = 'IBM'
    prices = stock = download_data_single(stock_name, '2010-01-01', '2020-01-01')
    stock_price = float(prices.tail(1)['Close'])
    print("Stock price: ", stock_price)
    strike = stock_price * 1
    print("Strike at 100%: ", strike)
    expiry = 1
    print("Expiry 1y: ", 1)
    risk_free_rate = 0.009 # switzerland
    print("Expiry 1y: ", 1)
    volatility = calculate_volatility(prices)
    print("Volatility: ", volatility)
    model = OptionPricing(stock_price, strike, expiry, risk_free_rate, volatility, 10000000)
    model.call_option_simulation()
    model.put_option_simulation()



