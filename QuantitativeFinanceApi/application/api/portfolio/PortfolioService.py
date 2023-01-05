import json
import time

import QuantitativeFinanceApi.application.api.finance.models.markowitz.MarkowitzModelApi as mma
from QuantitativeFinanceApi.application.api.common.QFLogger import QFLogger
from QuantitativeFinanceApi.application.api.common.YahooFinanceApi import is_ticker_exist, update_json
from QuantitativeFinanceApi.application.api.finance.models.montecarlo.PriceSimulation import monte_carlo_price_simulation

logger = QFLogger(logger_name=__name__).get_logger()


def portfolio_calculation(request_id,
                          data_set,
                          period,
                          num_portfolios,
                          daily_return_callback,
                          expected_return):
    mmapi = mma.MarkowitzModelApi(request_id, data_set, period, num_portfolios, daily_return_callback, expected_return)
    mmapi.calculate_return()
    mmapi.create_portfolios()
    return mmapi.calculate_optimized_portfolio()


def get_relevant_urls(request_id, pf_request):
    return {'portfolio': 'http://localhost:5000/portfolio/plot/{}'.format(request_id)}


def calculate_future_price(pf_request, data_set_all):
    result = None
    if pf_request.future_price:
        result = {}
        for ticker in pf_request.tickers:
            data_set = data_set_all[ticker]
            close_price, future_price = monte_carlo_price_simulation(pf_request, data_set, pf_request.future_days)
            result[ticker] = {
                'close_price': close_price,
                'future_price': future_price
            }
            time.sleep(3)
        logger.info("Future Prices:")
        logger.info(result)
    return result


def calculate_portfolio(request_id, pf_request, data_set):
    return portfolio_calculation(request_id,
                                 data_set,
                                 pf_request.period,
                                 pf_request.num_simulations,
                                 pf_request.daily_return_fun,
                                 pf_request.solver)


def plot_portfolio(request_id):
    return mma.show_optimal_portfolio_by_request(request_id)


def validate_tickers(tickers):
    valid_tickers = []
    invalid_tickers = []
    for ticker in tickers:
        exist = is_ticker_exist(ticker)
        print('ticker: {}, result: {}'.format(ticker, exist))
        if not exist:
            invalid_tickers.append(ticker)
        else:
            valid_tickers.append(ticker)
    update_json(valid_tickers)
    return invalid_tickers


if __name__ == '__main__':
    print(validate_tickers(['k123', 'NFLX', 'NTES', 'EA', 'MGOM', 'GOOGL', 'TTWO', 'SJRB.CN', 'DJCO', 'OMC', 'FMPR', 'TTD', 'CGO.CN', 'CMCSA', 'GWOX', 'NXST', 'QBRA.CN', 'RCIB.CN', 'DIS', 'SHEN', 'BIDU', 'CHTR', 'CIBY', 'TMUS', 'ZD', 'DISH', 'CCA.CN', 'LYV', 'WLY', 'IRDM', 'KTEL', 'ATNI', 'ATVI', 'IPG', 'SADL', 'THRY', 'NYT', 'FWONK', 'CRKM', 'EZOO', 'SPOK', 'SE', 'META', 'DTRL', 'TTGT', 'SCHL', 'YY', 'WWE', 'LPTV', 'SSTK', 'IMAX', 'T.CN', 'BCE.CN', 'SGA', 'BILI']))



