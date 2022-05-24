from flask import Flask
from application.api.PortfolioController import portfolio


def create_app():
    app = Flask(__name__)
    app.register_blueprint(portfolio, url_prefix=portfolio.url_prefix)

    return app