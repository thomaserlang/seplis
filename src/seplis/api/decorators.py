import functools
import sqlalchemy.orm.session
from tornado.web import HTTPError
from seplis.api import exceptions
from seplis.api.connections import database
from seplis import config
from contextlib import contextmanager

def authenticated(level):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user:
                raise exceptions.Not_signed_in_exception()
            if self.current_user.level < level:
                raise exceptions.Restricted_access_exception(
                    self.current_user.level, 
                    level
                )
            if self.request.method in ('PUT', 'POST', 'DELETE'):
                if 'user_id' in kwargs:
                    if int(kwargs['user_id']) != self.current_user.id:
                        self.check_edit_another_user_right()
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


def auto_session(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, sqlalchemy.orm.session.Session):
                kwargs['session'] = arg
                args = list(args)
                args.remove(arg)
                args = tuple(args)
                break        
        if ('session' in kwargs) and (kwargs['session'] != None):
            return method(self, *args, **kwargs)
        else:
            with new_session() as session:
                kwargs['session'] = session
                result = method(self, *args, **kwargs)
                session.commit()
                return result
    return wrapper

def auto_pipe(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):     
        if ('pipe' in kwargs) and (kwargs['pipe'] != None):
            return method(self, *args, **kwargs)
        else:                
            kwargs['pipe'] = database.redis.pipeline()
            result = method(self, *args, **kwargs)
            kwargs['pipe'].execute()
            return result
    return wrapper

@contextmanager
def new_session():
    '''
    Creates a new session, remembers to close and rollsback
    if the session fails.

    Usage:
    
        with new_session() as session:
            session.add(some_model())
    '''
    s = database.session()
    s.autoflush = False
    try:
        yield s
    except:
        # breaks the unittest
        #if not config['debug']:
        #    s.rollback()
        raise
    finally:
        s.close()