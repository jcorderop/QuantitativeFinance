import numpy as np
from scipy.stats import norm

from QuantitativeFinanceApi.application.api.finance.models.markowitz.MarkowitzModelApi import daily_log_return
from QuantitativeFinanceApi.poc.models.CommonModel import download_data_single

'''
position      
c       is the confident value, e.g.:95%
mu      mean
sigma   the standard deviation

This is how VaR is calculated tomorrow (n=1), otherwise days in the future
'''
def calculate_var(position, c, mu, sigma, n=1):
    # norm.ppf(1 - c) => distribution function
    var = position * (mu * n - sigma * np.sqrt(n) * norm.ppf(1 - c))
    return var


if __name__ == '__main__':
    stock_symbol = 'C'
    start_date = '2010-01-01'
    end_date = '2022-01-01'
    data = download_data_single(stock_symbol, start_date, end_date)
    print(data)

    data['returns'] = daily_log_return(data)[1:]
    print(data)

    # investment S
    position = 1000000
    # confident level - e.g.: 95%, higher more risk
    c = 0.95
    # assumption is that daily returns are normally distributed
    mu = np.mean(data['returns'])
    sigma = np.std(data['returns'])

    var = calculate_var(position=position, c=c, mu=mu, sigma=sigma)
    print('Value at risk is: $%0.2f' % var)

    days = 10
    var = calculate_var(position=position, c=c, mu=mu, sigma=sigma, n=days)
    print('Value at risk in %s days is: $%0.2f' % (days, var))