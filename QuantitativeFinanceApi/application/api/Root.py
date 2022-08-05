import json

from flask import Blueprint, render_template

from QuantitativeFinanceApi.application.api.common.QFLogger import QFLogger

logger = QFLogger(logger_name=__name__).get_logger()

root = Blueprint('root', __name__)
root.url_prefix = '/'

APPLICATION_JSON = 'application/json'


@root.route('/')
def index():
    return render_template('index.html')
