import os
import os.path
import yaml
from seplis.utils import json_loads

config = {
    'debug': False,
    'database': {
        'url': 'sqlite:///seplis.db',
    },
    'web': {
        'url': 'http://localhost:8001/',
        'cookie_secret': 'CHANGE_ME',
        'port': 8001,
        'api_url': 'http://localhost:8002/1',
        'client_id': 'CHANGE_ME',
    },
    'api': {
        'url': 'http://localhost:8002/',
        'port': 8002,
        'max_workers': 5,
    },
    'redis': {
        'ip': '127.0.0.1',
        'port': 6379,
    },
    'logging': {
        'level': 'warning',
        'path': None,
        'max_size': 100 * 1000 * 1000,# ~ 95 mb
        'num_backups': 10,
    },
    'elasticsearch': 'localhost:9200',
}

def load(path=None):
    default_paths = [
        './seplis_conf.yaml',
        '~/seplis_conf.yaml',
        '/etc/seplis/seplis_conf.yaml',
    ]
    if not path:
        path = os.environ.get('SEPLIS_CONFIG', None)
        if not path:
            for p in default_paths:
                p = os.path.expanduser(p)
                if os.path.isfile(p):
                    path = p
                    break
    if not path:
        raise Exception('No config file specified.')
    if not os.path.isfile(path):
        raise Exception('Config: "{}" could not be found.'.format(path))
    with open(path) as f:
        data = yaml.load(f)
    for key in data:
        if key in config:
            if isinstance(config[key], dict):
                config[key].update(data[key])
            else:
                config[key] = data[key]

        