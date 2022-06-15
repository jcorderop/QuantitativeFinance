from QuantitativeFinanceApi.application.api.common.Sigleton import SingletonMeta


class RequestId(metaclass=SingletonMeta):

    __REQUEST_ID__ = 10000

    def get_next_request_id(self):
        self.__REQUEST_ID__ = self.__REQUEST_ID__ + 1;
        return self.__REQUEST_ID__


class Storage(metaclass=SingletonMeta):

    def __init__(self):
        self.mem_table = {}

    def __validate_request_id__(self, request_id):
        if request_id is None or request_id == '':
            raise Exception('Request Id cannot be null or empty.')

    def store(self, request_id, section, content):
        request_id = str(request_id)
        self.__validate_request_id__(request_id)
        req_section = self.mem_table.get(request_id, {})
        req_section[section] = content
        self.mem_table[request_id] = req_section

    def get_request_id(self, request_id):
        return self.mem_table.get(str(request_id), None)


