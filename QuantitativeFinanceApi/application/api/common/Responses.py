class Status:
    successful = 'Successful'
    error = 'Error'


class CommonResponse:

    def __init__(self, request_id, status, message):
        self.request_id = request_id
        self.status = status
        self.message = message


class PortfolioResponse(CommonResponse):

    def __init__(self, request_id, performance, weights_by_underlying, performance_by_underlying, future_prices, urls):
        super(PortfolioResponse, self).__init__(request_id=request_id, status=Status.successful, message='Completed...')
        self.performance = performance
        self.weights_by_underlying = weights_by_underlying
        self.performance_by_underlying = performance_by_underlying
        self.future_prices = future_prices
        self.urls = urls


class CapmResponse(CommonResponse):

    def __init__(self, request_id, beta, expected_return):
        super(CapmResponse, self).__init__(request_id=request_id, status=Status.successful, message='Completed...')
        self.beta = beta
        self.expected_return = expected_return