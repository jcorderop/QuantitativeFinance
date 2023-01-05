from QuantitativeFinanceApi.application.api.capm.CapmRequest import CapmRequest
from QuantitativeFinanceApi.application.api.common.YahooFinanceApi import preparing_dataset
from QuantitativeFinanceApi.application.api.finance.models.capm.CAPMApi import CAPMApi


def calculate_capm(tickers, data_set):
    camp = CAPMApi()
    camp.initialize(tickers, data_set)
    camp.calculate_beta()
    return camp.regression()


def calculate(capm_request):
    data_set = preparing_dataset(capm_request)
    return calculate_capm(capm_request.tickers, data_set)


if __name__ == '__main__':
    capm_request = CapmRequest(['sol', 'btc'], '2020-05-01')
    data_set = preparing_dataset(capm_request)
    calculate_capm(capm_request.tickers, data_set)