import traceback
import base64
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.optimize as optimization

from QuantitativeFinanceApi.application.api.common.Constants import SolverType
from QuantitativeFinanceApi.application.api.common.QFException import QFException
from QuantitativeFinanceApi.application.api.common.QFLogger import QFLogger
from QuantitativeFinanceApi.application.api.common.Storage import Storage

logger = QFLogger(logger_name=__name__).get_logger()

NUM_PORTFOLIOS = 10000


def show_optimal_portfolio_by_request(request_id):
    request_storage = Storage().get_request_id(request_id)
    portfolios = request_storage['portfolios']
    performance = request_storage['performance']
    underlyings = request_storage['underlyings']
    if request_storage:
        opt_portfolio_mean = performance['Return']  # mean
        opt_portfolio_risk = performance['Volatility']  # risk
        return show_optimal_portfolio(np.array(portfolios['mean']),
                                      np.array(portfolios['risk']),
                                      np.array(portfolios['ratio']),
                                      opt_portfolio_mean,
                                      opt_portfolio_risk,
                                      underlyings)
    else:
        raise Exception("Invalid request id...")


def show_portfolios(portfolio_mean, portfolio_risk, sharp_ratio):
    plt.figure(figsize=(10, 6))
    plt.scatter(portfolio_risk, portfolio_mean, c=sharp_ratio, marker='.')
    plt.grid(True)
    plt.xlabel("Expected Volatility")
    plt.ylabel("Expected Return")
    plt.colorbar(label="Sharp Ratio")
    plt.title('Random Portfolio Generation')
    plt.show()


def show_optimal_portfolio(portfolio_mean,
                           portfolio_risk,
                           sharp_ratio,
                           opt_portfolio_mean,
                           opt_portfolio_risk,
                           underlyings):
    plt.subplots(figsize=(12, 7))
    plt.scatter(portfolio_risk, portfolio_mean, c=sharp_ratio, marker='.')
    plt.grid(True)
    plt.xlabel("Expected Volatility")
    plt.ylabel("Expected Return")
    plt.colorbar(label="Sharp Ratio")
    plt.title('Portfolio Optimization')

    for i in range(len(underlyings)):
        plt.annotate(underlyings[i],
                     (portfolio_risk[i], portfolio_mean[i]),
                     xytext=(4, 0),
                     textcoords='offset points',
                     fontsize=10,
                     color='red')
        plt.plot(portfolio_risk[i], portfolio_mean[i], 'g*', markersize=5.0,
                 color='red')

    plt.plot(opt_portfolio_risk, opt_portfolio_mean, 'g*', markersize=10.0)

    # Save it to a temporary buffer.
    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


# log daily return
# S(t+1) / S(t)
# NORMALIZATION - to measure all variables in comparable metrics
def daily_log_return(data_set):
    return np.log(data_set / data_set.shift(1))


# Compute daily simple returns
def daily_pct_change_return(data_set):
    return data_set.pct_change()


def calculate_daily_return(data_set, callback):
    logger.info('Calculating daily return...')
    # shifting the data means first calculation will be NaN
    try:
        daily_return = callback(data_set)
        # return from second date
        return daily_return[1:]
    except Exception:
        traceback.print_stack()
        raise QFException("Invalid calculation using daily return function {}...".format(callback))


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
    sharp_ratio = 0.0
    if portfolio_risk and portfolio_risk != 0.0:
        sharp_ratio = portfolio_mean / portfolio_risk
    #print("calculate_sharp_ratio: {} / {} = {}".format(portfolio_mean, portfolio_risk, sharp_ratio))
    return sharp_ratio


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
    return np.array([portfolio_mean, portfolio_risk, sharp_ratio], dtype="object")


# scipy optimization can find the minimum of a given function
# the maximum is calculated with the inverse => f(x) is the minimum of -f(x)
def optimization_minimum(weights, daily_return, period):
    return -calculate_optimization_inputs(daily_return,
                                          weights,
                                          period)[2]


def create_portfolio_weights(optimum_weights, underlyings):
    logger.info('Calculating optimized weights...')
    return pd.Series(optimum_weights,
                     index=underlyings,
                     name='weights').to_dict()


def create_performance(optimization_inputs):
    return pd.Series(optimization_inputs,
                     index=['Return', 'Volatility', 'SharpRatio'],
                     name='performance').to_dict()


def print_optimal_portfolio(weights_by_underlying, performance):
    logger.info("Optimal portfolio: ")
    logger.info('\n{}'.format(weights_by_underlying))
    logger.info("Expected return, volatility and sharp ratio: ")
    logger.info('\n{}'.format(performance))


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
    logger.info('Calculating optimized portfolio...')
    elements = len(daily_return.columns)
    # the sum of weights is 1
    const_sum_of_weights = {'type': 'eq',
                            'fun': lambda x: np.sum(x) - 1}
    if solver:
        const_solver_fun = get_solver_fun(daily_return, period, solver)
        constraints = (const_sum_of_weights, const_solver_fun)
    else:
        constraints = (const_sum_of_weights)
    logger.info('constraints: {}'.format(constraints))
    # the weights can be 1 at mist: 1 when 100% of money is invested into a single stock
    bounds = tuple((0, 1) for _ in range(elements))
    weights = [1 / elements for x in range(elements)]
    logger.info('underlying: {}'.format(elements))
    logger.info('Equal weight to be used for optimization: {}'.format(weights))
    optimized_portfolio = optimization.minimize(fun=optimization_minimum,
                                                x0=weights,
                                                args=(daily_return, period),
                                                method='SLSQP',  # optimization method
                                                bounds=bounds,
                                                constraints=constraints)
    logger.info('\n{}'.format(optimized_portfolio))
    return optimized_portfolio


def get_daily_return_callback(daily_return_callback):
    callback = {
        'daily_log_return': daily_log_return,
        'daily_pct_change_return': daily_pct_change_return
    }
    try:
        return callback.get(daily_return_callback)
    except Exception:
        traceback.print_stack()
        raise QFException("Invalid daily calculation function...")


class MarkowitzModelApi(object):

    def __init__(self,
                 request_id,
                 data_set,
                 period,
                 num_portfolios=NUM_PORTFOLIOS,
                 daily_return_callback="daily_pct_change_return",
                 solver=None):
        self.request_id = request_id
        self.data_set = data_set
        self.period = period
        self.num_portfolios = num_portfolios
        self.daily_return_callback = get_daily_return_callback(daily_return_callback)
        self.solver = solver

        self.daily_return = None
        self.portfolios = None

    def store(self, section, content):
        Storage().store(self.request_id, section, content)

    def calculate_return(self):
        logger.info('Showing statistics from daily return...')
        # catching calculation
        self.daily_return = calculate_daily_return(self.data_set, self.daily_return_callback)
        logger.info('Data set - daily:')
        logger.info('\n{}'.format(self.daily_return))

        logger.info('Data set - mean:')
        logger.info('\n{}'.format(calculate_mean_by_period(self.daily_return, self.period)))

        logger.info('Data set - covariance:')
        logger.info('\n{}'.format(calculate_covariance_by_period(self.daily_return, self.period)))

    def create_portfolios(self):
        logger.info('Generating random portfolios...')
        self.portfolios = generate_portfolios(self.daily_return,
                                              self.period,
                                              self.num_portfolios)
        self.store('portfolios', self.portfolios)
        self.store('underlyings', self.daily_return.columns)
        return self.portfolios
        # logger.info('Plotting portfolios...')
        # self.show_portfolios(np.array(self.portfolios['mean']),
        #                     np.array(self.portfolios['risk']),
        #                     np.array(self.portfolios['ratio']))

    def calculate_performance_by_underlying(self, weights_by_underlying):
        performance_by_underlying = {}

        for udl in weights_by_underlying:
            weight = np.array(weights_by_underlying[udl])
            daily_return_udl = pd.DataFrame(self.daily_return[udl])
            performance_udl = calculate_optimization_inputs(daily_return_udl,
                                                            weight,
                                                            self.period)

            print("Underlying: {}, performance_udl: {}".format(udl, performance_udl))

            mean = performance_udl[0]
            risk = performance_udl[1][0][0]
            ratio = 0.0
            try:
                ratio = performance_udl[2][0][0]
            except:
                pass

            performance_by_underlying[udl] = {
                "mean": mean,
                "risk": risk,
                "ratio": ratio
            }
            print("Underlying: {}, performance_udl: {}".format(udl, performance_udl))

        logger.info('Calculating performance by underlying...')
        logger.info('\n{}'.format(performance_by_underlying))
        return performance_by_underlying

    def calculate_optimized_portfolio(self):
        optimum_portfolio = optimized_portfolio(self.daily_return,
                                                self.period,
                                                self.solver)
        logger.info('Calculating optimized performance...')
        optimization_inputs = calculate_optimization_inputs(self.daily_return,
                                                            optimum_portfolio['x'].round(3),
                                                            self.period)
        performance = create_performance(optimization_inputs)
        weights_by_underlying = create_portfolio_weights(optimum_portfolio['x'].round(3),
                                                         self.daily_return.columns)

        print_optimal_portfolio(weights_by_underlying, performance)
        # opt_portfolio_mean = optimization_inputs[0]
        # opt_portfolio_risk = optimization_inputs[1]
        # self.show_optimal_portfolio(np.array(self.portfolios['mean']),
        #                            np.array(self.portfolios['risk']),
        #                            np.array(self.portfolios['ratio']),
        #                            opt_portfolio_mean,
        #                            opt_portfolio_risk,
        #                            self.daily_return.columns)
        performance_by_underlying = self.calculate_performance_by_underlying(weights_by_underlying)
        self.store('performance', performance)
        self.store('weights_by_underlying', weights_by_underlying)
        self.store('performance_by_underlying', performance_by_underlying)
        return performance, weights_by_underlying, performance_by_underlying


if __name__ == '__main__':
    pass
