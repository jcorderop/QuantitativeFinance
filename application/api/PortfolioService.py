from application.api.coinGecko.CoinGeckoApi import CoinGeckoApi
from application.api.model.markowitz.MarkowitzModelApi import MarkowitzModelApi


def preparing_data_set(list_of_tickers, from_date, to_date, quote_currency):
    papi = CoinGeckoApi(quote_currency)
    return papi.loading_historical_data(list_of_tickers, from_date, to_date)


def portfolio_calculation(data_set, period, num_portfolios, daily_return_callback, expected_return):
    mmapi = MarkowitzModelApi(data_set, period, num_portfolios, daily_return_callback, expected_return)
    mmapi.calculate_return()
    mmapi.create_portfolios()
    return mmapi.calculate_optimized_portfolio()


def calculate_portfolio(pf_request):
    # data_set = preparing_data_set(CRYPTO_TICKERS, FROM_DATE, datetime.now().strftime(DateFormats.date_format), QUOTE_CURRENCY)
    data_set = preparing_data_set(pf_request.tickers,
                                  pf_request.from_date,
                                  pf_request.to_date,
                                  pf_request.quote_currency)
    return portfolio_calculation(data_set,
                                 pf_request.period,
                                 pf_request.num_portfolios,
                                 pf_request.daily_return_fun,
                                 pf_request.solver)


if __name__ == '__main__':
    calculate_portfolio()
