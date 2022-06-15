from dataclasses import dataclass
from typing import Any

from QuantitativeFinanceApi.application.api.common.QFLogger import QFLogger

logger = QFLogger(logger_name=__name__).get_logger()

CRYPTO_TICKERS = ['btc', 'eth', 'bnb', 'sol', 'luna', 'xrp',
                  'leo', 'kcs', 'ftm', 'midas', 'ftt',
                  'cro', 'cake', 'shib', 'ada', 'avax',
                  'trx', 'ltc', 'matic', 'okb', 'klay',
                  'doge', 'dot', 'steth', 'near', 'xmr',
                  'link', 'atom', 'xlm', 'etc', 'flow',
                  'algo', 'uni', 'ape', 'vet', 'xnc',
                  'paxg', 'xtz', 'icp', 'axs', 'fil']

FROM_DATE = '2017-01-01'
TO_DATE = '2022-01-01'

QUOTE_CURRENCY = 'usd'

PERIOD = 365

NUM_SIMULATIONS = 100000


@dataclass
class PortfolioRequest:

    def __init__(self,
                 tickers,
                 asset_class,
                 from_date=FROM_DATE,
                 to_date=TO_DATE,
                 quote_currency=QUOTE_CURRENCY,
                 period=PERIOD,
                 num_simulations=NUM_SIMULATIONS,
                 daily_return_fun="daily_pct_change_return",
                 solver=None,
                 future_price=None):
        self.tickers = tickers
        self.asset_class = asset_class
        self.from_date = from_date
        self.to_date = to_date
        self.quote_currency = quote_currency
        self.period = period
        self.num_simulations = num_simulations
        self.daily_return_fun = daily_return_fun
        self.solver = solver
        self.future_price = future_price

    @staticmethod
    def from_dict(obj: Any) -> 'PortfolioRequest':
        logger.info('Request:'.format(obj))
        _tickers = obj.get("tickers")
        _asset_class = str(obj.get("asset_class"))
        _from_date = str(obj.get("from_date"))
        _to_date = str(obj.get("to_date"))
        _quote_currency = str(obj.get("quote_currency"))
        _period = int(obj.get("period"))
        _num_simulations = int(obj.get("num_simulations"))
        _daily_return_fun = str(obj.get("daily_return_fun", None))
        _solver = obj.get("solver", None)
        solver = None
        if _solver:
            _type = str(_solver.get("type", None))
            _target = float(_solver.get("target", None))
            solver = Solver(_type, _target)

        _future_price = bool(obj.get("future_price"))
        new_request = PortfolioRequest(_tickers,
                                       _asset_class,
                                       _from_date,
                                       _to_date,
                                       _quote_currency,
                                       _period,
                                       _num_simulations,
                                       _daily_return_fun,
                                       solver,
                                       _future_price)
        logger.info('Request was mapped properly...')
        return new_request


class Solver:
    def __init__(self, type, target):
        self.type = type
        self.target = target
