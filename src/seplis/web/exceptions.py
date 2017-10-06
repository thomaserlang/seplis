from tornado.web import HTTPError
from seplis import utils

class API_error(HTTPError):
    
    def __init__(self, status_code, code, message, errors=None, extra=None):
        '''
        :param status_code: int
            HTTP status code e.g. 400
        :param code: int
            internal error code
        :param message: str
        :param errors: list of error
        :param extra: object
            Extra information for the exception.
        '''
        super().__init__(status_code, message)
        self.status_code = status_code
        self.code = code
        self.errors = errors
        self.message = message
        self.extra = extra

    def __str__(self):
        result = '{} ({})'.format(self.message, self.code)
        if self.errors:
            result += '\n\nErrors:\n'
            result += utils.json_dumps(
                self.errors,
                indent=4, 
                separators=(',', ': ')
            )
        if self.extra:
            result += '\n\nExtra:\n'
            result += utils.json_dumps(
                self.extra,
                indent=4, 
                separators=(',', ': ')
            )
        return result

class Validation_exception(API_error):

    def __init__(self, errors):
        super().__init__(
            status_code=400,
            code=1001,
            message='one or more fields failed validation',
            errors=errors,
        )