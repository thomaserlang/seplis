import os
import os.path
import yaml
from seplis.utils import json_loads

config = {
    'debug': False,
    'database': 'sqlite:///seplis.db',
    'web': {
        'url': 'https://seplis.net',
        'cookie_secret': 'CHANGE_ME',
        'port': 8001,
        'image_url': 'http://storitch.local',
    },
    'sentry_dsn': None,
    'api': {
        'url': 'https://api.seplis.net',
        'port': 8002,
        'max_workers': 5,
        'storitch': 'http://storitch.local',
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
    'client': {
        'access_token': None,
        'thetvdb': None,
        'id': 'CHANGE_ME',
    },
}

def load(path=None):
    default_paths = [
        './seplis_conf.yaml',
        '~/seplis_conf.yaml',
        '/etc/seplis/seplis_conf.yaml',
        '/etc/seplis_conf.yaml',
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

        