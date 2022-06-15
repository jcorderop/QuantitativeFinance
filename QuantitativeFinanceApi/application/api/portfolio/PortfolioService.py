import time

from QuantitativeFinanceApi.application.api.coinGecko.CoinGeckoApi import CoinGeckoApi
from QuantitativeFinanceApi.application.api.common.Constants import Asset
import QuantitativeFinanceApi.application.api.finance.models.markowitz.MarkowitzModelApi as mma
from QuantitativeFinanceApi.application.api.common.QFLogger import QFLogger
from QuantitativeFinanceApi.application.api.finance.models.montecarlo.PriceSimulation import \
    monte_carlo_price_simulation
from QuantitativeFinanceApi.poc.models.CommonModel import download_data

logger = QFLogger(logger_name=__name__).get_logger()


def preparing_crypto_data_set(list_of_tickers, from_date, to_date, quote_currency):
    papi = CoinGeckoApi(quote_currency)
    return papi.loading_historical_data(list_of_tickers, from_date, to_date)


def preparing_stocks_data_set(list_of_tickers, from_date, to_date):
    return download_data(list_of_tickers, from_date, to_date)


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


def calculate_future_price(pf_request):
    result = None
    if pf_request.future_price:
        result = {}
        for ticker in pf_request.tickers:
            close_price, future_price = monte_carlo_price_simulation(ticker=ticker,
                                                                     to_date=pf_request.to_date,
                                                                     quote_currency=pf_request.quote_currency,
                                                                     future_date=pf_request.period,
                                                                     num_simulations=pf_request.num_simulations)
            result[ticker] = {
                'close_price': close_price,
                'future_price': future_price
            }
            time.sleep(3)
        logger.info("Future Prices:")
        logger.info(result)
    return result


def calculate_portfolio(request_id, pf_request):
    # data_set = preparing_data_set(CRYPTO_TICKERS, FROM_DATE, datetime.now().strftime(DateFormats.date_format), QUOTE_CURRENCY)
    if pf_request.asset_class == Asset.STOCK:
        data_set = preparing_stocks_data_set(pf_request.tickers,
                                             pf_request.from_date,
                                             pf_request.to_date)
    elif pf_request.asset_class == Asset.CRYPTO:
        data_set = preparing_crypto_data_set(pf_request.tickers,
                                             pf_request.from_date,
                                             pf_request.to_date,
                                             pf_request.quote_currency)
    else:
        raise Exception('Asset type [' + pf_request.asset_class + '] is not supported...')

    return portfolio_calculation(request_id,
                                 data_set,
                                 pf_request.period,
                                 pf_request.num_simulations,
                                 pf_request.daily_return_fun,
                                 pf_request.solver)


def plot_portfolio(request_id):
    return mma.show_optimal_portfolio_by_request(request_id)


if __name__ == '__main__':
    calculate_portfolio()
