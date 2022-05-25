class Status:
    successful = 'Successful'
    error = 'Error'


class CommonResponse:

    def __init__(self, status, message):
        self.status = status
        self.message = message


class PortfolioResponse(CommonResponse):

    def __init__(self, performance, weights_by_underlying):
        super(PortfolioResponse, self).__init__(Status.successful, 'Completed...')
        self.performance = performance
        self.weights_by_underlying = weights_by_underlying