import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from poc.models.CommonModel import download_data

# market interest rate
RISK_FREE_RATE = 0.05

# based in monthly returns that has be converted to years
MONTHS_IN_YEARS = 12


class CAPM:

    def __init__(self, stocks, start_date, end_date):
        self.stocks = stocks
        self.start_date = start_date
        self.end_date = end_date

        self.data = None

    def initialize(self):
        stock_data = download_data(self.stocks, self.start_date, self.end_date)
        # calculate Monthly returns instead of daily returns
        stock_data = stock_data.resample('M').last()
        print(stock_data)
        self.data = pd.DataFrame({
            's_close': stock_data[self.stocks[0]],
            'm_close': stock_data[self.stocks[1]]
        })
        print(self.data)
        # log monthly returns
        self.data[['s_returns', 'm_returns']] = np.log(self.data[['s_close', 'm_close']] / self.data[['s_close', 'm_close']].shift(1))
        # remove the NaN values
        self.data = self.data[1:]
        print(self.data)

    def calculate_beta(self):
        # covariance matrix: the diagonal items are the variances
        # off diagonals are the covariances
        # the matrix is symmetric: cov[0,1] = cov[1,0] !!!
        covariance_matrix = np.cov(self.data['s_returns'], self.data['m_returns'])
        beta = covariance_matrix[0, 1] / covariance_matrix[1, 1]
        print("Beta: ", beta)

    def regression(self):
        # using linear regression to fit a linear to the data
        # [stock_return, market_returns] - slope is the beta
        beta, alpha = np.polyfit(self.data['m_returns'], self.data['s_returns'], deg=1)
        print("Beta from regression: ", beta)
        # calculate the expected return according to the CAPM formula
        # we are after annual return (this is why multiply by 12)
        expected_return = RISK_FREE_RATE + beta * (self.data['m_returns'].mean() * MONTHS_IN_YEARS - RISK_FREE_RATE)
        print("Expected Return: ", expected_return)
        self.plot_regression(beta, alpha)

    def plot_regression(self, beta, alpha):
        fig, axis = plt.subplots(1, figsize=(20, 10))
        axis.scatter(self.data['m_returns'], self.data['s_returns'], label='Data points')
        axis.plot(self.data['m_returns'], beta * self.data['m_returns'] + alpha, color='red', label='CAPM Linear')
        plt.title('Capital Asset Pricing Model, finding beta & alpha')
        plt.xlabel("Market return $R_m$", fontsize=18)
        plt.ylabel("Stock return $R_a$", fontsize=18)
        plt.text(0.08, 0.05, r'$R_a = \beta * R_m + \alpha$', fontsize=18)
        plt.legend()
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    camp = CAPM(['IBM', '^GSPC'], '2010-01-01', '2022-01-01')
    camp.initialize()
    camp.calculate_beta()
    camp.regression()