import sys
from seplis.api import elasticcreate
from collections import defaultdict

rebuilders = defaultdict(list)

def register(ident):
    '''Decorate a method to register a rebuilder.'''
    def decorate(fn):
        rebuilders[ident].append(fn)
        return fn
    return decorate

def rebuild():
    from seplis.api import models
    print('Rebuilding cache/search data for:')
    sys.stdout.flush()
    database.redis.flushdb()
    elasticcreate.create_indices()
    for ident in rebuilders:
        print('... {}'.format(ident))
        for rebuilder in rebuilders[ident]:
            rebuilder()
        sys.stdout.flush()
    print('Done!')

def main():
    rebuild()