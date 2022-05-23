from pycoingecko import CoinGeckoAPI
from datetime import datetime
import pandas as pd

from api.Constants import DateFormats


class PortfolioCoinGeckoApi(object):

    def __init__(self, quote_currency):
        self.api_cg = CoinGeckoAPI()
        self.quote_currency = quote_currency
        self.__tickers = {}
        self.__load_tickers__()

    def __load_tickers__(self):
        list_of_coins = self.get_coins()

        list_of_coins = list(filter(lambda x: 'wrapped' not in x['id'], list_of_coins))
        list_of_coins = list(filter(lambda x: 'wormhole' not in x['id'], list_of_coins))
        list_of_coins = list(filter(lambda x: 'peg' not in x['id'], list_of_coins))

        for ticker in list_of_coins:
            if self.__tickers.get(ticker['symbol'], None) is None:
                self.__tickers[ticker['symbol']] = ticker['id']

    def get_price(self, ticker):
        coin_id = self.get_coin_id(ticker)
        return self.api_cg.get_price(ids=coin_id, vs_currencies=self.quote_currency)

    def get_coins(self):
        return self.api_cg.get_coins_list()

    def get_coins_markets(self):
        return self.api_cg.get_coins_markets(vs_currency=self.quote_currency)

    def get_coin_id(self, ticker):
        return self.__tickers[ticker]

    def __convert_date_to_timestamp__(self, date_string):
        dt_object = datetime.strptime(date_string, DateFormats.date_format)
        return datetime.timestamp(dt_object)

    def __json_price_to_pandas_series__(self, historic_prices):
        data = []
        index = []
        for price in historic_prices:
            data.append(price[1])
            index.append(datetime.fromtimestamp(price[0]/1000))
        return pd.Series(data, index=index, name='close')

    def get_historical_prices(self, ticker, from_date, to_date):
        print('Loading data from: ', from_date, ' to: ', to_date)
        from_timestamp = self.__convert_date_to_timestamp__(from_date)
        to_timestamp = self.__convert_date_to_timestamp__(to_date)
        coin_id = self.get_coin_id(ticker)
        print('ticker: ', coin_id)

        historic_data = self.api_cg.get_coin_market_chart_range_by_id(id=coin_id,
                                                                      vs_currency=self.quote_currency,
                                                                      from_timestamp=from_timestamp,
                                                                      to_timestamp=to_timestamp)
        print('Loading data has finished...')
        return self.__json_price_to_pandas_series__(historic_data['prices'])


if __name__ == '__main__':
    ticker = 'btc'
    papi = PortfolioCoinGeckoApi('usd')
    prices = papi.get_historical_prices(ticker, '2020-01-01', '2022-01-01')
    print(prices)
    data_set = pd.DataFrame({ticker: prices})
