import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimization

NUM_PORTFOLIOS = 100000

class MarkowitzModelApi(object):

    def __init__(self, data_set, period, num_portfolios=NUM_PORTFOLIOS):
        self.data_set = data_set
        self.period = period
        self.num_portfolios = num_portfolios

        self.log_daily_return = None

    def calculate_return(self):
        print('Showing statistics from daily return...')
        # catching calculation
        self.log_daily_return = self.calculate_daily_return(self.data_set)
        print('Data set - daily:')
        print(self.log_daily_return)

        print('Data set - mean:')
        print(self.calculate_mean_by_period(self.log_daily_return, self.period))

        print('Data set - covariance:')
        print(self.calculate_covariance_by_period(self.log_daily_return, self.period))

    # instead of daily metric we can to calculate them by period
    @staticmethod
    def calculate_mean_by_period(log_daily_return, period):
        return log_daily_return.mean() * period

    # instead of daily metric we can to calculate them by period
    @staticmethod
    def calculate_covariance_by_period(log_daily_return, period):
        return log_daily_return.cov() * period

    # log daily return
    # S(t+1) / S(t)
    # NORMALIZATION - to measure all variables in comparable metrics
    @staticmethod
    def calculate_daily_return(data_set):
        print('Calculating daily return...')
        # shifting the data means first calculation will be NaN
        log_daily_return = np.log(data_set / data_set.shift(1))
        # return from second date
        return log_daily_return[1:]

    def create_portfolios(self):
        print('Generating random portfolios...')
        portfolio_weights_list, portfolio_mean_list, portfolio_risk_list = self.generate_portfolios(self.log_daily_return,
                                                                                                               self.period,
                                                                                                               self.num_portfolios)

        self.portfolio_weights_arr = np.array(portfolio_weights_list)
        self.portfolio_mean_arr = np.array(portfolio_mean_list)
        self.portfolio_risk_arr = np.array(portfolio_risk_list)

        print('Calculate sharp ratio...')
        self.sharp_ratio_arr = self.calculate_sharp_ratio(self.portfolio_mean_arr, self.portfolio_risk_arr)
        print('Plotting portfolios...')
        self.show_portfolios(self.portfolio_mean_arr, self.portfolio_risk_arr, self.sharp_ratio_arr)

    # Expected portfolio mean (return)
    @staticmethod
    def calculate_portfolio_return(log_daily_return, weights, period):
        return np.sum(log_daily_return.mean() * weights) * period

    # Expected portfolio volatility (standard deviation)
    @staticmethod
    def calculate_portfolio_volatility(log_daily_return, weights, period):
        return np.sqrt(np.dot(weights.T, np.dot(log_daily_return.cov() * period, weights)))

    # sharp ratio
    @staticmethod
    def calculate_sharp_ratio(portfolio_mean, portfolio_risk):
        return portfolio_mean / portfolio_risk

    @staticmethod
    def generate_portfolios(log_daily_return, period, num_portfolios):
        portfolio_weights = []
        portfolio_mean = []
        portfolio_risk = []

        for _ in range(num_portfolios):
            w = np.random.random(len(log_daily_return.columns))
            # normalize to 1
            w /= np.sum(w)
            portfolio_weights.append(w)
            portfolio_mean.append(MarkowitzModelApi.calculate_portfolio_return(log_daily_return, w, period))
            portfolio_risk.append(MarkowitzModelApi.calculate_portfolio_volatility(log_daily_return, w, period))

        return portfolio_weights, portfolio_mean, portfolio_risk

    @staticmethod
    def show_portfolios(portfolio_mean, portfolio_risk, sharp_ratio):
        plt.figure(figsize=(10, 6))
        plt.scatter(portfolio_risk, portfolio_mean, c=portfolio_mean/portfolio_risk, marker='.')
        plt.grid(True)
        plt.xlabel("Expected Volatility")
        plt.ylabel("Expected Return")
        plt.colorbar(label="Sharp Ratio")
        plt.show()

    def calculate_optimized_portfolio(self):
        print('Calculating optimized portfolio...')
        optimum_portfolio = self.optimized_portfolio(self.log_daily_return,
                                                self.portfolio_weights_arr,
                                                self.period)

        optimization_inputs = self.calculate_optimization_inputs(self.log_daily_return,
                                                            optimum_portfolio['x'].round(3),
                                                            self.period)
        opt_portfolio_mean = optimization_inputs[0]
        opt_portfolio_risk = optimization_inputs[1]
        self.print_optimal_portfolio(optimum_portfolio, self.log_daily_return, self.period)
        self.show_optimal_portfolio(self.portfolio_mean_arr, self.portfolio_risk_arr, self.sharp_ratio_arr,
                               opt_portfolio_mean, opt_portfolio_risk)

    @staticmethod
    def print_optimal_portfolio(optimum_portfolio, log_daily_return, period):
        weigths = pd.Series(optimum_portfolio['x'].round(3), index=log_daily_return.columns, name='weights')
        print("Optimal portfolio: ")
        print(weigths)
        print("Expected return, volatility and sharp ratio: ",
              MarkowitzModelApi.calculate_optimization_inputs(log_daily_return, optimum_portfolio['x'].round(3), period))

    @staticmethod
    def calculate_optimization_inputs(log_daily_return, weights, period):
        portfolio_mean = MarkowitzModelApi.calculate_portfolio_return(log_daily_return, weights, period)
        portfolio_risk = MarkowitzModelApi.calculate_portfolio_volatility(log_daily_return, weights, period)
        sharp_ratio = MarkowitzModelApi.calculate_sharp_ratio(portfolio_mean, portfolio_risk)
        return np.array([portfolio_mean, portfolio_risk, sharp_ratio])

    # scipy optimization can find the minimum of a given function
    # the maximum is calculated with the inverse => f(x) is the minimum of -f(x)
    @staticmethod
    def optimization_minimum(weights, log_daily_return, period):
        return -MarkowitzModelApi.calculate_optimization_inputs(log_daily_return, weights, period)[2]

    # definition of constrains
    @staticmethod
    def optimized_portfolio(log_daily_return, weights, period):
        # the sum of weights is 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        # the weights can be 1 at mist: 1 when 100% of money is invested into a single stock
        bounds = tuple((0, 1) for _ in range(len(log_daily_return.columns)))

        return optimization.minimize(fun=MarkowitzModelApi.optimization_minimum,
                                     x0=weights[0],
                                     args=(log_daily_return, period),
                                     method='SLSQP',  # optimization method
                                     bounds=bounds,
                                     constraints=constraints)

    @staticmethod
    def show_optimal_portfolio(portfolio_mean, portfolio_risk, sharp_ratio,
                               opt_portfolio_mean, opt_portfolio_risk):
        plt.figure(figsize=(10, 6))
        plt.scatter(portfolio_risk, portfolio_mean, c=sharp_ratio, marker='.')
        plt.grid(True)
        plt.xlabel("Expected Volatility")
        plt.ylabel("Expected Return")
        plt.colorbar(label="Sharp Ratio")

        plt.plot(opt_portfolio_risk, opt_portfolio_mean, 'g*', markersize=20.0)

        plt.show()


if __name__ == '__main__':
    pass
