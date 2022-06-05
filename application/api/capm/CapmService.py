from application.api.capm.CapmRequest import CapmRequest
from application.api.coinGecko.CoinGeckoApi import CoinGeckoApi
from application.api.finance.models.capm.CAPMApi import CAPMApi


def preparing_data_set(list_of_tickers, from_date, to_date, quote_currency):
    papi = CoinGeckoApi(quote_currency)
    return papi.loading_historical_data(list_of_tickers, from_date, to_date)


def calculate_capm(tickers, data_set):
    camp = CAPMApi()
    camp.initialize(tickers, data_set)
    camp.calculate_beta()
    return camp.regression()


def calculate(capm_request):
    data_set = preparing_data_set(capm_request.tickers,
                                  capm_request.from_date,
                                  capm_request.to_date,
                                  capm_request.quote_currency)
    return calculate_capm(capm_request.tickers, data_set)


if __name__ == '__main__':
    capm_request = CapmRequest(['sol', 'btc'], '2020-05-01')
    data_set = preparing_data_set(capm_request.tickers,
                                  capm_request.from_date,
                                  capm_request.to_date,
                                  capm_request.quote_currency)
    calculate_capm(capm_request.tickers, data_set)