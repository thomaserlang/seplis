import functools
from tornado.web import HTTPError
from seplis.api import exceptions

def authenticated(level=0):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user:
                raise exceptions.Not_signed_in_exception()
            if self.current_user.level < level:
                raise exceptions.Restricted_access_exception(self.current_user.level, level)
            return method(self, *args, **kwargs)
        return wrapper
    return decorator