import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as optimization

from QuantitativeFinanceApi.poc.models.CommonModel import download_data

# Stocks of the index
STOCKS = ['AAPL', 'WMT', 'TSLA', 'GE', 'AMZN', 'DB']

# Historical data - define Start and End dates
start_date = '2010-01-01'
end_date = '2022-01-01'

# on average there are 252 trading days
NUM_TRADING_DAYS = 252

# on average there are 365 calendar days
NUM_CALENDAR_DAYS = 365

# It will generate random w (different portfolios)
NUM_PORTFOLIOS = 100000


# log daily return
# S(t+1) / S(t)
# NORMALIZATION - to measure all variables in comparable metrics
def calculate_return(data_set):
    # shifting the data means first calculation will be NaN
    log_daily_return = np.log(data_set / data_set.shift(1))
    # return from second date
    return log_daily_return[1:]


# instead of daily metric we can to calculate them by period
def show_statistics(log_daily_return, period):
    print('Data set - mean:')
    print(calculate_mean_by_period(log_daily_return, period))

    print('Data set - covariance:')
    print(calculate_covariance_by_period(log_daily_return, period))


def calculate_mean_by_period(log_daily_return, period):
    return log_daily_return.mean() * period


def calculate_covariance_by_period(log_daily_return, period):
    return log_daily_return.cov() * period


def show_portfolio_statistics(log_daily_return, weights, period):
    print('Expected portfolio mean (return): ', calculate_portfolio_return(log_daily_return, weights, period))
    print('Expected portfolio volatility (standard deviation): ', calculate_portfolio_volatility(log_daily_return, weights, period))


# Expected portfolio mean (return)
def calculate_portfolio_return(log_daily_return, weights, period):
    return np.sum(log_daily_return.mean() * weights) * period


# Expected portfolio volatility (standard deviation)
def calculate_portfolio_volatility(log_daily_return, weights, period):
    return np.sqrt(np.dot(weights.T, np.dot(log_daily_return.cov() * period, weights)))


# sharp ratio
def calculate_sharp_ratio(portfolio_mean, portfolio_risk):
    return portfolio_mean/portfolio_risk


def generate_portfolios(log_daily_return, period):
    portfolio_weights = []
    portfolio_mean = []
    portfolio_risk = []

    for _ in range(NUM_PORTFOLIOS):
        w = np.random.random(len(STOCKS))
        # normalize to 1
        w /= np.sum(w)
        portfolio_weights.append(w)
        portfolio_mean.append(calculate_portfolio_return(log_daily_return, w, period))
        portfolio_risk.append(calculate_portfolio_volatility(log_daily_return, w, period))

    return portfolio_weights, portfolio_mean, portfolio_risk


def calculate_optimization_inputs(log_daily_return, weights, period):
    portfolio_mean = calculate_portfolio_return(log_daily_return, weights, period)
    portfolio_risk = calculate_portfolio_volatility(log_daily_return, weights, period)
    sharp_ratio = calculate_sharp_ratio(portfolio_mean, portfolio_risk)
    return np.array([portfolio_mean, portfolio_risk, sharp_ratio])


# scipy optimization can find the minimum of a given function
# the maximum is calculated with the inverse => f(x) is the minimum of -f(x)
def optimization_minimum(weights, log_daily_return, period):
    return -calculate_optimization_inputs(log_daily_return, weights, period)[2]


# definition of constrains
def optimized_portfolio(log_daily_return, weights, period):
    # the sum of weights is 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    # the weights can be 1 at mist: 1 when 100% of money is invested into a single stock
    bounds = tuple((0, 1) for _ in range(len(STOCKS)))

    return optimization.minimize(fun=optimization_minimum,
                                 x0=weights[0],
                                 args=(log_daily_return, period),
                                 method='SLSQP', # optimization method
                                 bounds=bounds,
                                 constraints=constraints)


def print_optimal_portfolio(optimum_portfolio, log_daily_return, period):
    print("Optimal portfolio: ", optimum_portfolio['x'].round(3))
    print("Expected return, volatility and sharp ratio: ", calculate_optimization_inputs(log_daily_return, optimum_portfolio['x'].round(3), period))


def show_portfolios(portfolio_mean, portfolio_risk, sharp_ratio):
    plt.figure(figsize=(10, 6))
    plt.scatter(portfolio_risk, portfolio_mean, c=portfolio_mean/portfolio_risk, marker='.')
    plt.grid(True)
    plt.xlabel("Expected Volatility")
    plt.ylabel("Expected Return")
    plt.colorbar(label="Sharp Ratio")
    plt.show()


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


def show_data(data_set):
    print('Data set:')
    print(data_set)
    data_set.plot(figsize=(10, 5))
    plt.show()


if __name__ == '__main__':
    period = NUM_TRADING_DAYS

    print('Loading data...')
    data_set = download_data(STOCKS, start_date, end_date)
    print('Plotting data-set...')
    show_data(data_set)

    print('Calculating return...')
    log_daily_return = calculate_return(data_set)
    print('Showing statistics from return...')
    show_statistics(log_daily_return, NUM_TRADING_DAYS)
    print('Generating random portfolios...')
    portfolio_weights_list, portfolio_mean_list, portfolio_risk_list = generate_portfolios(log_daily_return, period)
    portfolio_weights_arr = np.array(portfolio_weights_list)
    portfolio_mean_arr = np.array(portfolio_mean_list)
    portfolio_risk_arr = np.array(portfolio_risk_list)
    print('Calculate sharp ratio...')
    sharp_ratio_arr = calculate_sharp_ratio(portfolio_mean_arr, portfolio_risk_arr)
    print('Plotting portfolios...')
    show_portfolios(portfolio_mean_arr, portfolio_risk_arr, sharp_ratio_arr)

    print('Calculating optimized portfolio...')
    optimum_portfolio = optimized_portfolio(log_daily_return,
                                            portfolio_weights_arr,
                                            period)
    optimization_inputs = calculate_optimization_inputs(log_daily_return,
                                                        optimum_portfolio['x'].round(3),
                                                        period)
    opt_portfolio_mean = optimization_inputs[0]
    opt_portfolio_risk = optimization_inputs[1]
    print_optimal_portfolio(optimum_portfolio, log_daily_return, period)
    show_optimal_portfolio(portfolio_mean_arr, portfolio_risk_arr, sharp_ratio_arr,
                           opt_portfolio_mean, opt_portfolio_risk)


