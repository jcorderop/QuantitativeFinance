import json

import pandas as pd
import yfinance as yf

from QuantitativeFinanceApi.application.api.coinGecko.CoinGeckoApi import CoinGeckoApi
from QuantitativeFinanceApi.application.api.common.Constants import Asset


TICKET_CACHE = None
JSON_FILE_CACHE_NAME = 'valid_yahoo_stocks.json'


def load_cache():
    global TICKET_CACHE
    if TICKET_CACHE is None:
        TICKET_CACHE = load_tickers()
    return TICKET_CACHE


def update_cache(cache_snapshot):
    global TICKET_CACHE
    TICKET_CACHE = cache_snapshot


def write_json(data):
    global JSON_FILE_CACHE_NAME
    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(JSON_FILE_CACHE_NAME, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def load_tickers():
    global JSON_FILE_CACHE_NAME
    try:
        tickers_file = open(JSON_FILE_CACHE_NAME, "rb" )
        mapped_tickers = json.load(tickers_file)
        tickers_file.close()
        return mapped_tickers
    except:
        return []


def update_json(data):
    mapped_tickers = load_tickers()
    for element in data:
        if element not in mapped_tickers:
            mapped_tickers.append(element)
    write_json(mapped_tickers)
    update_cache(mapped_tickers)


def download_data_common(stocks, start_date, end_date):
    # name of the stocks(key) - stocks values
    stock_data = {}
    for stock in stocks:
        ticker = yf.Ticker(stock)
        stock_data[stock] = ticker.history(period="max", auto_adjust=False)['Adj Close']
        print(stock_data[stock])
    return stock_data


def is_ticker_exist(ticker):
    cache = load_cache()
    if ticker in cache:
        return True
    elif ticker:
        ticker = yf.Ticker(ticker)
        test = ticker.history()
        return not str(test).__contains__('Empty')
    else:
        print('invalid ticker {}'.format(ticker))
        return False


def download_data(stocks, start_date, end_date):
    json_prices = download_data_common(stocks, start_date, end_date)
    return pd.DataFrame(json_prices)


def download_data_single(stock_symbol, start_date, end_date):
    json_prices = download_data_common([stock_symbol], start_date, end_date)
    prices = pd.DataFrame(json_prices[stock_symbol])
    return pd.DataFrame(prices)


def preparing_crypto_data_set(list_of_tickers, from_date, to_date, quote_currency):
    papi = CoinGeckoApi(quote_currency)
    return papi.loading_historical_data(list_of_tickers, from_date, to_date)


def preparing_stocks_data_set(list_of_tickers, from_date, to_date):
    return download_data(list_of_tickers, from_date, to_date)


def preparing_dataset(pf_request):
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
    return data_set