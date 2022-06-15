import json
import traceback

from flask import Blueprint, Response, request

from QuantitativeFinanceApi.application.api.capm import CapmService
from QuantitativeFinanceApi.application.api.capm.CapmRequest import CapmRequest
from QuantitativeFinanceApi.application.api.common.QFException import QFException
from QuantitativeFinanceApi.application.api.common.QFLogger import QFLogger
from QuantitativeFinanceApi.application.api.common.Responses import CommonResponse, Status, CapmResponse
from QuantitativeFinanceApi.application.api.common.Storage import RequestId

logger = QFLogger(logger_name=__name__).get_logger()

capm = Blueprint('capm', __name__)
capm.url_prefix = '/capm'

APPLICATION_JSON = 'application/json'

requestIdGenerator = RequestId()


@capm.route('/')
def index():
    return Response(json.dumps("CAPM API"), mimetype=APPLICATION_JSON)


@capm.route('/calculate', methods=['POST'])
def calculate_portfolio():
    request_id = requestIdGenerator.get_next_request_id()
    logger.info('New request: {}'.format(request_id))
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        capm_request = CapmRequest.from_dict(request.json)
        try:
            beta, expected_return = CapmService.calculate(capm_request)
            return Response(json.dumps(CapmResponse(beta, expected_return).__dict__),
                            mimetype=APPLICATION_JSON)
        except QFException as e:
            traceback.print_stack()
            return Response(json.dumps(request_id, CommonResponse(Status.error, 'Invalid request: ' + e.__str__()).__dict__),
                            mimetype=APPLICATION_JSON)
        else:
            traceback.print_stack()
            return Response(json.dumps(request_id, CommonResponse(Status.error, 'Internal error, check the request').__dict__),
                            mimetype=APPLICATION_JSON)

    else:
        return Response(json.dumps(request_id, CommonResponse(Status.error, 'Content-Type not supported!').__dict__),
                        mimetype=APPLICATION_JSON)