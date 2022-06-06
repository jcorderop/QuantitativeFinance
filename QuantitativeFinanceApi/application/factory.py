from flask import Flask

from QuantitativeFinanceApi.application.api.RestImage import plot
from QuantitativeFinanceApi.application.api.capm.CapmController import capm
from QuantitativeFinanceApi.application.api.portfolio.PortfolioController import portfolio


def create_app():
    app = Flask(__name__)
    app.register_blueprint(portfolio, url_prefix=portfolio.url_prefix)
    app.register_blueprint(capm, url_prefix=capm.url_prefix)
    app.register_blueprint(plot, url_prefix=plot.url_prefix)

    return app