from flask import Blueprint, Response
import json

from application.api import PortfolioService
from application.api.CommonResponse import CommonResponse

portfolio = Blueprint('portfolio', __name__)
portfolio.url_prefix = '/portfolio'

APPLICATION_JSON = 'application/json'


@portfolio.route('/')
def index():
    return Response(json.dumps("Portfolio API"), mimetype=APPLICATION_JSON)


@portfolio.route('/calculate')
def calculate_portfolio():
    PortfolioService.calculate_portfolio()
    return Response(json.dumps(CommonResponse('OK', 'all is cool...').__dict__),
                    mimetype=APPLICATION_JSON)