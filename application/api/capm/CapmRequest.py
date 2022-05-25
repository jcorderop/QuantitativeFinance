from dataclasses import dataclass
from typing import Any, List

CRYPTO_TICKERS = ['bnb', 'btc']

FROM_DATE = '2018-01-01'
TO_DATE = '2022-01-01'

QUOTE_CURRENCY = 'usd'


@dataclass
class CapmRequest:

    def __init__(self,
                 tickers,
                 from_date=FROM_DATE,
                 to_date=TO_DATE,
                 quote_currency=QUOTE_CURRENCY):
        self.tickers = tickers
        self.from_date = from_date
        self.to_date = to_date
        self.quote_currency = quote_currency

    @staticmethod
    def from_dict(obj: Any) -> 'CapmRequest':
        print('Request:', obj)
        _tickers = obj.get("tickers")
        _from_date = str(obj.get("from_date"))
        _to_date = str(obj.get("to_date"))
        _quote_currency = str(obj.get("quote_currency"))
        new_request = CapmRequest(_tickers,
                                  _from_date,
                                  _to_date,
                                  _quote_currency)
        print('Valid request:', new_request)
        return new_request
