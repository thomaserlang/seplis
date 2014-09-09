import functools
import sqlalchemy.orm.session
from contextlib import contextmanager
from seplis.connections import database

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
    try:
        yield s
    except:
        s.rollback()
        raise
    finally:
        s.close()