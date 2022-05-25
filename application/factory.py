from flask import Flask

from application.api.capm.CapmController import capm
from application.api.portfolio.PortfolioController import portfolio


def create_app():
    app = Flask(__name__)
    app.register_blueprint(portfolio, url_prefix=portfolio.url_prefix)
    app.register_blueprint(capm, url_prefix=capm.url_prefix)

    return app