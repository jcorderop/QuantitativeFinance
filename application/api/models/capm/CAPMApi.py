import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from poc.models.CommonModel import download_data

# market interest rate
RISK_FREE_RATE = 0.011

# based in monthly returns that has be converted to years
MONTHS_IN_YEARS = 12


class CAPMApi:

    def __init__(self):
        self.data = None

    def initialize(self, tickers, data_set):
        # calculate Monthly returns instead of daily returns
        stock_data = data_set.resample('M').last()
        print(stock_data)
        self.data = pd.DataFrame({
            's_close': stock_data[tickers[0]],
            'm_close': stock_data[tickers[1]]
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
        return beta, expected_return

    def plot_regression(self, beta, alpha):
        fig, axis = plt.subplots(1, figsize=(10, 6))
        axis.scatter(self.data['m_returns'], self.data['s_returns'], label='Data points')
        axis.plot(self.data['m_returns'], beta * self.data['m_returns'] + alpha, color='red', label='CAPM Linear')
        plt.title('Capital Asset Pricing Model, finding beta & alpha')
        plt.xlabel("Market return $R_m$", fontsize=12)
        plt.ylabel("Stock return $R_a$", fontsize=12)
        plt.text(0.08, 0.05, r'$R_a = \beta * R_m + \alpha$', fontsize=14)
        plt.legend()
        plt.grid(True)
        plt.show()
"sol", "trx", "shib", "midas", "xnc", "paxg", "axs", "matic"

if __name__ == '__main__':
    camp = CAPMApi(['IBM', '^GSPC'], '2010-01-01', '2022-01-01')
    camp.initialize()
    camp.calculate_beta()
    camp.regression()