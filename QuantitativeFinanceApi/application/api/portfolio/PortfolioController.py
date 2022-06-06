import json
import traceback

from flask import Blueprint, Response, request

from QuantitativeFinanceApi.application.api.common.FinanceException import FinanceException
from QuantitativeFinanceApi.application.api.common.Responses import CommonResponse, PortfolioResponse, Status
from QuantitativeFinanceApi.application.api.portfolio import PortfolioRequest, PortfolioService

portfolio = Blueprint('portfolio', __name__)
portfolio.url_prefix = '/portfolio'

APPLICATION_JSON = 'application/json'


@portfolio.route('/')
def index():
    return Response(json.dumps("Portfolio API"), mimetype=APPLICATION_JSON)


'''
https://stackabuse.com/how-to-get-and-parse-http-post-body-in-flask-json-and-form-data/
'''


@portfolio.route('/calculate', methods=['POST'])
def calculate_portfolio():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        pf_request = PortfolioRequest.PortfolioRequest.from_dict(request.json)
        try:
            performance, weights_by_underlying = PortfolioService.calculate_portfolio(pf_request)
            return Response(json.dumps(PortfolioResponse(performance, weights_by_underlying).__dict__),
                            mimetype=APPLICATION_JSON)
        except FinanceException as e:
            traceback.print_stack()
            return Response(json.dumps(CommonResponse(Status.error, 'Invalid request: ' + e.__str__()).__dict__),
                            mimetype=APPLICATION_JSON)
        else:
            traceback.print_stack()
            return Response(json.dumps(CommonResponse(Status.error, 'Internal error, check the request').__dict__),
                            mimetype=APPLICATION_JSON)

    else:
        return Response(json.dumps(CommonResponse(Status.error, 'Content-Type not supported!').__dict__),
                        mimetype=APPLICATION_JSON)
