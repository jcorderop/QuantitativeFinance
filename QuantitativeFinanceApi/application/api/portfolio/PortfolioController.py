import json
import traceback

from flask import Blueprint, Response, request

from QuantitativeFinanceApi.application.api.common.QFException import QFException
from QuantitativeFinanceApi.application.api.common.QFLogger import QFLogger
from QuantitativeFinanceApi.application.api.common.Responses import CommonResponse, PortfolioResponse, Status
from QuantitativeFinanceApi.application.api.common.Storage import RequestId
from QuantitativeFinanceApi.application.api.portfolio import PortfolioRequest, PortfolioService

logger = QFLogger(logger_name=__name__).get_logger()

portfolio = Blueprint('portfolio', __name__)
portfolio.url_prefix = '/portfolio'

APPLICATION_JSON = 'application/json'


@portfolio.route('/')
def index():
    return Response(json.dumps("Portfolio API"), mimetype=APPLICATION_JSON)


@portfolio.route('/plot/<request_id>', methods=['GET'])
def plot_portfolio(request_id):
    logger.info('New request to plot portfolio: {}'.format(request_id))
    return PortfolioService.plot_portfolio(request_id)


'''
https://stackabuse.com/how-to-get-and-parse-http-post-body-in-flask-json-and-form-data/
'''


@portfolio.route('/calculate', methods=['POST'])
def calculate_portfolio():
    request_id = RequestId().get_next_request_id()
    logger.info('New request: {}'.format(request_id))
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        pf_request = PortfolioRequest.PortfolioRequest.from_dict(request.json)
        try:
            performance, weights_by_underlying, performance_by_underlying = PortfolioService.calculate_portfolio(request_id,
                                                                                                                 pf_request)
            future_prices = PortfolioService.calculate_future_price(pf_request)
            urls = PortfolioService.get_relevant_urls(request_id, pf_request)

            return Response(json.dumps(PortfolioResponse(request_id,
                                                         performance,
                                                         weights_by_underlying,
                                                         performance_by_underlying,
                                                         future_prices,
                                                         urls).__dict__),
                            mimetype=APPLICATION_JSON)
        except QFException as e:
            traceback.print_stack()
            return Response(
                json.dumps(CommonResponse(request_id, Status.error, 'Invalid request: ' + e.__str__()).__dict__),
                mimetype=APPLICATION_JSON)
        else:
            traceback.print_stack()
            return Response(
                json.dumps(CommonResponse(request_id, Status.error, 'Internal error, check the request').__dict__),
                mimetype=APPLICATION_JSON)

    else:
        return Response(json.dumps(CommonResponse(request_id, Status.error, 'Content-Type not supported!').__dict__),
                        mimetype=APPLICATION_JSON)
