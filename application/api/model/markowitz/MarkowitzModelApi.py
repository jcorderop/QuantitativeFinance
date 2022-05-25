import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimization

from application.api.Constants import SolverType
from application.api.common.PortfolioException import PortfolioException

NUM_PORTFOLIOS = 10000


# log daily return
# S(t+1) / S(t)
# NORMALIZATION - to measure all variables in comparable metrics
def daily_log_return(data_set):
    return np.log(data_set / data_set.shift(1))


# Compute daily simple returns
def daily_pct_change_return(data_set):
    return data_set.pct_change()


def calculate_daily_return(data_set, callback):
    print('Calculating daily return...')
    # shifting the data means first calculation will be NaN
    try:
        daily_return = callback(data_set)
        # return from second date
        return daily_return[1:]
    except Exception:
        traceback.print_stack()
        raise PortfolioException("Invalid calculation using daily return function {}...".format(callback))


# instead of daily metric we can to calculate them by period
def calculate_mean_by_period(daily_return, period):
    return daily_return.mean() * period


# instead of daily metric we can to calculate them by period
def calculate_covariance_by_period(daily_return, period):
    return daily_return.cov() * period


# Expected portfolio mean (return)
def calculate_portfolio_return(daily_return, weights, period):
    return np.sum(daily_return.mean() * weights) * period


# Expected portfolio volatility (standard deviation)
def calculate_portfolio_volatility(daily_return, weights, period):
    return np.sqrt(np.dot(weights.T, np.dot(daily_return.cov() * period, weights)))


# sharp ratio
def calculate_sharp_ratio(portfolio_mean, portfolio_risk):
    return portfolio_mean / portfolio_risk


def generate_portfolios(daily_return, period, num_portfolios):
    portfolio_weights = []
    portfolio_mean = []
    portfolio_risk = []
    portfolio_sharp_ratio = []

    for _ in range(num_portfolios):
        weight = np.random.random(len(daily_return.columns))
        # normalize to 1
        weight /= np.sum(weight)
        portfolio_weights.append(weight)
        mean = calculate_portfolio_return(daily_return,
                                          weight,
                                          period)
        portfolio_mean.append(mean)
        risk = calculate_portfolio_volatility(daily_return,
                                              weight,
                                              period)
        portfolio_risk.append(risk)
        portfolio_sharp_ratio.append(calculate_sharp_ratio(mean, risk))

    return {
        'weights': portfolio_weights,
        'mean': portfolio_mean,
        'risk': portfolio_risk,
        'ratio': portfolio_sharp_ratio
    }


def calculate_optimization_inputs(daily_return, weights, period):
    portfolio_mean = calculate_portfolio_return(daily_return, weights, period)
    portfolio_risk = calculate_portfolio_volatility(daily_return, weights, period)
    sharp_ratio = calculate_sharp_ratio(portfolio_mean, portfolio_risk)
    return np.array([portfolio_mean, portfolio_risk, sharp_ratio])


# scipy optimization can find the minimum of a given function
# the maximum is calculated with the inverse => f(x) is the minimum of -f(x)
def optimization_minimum(weights, daily_return, period):
    return -calculate_optimization_inputs(daily_return,
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
def get_solver_fun(daily_return, period, solver):
    solver_function = {
        SolverType().RETURN: {'type': 'eq',
                              'fun': lambda x: np.sum(
                                  calculate_portfolio_return(daily_return, x, period)) - solver.target},
        SolverType().VOLATILITY: {'type': 'eq',
                                  'fun': lambda x: np.sum(
                                      calculate_portfolio_volatility(daily_return, x, period)) - solver.target}
    }
    return solver_function[solver.type]


def optimized_portfolio(daily_return, period, solver=None):
    elements = len(daily_return.columns)
    # the sum of weights is 1
    const_sum_of_weights = {'type': 'eq',
                            'fun': lambda x: np.sum(x) - 1}
    if solver:
        const_solver_fun = get_solver_fun(daily_return, period, solver)
        constraints = (const_sum_of_weights, const_solver_fun)
    else:
        constraints = (const_sum_of_weights)
    # the weights can be 1 at mist: 1 when 100% of money is invested into a single stock
    bounds = tuple((0, 1) for _ in range(elements))
    weights = [1 / elements for x in range(elements)]
    print('underlying:', elements)
    print('Equal weight to be used for optimization:', weights)
    return optimization.minimize(fun=optimization_minimum,
                                 x0=weights,
                                 args=(daily_return, period),
                                 method='SLSQP',  # optimization method
                                 bounds=bounds,
                                 constraints=constraints)


def get_daily_return_callback(daily_return_callback):
    callback = {
        'daily_log_return': daily_log_return,
        'daily_pct_change_return': daily_pct_change_return
    }
    try:
        return callback.get(daily_return_callback)
    except Exception:
        traceback.print_stack()
        raise PortfolioException("Invalid daily calculation function...")


class MarkowitzModelApi(object):

    def __init__(self,
                 data_set,
                 period,
                 num_portfolios=NUM_PORTFOLIOS,
                 daily_return_callback="daily_pct_change_return",
                 solver=None):
        self.data_set = data_set
        self.period = period
        self.num_portfolios = num_portfolios
        self.daily_return_callback = get_daily_return_callback(daily_return_callback)
        self.solver = solver

        self.daily_return = None
        self.portfolios = None

    def calculate_return(self):
        print('Showing statistics from daily return...')
        # catching calculation
        self.daily_return = calculate_daily_return(self.data_set, self.daily_return_callback)
        print('Data set - daily:')
        print(self.daily_return)

        print('Data set - mean:')
        print(calculate_mean_by_period(self.daily_return, self.period))

        print('Data set - covariance:')
        print(calculate_covariance_by_period(self.daily_return, self.period))

    def create_portfolios(self):
        print('Generating random portfolios...')
        self.portfolios = generate_portfolios(self.daily_return,
                                              self.period,
                                              self.num_portfolios)
        print('Plotting portfolios...')
        self.show_portfolios(np.array(self.portfolios['mean']),
                             np.array(self.portfolios['risk']),
                             np.array(self.portfolios['ratio']))

    def calculate_optimized_portfolio(self):
        print('Calculating optimized portfolio...')
        optimum_portfolio = optimized_portfolio(self.daily_return,
                                                self.period,
                                                self.solver)
        print(optimum_portfolio)
        print('Calculating optimized performance...')
        optimization_inputs = calculate_optimization_inputs(self.daily_return,
                                                            optimum_portfolio['x'].round(3),
                                                            self.period)
        performance = create_performance(optimization_inputs)
        print('Calculating optimized weights...')
        weights_by_underlying = create_portfolio_weights(optimum_portfolio['x'].round(3),
                                                         self.daily_return.columns)

        print_optimal_portfolio(weights_by_underlying, performance)
        opt_portfolio_mean = optimization_inputs[0]
        opt_portfolio_risk = optimization_inputs[1]
        self.show_optimal_portfolio(np.array(self.portfolios['mean']),
                                    np.array(self.portfolios['risk']),
                                    np.array(self.portfolios['ratio']),
                                    opt_portfolio_mean,
                                    opt_portfolio_risk,
                                    self.daily_return.columns)
        return performance.to_dict(), weights_by_underlying.to_dict()

    def show_portfolios(self, portfolio_mean, portfolio_risk, sharp_ratio):
        plt.figure(figsize=(10, 6))
        plt.scatter(portfolio_risk, portfolio_mean, c=sharp_ratio, marker='.')
        plt.grid(True)
        plt.xlabel("Expected Volatility")
        plt.ylabel("Expected Return")
        plt.colorbar(label="Sharp Ratio")
        plt.title('Random Portfolio Generation')
        plt.show()

    def show_optimal_portfolio(self, portfolio_mean, portfolio_risk, sharp_ratio,
                               opt_portfolio_mean, opt_portfolio_risk,
                               underlyings):
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.scatter(portfolio_risk, portfolio_mean, c=sharp_ratio, marker='.')
        plt.grid(True)
        plt.xlabel("Expected Volatility")
        plt.ylabel("Expected Return")
        plt.colorbar(label="Sharp Ratio")
        plt.title('Portfolio Optimization with Individual Stocks')

        for i in range(len(underlyings)):
            plt.annotate(underlyings[i],
                         (portfolio_risk[i], portfolio_mean[i]),
                         xytext=(4, 0),
                         textcoords='offset points',
                         fontsize=10,
                         color='red')
            plt.plot(portfolio_risk[i], portfolio_mean[i], 'g*', markersize=5.0, color='red')

        plt.plot(opt_portfolio_risk, opt_portfolio_mean, 'g*', markersize=10.0)
        plt.show()


if __name__ == '__main__':
    pass
