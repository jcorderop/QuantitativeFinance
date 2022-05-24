import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimization

NUM_PORTFOLIOS = 10000


# log daily return
# S(t+1) / S(t)
# NORMALIZATION - to measure all variables in comparable metrics
def calculate_daily_return(data_set):
    print('Calculating daily return...')
    # shifting the data means first calculation will be NaN
    log_daily_return = np.log(data_set / data_set.shift(1))
    # return from second date
    return log_daily_return[1:]


# instead of daily metric we can to calculate them by period
def calculate_mean_by_period(log_daily_return, period):
    return log_daily_return.mean() * period


# instead of daily metric we can to calculate them by period
def calculate_covariance_by_period(log_daily_return, period):
    return log_daily_return.cov() * period


# Expected portfolio mean (return)
def calculate_portfolio_return(log_daily_return, weights, period):
    return np.sum(log_daily_return.mean() * weights) * period


# Expected portfolio volatility (standard deviation)
def calculate_portfolio_volatility(log_daily_return, weights, period):
    return np.sqrt(np.dot(weights.T, np.dot(log_daily_return.cov() * period, weights)))


# sharp ratio
def calculate_sharp_ratio(portfolio_mean, portfolio_risk):
    return portfolio_mean / portfolio_risk


def generate_portfolios(log_daily_return, period, num_portfolios):
    portfolio_weights = []
    portfolio_mean = []
    portfolio_risk = []

    for _ in range(num_portfolios):
        weight = np.random.random(len(log_daily_return.columns))
        # normalize to 1
        weight /= np.sum(weight)
        portfolio_weights.append(weight)
        portfolio_mean.append(calculate_portfolio_return(log_daily_return,
                                                         weight,
                                                         period))
        portfolio_risk.append(calculate_portfolio_volatility(log_daily_return,
                                                             weight,
                                                             period))

    return portfolio_weights, portfolio_mean, portfolio_risk


def calculate_optimization_inputs(log_daily_return, weights, period):
    portfolio_mean = calculate_portfolio_return(log_daily_return, weights, period)
    portfolio_risk = calculate_portfolio_volatility(log_daily_return, weights, period)
    sharp_ratio = calculate_sharp_ratio(portfolio_mean, portfolio_risk)
    return np.array([portfolio_mean, portfolio_risk, sharp_ratio])


# scipy optimization can find the minimum of a given function
# the maximum is calculated with the inverse => f(x) is the minimum of -f(x)
def optimization_minimum(weights, log_daily_return, period):
    return -calculate_optimization_inputs(log_daily_return,
                                          weights,
                                          period)[2]


def create_portfolio_weights(optimum_weights, underlyings):
    return pd.Series(optimum_weights,
                     index=underlyings,
                     name='weights')


def create_performance(optimization_inputs):
    return pd.Series(optimization_inputs,
                     index=['Return', 'Volatility', 'SharpRatio'],
                     name='performance')


def print_optimal_portfolio(weights_by_underlying, performance):
    print("Optimal portfolio: ")
    print(weights_by_underlying)
    print("Expected return, volatility and sharp ratio: ")
    print(performance)


# definition of constrains
def optimized_portfolio(log_daily_return, weights, period):
    # the sum of weights is 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    # the weights can be 1 at mist: 1 when 100% of money is invested into a single stock
    bounds = tuple((0, 1) for _ in range(len(log_daily_return.columns)))
    return optimization.minimize(fun=optimization_minimum,
                                 x0=weights[0],
                                 args=(log_daily_return, period),
                                 method='SLSQP',  # optimization method
                                 bounds=bounds,
                                 constraints=constraints)


class MarkowitzModelApi(object):

    def __init__(self, data_set, period, num_portfolios=NUM_PORTFOLIOS):
        self.data_set = data_set
        self.period = period
        self.num_portfolios = num_portfolios

        self.log_daily_return = None

        self.portfolio_risk_arr = None
        self.portfolio_mean_arr = None
        self.portfolio_weights_arr = None
        self.sharp_ratio_arr = None

    def calculate_return(self):
        print('Showing statistics from daily return...')
        # catching calculation
        self.log_daily_return = calculate_daily_return(self.data_set)
        print('Data set - daily:')
        print(self.log_daily_return)

        print('Data set - mean:')
        print(calculate_mean_by_period(self.log_daily_return, self.period))

        print('Data set - covariance:')
        print(calculate_covariance_by_period(self.log_daily_return, self.period))

    def create_portfolios(self):
        print('Generating random portfolios...')
        portfolio_weights_list, portfolio_mean_list, portfolio_risk_list = generate_portfolios(
            self.log_daily_return,
            self.period,
            self.num_portfolios)

        self.portfolio_weights_arr = np.array(portfolio_weights_list)
        self.portfolio_mean_arr = np.array(portfolio_mean_list)
        self.portfolio_risk_arr = np.array(portfolio_risk_list)

        print('Calculate sharp ratio...')
        self.sharp_ratio_arr = calculate_sharp_ratio(self.portfolio_mean_arr, self.portfolio_risk_arr)
        print('Plotting portfolios...')
        self.show_portfolios(self.portfolio_mean_arr, self.portfolio_risk_arr, self.sharp_ratio_arr)

    def calculate_optimized_portfolio(self):
        print('Calculating optimized portfolio...')
        optimum_portfolio = optimized_portfolio(self.log_daily_return,
                                                self.portfolio_weights_arr,
                                                self.period)
        print(optimum_portfolio)
        print('Calculating optimized performance...')
        optimization_inputs = calculate_optimization_inputs(self.log_daily_return,
                                                            optimum_portfolio['x'].round(3),
                                                            self.period)
        performance = create_performance(optimization_inputs)

        print('Calculating optimized weights...')
        weights_by_underlying = create_portfolio_weights(optimum_portfolio['x'].round(3),
                                                         self.log_daily_return.columns)

        print_optimal_portfolio(weights_by_underlying, performance)
        opt_portfolio_mean = optimization_inputs[0]
        opt_portfolio_risk = optimization_inputs[1]
        self.show_optimal_portfolio(self.portfolio_mean_arr,
                                    self.portfolio_risk_arr,
                                    self.sharp_ratio_arr,
                                    opt_portfolio_mean,
                                    opt_portfolio_risk)
        return performance, weights_by_underlying

    def show_portfolios(self, portfolio_mean, portfolio_risk, sharp_ratio):
        plt.figure(figsize=(10, 6))
        plt.scatter(portfolio_risk, portfolio_mean, c=sharp_ratio, marker='.')
        plt.grid(True)
        plt.xlabel("Expected Volatility")
        plt.ylabel("Expected Return")
        plt.colorbar(label="Sharp Ratio")
        plt.show()

    def show_optimal_portfolio(self, portfolio_mean, portfolio_risk, sharp_ratio,
                               opt_portfolio_mean, opt_portfolio_risk):
        plt.figure(figsize=(10, 6))
        plt.scatter(portfolio_risk, portfolio_mean, c=sharp_ratio, marker='.')
        plt.grid(True)
        plt.xlabel("Expected Volatility")
        plt.ylabel("Expected Return")
        plt.colorbar(label="Sharp Ratio")

        plt.plot(opt_portfolio_risk, opt_portfolio_mean, 'g*', markersize=10.0)
        plt.show()


if __name__ == '__main__':
    pass
